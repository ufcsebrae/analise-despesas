# analise_despesa/extracao.py
# VERSÃO FINAL: Lendo de um arquivo CSV local e fatiando em memória.

import logging
import time
import pandas as pd
from typing import Optional, Dict, Any

from .exceptions import AnaliseDespesaError

logger = logging.getLogger(__name__)

# Cache em memória para armazenar o DataFrame completo e evitar releituras do CSV.
_FULL_DATA_CACHE: Optional[pd.DataFrame] = None
_LAST_FILE_PATH: Optional[str] = None

def buscar_dados(nome_da_query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Lê dados de um arquivo CSV local, armazena em cache e fatia em memória
    conforme a unidade gestora e o período especificados.
    """
    global _FULL_DATA_CACHE, _LAST_FILE_PATH

    if nome_da_query != "BaseDespesas":
        raise NotImplementedError(f"A lógica de extração para '{nome_da_query}' não está configurada para leitura local.")
    
    if not params:
        raise ValueError("O dicionário de parâmetros 'params' é obrigatório.")

    try:
        # Extrai os parâmetros necessários do dicionário
        arquivo_csv = params["caminho_csv"]
        unidade_gestora = params["unidade_gestora"]
        data_inicio = pd.to_datetime(params["data_inicio"])
        data_fim = pd.to_datetime(params["data_fim"])
    except KeyError as e:
        raise ValueError(f"Parâmetro obrigatório não encontrado no dicionário 'params': {e}")

    try:
        # --- Lógica de Cache: Carrega o CSV completo APENAS uma vez ---
        if _FULL_DATA_CACHE is None or _LAST_FILE_PATH != arquivo_csv:
            logger.info(f"Carregando base de dados completa do arquivo local: '{arquivo_csv}'")
            inicio_leitura = time.perf_counter()
            
            # Lê o CSV, especificando o separador e a codificação corretos.
            # 'parse_dates' já converte a coluna 'DATA' para o formato datetime, o que é ótimo para performance.
            _FULL_DATA_CACHE = pd.read_csv(
                arquivo_csv, 
                sep=';', 
                encoding='utf-8-sig',
                parse_dates=['DATA'],
                low_memory=False
            )
            
            _LAST_FILE_PATH = arquivo_csv
            fim_leitura = time.perf_counter()
            logger.info(f"Arquivo CSV completo carregado e em cache. ({len(_FULL_DATA_CACHE)} linhas em {fim_leitura - inicio_leitura:.2f}s)")
        else:
            logger.info("Usando dados em cache do arquivo CSV.")

        # --- Fatiamento no Pandas ---
        logger.info(f"Fatiando dados em memória para a unidade: '{unidade_gestora}'")
        
        # O nome da coluna que contém a unidade gestora.
        # Se o nome for diferente no seu CSV, altere esta string.
        coluna_unidade = 'UNIDADE' 

        if coluna_unidade not in _FULL_DATA_CACHE.columns:
            raise AnaliseDespesaError(f"A coluna '{coluna_unidade}' não foi encontrada no arquivo CSV. Colunas disponíveis: {_FULL_DATA_CACHE.columns.tolist()}")

        # Filtra o DataFrame em memória
        df_unidade = _FULL_DATA_CACHE[
            (_FULL_DATA_CACHE[coluna_unidade] == unidade_gestora) &
            (_FULL_DATA_CACHE['DATA'] >= data_inicio) &
            (_FULL_DATA_CACHE['DATA'] <= data_fim)
        ].copy() # .copy() é crucial para evitar avisos de SettingWithCopyWarning

        logger.info(f"Fatiamento concluído. {len(df_unidade)} linhas encontradas para a unidade.")
        return df_unidade

    except FileNotFoundError:
        logger.error(f"ERRO CRÍTICO: O arquivo '{arquivo_csv}' não foi encontrado. "
                     "Execute o script 'exportar_relatorio.py' ou exporte manualmente do SSMS primeiro.")
        raise
    except Exception as e:
        logger.error(f"Falha crítica ao processar o arquivo CSV local. Erro: {e}", exc_info=True)
        raise AnaliseDespesaError("Falha ao ler ou fatiar o arquivo CSV.") from e
