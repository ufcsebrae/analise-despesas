# analise_despesa/extracao.py
# VERSÃO FINAL (AGORA COM A CERTEZA QUE OS SQLS ESTÃO COM '?'):
# Usa '?' na query e passa os parâmetros como uma TUPLA.

import logging
import pandas as pd
from . import database
from .exceptions import AnaliseDespesaError
from .utils import carregar_sql

logger = logging.getLogger(__name__)

def buscar_dados_realizado(ano: int) -> pd.DataFrame:
    """Lê os dados BRUTOS de despesas, usando marcador '?' na query."""
    logger.info("Iniciando extração de dados BRUTOS do Realizado (estilo de parâmetro '?').")
    
    engine = database.obter_conexao("SPSVSQL39_FINANCA")
    # Agora, sql_query_str DEVE conter '?' em vez de ':ano'.
    sql_query_str = carregar_sql('sql/extracao_realizado.sql')
    
    try:
        # Passamos os parâmetros como uma TUPLA -> (ano,)
        # A vírgula é importante para garantir que o Python crie uma tupla de um único elemento.
        # Agora que o SQL tem '?', esta chamada está 100% correta.
        df = pd.read_sql(sql_query_str, engine, params=(ano,))
        
        logger.info(f"Leitura do REALIZADO BRUTO concluída ({len(df)} linhas).")
        return df
    except Exception as e:
        logger.error(f"Falha ao ler dados do Realizado. Verifique se o arquivo 'extracao_realizado.sql' realmente usa '?' como marcador de parâmetro. Erro detalhado: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler dados do Realizado.") from e

def buscar_dados_orcamento(id_periodo: str) -> pd.DataFrame:
    """Lê os dados de ORÇAMENTO, usando marcador '?' na query."""
    logger.info("Iniciando extração de dados de ORÇAMENTO (estilo de parâmetro '?').")

    engine = database.obter_conexao("SPSVSQL39_HubDados")
    # Agora, sql_query_str DEVE conter '?' em vez de ':id_periodo'.
    sql_query_str = carregar_sql('sql/extracao_orcamento.sql')
    
    try:
        # Aplicando a mesma sintaxe de TUPLA aqui.
        df = pd.read_sql(sql_query_str, engine, params=(id_periodo,))
        
        logger.info(f"Leitura do ORÇAMENTO concluída ({len(df)} linhas).")
        return df
    except Exception as e:
        logger.error(f"Falha ao ler dados de Orçamento. Verifique se o arquivo 'extracao_orcamento.sql' usa '?' como marcador de parâmetro. Erro detalhado: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler dados de Orçamento.") from e
