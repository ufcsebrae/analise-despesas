# analise_despesa/config.py
"""
Define as configurações de conexão, parâmetros de execução e mapeamentos
utilizados pelo projeto.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Union

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


# ==============================================================================
# ||                      1. PARÂMETROS GLOBAIS DA ANÁLISE                      ||
# ==============================================================================
# Centraliza os parâmetros que controlam a execução do pipeline.
# Para alterar o período da análise, descomente o bloco desejado e comente os outros.

PARAMETROS_ANALISE: Dict[str, Union[int, str, bool]] = {
    
    # --- OPÇÃO 1: Análise Anual (Modo Padrão) ---
    # Para rodar a análise para um ano fiscal inteiro.
    "TIPO_PERIODO": "anual",
    "ANO_REFERENCIA": 2025,
    "ARQUIVO_CSV_LOCAL": 'C:/Temp/RelatoriosSQL/base_completa_2025.csv'

    # --- OPÇÃO 2: Análise Mensal ---
    # Para rodar a análise para um mês específico de um ano.
    # "TIPO_PERIODO": "mensal",
    # "ANO_REFERENCIA": 2024,
    # "MES_REFERENCIA": 9,  # 1 = Janeiro, ..., 12 = Dezembro

    # --- OPÇÃO 3: Período Customizado ---
    # Para definir um intervalo de datas manualmente.
    # "TIPO_PERIODO": "customizado",
    # "DATA_INICIO_CUSTOM": "2024-08-01",
    # "DATA_FIM_CUSTOM": "2024-08-15",

    # --- OPÇÃO 4: Análise do Mês Anterior (Totalmente Automático) ---
    # Para agendamentos mensais. O script calculará o mês anterior automaticamente.
    # "TIPO_PERIODO": "mes_anterior_automatico",
}


# ==============================================================================
# ||                      2. CONFIGURAÇÕES DE CONEXÃO                         ||
# ==============================================================================
# Define os dados de acesso para os diversos bancos de dados e serviços.

CONEXOES: Dict[str, Dict[str, Any]] = {
    "SPSVSQL39_FINANCA": {
        "tipo": "sql",
        "servidor": os.getenv("DB_SERVER_FINANCA"),
        "banco": os.getenv("DB_DATABASE_FINANCA"),
        "driver": "ODBC Driver 17 for SQL Server",
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

# --- 4. LISTA DE CONTAS PARA ANÁLISE ---
# Esta lista será passada como parâmetro para a função no banco de dados.
CONTAS_PARA_ANALISE = [
    '3.1.1.1.01.001', '3.1.1.1.01.002', '3.1.1.1.01.004', '3.1.1.1.01.005', '3.1.1.1.01.008',
    '3.1.1.1.02.001', '3.1.1.1.03.001', '3.1.1.1.04.001', '3.1.1.1.04.999', '3.1.1.2.01.004',
    '3.1.1.2.01.005', '3.1.1.2.01.006', '3.1.1.3.01.001', '3.1.1.3.01.002', '3.1.1.3.01.003',
    '3.1.1.3.01.004', '3.1.1.3.01.005', '3.1.1.3.01.008', '3.1.1.3.01.999', '3.1.2.1.01.001',
    '3.1.2.1.01.002', '3.1.2.1.02.001', '3.1.2.1.02.002', '3.1.2.1.02.003', '3.1.2.1.02.004',
    '3.1.2.1.02.005', '3.1.2.1.02.006', '3.1.2.1.02.007', '3.1.2.1.02.008', '3.1.2.1.02.009',
    '3.1.2.1.02.010', '3.1.2.1.02.013', '3.1.2.1.02.014', '3.1.2.1.02.019', '3.1.2.1.02.022',
    '3.1.2.1.02.999', '3.1.2.1.03.001', '3.1.2.2.01.001', '3.1.2.2.01.002', '3.1.2.2.01.003',
    '3.1.2.2.01.004', '3.1.2.2.01.005', '3.1.2.2.01.006', '3.1.2.2.01.008', '3.1.2.2.01.999',
    '3.1.2.2.02.001', '3.1.2.2.02.002', '3.1.2.2.02.004', '3.1.2.2.02.007', '3.1.2.2.02.999',
    '3.1.2.3.01.001', '3.1.3.1.01.001', '3.1.3.1.01.002', '3.1.3.1.01.003', '3.1.3.1.01.004',
    '3.1.3.1.01.005', '3.1.3.1.01.006', '3.1.3.1.01.999', '3.1.3.1.02.001', '3.1.3.1.02.002',
    '3.1.3.1.02.003', '3.1.3.1.02.004', '3.1.3.1.02.005', '3.1.3.1.02.006', '3.1.3.1.02.009',
    '3.1.3.1.02.010', '3.1.3.1.02.999', '3.1.3.2.01.001', '3.1.3.2.01.002', '3.1.3.2.01.003',
    '3.1.3.2.01.004', '3.1.3.2.01.999', '3.1.3.2.02.004', '3.1.3.3.01.001', '3.1.3.3.01.002',
    '3.1.3.3.01.003', '3.1.3.3.01.005', '3.1.3.3.01.007', '3.1.3.3.01.008', '3.1.3.3.01.999',
    '3.1.3.4.01.002', '3.1.3.4.01.003', '3.1.3.4.01.005', '3.1.3.4.01.999', '3.1.3.5.01.001',
    '3.1.3.5.01.002', '3.1.3.5.01.003', '3.1.3.5.01.004', '3.1.3.5.01.005', '3.1.3.6.01.001',
    '3.1.3.6.01.002', '3.1.3.6.01.003', '3.1.3.6.01.004', '3.1.3.6.01.005', '3.1.3.6.01.006',
    '3.1.3.6.01.999', '3.1.3.7.01.001', '3.1.3.7.01.004', '3.1.3.7.01.005', '3.1.3.7.01.006',
    '3.1.3.7.01.007', '3.1.3.7.01.008', '3.1.3.7.01.009', '3.1.3.7.01.010', '3.1.3.7.01.011',
    '3.1.3.7.01.015', '3.1.3.7.01.021', '3.1.3.7.01.023', '3.1.3.7.01.999', '3.1.3.8.01.001',
    '3.1.4.1.01.002', '3.1.4.1.01.003', '3.1.4.1.02.001', '3.1.4.2.01.001', '3.1.4.2.01.002',
    '3.1.4.2.01.004', '3.1.4.2.01.005', '3.1.4.2.01.006', '3.1.4.2.01.007', '3.1.4.2.01.999',
    '5.1.1.2.01.001', '5.2.2.2.01.001', '5.2.2.2.01.003', '5.2.2.2.01.004', '5.2.2.2.01.006',
    '5.2.4.1.01.001', '5.2.5.2.01.001'
]


# ==============================================================================
# ||                 3. MAPEAMENTO DE GESTORES POR UNIDADE                    ||
# ==============================================================================
# Mapeia a unidade de negócio (exatamente como vem do banco) para o e-mail do responsável.
# Apenas as unidades listadas aqui serão processadas pelo pipeline.

MAPA_GESTORES: Dict[str, str] = {
    # Chave: Nome EXATO da Unidade, como aparece no resultado da query SQL.
    # Valor: E-mail do gestor responsável.
    
    "SP - Finanças e Controladoria": "cesargl@sebraesp.com.br",
    "SP - Inovação": "cesargl@sebraesp.com.br",
    "SP - ER CAMPINAS": "cesargl@sebraesp.com.br",
    "SP - Gestão de Soluções e Transformação Digital": "cesargl@sebraesp.com.br"
}
