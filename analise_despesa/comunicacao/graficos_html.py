# analise_despesa/comunicacao/graficos_html.py (VERSÃO FINAL COMPLETA)

import pandas as pd

def _get_colors(n, alpha='0.7'):
    """Retorna uma lista de cores para os gráficos."""
    palette = [
        f'rgba(54, 162, 235, {alpha})',  # Azul
        f'rgba(255, 99, 132, {alpha})',  # Vermelho
        f'rgba(75, 192, 192, {alpha})',  # Verde Água
        f'rgba(255, 206, 86, {alpha})',  # Amarelo
        f'rgba(153, 102, 255, {alpha})', # Roxo
        f'rgba(255, 159, 64, {alpha})',   # Laranja
        f'rgba(199, 199, 199, {alpha})', # Cinza
        f'rgba(83, 102, 255, {alpha})'   # Azul Violeta
    ]
    return (palette * (n // len(palette) + 1))[:n]

def preparar_dados_execucao_orcamentaria(df_orcamento: pd.DataFrame) -> dict:
    if df_orcamento.empty: return {}
    df_chart = df_orcamento[df_orcamento['Iniciativa'] != 'Total Geral'].copy()
    df_chart = df_chart.sort_values(by='% Execução', ascending=False).head(10)
    
    return {
        'labels': df_chart['Iniciativa'].tolist(),
        'datasets': [{'label': '% Execução', 'data': (df_chart['% Execução'] * 100).tolist(), 'backgroundColor': _get_colors(len(df_chart))}]
    }

def preparar_dados_tendencia_mensal(df_mes_agregado: pd.DataFrame) -> dict:
    if df_mes_agregado.empty: return {}
    df_chart = df_mes_agregado.copy()
    
    return {
        'labels': df_chart['Mês'].tolist(),
        'datasets': [
            {'label': 'Gastos Exclusivos', 'data': df_chart.get('Realizado (Exclusivo)', []).tolist(), 'borderColor': 'rgba(54, 162, 235, 1)', 'fill': False, 'tension': 0.1},
            {'label': 'Gastos Compartilhados', 'data': df_chart.get('Realizado (Compartilhado)', []).tolist(), 'borderColor': 'rgba(255, 99, 132, 1)', 'fill': False, 'tension': 0.1}
        ]
    }
    
def preparar_dados_top_fornecedores(df_fornecedores: pd.DataFrame) -> dict:
    if df_fornecedores.empty: return {}
    df_chart = df_fornecedores.sort_values(by='Realizado (Ano)', ascending=True)
    return {
        'labels': df_chart['Fornecedor'].tolist(),
        'datasets': [{'label': 'Valor Gasto (R$)', 'data': df_chart['Realizado (Ano)'].tolist(), 'backgroundColor': _get_colors(len(df_chart))}]
    }

def preparar_dados_ocorrencias_por_justificativa(df_ocorrencias: pd.DataFrame) -> dict:
    if df_ocorrencias.empty or 'Justificativa IA' not in df_ocorrencias.columns:
        return {}
    causas = {
        'Valor Atípico (Z-Score)': df_ocorrencias['Justificativa IA'].str.contains("pico ou vale estatístico", case=False).sum(),
        'Combinação Rara': df_ocorrencias['Justificativa IA'].str.contains("Combinação Fornecedor-Projeto rara", case=False).sum(),
        'Fornecedor Raro': df_ocorrencias['Justificativa IA'].str.contains("baixa atividade", case=False).sum()
    }
    labels = list(causas.keys())
    data_values = [int(v) for v in causas.values()] # Converte de numpy.int64 para int
    
    if sum(data_values) == 0: return {}
    
    return {
        "labels": labels,
        "datasets": [{'label': 'Contagem de Justificativas', 'data': data_values, 'backgroundColor': _get_colors(len(labels)), 'hoverOffset': 4}]
    }

def preparar_dados_treemap_contas(df_bruto: pd.DataFrame) -> dict:
    if df_bruto.empty: return {}
    df_agg = df_bruto.groupby('DESC_NIVEL_4')['VALOR'].sum().abs().reset_index()
    df_agg = df_agg[df_agg['VALOR'] > 0].sort_values(by='VALOR', ascending=False)
    return {
        'datasets': [{'label': 'Gasto por Agrupamento', 'data': df_agg.to_dict(orient='records'), 'key': 'DESC_NIVEL_4', 'groups': ['DESC_NIVEL_4'], 'backgroundColor': _get_colors(len(df_agg), alpha='0.8'), 'spacing': 0.1, 'borderWidth': 1, 'borderColor': 'white'}]
    }

def preparar_dados_distribuicao_tipo_projeto(resumo: dict) -> dict:
    labels = ['Gastos em Projetos Exclusivos', 'Gastos em Projetos Compartilhados']
    data_values = [resumo.get("gastos_ano_exclusivo", 0), resumo.get("gastos_ano_compartilhado", 0)]
    if sum(data_values) == 0: return {}
    return {"labels": labels, "datasets": [{'label': 'Distribuição de Gastos', 'data': data_values, 'backgroundColor': _get_colors(2)}]}

def preparar_dados_para_grafico_cluster(df_clusters: dict) -> dict:
    datasets, palette = [], _get_colors(len(df_clusters))
    for i, (nome_cluster, df) in enumerate(df_clusters.items()):
        color, data_points = palette[i % len(palette)], []
        for _, row in df.iterrows():
            freq = row['Qtd. Lançamentos (Ano)'] if row['Qtd. Lançamentos (Ano)'] > 0 else 0.1
            valor = row['Valor Total (Ano)'] if row['Valor Total (Ano)'] > 0 else 0.1
            data_points.append({'x': freq, 'y': valor, 'r': (row['Coeficiente de Variação (CV)'] * 20) + 8, 'label': row['Agrupamento Contábil (Nível 4)']})
        datasets.append({'label': nome_cluster, 'data': data_points, 'backgroundColor': color})
    return {'datasets': datasets}
