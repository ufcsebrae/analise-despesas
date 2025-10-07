# analise_despesa/analise/insights_ia.py (VERSÃO FINAL COM AJUSTE DE ROBUSTEZ)
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from scipy.sparse import hstack
from typing import Dict, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

def detectar_anomalias_de_contexto(df: pd.DataFrame, contamination: float = 0.03) -> pd.DataFrame:
    # (Código inalterado)
    if df.empty or len(df) < 10: return pd.DataFrame()
    logger.info("Iniciando detecção de ocorrências atípicas com Engenharia de Features e Z-Score...")
    df_analise = df.copy()
    df_analise['FREQ_FORNECEDOR'] = df_analise.groupby('FORNECEDOR')['FORNECEDOR'].transform('count')
    df_analise['FREQ_PROJETO'] = df_analise.groupby('PROJETO')['PROJETO'].transform('count')
    group_stats = df_analise.groupby(['FORNECEDOR', 'PROJETO'])['VALOR'].agg(['mean', 'std']).reset_index()
    df_analise = pd.merge(df_analise, group_stats, on=['FORNECEDOR', 'PROJETO'], how='left')
    df_analise['std'] = df_analise['std'].fillna(0)
    df_analise['Z_SCORE_VALOR'] = np.where(df_analise['std'] > 0, (df_analise['VALOR'] - df_analise['mean']) / df_analise['std'], 0)
    df_analise['Z_SCORE_VALOR'] = df_analise['Z_SCORE_VALOR'].fillna(0)
    features_para_analise = ['Z_SCORE_VALOR', 'FREQ_FORNECEDOR', 'FREQ_PROJETO']
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df_analise[features_para_analise])
    modelo_ia = IsolationForest(contamination=contamination, random_state=42)
    df_analise['ocorrencia_contexto'] = modelo_ia.fit_predict(features_scaled)
    ocorrencias_contexto = df_analise[df_analise['ocorrencia_contexto'] == -1].copy()
    logger.info(f"Análise de contexto com Z-Score concluída. Encontradas {len(ocorrencias_contexto)} ocorrências atípicas.")
    colunas_relevantes = ['DATA', 'FORNECEDOR', 'PROJETO', 'VALOR', 'COMPLEMENTO', 'Z_SCORE_VALOR']
    return ocorrencias_contexto[colunas_relevantes]

def investigar_causa_raiz_ocorrencia(df_ocorrencias: pd.DataFrame, df_historico_completo: pd.DataFrame) -> pd.DataFrame:
    # (Código inalterado)
    if df_ocorrencias.empty: return df_ocorrencias
    logger.info(f"Iniciando investigação de causa raiz para {len(df_ocorrencias)} ocorrências...")
    df_investigado = df_ocorrencias.copy()
    freq_fornecedor_geral = df_historico_completo['FORNECEDOR'].value_counts()
    freq_combinacao_geral = df_historico_completo.groupby(['FORNECEDOR', 'PROJETO']).size()
    justificativas = []
    for idx, ocorrencia in df_investigado.iterrows():
        razoes = []
        fornecedor, projeto = ocorrencia['FORNECEDOR'], ocorrencia['PROJETO']
        if 'Z_SCORE_VALOR' in ocorrencia and abs(ocorrencia['Z_SCORE_VALOR']) > 2.0: razoes.append(f"Valor (R$ {ocorrencia['VALOR']:.0f}) é um pico ou vale estatístico (Z-Score: {ocorrencia['Z_SCORE_VALOR']:.2f}) para esta combinação.")
        if freq_combinacao_geral.get((fornecedor, projeto), 0) <= 2: razoes.append(f"Combinação Fornecedor-Projeto rara (vista {freq_combinacao_geral.get((fornecedor, projeto), 0)}x no ano).")
        if freq_fornecedor_geral.get(fornecedor, 0) <= 3: razoes.append(f"Fornecedor com baixa atividade geral na unidade ({freq_fornecedor_geral.get(fornecedor, 0)} lançamentos no ano).")
        if not razoes: razoes.append("Combinação de fatores (valor, frequência) considerada incomum pela IA.")
        justificativas.append(" | ".join(razoes))
    df_investigado['Justificativa IA'] = justificativas
    df_investigado.drop(columns=['Z_SCORE_VALOR'], inplace=True, errors='ignore')
    logger.info("Investigação concluída.")
    return df_investigado

