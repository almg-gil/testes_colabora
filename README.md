# ALMG — teste completo de extração de diários reais e geração de ODS via WebDAV

Este aplicativo Streamlit é **separado do aplicativo original**. Reaproveita, sem trocar por exemplos fictícios, os processadores e a distribuição de tarefas enviados pelo usuário no código de 4.559 linhas. O arquivo gerado é uma CÓPIA da planilha ODS existente no WebDrive, atualizada somente após confirmação explícita.

## Arquivos

- `app.py`: interface, seleção de datas, extração real, WebDAV e validação.
- `extracao_original.py`: funções originais de extração de PDFs, geração das linhas, distribuição e consulta ao Google Drive/Calendar.
- `ods_worker.py`: manipulação da planilha com LibreOffice UNO em processo separado.
- `requirements.txt`: dependências Python.
- `packages.txt`: LibreOffice e python3-uno para Streamlit Community Cloud.
- `secrets.toml.example`: exemplos de variáveis obrigatórias.

## Como executar no Streamlit

1. Crie um repositório **privado** (não inclua senhas) e envie os cinco arquivos de código/configuração, deixando `app.py` na raiz. Se preferir, use um novo aplicativo Streamlit Community Cloud ligado a esse repositório.
2. Use **Settings → Secrets** para copiar as configurações WebDAV que funcionaram no teste anterior. A rota mostrada pelo próprio WebDrive da ALMG é `/remote.php/webdav`.
3. Mantenha as credenciais do serviço Google **iguais às do aplicativo original**: `gcp_service_account` e `GOOGLE_CALENDAR_ID`, pois o extrator original busca o Diário Administrativo no Google Drive e consulta afastamentos pelo Google Calendar. Se houver `calendar_impersonate_user`, mantenha também. Não cole suas credenciais no repositório nem nesta conversa.
4. Deixe `ENABLE_REMOTE_WRITE = "false"` no primeiro teste.
5. Escolha **Data do jornal a extrair**. Há um campo separado de **Data para consultar Diário Administrativo e afastamentos** para preservar a regra operacional do aplicativo original: em alguns casos (segunda-feira), a data de trabalho e a edição do jornal são diferentes. Nenhum ajuste automático oculto será feito.
6. A data selecionada gera uma aba `DDMM` (ex.: 20/11/2026 → `2011`), inserida após `MODELO`. Se já existir, a operação é bloqueada e não tenta extrair nem sobrescrever.
7. Clique **1. Extrair diários reais e preparar ODS**. A operação usa os PDFs do Executivo, Legislativo e Administrativo reais e as regras originais de distribuição de tarefas.
8. Se alguma fonte falhar, a geração **será bloqueada**: não serão gravados campos vazios que possam parecer uma extração bem-sucedida. Corrija o erro de acesso ou selecione uma data cuja edição esteja disponível.
9. Se a extração for concluída, baixe **CSV por seção** e o **ODS preenchido com dados reais** para comparar com suas abas históricas.
10. Para gravar **somente na pasta de testes**, altere para `ENABLE_REMOTE_WRITE = "true"` em Secrets, reinicie o app se necessário, execute novamente o passo 7, confira a planilha baixada e marque a confirmação para habilitar o botão **2. Gravar a nova aba no WebDrive**.
11. O aplicativo utiliza o ETag recebido na leitura e o cabeçalho HTTP `If-Match` no PUT. Se a planilha tiver sido alterada, o WebDrive poderá retornar `412` e impedir a sobrescrita. Após o PUT, o aplicativo baixa o ODS novamente e confirma a nova aba.

## Segredos (Secrets)

Veja `secrets.toml.example`. Nomes de configuração:

```toml
WEB_DAV_BASE = "https://webdrive.almg.gov.br/remote.php/webdav"
WEB_DAV_USUARIO = "m12345"
WEB_DAV_SENHA_APP = "TOKEN_SEGURO_DO_WEBDRIVE"
WEB_DAV_PASTA = "GDI-GIL/Testes"
WEB_DAV_ARQUIVO = "Controle de Atividades 2026.ods"
SENHA_TESTE_STREAMLIT = "SENHA_EXCLUSIVA_DO_TESTE"
ENABLE_REMOTE_WRITE = "false"
GOOGLE_CALENDAR_ID = "ID_EXISTENTE_DO_APP_ORIGINAL"
```

O secret `gcp_service_account` também é necessário, como no aplicativo original. A aplicação restringe o caminho de escrita a `GDI-GIL/Testes/Controle de Atividades 2026.ods` e não oferece escolha de destino nesta versão.

## Limitações e avisos

- O código usa **dados reais**, mas ainda não foi testado contra os serviços institucionais a partir deste ambiente. O primeiro teste real de autenticação/leitura já funcionou no aplicativo anterior, mas este novo pacote ainda precisa ser executado no Streamlit.
- A rotina do Executivo instala Chromium pelo Playwright na primeira execução se necessário. Isso pode exigir permissões ou dependências adicionais no Streamlit Cloud.
- A leitura do Diário Administrativo depende das permissões do Google Drive configuradas na conta de serviço original; se a pasta corporativa não estiver acessível na nova implantação, a extração será interrompida.
- O código original de busca de afastamentos pode retornar aviso de configuração não encontrada; esse aviso bloqueia a geração para evitar distribuir tarefas para servidores afastados.
- A planilha possui seção de **Diário da Justiça** sem extrator no código original; ela permanece vazia, e o total respectivo é zero. A seção de implantação de normas antigas não é preenchida automaticamente.
- A existência de muitas abas e de mesclagens complexas pode causar diferenças visuais em versões do LibreOffice. Compare a cópia baixada antes de permitir a gravação remota.
- Uma sessão colaborativa aberta no editor do WebDrive ainda pode gerar conflitos, mesmo com ETag. Faça testes somente com a cópia, sem edições simultâneas durante a geração.
- A senha `SENHA_TESTE_STREAMLIT` é uma **senha de teste compartilhada**, não autenticação individual por matrícula. Esse aplicativo NÃO está pronto para acesso público ou produção.
- O conteúdo da planilha de testes tem registros operacionais. Confirme que o envio à instância Streamlit Community Cloud e o armazenamento dos segredos estão permitidos pelas políticas institucionais.
