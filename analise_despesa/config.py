# analise_despesa/config.py
"""
Define as configurações de conexão para os diversos bancos de dados
e serviços utilizados pelo projeto.
"""
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

CONEXOES = {
    "SPSVSQL39_FINANCA": {
        "tipo": "sql",
        "servidor": os.getenv("DB_SERVER_FINANCA"),
        "banco": os.getenv("DB_DATABASE_FINANCA"),
        "driver": "ODBC Driver 17 for SQL Server", # Removido '+' que não são necessários aqui
        "trusted_connection": True
    },
    "SPSVSQL39_HubDados": {
        "tipo": "sql",
        "servidor": os.getenv("DB_SERVER_HUB"),
        "banco": os.getenv("DB_DATABASE_HUB"),
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": True
    },
    "OLAP_SME": {
        "tipo": "mdx",
        "str_conexao": "Provider=MSOLAP;Data Source=NASRVUGESQLPW02;Catalog=SMEDW_V3_SSAS;",
    },
    "AZURE": {
        "tipo": "azure_sql",
        "servidor": "synapsesebraespprod-ondemand.sql.azuresynapse.net",
        "banco": "DatamartMeta",
        "driver": "ODBC Driver 17 for SQL Server",
        "authentication": "ActiveDirectoryInteractive"
    },
    "default": {
        "tipo": "sql",
        "servidor": "localhost",
        "banco": "master",
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": True
    }
}
MAPA_GESTORES = {
    # Chave: Nome EXATO da Unidade, como aparece no resultado da query SQL.
    # Valor: E-mail do gestor responsável.

    "SP - Finanças e Controladoria": "cesargl@sebraesp.com.br", # Substitua pelo e-mail real
    # "SP - Inovação": "gestor.inovacao@sebraesp.com.br",
    # "SP - ER CAMPINAS": "gestor.campinas@sebraesp.com.br",
    # "SP - Gestão de Soluções e Transformação Digital": "gestor.td@sebraesp.com.br"
}
