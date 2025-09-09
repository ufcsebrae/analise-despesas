# analise_despesa/exportacao.py
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def exportar_para_csv(df: pd.DataFrame, caminho_arquivo: str):
    """
    Exporta um DataFrame para um arquivo CSV.
    Garante que o diretório de destino exista.
    """
    if df.empty:
        logger.warning(f"DataFrame está vazio. Nenhum arquivo CSV será gerado em '{caminho_arquivo}'.")
        return

    logger.info(f"Exportando {len(df)} linhas para o arquivo CSV: '{caminho_arquivo}'...")
    try:
        # Garante que o diretório de saída exista
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        
        # Exporta para CSV com codificação UTF-8 e sem o índice do pandas
        df.to_csv(caminho_arquivo, index=False, encoding='utf-8-sig')
        
        logger.info("Arquivo CSV exportado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao exportar para CSV. Erro: {e}", exc_info=True)
        raise
