import pandas as pd
import logging
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

def detectar_anomalias_de_valor(df: pd.DataFrame, contamination: float = 0.01) -> pd.DataFrame:
    """
    Usa o algoritmo Isolation Forest para detectar despesas com valores anômalos.
    'contamination' é a proporção esperada de anomalias nos dados (ex: 0.01 = 1%).
    """
    logger.info("Iniciando detecção de anomalias com Isolation Forest...")
    df_analise = df.copy()
    
    # O modelo precisa de um array 2D, então usamos [[]]
    valores = df_analise[['VALOR']]
    
    # O modelo funciona melhor se os valores nulos ou zero forem tratados
    valores = valores.fillna(0)

    # Cria e treina o modelo de IA
    modelo_ia = IsolationForest(contamination=contamination, random_state=42)
    df_analise['ANOMALIA'] = modelo_ia.fit_predict(valores)
    
    # O modelo retorna 1 para normal e -1 para anomalia. Vamos mapear para algo mais claro.
    df_analise['ANOMALIA'] = df_analise['ANOMALIA'].map({1: 'Normal', -1: 'Anomalia'})
    
    anomalias_encontradas = df_analise[df_analise['ANOMALIA'] == 'Anomalia']
    logger.warning(f"Detecção de anomalias concluída. Encontradas {len(anomalias_encontradas)} possíveis anomalias.")
    
    return df_analise
