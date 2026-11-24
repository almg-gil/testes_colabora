import hmac
import io
import re
import zipfile
from urllib.parse import quote, urlsplit
from xml.etree import ElementTree as ET

import requests
import streamlit as st
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title='Teste WebDAV ALMG', page_icon='📁')
st.title('Teste de conexao - WebDrive ALMG')
st.caption('Somente leitura: este aplicativo nao grava nem altera arquivos.')


def secret(name):
    value = st.secrets.get(name, '')
    if not value or not str(value).strip():
        raise ValueError(f'Configure o segredo {name} no Streamlit.')
    return str(value).strip()


def url_for(base, user, relative):
    # Keep all path components encoded separately (including spaces and accents).
    base = base.rstrip('/')
    if urlsplit(base).scheme != 'https' or urlsplit(base).hostname != 'webdrive.almg.gov.br':
        raise ValueError('WEB_DAV_BASE deve ser https://webdrive.almg.gov.br/remote.php/dav/files')
    if urlsplit(base).path != '/remote.php/dav/files':
        raise ValueError('WEB_DAV_BASE tem um caminho inesperado.')
    if not re.fullmatch(r'm\d{5,6}', user, flags=re.IGNORECASE):
        raise ValueError('WEB_DAV_USUARIO deve ser uma matricula como m12345 (5 ou 6 digitos).')
    components = [quote(user, safe='')] + [quote(p, safe='') for p in relative.split('/') if p]
    return base + '/' + '/'.join(components)


def propfind(session, url):
    return session.request('PROPFIND', url, headers={'Depth': '0', 'Content-Type': 'application/xml'},
        data=b'<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:displayname/><d:getetag/><d:getcontentlength/><d:resourcetype/></d:prop></d:propfind>',
        timeout=(10, 35), allow_redirects=False)


def explain(status):
    return {207: 'Encontrado e acessivel.', 301: 'Redirecionamento inesperado.', 302: 'Redirecionamento inesperado.',
            401: 'Credencial recusada (ou senha de aplicativo necessaria).',
            403: 'Permissao negada.', 404: 'Recurso nao encontrado nesse caminho.',
            405: 'PROPFIND nao permitido.', 423: 'Recurso bloqueado.'}.get(status, f'HTTP {status}')


def list_sheet_names(content):
    if not zipfile.is_zipfile(io.BytesIO(content)):
        raise ValueError('O arquivo recebido nao e um pacote ODS valido (ZIP).')
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        mime = z.read('mimetype').decode('ascii', 'replace').strip()
        if mime != 'application/vnd.oasis.opendocument.spreadsheet':
            raise ValueError('MIME inesperado: arquivo nao parece ser uma planilha ODS.')
        with z.open('content.xml') as f:
            names = []
            # Streaming XML for large worksheets.
            table_ns = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}'
            for _event, el in ET.iterparse(f, events=('start',)):
                if el.tag == table_ns + 'table':
                    names.append(el.attrib.get(table_ns + 'name', ''))
            return names

try:
    user = secret('WEB_DAV_USUARIO')
    password = secret('WEB_DAV_SENHA_APP')
    gate_password = secret('SENHA_TESTE_STREAMLIT')
    base = st.secrets.get('WEB_DAV_BASE', 'https://webdrive.almg.gov.br/remote.php/dav/files')
    folder = st.secrets.get('WEB_DAV_PASTA', 'GDI-GIL/Testes')
    filename = st.secrets.get('WEB_DAV_ARQUIVO', 'Controle de Atividades 2026.ods')
    folder_url = url_for(base, user, folder)
    file_url = url_for(base, user, folder.strip('/') + '/' + filename)
except Exception as exc:
    st.error(str(exc))
    st.stop()

# Protect this diagnostic from anonymous visitors on public Streamlit Community Cloud.
entered = st.text_input('Senha do aplicativo de teste (nao e a senha institucional)', type='password')
if not entered or not hmac.compare_digest(entered, gate_password):
    st.info('Informe a senha de teste para iniciar a verificacao.')
    st.stop()

st.write('Pasta configurada: `GDI-GIL/Testes` (ou valor de WEB_DAV_PASTA)')
st.write('Arquivo configurado:', filename)
if st.button('Testar conexao e leitura do ODS', type='primary'):
    try:
        session = requests.Session()
        session.auth = HTTPBasicAuth(user, password)
        session.headers.update({'User-Agent': 'Streamlit-WebDAV-ALMG-ReadOnly-Test/1.0'})
        folder_response = propfind(session, folder_url + '/')
        st.write('Verificacao da pasta:', folder_response.status_code, '-', explain(folder_response.status_code))
        if folder_response.status_code != 207:
            st.stop()
        file_response = propfind(session, file_url)
        st.write('Verificacao do arquivo:', file_response.status_code, '-', explain(file_response.status_code))
        if file_response.status_code != 207:
            st.stop()
        etag = file_response.headers.get('ETag', '')
        if etag:
            st.write('ETag:', etag)
        with session.get(file_url, stream=True, timeout=(10, 90), allow_redirects=False) as response:
            response.raise_for_status()
            # 25MB cap for diagnostic memory safety.
            max_bytes = 25 * 1024 * 1024
            buf = io.BytesIO()
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if chunk:
                    if buf.tell() + len(chunk) > max_bytes:
                        raise ValueError('Arquivo maior que 25 MB; aumente o limite no codigo se necessario.')
                    buf.write(chunk)
        tabs = list_sheet_names(buf.getvalue())
        st.success(f'Leitura OK: {len(tabs)} abas encontradas. Nenhum arquivo foi alterado.')
        st.write('Primeiras 15 abas:', tabs[:15])
        st.write('Aba MODELO presente:', 'SIM' if 'MODELO' in tabs else 'NAO')
        st.write('Tamanho recebido:', f'{len(buf.getvalue()):,}', 'bytes')
    except requests.exceptions.RequestException as exc:
        # Do not print the exception's URL: may expose user identifiers.
        st.error(f'Falha de conexao HTTP: {type(exc).__name__}. Verifique conectividade, senha de aplicativo e permissoes.')
    except Exception as exc:
        st.error(f'Teste nao concluido: {exc}')
