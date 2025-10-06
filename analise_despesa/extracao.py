# analise_despesa/extracao.py (VERSÃO FINAL COM BUSCA DE UNIDADES)

import logging
import pandas as pd
from . import database
from .exceptions import AnaliseDespesaError
from .utils import carregar_sql
from typing import List

logger = logging.getLogger(__name__)

def buscar_dados_realizado(ano: int) -> pd.DataFrame:
    """Lê os dados BRUTOS de despesas do arquivo SQL."""
    logger.info("Iniciando extração de dados BRUTOS do Realizado.")
    
    engine = database.obter_conexao("SPSVSQL39_FINANCA")
    
    try:
        sql_query_str = carregar_sql('sql/extracao_realizado.sql')
        
        df = pd.read_sql(sql_query_str, engine, params=(ano,))
        
        logger.info(f"Leitura do REALIZADO BRUTO concluída ({len(df)} linhas).")
        logger.debug(f"Colunas extraídas: {df.columns.tolist()}")

        colunas_necessarias = ['VALOR', 'DATA', 'PROJETO', 'FORNECEDOR', 'CC', 'UNIDADE', 'COD_CONTA', 'DESC_NIVEL_4']
        colunas_faltando = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltando:
            logger.error(f"ERRO FATAL: As seguintes colunas essenciais não foram encontradas no resultado da query: {colunas_faltando}. Verifique o script em 'sql/extracao_realizado.sql'.")
            raise AnaliseDespesaError(f"Extração falhou em trazer colunas essenciais: {colunas_faltando}")

        return df
    except Exception as e:
        logger.error(f"Falha ao ler dados do Realizado. Verifique a conexão e o script SQL. Erro detalhado: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler dados do Realizado.") from e

def buscar_dados_orcamento(id_periodo: str) -> pd.DataFrame:
    """Lê os dados de ORÇAMENTO."""
    logger.info("Iniciando extração de dados de ORÇAMENTO.")

    engine = database.obter_conexao("SPSVSQL39_HubDados")
    sql_query_str = carregar_sql('sql/extracao_orcamento.sql')
    
    try:
        df = pd.read_sql(sql_query_str, engine, params=(id_periodo,))
        logger.info(f"Leitura do ORÇAMENTO concluída ({len(df)} linhas).")
        return df
    except Exception as e:
        logger.error(f"Falha ao ler dados de Orçamento. Erro: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler dados de Orçamento.") from e

# --- NOVA FUNÇÃO ---
def buscar_unidades_disponiveis() -> List[str]:
    """Busca no banco de dados todas as unidades de negócio únicas."""
    logger.info("Buscando lista de unidades de negócio disponíveis...")
    engine = database.obter_conexao("SPSVSQL39_FINANCA")
    try:
        # A query assume que a sua view principal é a fonte das unidades
        query = "SELECT DISTINCT UNIDADE FROM vw_AnaliseDespesa WHERE UNIDADE IS NOT NULL ORDER BY UNIDADE ASC"
        df_unidades = pd.read_sql(query, engine)
        unidades = df_unidades['UNIDADE'].tolist()
        logger.info(f"{len(unidades)} unidades encontradas.")
        return unidades
    except Exception as e:
        logger.error(f"Não foi possível buscar a lista de unidades. Erro: {e}")
        return []
