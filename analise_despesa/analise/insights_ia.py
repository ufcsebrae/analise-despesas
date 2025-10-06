# analise_despesa/analise/insights_ia.py (VERSÃO FINAL COM DESC_NIVEL_4)
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from scipy.sparse import hstack
from typing import Dict, Tuple, Any

logger = logging.getLogger(__name__)

def detectar_anomalias_de_contexto(df: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
    if df.empty or len(df) < 2:
        logger.warning("Dados insuficientes para a análise de ocorrências atípicas de contexto.")
        return pd.DataFrame()
    logger.info("Iniciando detecção de ocorrências atípicas de contexto...")
    df_analise = df.copy()
    features_categoricas = ['FORNECEDOR', 'PROJETO']
    features_numericas = ['VALOR']
    df_analise[features_categoricas] = df_analise[features_categoricas].fillna('N/A')
    df_analise[features_numericas] = df_analise[features_numericas].fillna(0)
    encoder = OneHotEncoder(handle_unknown='ignore')
    features_encoded = encoder.fit_transform(df_analise[features_categoricas])
    features_final = hstack([df_analise[features_numericas], features_encoded])
    modelo_ia = IsolationForest(contamination=contamination, random_state=42)
    df_analise['ocorrencia_contexto'] = modelo_ia.fit_predict(features_final)
    ocorrencias_contexto = df_analise[df_analise['ocorrencia_contexto'] == -1].copy()
    logger.info(f"Análise de contexto concluída. Encontradas {len(ocorrencias_contexto)} ocorrências atípicas.")
    colunas_relevantes = ['DATA', 'FORNECEDOR', 'PROJETO', 'VALOR', 'COMPLEMENTO']
    return ocorrencias_contexto[colunas_relevantes]

def investigar_causa_raiz_ocorrencia(df_ocorrencias: pd.DataFrame, df_historico_completo: pd.DataFrame) -> pd.DataFrame:
    if df_ocorrencias.empty: return df_ocorrencias
    logger.info(f"Iniciando investigação de causa raiz para {len(df_ocorrencias)} ocorrências...")
    df_investigado = df_ocorrencias.copy()
    df_investigado['Justificativa IA'] = ''
    df_historico_completo['DATA'] = pd.to_datetime(df_historico_completo['DATA'])
    for idx, ocorrencia in df_investigado.iterrows():
        razoes = []
        hist_combinacao = df_historico_completo[(df_historico_completo['FORNECEDOR'] == ocorrencia['FORNECEDOR']) & (df_historico_completo['PROJETO'] == ocorrencia['PROJETO'])]
        if len(hist_combinacao) <= 1:
            razoes.append(f"Primeiro registro do fornecedor '{ocorrencia['FORNECEDOR']}' no projeto '{ocorrencia['PROJETO']}'.")
        else:
            media_historica = hist_combinacao[hist_combinacao.index != idx]['VALOR'].mean()
            if pd.notna(media_historica) and media_historica > 0 and ocorrencia['VALOR'] > media_historica * 5:
                razoes.append(f"Valor (R$ {ocorrencia['VALOR']:.0f}) é um pico significativo (>5x a média de R$ {media_historica:.0f}) para esta combinação.")
        hist_fornecedor = df_historico_completo[df_historico_completo['FORNECEDOR'] == ocorrencia['FORNECEDOR']]
        if len(hist_fornecedor) <= 1:
             razoes.append(f"Primeiro lançamento registrado para o fornecedor '{ocorrencia['FORNECEDOR']}' nesta unidade.")
        df_investigado.loc[idx, 'Justificativa IA'] = " | ".join(razoes) if razoes else "Combinação rara de Fornecedor, Projeto e Valor."
    logger.info("Investigação concluída.")
    return df_investigado

def segmentar_contas_por_comportamento(df_folha_unidade: pd.DataFrame, n_clusters: int = 3) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Dict[str, Any]]]:
    logger.info(f"Iniciando segmentação de contas contábeis (Nível 4) para a unidade com {n_clusters} clusters...")
    if df_folha_unidade.empty or 'DESC_NIVEL_4' not in df_folha_unidade.columns:
        logger.warning("DataFrame da folha vazio ou sem 'DESC_NIVEL_4'. Não é possível segmentar.")
        return {}, {}

    # --- CORREÇÃO: Agrupamento pelo DESC_NIVEL_4 ---
    df_mensal_conta = df_folha_unidade.groupby(['DESC_NIVEL_4', 'MES'])['VALOR'].sum().unstack(fill_value=0)
    df_comportamento = df_folha_unidade.groupby('DESC_NIVEL_4').agg(
        valor_total=('VALOR', 'sum'),
        frequencia=('VALOR', 'count')
    ).reset_index()

    df_comportamento['volatilidade_mensal'] = df_comportamento['DESC_NIVEL_4'].apply(lambda dc: df_mensal_conta.loc[dc].std() if dc in df_mensal_conta.index and len(df_mensal_conta.loc[dc].dropna()) > 1 else 0)
    df_comportamento = df_comportamento[(df_comportamento['valor_total'] != 0) & (df_comportamento['frequencia'] > 0)].copy()

    if len(df_comportamento) < n_clusters:
        n_clusters = len(df_comportamento) if len(df_comportamento) > 1 else 0
        if n_clusters == 0: return {}, {}
        logger.warning(f"Número de agrupamentos ({len(df_comportamento)}) é menor que o de clusters desejado ({n_clusters}). Ajustando para {n_clusters} clusters.")

    features_para_cluster = ['valor_total', 'frequencia', 'volatilidade_mensal']
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_comportamento[features_para_cluster]), columns=features_para_cluster, index=df_comportamento.index)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    df_comportamento['cluster'] = kmeans.fit_predict(df_scaled)

    clusters_tabelas = {}
    clusters_resumo = {}
    cluster_order = df_comportamento.groupby('cluster')['valor_total'].mean().sort_values(ascending=False).index
    
    mean_valor_total_global = df_comportamento['valor_total'].mean()
    mean_frequencia_global = df_comportamento['frequencia'].mean()
    mean_volatilidade_global = df_comportamento['volatilidade_mensal'].mean()

    for i, cluster_id in enumerate(cluster_order):
        df_cluster = df_comportamento[df_comportamento['cluster'] == cluster_id].copy()
        centroid_data = df_cluster[features_para_cluster].mean().to_dict()
        
        name = f"Perfil {i+1}: "
        description = ""

        is_high_value = centroid_data['valor_total'] > mean_valor_total_global
        is_high_frequency = centroid_data['frequencia'] > mean_frequencia_global
        is_high_volatility = centroid_data['volatilidade_mensal'] > mean_volatilidade_global * 1.2

        if is_high_value and is_high_frequency and not is_high_volatility:
            name += "Contas de Rotina e Alto Impacto (Ex: Salários e Encargos)"
            description = "Este perfil agrupa contas com valores totais elevados e alta frequência de lançamentos, caracterizando despesas essenciais e recorrentes da folha de pagamento, com pouca variação mensal. São contas estáveis e previsíveis, representando o custo fixo principal."
        elif is_high_volatility:
            name += "Contas de Eventos Esporádicos e Variáveis (Ex: Bônus, Rescisões)"
            description = "Aqui estão as contas cujos valores variam significativamente de mês a mês, indicando pagamentos não regulares ou eventos específicos como bônus, rescisões ou encargos sazonais. Exigem atenção especial devido à sua imprevisibilidade e picos de gastos."
        elif is_high_frequency and not is_high_value:
            name += "Contas de Benefícios e Baixo Valor Recorrente (Ex: Vale-Transporte)"
            description = "Este perfil inclui contas com muitos lançamentos, mas de valores unitários menores, representando benefícios ou despesas de baixo custo, porém muito frequentes. Somam um volume considerável ao longo do ano e geralmente são estáveis."
        elif not is_high_value and not is_high_frequency:
            name += "Contas de Pequeno Impacto e Baixa Atividade"
            description = "Agrupa contas com baixo valor total e pouca frequência de lançamentos, tipicamente despesas menores ou ajustes pontuais na folha de pagamento, que não representam um volume significativo de transações."
        else:
            name += "Contas de Comportamento Moderado"
            description = "Contas com um comportamento de gastos mais equilibrado, sem características extremas de valor, frequência ou volatilidade. Podem representar diversas despesas operacionais da folha de pagamento que não se encaixam claramente nos outros perfis."
        
        centroid_data['description'] = description
        
        # --- CORREÇÃO: Usando a coluna correta DESC_NIVEL_4 ---
        df_cluster_display = df_cluster[['DESC_NIVEL_4', 'valor_total', 'frequencia', 'volatilidade_mensal']].copy()
        df_cluster_display.rename(columns={
            'DESC_NIVEL_4': 'Agrupamento Contábil (Nível 4)',
            'valor_total': 'Valor Total (Ano)',
            'frequencia': 'Qtd. Lançamentos (Ano)',
            'volatilidade_mensal': 'Volatilidade Mensal (R$)'
        }, inplace=True)
        
        clusters_tabelas[name] = df_cluster_display.sort_values('Valor Total (Ano)', ascending=False)
        clusters_resumo[name] = centroid_data
        logger.info(f"Cluster {cluster_id} nomeado como '{name}' com {len(df_cluster)} agrupamentos.")
    logger.info("Segmentação de contas contábeis (Nível 4) concluída.")
    return clusters_tabelas, clusters_resumo
