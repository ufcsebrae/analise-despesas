# analise_despesa/extracao.py
import logging
import time
import pandas as pd
from typing import Optional, Dict, Any

from . import database
from .queries import consultas
from .query_executor import CriadorDataFrame
from .exceptions import QueryNaoEncontradaError, FalhaDeConexaoError

logger = logging.getLogger(__name__)

# ESTA É A ÚNICA DEFINIÇÃO DA FUNÇÃO NO ARQUIVO
def buscar_dados(nome_da_query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Busca dados utilizando uma consulta pré-definida e parâmetros opcionais.

    Args:
        nome_da_query (str): A chave da consulta no dicionário 'consultas'.
        params (dict, optional): Parâmetros para a query SQL.

    Returns:
        pd.DataFrame: O resultado da consulta como um DataFrame.
    """
    if nome_da_query not in consultas:
        raise QueryNaoEncontradaError(nome_da_query)

    consulta_obj = consultas[nome_da_query]
    logger.info(f"Iniciando extração da consulta: '{consulta_obj.titulo}'")
    inicio = time.perf_counter()

    try:
        conexao_obj = database.obter_conexao(consulta_obj.conexao)
        
        executor = CriadorDataFrame(
            conexao_obj=conexao_obj,
            consulta_sql=consulta_obj.sql,
            tipo=consulta_obj.tipo,
            params=params
        )
        
        df = executor.executar()

        fim = time.perf_counter()
        if not df.empty:
            logger.info(f"Consulta '{consulta_obj.titulo}' concluída em {fim - inicio:.2f}s. "
                        f"({len(df)} linhas)")
        else:
            logger.warning(f"Consulta '{consulta_obj.titulo}' não retornou dados.")
            
        return df

    except ValueError as e:
        logger.error(f"Erro de configuração para a query '{nome_da_query}': {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Falha crítica na extração '{nome_da_query}'. Erro: {e}", exc_info=True)
        raise FalhaDeConexaoError(f"Falha ao executar a query '{nome_da_query}'.") from e

