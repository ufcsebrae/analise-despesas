import pandas as pd
import logging

logger = logging.getLogger(__name__)

def tratar_dados_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Preenche valores nulos em colunas categóricas importantes."""
    logger.info("Iniciando tratamento de valores nulos...")
    
    # Faz uma cópia para evitar SettingWithCopyWarning
    df_limpo = df.copy()
    
    colunas_para_tratar = ['FORNECEDOR', 'CLASSIFICA', 'PROJETO', 'ACAO']
    for coluna in colunas_para_tratar:
        if coluna in df_limpo.columns:
            # Preenche nulos com um valor padrão claro
            df_limpo[coluna] = df_limpo[coluna].fillna('Não Informado')
            
    logger.info("Tratamento de nulos concluído.")
    return df_limpo
