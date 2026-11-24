# Teste de acesso WebDAV da ALMG (somente leitura)

## Implantacao no Streamlit Community Cloud

1. Crie um repositorio privado com `app.py` e `requirements.txt`. Nao envie seu arquivo de secrets para o repositorio.
2. Crie um aplicativo no Streamlit Community Cloud apontando para `app.py`.
3. Em **App settings > Secrets**, insira os dados do `secrets.toml.example`, substituindo os placeholders. Use uma senha de aplicativo do Nextcloud, se a politica institucional permitir. Nunca envie as credenciais neste chat.
4. Abra o aplicativo, informe a senha de teste e clique em **Testar conexao e leitura do ODS**.
5. Resultado esperado: respostas HTTP 207 para pasta e arquivo; mensagem `Leitura OK`, relacao de abas e `MODELO presente: SIM`.

## Permissoes e seguranca

- O aplicativo apenas consulta metadados e baixa o ODS para inspecao em memoria; nao faz PUT, MOVE, DELETE, nem modifica a planilha.
- A pasta `GDI-GIL/Testes` e uma suposicao com base na navegacao exibida. Se a pasta foi compartilhada e montada com outro nome, ajuste `WEB_DAV_PASTA` para o caminho que consta na visao **Arquivos** da conta autenticada.
- Matrícula nao substitui autenticacao. O acesso depende de credencial do WebDAV em `WEB_DAV_SENHA_APP` e de senha exclusiva para proteger a pagina publica do Streamlit em `SENHA_TESTE_STREAMLIT`.
- Se houver 401, confira usuario e credencial de aplicativo; 403 indica falta de permissao; 404 significa que o caminho nao foi localizado sob a conta autenticada.
- Por seguranca, nunca coloque senhas em codigo-fonte ou logs nem desative a verificacao TLS.
- Se a politica institucional proibir usar credenciais do WebDrive no Streamlit Cloud, nao prossiga com a configuracao; solicite uma conta tecnica ou integracao autorizada.
