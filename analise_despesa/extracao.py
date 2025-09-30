# analise_despesa/extracao.py
# VERSÃO FINAL: Lê a VIEW completa do banco de dados.

import logging
import time
import pandas as pd
from typing import Dict, Any

from . import database
from .exceptions import AnaliseDespesaError
from sqlalchemy import text
from .utils import carregar_sql

logger = logging.getLogger(__name__)



def buscar_dados_completos(params: Dict[str, Any]) -> pd.DataFrame:
    """Lê TODOS os dados para um ano inteiro da VIEW 'vw_AnaliseDespesas'."""
    logger.info("Iniciando extração completa da VIEW 'vw_AnaliseDespesas'")
    inicio = time.perf_counter()

    engine = database.obter_conexao("SPSVSQL39_FINANCA")
    
    # Carrega a query do arquivo .sql
    sql_query_str = carregar_sql('sql/extracao_completa_vw.sql')
    sql_query = text(sql_query_str) # Mantém o uso do text()
    
    try:
        df = pd.read_sql(sql_query, engine, params={"ano": params['ano']})
        
        fim = time.perf_counter()
        logger.info(f"Leitura da VIEW concluída em {fim - inicio:.2f}s. ({len(df)} linhas)")
        return df
    except Exception as e:
        logger.error(f"Falha crítica na leitura da VIEW 'vw_AnaliseDespesas'. Erro: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler dados da VIEW.") from e
