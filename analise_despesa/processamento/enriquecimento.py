import pandas as pd
import logging

logger = logging.getLogger(__name__)

def adicionar_colunas_de_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas de Mês, Ano e Trimestre a partir da coluna 'DATA'."""
    logger.info("Enriquecendo DataFrame com colunas de data (Mês, Trimestre)...")
    df_enriquecido = df.copy()
    
    # Garante que a coluna 'DATA' é do tipo datetime
    df_enriquecido['DATA'] = pd.to_datetime(df_enriquecido['DATA'])
    
    df_enriquecido['MES'] = df_enriquecido['DATA'].dt.month
    df_enriquecido['TRIMESTRE'] = df_enriquecido['DATA'].dt.quarter
    
    logger.info("Colunas de data adicionadas.")
    return df_enriquecido
