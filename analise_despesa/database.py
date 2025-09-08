# analise_despesa/database.py
"""
Módulo responsável pela interação com o banco de dados:
criação de conexões e persistência de dados.
"""
import logging
from typing import Union
from urllib.parse import quote_plus

import pandas as pd
import sqlalchemy
from sqlalchemy.engine import Engine

from .config import CONEXOES

logger = logging.getLogger(__name__)

def obter_conexao(nome_conexao: str) -> Union[Engine, str]:
    """
    Cria e retorna um objeto de conexão (Engine SQLAlchemy ou string MDX).

    Retorna:
        Engine | str: Objeto de conexão pronto para uso.
    """
    info = CONEXOES[nome_conexao]
    tipo = info.get("tipo", "sql").lower()

    if tipo in ("sql", "azure_sql"):
        # Lógica de construção da URL foi centralizada e melhorada
        url = sqlalchemy.engine.URL.create(
            drivername="mssql+pyodbc",
            query={"odbc_connect": _construir_odbc_str(info)}
        )
        return sqlalchemy.create_engine(url)
    
    elif tipo == "mdx":
        return info["str_conexao"]
    
    raise ValueError(f"Tipo de conexão '{tipo}' não suportado.")

def _construir_odbc_str(info: dict) -> str:
    """Função auxiliar para montar a string ODBC."""
    driver = info["driver"]
    servidor = info["servidor"]
    banco = info["banco"]
    
    odbc_parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={servidor}",
        f"DATABASE={banco}",
    ]
    if info.get("trusted_connection"):
        odbc_parts.append("Trusted_Connection=yes")
    if info.get("authentication"):
        odbc_parts.append(f"Authentication={info['authentication']}")

    return ";".join(odbc_parts)

def salvar_dataframe(df: pd.DataFrame, nome_tabela: str, nome_conexao: str):
    """
    Salva um DataFrame em uma tabela de banco de dados.
    """
    if df.empty:
        logger.warning(f"DataFrame para a tabela '{nome_tabela}' está vazio. Nada foi salvo.")
        return

    logger.info(f"Iniciando salvamento de {len(df)} linhas na tabela '{nome_tabela}'...")
    try:
        engine = obter_conexao(nome_conexao)
        with engine.connect() as conn:
            df.to_sql(
                name=nome_tabela,
                con=conn,
                if_exists="replace",
                index=False
            )
        logger.info(f"Dados salvos com sucesso em '{nome_tabela}'.")
    except Exception as e:
        logger.error(f"Falha ao salvar dados na tabela '{nome_tabela}'. Erro: {e}", exc_info=True)
