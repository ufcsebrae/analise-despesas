# analise_despesa/extracao.py
import logging
import time
import pandas as pd
from typing import Dict, Any
from . import database
from .exceptions import AnaliseDespesaError

logger = logging.getLogger(__name__)

def buscar_dados_completos(params: Dict[str, Any]) -> pd.DataFrame:
    """
    Lê TODOS os dados para um ano inteiro da VIEW 'vw_AnaliseDespesas'.
    """
    logger.info("Iniciando extração completa da VIEW 'vw_AnaliseDespesas'")
    inicio = time.perf_counter()

    engine = database.obter_conexao("SPSVSQL39_FINANCA")
    
    sql_query = f"""
        SELECT * 
        FROM vw_AnaliseDespesas
        WHERE [DATA] >= '{params["data_inicio"]}'
          AND [DATA] < DATEADD(day, 1, CAST('{params["data_fim"]}' AS DATE))
    """
    try:
        df = pd.read_sql(sql_query, engine)
        fim = time.perf_counter()
        logger.info(f"Leitura da VIEW concluída em {fim - inicio:.2f}s. ({len(df)} linhas)")
        return df
    except Exception as e:
        logger.error(f"Falha crítica na leitura da VIEW. Erro: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler dados da VIEW.") from e
