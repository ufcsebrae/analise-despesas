# analise_despesa/analise/insights_ia.py
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

def detectar_anomalias_de_valor(df: pd.DataFrame, contamination: float = 0.01) -> pd.DataFrame:
    """Usa Isolation Forest para detectar anomalias na coluna 'VALOR'."""
    logger.info("Iniciando detecção de anomalias com Isolation Forest...")
    df_analise = df.copy()
    
    # Usa a coluna 'VALOR'
    valores = df_analise[['VALOR']]
    valores = valores.fillna(0)

    modelo_ia = IsolationForest(contamination=contamination, random_state=42)
    df_analise['ANOMALIA'] = modelo_ia.fit_predict(valores)
    
    df_analise['ANOMALIA'] = df_analise['ANOMALIA'].map({1: 'Normal', -1: 'Anomalia'})
    
    anomalias_encontradas = df_analise[df_analise['ANOMALIA'] == 'Anomalia']
    if len(anomalias_encontradas) > 0:
        logger.warning(f"Detecção de anomalias concluída. Encontradas {len(anomalias_encontradas)} possíveis anomalias.")
    else:
        logger.info("Detecção de anomalias concluída. Nenhuma anomalia encontrada.")
    
    return df_analise
