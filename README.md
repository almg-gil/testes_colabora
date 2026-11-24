# Teste real - somente Executivo e Legislativo

Aplicativo Streamlit isolado que processa Jornal Minas Gerais (Executivo) e Diario do Legislativo da data escolhida. Nao consulta Diario Administrativo, Google Calendar nem servicos do Google. Nao requer credenciais Google.

## Instalar

Coloque app.py, extracao_original.py, ods_worker.py, requirements.txt e packages.txt na raiz do repositorio de testes do Streamlit. Configure os Secrets a partir de secrets.toml.example com o token WebDAV ja testado. Nao publique tokens no repositorio.

## Testar

1. Guarde uma copia do ODS de teste no WebDrive e remova apenas uma aba diaria da COPIA, nunca de MODELO ou do arquivo oficial.
2. Selecione a data do jornal no date picker. A aba criada sera DDMM.
3. Clique em '1. Extrair diarios reais e preparar ODS'. Sao extraidos dados reais do Executivo e Legislativo. O Administrativo fica sem dados extraidos; o Calendar nao e consultado.
4. Baixe o ZIP de CSVs e o ODS preenchido. Confira especialmente registros, totais, links, formatações e se a aba foi colocada logo apos MODELO.
5. Somente depois da conferencia, configure ENABLE_REMOTE_WRITE = "true", prepare novamente e confirme a gravacao no arquivo GDI-GIL/Testes/Controle de Atividades 2026.ods.

## Importante

A distribuicao de tarefas aplica as regras originais SEM considerar ferias e licencas, pois nao ha consulta ao Google Calendar. O ODS resultante nao altera o arquivo remoto ate confirmacao. O PUT WebDAV usa If-Match do ETag para prevenir sobrescrita entre download e envio. Isso nao substitui a necessidade de ninguem editar a COPIA enquanto a gravacao e feita. Os registros nao foram comparados com publicacoes remotas neste ambiente: este e um teste para executar no Streamlit.
