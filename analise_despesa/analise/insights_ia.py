# analise_despesa/analise/insights_ia.py (VERSÃO FINAL COM LÓGICA HIERÁRQUICA)
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from scipy.sparse import hstack
from typing import Dict, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

def detectar_anomalias_de_contexto(df: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
    # (Código inalterado)
    if df.empty or len(df) < 2: return pd.DataFrame()
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
    # (Código inalterado)
    if df_ocorrencias.empty: return df_ocorrencias
    logger.info(f"Iniciando investigação de causa raiz para {len(df_ocorrencias)} ocorrências...")
    df_investigado = df_ocorrencias.copy()
    df_investigado['Justificativa IA'] = ''
    df_historico_completo['DATA'] = pd.to_datetime(df_historico_completo['DATA'])
    for idx, ocorrencia in df_investigado.iterrows():
        razoes = []
        hist_combinacao = df_historico_completo[(df_historico_completo['FORNECEDOR'] == ocorrencia['FORNECEDOR']) & (df_historico_completo['PROJETO'] == ocorrencia['PROJETO'])]
        if len(hist_combinacao) <= 1: razoes.append(f"Primeiro registro do fornecedor '{ocorrencia['FORNECEDOR']}' no projeto '{ocorrencia['PROJETO']}'.")
        else:
            media_historica = hist_combinacao[hist_combinacao.index != idx]['VALOR'].mean()
            if pd.notna(media_historica) and media_historica > 0 and ocorrencia['VALOR'] > media_historica * 5: razoes.append(f"Valor (R$ {ocorrencia['VALOR']:.0f}) é um pico significativo (>5x a média de R$ {media_historica:.0f}) para esta combinação.")
        hist_fornecedor = df_historico_completo[df_historico_completo['FORNECEDOR'] == ocorrencia['FORNECEDOR']]
        if len(hist_fornecedor) <= 1: razoes.append(f"Primeiro lançamento registrado para o fornecedor '{ocorrencia['FORNECEDOR']}' nesta unidade.")
        df_investigado.loc[idx, 'Justificativa IA'] = " | ".join(razoes) if razoes else "Combinação rara de Fornecedor, Projeto e Valor."
    logger.info("Investigação concluída.")
    return df_investigado

def segmentar_contas_por_comportamento(df_a_segmentar: pd.DataFrame, n_clusters: int = 3) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Dict[str, Any]]]:
    logger.info(f"Iniciando segmentação de contas contábeis (Nível 4) com {n_clusters} clusters...")
    if df_a_segmentar.empty or 'DESC_NIVEL_4' not in df_a_segmentar.columns:
        logger.warning("DataFrame para segmentação vazio ou sem 'DESC_NIVEL_4'.")
        return {}, {}

    df_mensal_conta = df_a_segmentar.groupby(['DESC_NIVEL_4', 'MES'])['VALOR'].sum().unstack(fill_value=0)
    df_comportamento = df_a_segmentar.groupby('DESC_NIVEL_4').agg(
        valor_total=('VALOR', 'sum'),
        frequencia=('VALOR', 'count')
    ).reset_index()

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

    if len(df_comportamento) < n_clusters:
        n_clusters = len(df_comportamento) if len(df_comportamento) > 1 else 0
        if n_clusters == 0: return {}, {}
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
        
        name = f"Perfil {perfil_counter}: "
        description = ""

        # --- LÓGICA HIERÁRQUICA E DETALHADA DE INTERPRETAÇÃO ---
        if centroid_data['coef_variacao'] > 0.8 and 'Eventos Esporádicos' not in nomes_usados:
            name += "Contas de Eventos Esporádicos e Variáveis"
            description = "Aqui estão as contas mais imprevisíveis, com alta variação nos valores mensais. Exemplos incluem gastos com **consultorias para projetos específicos**, **manutenções não planejadas** ou **campanhas de marketing pontuais**. Elas exigem atenção no planejamento orçamentário."
            nomes_usados.append('Eventos Esporádicos')
        elif centroid_data['frequencia'] > df_comportamento['frequencia'].quantile(0.75) and 'Recorrência e Volume' not in nomes_usados:
            name += "Contas de Recorrência e Volume"
            description = "Este perfil inclui contas com muitos lançamentos, indicando despesas operacionais constantes e de alto volume, como **serviços de limpeza, segurança**, ou **licenças de software por usuário**. São a 'espinha dorsal' das operações do dia a dia."
            nomes_usados.append('Recorrência e Volume')
        elif centroid_data['valor_total'] > df_comportamento['valor_total'].quantile(0.75) and 'Alto Impacto Financeiro' not in nomes_usados:
            name += "Contas de Alto Impacto Financeiro"
            description = "Agrupa contas com os maiores valores totais. Embora não sejam necessariamente as mais frequentes, representam os maiores desembolsos do período. Exemplos incluem **aluguéis**, **grandes contratos de fornecedores** ou **compras de ativos**."
            nomes_usados.append('Alto Impacto Financeiro')
        else:
            name += "Contas de Baixo Impacto e Atividade"
            description = "Contas com um comportamento de gastos mais contido, sem características extremas. Representam **despesas administrativas menores**, **taxas pontuais** ou **compras de materiais de baixo custo**."
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
