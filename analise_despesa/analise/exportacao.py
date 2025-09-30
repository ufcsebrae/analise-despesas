# analise_despesa/exportacao.py
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def exportar_dataframe_para_csv(df: pd.DataFrame, caminho_arquivo: str, nome_relatorio: str):
    """
    Função genérica para exportar qualquer DataFrame para um arquivo CSV.
    """
    # Garante que o diretório de saída exista
    try:
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
    except Exception as e:
        logger.error(f"Não foi possível criar o diretório de saída para '{nome_relatorio}'. Erro: {e}")
        return

    if df.empty:
        logger.warning(f"O DataFrame para '{nome_relatorio}' está vazio. Nenhum arquivo CSV será gerado.")
        return

    logger.info(f"Exportando {len(df)} linhas para o relatório '{nome_relatorio}' em: '{caminho_arquivo}'...")
    try:
        df.to_csv(
            caminho_arquivo,
            index=False,
            sep=';',
            encoding='utf-8-sig'
        )
        logger.info(f"Relatório '{nome_relatorio}' salvo com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao exportar o relatório '{nome_relatorio}'. Erro: {e}", exc_info=True)

