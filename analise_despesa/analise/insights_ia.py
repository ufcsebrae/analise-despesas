# analise_despesa/analise/insights_ia.py (VERSÃO FINAL, SEM ALTERAÇÕES NESTA ETAPA)
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

def detectar_anomalias_de_valor(df: pd.DataFrame, contamination: float = 0.01) -> pd.DataFrame:
    logger.info("Iniciando classificação de lançamentos com Isolation Forest...")
    df_analise = df.copy()
    
    if df_analise.empty or 'VALOR' not in df_analise.columns:
        logger.warning("O DataFrame para detecção de lançamentos atípicos está vazio ou não contém a coluna 'VALOR'.")
        df_analise['Classificacao'] = None
        return df_analise

    valores = df_analise[['VALOR']].fillna(0)
    modelo_ia = IsolationForest(contamination=contamination, random_state=42)
    
    df_analise['Classificacao'] = modelo_ia.fit_predict(valores)
    
    df_analise['Classificacao'] = df_analise['Classificacao'].map({1: 'Lançamento Regular', -1: 'Lançamento Atípico'})
    
    anomalias_encontradas = df_analise[df_analise['Classificacao'] == 'Lançamento Atípico']
    if len(anomalias_encontradas) > 0:
        logger.warning(f"Detecção concluída. Encontrados {len(anomalias_encontradas)} possíveis lançamentos atípicos.")
    else:
        logger.info("Detecção concluída. Nenhum lançamento atípico encontrado.")
    
    return df_analise
