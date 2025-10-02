# analise_despesa/query_executor.py
# VERSÃO CORRIGIDA FINAL: Usa text() para traduzir os parâmetros.

import logging
from typing import Union, Optional, Dict, Any
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text
from .exceptions import AnaliseDespesaError

logger = logging.getLogger(__name__)

class CriadorDataFrame:
    """Executa uma consulta e retorna um DataFrame do pandas."""

    def __init__(self, conexao_obj: Union[Engine, str], consulta_sql: str, tipo: str, params: Optional[Dict[str, Any]] = None):
        self.conexao_obj = conexao_obj
        self.consulta_sql = consulta_sql
        self.tipo = tipo
        self.params = params

    def executar(self) -> pd.DataFrame:
        """Executa a consulta e retorna o resultado."""
        logger.info(f"Executando consulta do tipo '{self.tipo}' com parâmetros: {self.params}")
        try:
            if self.tipo in ("sql", "azure_sql"):
                # CORREÇÃO FINAL: Usa pd.read_sql_query com text() e params.
                return pd.read_sql_query(text(self.consulta_sql), self.conexao_obj, params=self.params)

            elif self.tipo == "mdx":
                from pyadomd import Pyadomd
                with Pyadomd(self.conexao_obj) as conn:
                    return conn.to_dataframe(self.consulta_sql)
            
            raise ValueError(f"Tipo de consulta '{self.tipo}' não suportado.")

        except Exception as e:
            raise AnaliseDespesaError(f"Erro ao executar a consulta: {e}") from e
