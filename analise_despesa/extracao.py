# analise_despesa/extracao.py (VERSÃO FINAL COM QUERY OTIMIZADA)

import logging
import pandas as pd
from . import database
from .exceptions import AnaliseDespesaError
from .utils import carregar_sql
from typing import List
import re

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
    """Lê os dados de OR��AMENTO."""
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

def buscar_unidades_disponiveis() -> List[str]:
    """Busca no banco de dados todas as unidades de negócio únicas de forma otimizada."""
    logger.info("Buscando lista de unidades de negócio disponíveis...")
    engine = database.obter_conexao("SPSVSQL39_FINANCA")
    try:
        # --- CORREÇÃO OTIMIZADA ---
        # 1. Lê o script original para descobrir o nome da tabela/view
        query_original_bruta = carregar_sql('sql/extracao_realizado.sql')
        
        # 2. Usa uma expressão regular para encontrar o nome do objeto após a cláusula FROM
        # Isso é mais robusto do que um simples split.
        match = re.search(r'FROM\s+([a-zA-Z0-9_.\-\[\]]+)', query_original_bruta, re.IGNORECASE)
        
        if not match:
            logger.error("Não foi possível determinar o nome da tabela/view a partir do script 'extracao_realizado.sql'.")
            return []
            
        nome_tabela_view = match.group(1)
        logger.debug(f"Nome do objeto de dados identificado: {nome_tabela_view}")

        # 3. Cria e executa uma query nova, simples e rápida
        query_unidades = f"SELECT DISTINCT UNIDADE FROM {nome_tabela_view} WHERE UNIDADE IS NOT NULL ORDER BY UNIDADE ASC"
        
        df_unidades = pd.read_sql(query_unidades, engine)
        unidades = df_unidades['UNIDADE'].tolist()
        logger.info(f"{len(unidades)} unidades encontradas.")
        return unidades
    except Exception as e:
        logger.error(f"Não foi possível buscar a lista de unidades. Verifique se o script 'extracao_realizado.sql' está correto e se o nome do objeto é válido. Erro: {e}")
        return []