def segmentar_contas_por_comportamento(df_a_segmentar: pd.DataFrame, n_clusters: int = 3) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Dict[str, Any]]]:
    logger.info(f"Iniciando segmentação de contas contábeis (Nível 4) com {n_clusters} clusters...")
    if df_a_segmentar.empty or 'DESC_NIVEL_4' not in df_a_segmentar.columns:
        logger.warning("DataFrame para segmentação vazio ou sem 'DESC_NIVEL_4'.")
        return {}, {}
    df_mensal_conta = df_a_segmentar.groupby(['DESC_NIVEL_4', 'MES'])['VALOR'].sum().unstack(fill_value=0)
    df_comportamento = df_a_segmentar.groupby('DESC_NIVEL_4').agg(valor_total=('VALOR', 'sum'), frequencia=('VALOR', 'count')).reset_index()
    def calcular_cv(group_name):
        if group_name in df_mensal_conta.index:
            valores_mensais = df_mensal_conta.loc[group_name][df_mensal_conta.loc[group_name] > 0]
            if len(valores_mensais) < 2: return 0.0
            media = valores_mensais.mean()
            desvio_padrao = valores_mensais.std()
            if media > 0: return desvio_padrao / media
        return 0.0
    df_comportamento['coef_variacao'] = df_comportamento['DESC_NIVEL_4'].apply(calcular_cv)
    df_comportamento = df_comportamento[(df_comportamento['valor_total'] != 0) & (df_comportamento['frequencia'] > 0)].copy()
    
    # --- CORREÇÃO DE ROBUSTEZ ---
    if len(df_comportamento) < n_clusters:
        n_clusters = len(df_comportamento)
        if n_clusters < 2: # KMeans precisa de pelo menos 2 amostras para 1 cluster, ou n_samples >= n_clusters
            logger.warning(f"Apenas {len(df_comportamento)} agrupamentos contábeis encontrados. Não é possível executar a clusterização.")
            return {}, {}
        logger.warning(f"Número de agrupamentos ({len(df_comportamento)}) é menor que o de clusters desejado. Ajustando para {n_clusters} clusters.")

    features_para_cluster = ['valor_total', 'frequencia', 'coef_variacao']
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_comportamento[features_para_cluster]), columns=features_para_cluster, index=df_comportamento.index)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    df_comportamento['cluster'] = kmeans.fit_predict(df_scaled)
    clusters_tabelas = {}
    clusters_resumo = {}
    centroids = df_comportamento.groupby('cluster')[features_para_cluster].mean()
    prioridade = centroids.sort_values(by=['coef_variacao', 'frequencia', 'valor_total'], ascending=[False, False, False]).index
    nomes_usados = []
    perfil_counter = 1
    for cluster_id in prioridade:
        centroid_data = centroids.loc[cluster_id].to_dict()
        name, description = f"Perfil {perfil_counter}: ", ""
        if centroid_data['coef_variacao'] > 0.8 and 'Eventos Esporádicos' not in nomes_usados:
            name += "Contas de Eventos Esporádicos e Variáveis"
            description = "Contas com alta imprevisibilidade nos valores mensais, indicando pagamentos pontuais ou projetos sazonais (Ex: Consultorias, Manutenções não planejadas)."
            nomes_usados.append('Eventos Esporádicos')
        elif centroid_data['frequencia'] > df_comportamento['frequencia'].quantile(0.75) and 'Recorrência e Volume' not in nomes_usados:
            name += "Contas de Recorrência e Volume"
            description = "Contas com muitos lançamentos, indicando despesas operacionais constantes (Ex: Serviços de Limpeza, Licenças de Software)."
            nomes_usados.append('Recorrência e Volume')
        elif centroid_data['valor_total'] > df_comportamento['valor_total'].quantile(0.75) and 'Alto Impacto Financeiro' not in nomes_usados:
            name += "Contas de Alto Impacto Financeiro"
            description = "Agrupa contas com os maiores valores totais, representando os maiores desembolsos do período (Ex: Aluguéis, Grandes Contratos)."
            nomes_usados.append('Alto Impacto Financeiro')
        else:
            name += "Contas de Baixo Impacto e Atividade"
            description = "Contas com comportamento contido, representando despesas administrativas menores ou taxas pontuais."
            nomes_usados.append('Baixo Impacto')
        perfil_counter += 1
        centroid_data['description'] = description
        df_cluster = df_comportamento[df_comportamento['cluster'] == cluster_id].copy()
        df_cluster_display = df_cluster[['DESC_NIVEL_4', 'valor_total', 'frequencia', 'coef_variacao']].copy()
        df_cluster_display.rename(columns={'DESC_NIVEL_4': 'Agrupamento Contábil (Nível 4)', 'valor_total': 'Valor Total (Ano)', 'frequencia': 'Qtd. Lançamentos (Ano)', 'coef_variacao': 'Coeficiente de Variação (CV)'}, inplace=True)
        clusters_tabelas[name] = df_cluster_display.sort_values('Valor Total (Ano)', ascending=False)
        clusters_resumo[name] = centroid_data
        logger.info(f"Cluster {cluster_id} nomeado como '{name}' com {len(df_cluster)} agrupamentos.")
    logger.info("Segmentação de contas contábeis (Nível 4) concluída.")
    return clusters_tabelas, clusters_resumo
