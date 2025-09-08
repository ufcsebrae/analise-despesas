# analise_despesa/extracao.py
"""
Módulo responsável por orquestrar a extração de dados.
"""
import logging
import time
import pandas as pd

from . import database
from .queries import consultas
from .query_executor import CriadorDataFrame

logger = logging.getLogger(__name__)

def buscar_dados(nome_da_query: str) -> pd.DataFrame:
    """
    Busca dados utilizando uma consulta pré-definida.
    """
    if nome_da_query not in consultas:
        logger.error(f"A query '{nome_da_query}' não existe em queries.py")
        raise ValueError(f"Query não encontrada: '{nome_da_query}'")

    consulta_obj = consultas[nome_da_query]
    logger.info(f"Iniciando extração da consulta: '{consulta_obj.titulo}'")
    inicio = time.perf_counter()

    try:
        # 1. Pede ao 'database' para criar a conexão
        conexao_obj = database.obter_conexao(consulta_obj.conexao)
        
        # 2. Cria o executor com a conexão e a query
        executor = CriadorDataFrame(
            conexao_obj=conexao_obj,
            consulta_sql=consulta_obj.sql,
            tipo=consulta_obj.tipo
        )
        
        # 3. Executa e obtém o DataFrame
        df = executor.executar()

        fim = time.perf_counter()
        if not df.empty:
            logger.info(f"Consulta '{consulta_obj.titulo}' concluída em {fim - inicio:.2f}s. "
                        f"({len(df)} linhas)")
        return df

    except Exception as e:
        logger.error(f"Falha crítica na orquestração da extração '{nome_da_query}'. Erro: {e}", exc_info=True)
        return pd.DataFrame()
