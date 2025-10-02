# analise_despesa/leitor_local.py
# VERSÃO FINAL: Corrigido para usar a coluna 'UNIDADE'

import logging
import time
import pandas as pd
from typing import Optional, Dict, Any
from .exceptions import AnaliseDespesaError

logger = logging.getLogger(__name__)

_FULL_DATA_CACHE: Optional[pd.DataFrame] = None
_LAST_FILE_PATH: Optional[str] = None

def carregar_e_fatiar_dados(params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Lê o CSV, armazena em cache e fatia em memória pela coluna 'UNIDADE'.
    """
    global _FULL_DATA_CACHE, _LAST_FILE_PATH

    if not params: raise ValueError("Parâmetros são obrigatórios.")

    try:
        arquivo_csv = params["caminho_csv"]
        unidade_gestora = params["unidade_gestora"]
        data_inicio = pd.to_datetime(params["data_inicio"])
        data_fim = pd.to_datetime(params["data_fim"])
    except KeyError as e:
        raise ValueError(f"Parâmetro obrigatório não encontrado: {e}")

    try:
        if _FULL_DATA_CACHE is None or _LAST_FILE_PATH != arquivo_csv:
            logger.info(f"Carregando base de dados completa do arquivo: '{arquivo_csv}'")
            inicio_leitura = time.perf_counter()
            
            _FULL_DATA_CACHE = pd.read_csv(
                arquivo_csv, sep=';', encoding='utf-8-sig',
                parse_dates=['DATA'], low_memory=False
            )
            
            _LAST_FILE_PATH = arquivo_csv
            fim_leitura = time.perf_counter()
            logger.info(f"Arquivo CSV carregado e em cache. ({len(_FULL_DATA_CACHE)} linhas em {fim_leitura - inicio_leitura:.2f}s)")
        else:
            logger.info("Usando dados em cache do arquivo CSV.")

        # --- PONTO CRÍTICO DA CORREÇÃO ---
        coluna_unidade = 'UNIDADE' 

        if coluna_unidade not in _FULL_DATA_CACHE.columns:
            raise AnaliseDespesaError(f"A coluna '{coluna_unidade}' não foi encontrada no CSV. Colunas disponíveis: {_FULL_DATA_CACHE.columns.tolist()}")

        df_unidade = _FULL_DATA_CACHE[
            (_FULL_DATA_CACHE[coluna_unidade] == unidade_gestora) &
            (_FULL_DATA_CACHE['DATA'] >= data_inicio) &
            (_FULL_DATA_CACHE['DATA'] <= data_fim)
        ].copy()

        logger.info(f"Fatiamento concluído. {len(df_unidade)} linhas encontradas para a unidade '{unidade_gestora}'.")
        return df_unidade

    except FileNotFoundError:
        logger.error(f"ERRO CRÍTICO: Arquivo '{arquivo_csv}' não foi encontrado.")
        raise
    except Exception as e:
        logger.error(f"Falha crítica ao processar o arquivo CSV local. Erro: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler ou fatiar o arquivo CSV.") from e
    