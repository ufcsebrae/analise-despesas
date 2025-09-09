# analise_despesa/query_executor.py
"""
Contém a classe CriadorDataFrame, responsável por executar uma consulta
e retornar os resultados como um DataFrame.
"""
import logging
from typing import Union, Optional, Dict, Any
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text  # <--- 1. IMPORTAR a função text
from .exceptions import AnaliseDespesaError

logger = logging.getLogger(__name__)

class CriadorDataFrame:
    """Executa uma consulta e retorna um DataFrame do pandas."""

    def __init__(self, conexao_obj: Union[Engine, str], consulta_sql: str, tipo: str, params: Optional[Dict[str, Any]] = None):
        """
        Args:
            conexao_obj (Engine | str): O objeto de conexão.
            consulta_sql (str): A string da consulta SQL ou MDX.
            tipo (str): O tipo de consulta ('sql', 'azure_sql', 'mdx').
            params (dict, optional): Parâmetros a serem passados para a consulta.
        """
        self.conexao_obj = conexao_obj
        self.consulta_sql = consulta_sql
        self.tipo = tipo
        self.params = params

    def executar(self) -> pd.DataFrame:
        """Executa a consulta e retorna o resultado."""
        logger.info(f"Executando consulta do tipo '{self.tipo}' com parâmetros: {self.params}")
        try:
            if self.tipo in ("sql", "azure_sql"):
                # --- 2. APLICAÇÃO DA CORREÇÃO ---
                # Envolvemos a query em `text()` para que o SQLAlchemy processe
                # corretamente os parâmetros nomeados (ex: ':ano') e os converta
                # para o formato que o driver DBAPI (pyodbc) espera (geralmente '?').
                sql_statement = text(self.consulta_sql)
                return pd.read_sql_query(sql_statement, self.conexao_obj, params=self.params)

            elif self.tipo == "mdx":
                # MDX geralmente não usa parâmetros da mesma forma
                from pyadomd import Pyadomd
                with Pyadomd(self.conexao_obj) as conn:
                    return conn.to_dataframe(self.consulta_sql)
            
            raise ValueError(f"Tipo de consulta '{self.tipo}' não suportado.")

        except Exception as e:
            # Envolve a exceção original para não perder o contexto
            raise AnaliseDespesaError(f"Erro ao executar a consulta: {e}") from e
