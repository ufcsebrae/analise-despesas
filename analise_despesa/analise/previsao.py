# analise_despesa/analise/previsao.py
# NOVO ARQUIVO: Contém a lógica para previsão de séries temporais.

import pandas as pd
import logging
from statsmodels.tsa.statespace.sarima import SARIMAX

logger = logging.getLogger(__name__)

def prever_proximos_meses(df_historico_mensal: pd.DataFrame, meses_a_prever: int = 3) -> pd.DataFrame:
    """
    Prevê os gastos para os próximos meses com base no histórico mensal.

    Args:
        df_historico_mensal (pd.DataFrame): DataFrame com as colunas 'Mês' e 'Valor'.
        meses_a_prever (int): Quantidade de meses a serem previstos.

    Returns:
        pd.DataFrame: DataFrame com a previsão, incluindo valores mínimos e máximos.
    """
    logger.info(f"Iniciando previsão de despesas para os próximos {meses_a_prever} meses.")
    
    # O modelo precisa de um índice de data e pelo menos alguns pontos para treinar
    if len(df_historico_mensal) < 4:
        logger.warning("Não há dados históricos suficientes para gerar uma previsão confiável (mínimo de 4 meses).")
        return pd.DataFrame()

    # Prepara a série temporal para o modelo
    # Converte a coluna 'Mês' (ex: 'Jan', 'Fev') para um índice de data real
    mes_map_inverso = {'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6, 'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12}
    df_historico_mensal['num_mes'] = df_historico_mensal['Mês'].map(mes_map_inverso)
    # Assume o ano atual para criar o índice de data
    ano_atual = pd.Timestamp.now().year
    df_historico_mensal.index = pd.to_datetime(df_historico_mensal.apply(lambda row: f"{ano_atual}-{int(row['num_mes'])}-01", axis=1))
    
    serie_temporal = df_historico_mensal['Valor'].resample('MS').sum()

    try:
        # Instancia e treina o modelo SARIMAX.
        # Parâmetros simples (1,1,1) são um bom ponto de partida.
        # A ordem sazonal está zerada por simplicidade nesta primeira versão.
        modelo_sarima = SARIMAX(serie_temporal, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
        resultado_sarima = modelo_sarima.fit(disp=False)

        # Gera a previsão
        previsao_obj = resultado_sarima.get_forecast(steps=meses_a_prever)
        
        # Converte a previsão para um DataFrame amigável
        previsao_df = previsao_obj.summary_frame(alpha=0.10) # Intervalo de confiança de 90%
        
        previsao_df.reset_index(inplace=True)
        previsao_df['Mês'] = previsao_df['index'].dt.strftime('%b/%Y')
        
        # Renomeia as colunas para o relatório
        previsao_final = previsao_df[['Mês', 'mean', 'mean_ci_lower', 'mean_ci_upper']]
        previsao_final.columns = ['Mês Previsto', 'Previsão', 'Mínimo Esperado', 'Máximo Esperado']
        
        logger.info("Previsão gerada com sucesso.")
        return previsao_final

    except Exception as e:
        logger.error(f"Falha ao gerar a previsão de despesas. Erro: {e}", exc_info=True)
        return pd.DataFrame()

