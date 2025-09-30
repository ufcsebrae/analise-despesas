# analise_despesa/config.py
# VERSÃO REATORADA PARA PORTABILIDADE

import os
from dotenv import load_dotenv
from typing import Dict, Any, Union
from pathlib import Path  # 1. Importar a biblioteca para lidar com caminhos

load_dotenv()

# 2. Definir o diretório raiz do projeto de forma dinâmica
# (funciona em qualquer computador)
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Definir um diretório padrão para todos os arquivos de saída (relatórios, logs, etc.)
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)  # Cria o diretório se ele não existir

# --- 1. PARÂMETROS GLOBAIS DA ANÁLISE ---
PARAMETROS_ANALISE: Dict[str, Union[int, str]] = {
    "ANO_REFERENCIA": 2025,
    
    # 4. Usar o novo caminho de saída dinâmico
    "ARQUIVO_CSV_VERIFICACAO": str(OUTPUT_DIR / "base_completa_extraida_hoje.csv")
}

# --- 2. MAPEAMENTO DE GESTORES ---
# (Esta seção permanece inalterada)
MAPA_GESTORES: Dict[str, str] = {
    "SP - Finanças e Controladoria": "cesargl@sebraesp.com.br",
    "SP - Inovação": "cesargl@sebraesp.com.br",
    "SP - ER CAMPINAS": "cesargl@sebraesp.com.br",
    "SP - Gestão de Soluções e Transformação Digital": "cesargl@sebraesp.com.br"
}

# --- 3. CONFIGURAÇÕES DE CONEXÃO ---
# (Esta seção permanece inalterada)
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
}
