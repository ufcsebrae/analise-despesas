# analise_despesa/analise/insights_ia.py (VERSÃO FINAL COM LÓGICA DE FREQUÊNCIA E RARIDADE)
import pandas as pd
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

def detectar_anomalias_de_contexto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica ocorrências atípicas com base em regras de negócio claras:
    1. Combinações de Fornecedor/Projeto que aparecem apenas uma vez no ano.
    2. Transações de fornecedores que são muito raros para a unidade no ano.
    """
    if df.empty or len(df) < 2:
        logger.warning("Dados insuficientes para a análise de ocorrências atípicas de contexto.")
        return pd.DataFrame()
    
    logger.info("Iniciando detecção de ocorrências por frequência e raridade...")
    df_analise = df.copy()

    # REGRA 1: Identificar combinações Fornecedor/Projeto que ocorrem apenas uma vez
    frequencia_combinacao = df_analise.groupby(['FORNECEDOR', 'PROJETO'])['VALOR'].transform('count')
    ocorrencias_combinacao_unica = df_analise[frequencia_combinacao == 1].copy()
    ocorrencias_combinacao_unica['Justificativa IA'] = 'Combinação Fornecedor-Projeto inédita (ocorre apenas 1 vez no ano).'
    
    # REGRA 2: Identificar transações de fornecedores muito raros
    frequencia_fornecedor = df_analise.groupby('FORNECEDOR')['FORNECEDOR'].transform('count')
    # Consideramos "raro" um fornecedor com 3 ou menos transações no ano todo
    ocorrencias_fornecedor_raro = df_analise[frequencia_fornecedor <= 3].copy()
    ocorrencias_fornecedor_raro['Justificativa IA'] = 'Fornecedor raro (pouca atividade na unidade durante o ano).'

    # Unir os dois tipos de ocorrências e remover duplicatas, mantendo a primeira justificativa
    ocorrencias_finais = pd.concat([ocorrencias_combinacao_unica, ocorrencias_fornecedor_raro]).drop_duplicates(subset=['DATA', 'FORNECEDOR', 'PROJETO', 'VALOR']).reset_index(drop=True)
    
    logger.info(f"Análise de frequência e raridade concluída. Encontradas {len(ocorrencias_finais)} ocorrências atípicas.")
    
    colunas_relevantes = ['DATA', 'FORNECEDOR', 'PROJETO', 'VALOR', 'COMPLEMENTO', 'Justificativa IA']
    return ocorrencias_finais[colunas_relevantes]

def investigar_causa_raiz_ocorrencia(df_ocorrencias: pd.DataFrame, df_historico_completo: pd.DataFrame) -> pd.DataFrame:
    # Com a nova abordagem, a justificativa já vem pronta. Esta função apenas repassa os dados.
    return df_ocorrencias

def segmentar_contas_por_comportamento(df_a_segmentar: pd.DataFrame, n_clusters: int = 3) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Dict[str, Any]]]:
    # (Código inalterado)
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
