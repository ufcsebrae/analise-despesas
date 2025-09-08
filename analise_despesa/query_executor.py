# analise_despesa/query_executor.py
"""
Contém a classe CriadorDataFrame, responsável por executar uma consulta
e retornar os resultados como um DataFrame.
"""
import logging
from typing import Union
import pandas as pd
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

class CriadorDataFrame:
    """Executa uma consulta e retorna um DataFrame do pandas."""

    def __init__(self, conexao_obj: Union[Engine, str], consulta_sql: str, tipo: str):
        """
        Args:
            conexao_obj (Engine | str): O objeto de conexão (Engine ou string MDX).
            consulta_sql (str): A string da consulta SQL ou MDX a ser executada.
            tipo (str): O tipo de consulta ('sql', 'azure_sql', 'mdx').
        """
        self.conexao_obj = conexao_obj
        self.consulta_sql = consulta_sql
        self.tipo = tipo

    def executar(self) -> pd.DataFrame:
        """Executa a consulta e retorna o resultado."""
        logger.info(f"Executando consulta do tipo '{self.tipo}'...")
        try:
            if self.tipo in ("sql", "azure_sql"):
                return pd.read_sql_query(self.consulta_sql, self.conexao_obj)

            elif self.tipo == "mdx":
                from pyadomd import Pyadomd # Importação tardia
                with Pyadomd(self.conexao_obj) as conn:
                    return conn.to_dataframe(self.consulta_sql) # Mais simples
            
            raise ValueError(f"Tipo de consulta '{self.tipo}' não suportado.")

        except Exception as e:
            logger.error(f"Erro ao executar a consulta: {e}", exc_info=True)
            return pd.DataFrame()
