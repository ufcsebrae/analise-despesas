# analise_despesa/config.py
# VERSÃO FINAL: Centraliza TODAS as configurações do projeto.

import os
from typing import Dict, Any, Union, List
from pathlib import Path
from dotenv import load_dotenv

# Carrega os SEGREDOS do arquivo .env
load_dotenv()

# --- PARÂMETRO DA "MÁQUINA DO TEMPO" REMOVIDO ---
# A lógica de sobrescrita de mês agora é feita de forma interativa no main.py

# --- DEFINIÇÃO DE CAMINHOS ---
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- PARÂMETROS GLOBAIS DA ANÁLISE (NÃO SÃO SEGREDOS) ---
PARAMETROS_ANALISE: Dict[str, Union[int, str]] = {
    "ANO_REFERENCIA": 2025,
    "ID_PERIODO_ORCAMENTO": "27",
    "ARQUIVO_CSV_VERIFICACAO": str(OUTPUT_DIR / "base_completa_extraida.csv")
}

# --- PARÂMETROS PARA MÓDULOS ESPECÍFICOS (NÃO SÃO SEGREDOS) ---
PROJETOS_A_IGNORAR_ANOMALIAS: List[str] = [
    "Suporte a Negócios - Remuneração de Recursos Humanos Relacionado a Negócios",
    "Gestão Operacional - Remuneração de Recursos Humanos - Custeio Administrativo",
    "Contrato de Temporários"
]

PROJETOS_FOLHA_PAGAMENTO: List[str] = [
    "Suporte a Negócios - Remuneração de Recursos Humanos Relacionado a Negócios",
    "Gestão Operacional - Remuneração de Recursos Humanos - Custeio Administrativo",
]

# --- MAPEAMENTO DE GESTORES (AGORA É O "MODO PADRÃO/AUTOMÁTICO") ---
MAPA_GESTORES: Dict[str, str] = {
    "SP - Finanças e Controladoria": "cesargl@sebraesp.com.br",
    "SP - Cultura Empreendedora": "cesargl@sebraesp.com.br",
    "SP - Administração": "cesargl@sebraesp.com.br"
}

# --- CONFIGURAÇÕES DE CONEXÃO (LÊ OS SEGREDOS DO .env) ---
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
