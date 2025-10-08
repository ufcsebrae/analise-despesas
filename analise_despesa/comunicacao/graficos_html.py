# analise_despesa/comunicacao/graficos_html.py (VERSÃO FINAL COM A CONVERSÃO DE TIPO)

import json
import pandas as pd

def _get_colors(n):
    """Retorna uma lista de cores para os gráficos."""
    colors = [
        'rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)', 'rgba(255, 206, 86, 0.7)', 
        'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)',
        'rgba(199, 199, 199, 0.7)', 'rgba(83, 102, 255, 0.7)', 'rgba(255, 102, 217, 0.7)',
        'rgba(102, 255, 178, 0.7)'
    ]
    return (colors * (n // len(colors) + 1))[:n]

def preparar_dados_execucao_orcamentaria(df_orcamento: pd.DataFrame) -> str:
    # (Código inalterado)
    if df_orcamento.empty: return json.dumps({})
    df_chart = df_orcamento[df_orcamento['Iniciativa'] != 'Total Geral'].copy()
    df_chart = df_chart.sort_values(by='% Execução', ascending=True)
    data = {
        'labels': df_chart['Iniciativa'].tolist(),
        'datasets': [{'label': '% Execução', 'data': (df_chart['% Execução'] * 100).tolist(), 'backgroundColor': _get_colors(len(df_chart)), 'borderColor': [color.replace('0.7', '1') for color in _get_colors(len(df_chart))], 'borderWidth': 1}]
    }
    return json.dumps(data)

def preparar_dados_tendencia_mensal(df_mes_agregado: pd.DataFrame) -> str:
    # (Código inalterado)
    if df_mes_agregado.empty: return json.dumps({})
    df_chart = df_mes_agregado.copy()
    df_chart['Total Mensal'] = df_chart.get('Realizado (Exclusivo)', 0) + df_chart.get('Realizado (Compartilhado)', 0)
    data = {
        'labels': df_chart['Mês'].tolist(),
        'datasets': [
            {'label': 'Gastos Exclusivos', 'data': df_chart['Realizado (Exclusivo)'].tolist(), 'borderColor': 'rgba(54, 162, 235, 1)', 'fill': False, 'tension': 0.1},
            {'label': 'Gastos Compartilhados', 'data': df_chart['Realizado (Compartilhado)'].tolist(), 'borderColor': 'rgba(255, 99, 132, 1)', 'fill': False, 'tension': 0.1}
        ]
    }
    return json.dumps(data)
    
def preparar_dados_top_fornecedores(df_fornecedores: pd.DataFrame) -> str:
    # (Código inalterado)
    if df_fornecedores.empty: return json.dumps({})
    df_chart = df_fornecedores.sort_values(by='Realizado (Ano)', ascending=True)
    data = {
        'labels': df_chart['Fornecedor'].tolist(),
        'datasets': [{'label': 'Valor Gasto (R$)', 'data': df_chart['Realizado (Ano)'].tolist(), 'backgroundColor': _get_colors(len(df_chart))}]
    }
    return json.dumps(data)

def preparar_dados_ocorrencias_por_justificativa(df_ocorrencias: pd.DataFrame) -> str:
    """Prepara dados para o gráfico de pizza de ocorrências por justificativa."""
    if df_ocorrencias.empty or 'Justificativa IA' not in df_ocorrencias.columns:
        return json.dumps({"labels": [], "datasets": []})

    causas = {
        'Valor Atípico (Z-Score)': df_ocorrencias['Justificativa IA'].str.contains("pico ou vale estatístico", case=False).sum(),
        'Combinação Rara': df_ocorrencias['Justificativa IA'].str.contains("Combinação Fornecedor-Projeto rara", case=False).sum(),
        'Fornecedor Raro': df_ocorrencias['Justificativa IA'].str.contains("baixa atividade", case=False).sum()
    }
    
    labels = list(causas.keys())
    # --- CORREÇÃO AQUI: Convertendo os valores de int64 do NumPy para int nativo do Python ---
    data_values = [int(v) for v in causas.values()]
    
    data = {
        "labels": labels,
        "datasets": [{'label': 'Contagem de Justificativas da IA', 'data': data_values, 'backgroundColor': _get_colors(len(labels)), 'hoverOffset': 4}]
    }
    return json.dumps(data)

def preparar_dados_treemap_contas(df_bruto: pd.DataFrame) -> str:
    # (Código inalterado)
    if df_bruto.empty: return json.dumps({})
    df_agg = df_bruto.groupby('DESC_NIVEL_4')['VALOR'].sum().abs().reset_index()
    df_agg = df_agg[df_agg['VALOR'] > 0].sort_values(by='VALOR', ascending=False)
    datasets = [{'label': 'Gastos por Agrupamento Contábil', 'data': df_agg.to_dict(orient='records'), 'key': 'DESC_NIVEL_4', 'groups': ['DESC_NIVEL_4'], 'backgroundColor': (lambda n: [c.replace('0.7', '0.8') for c in _get_colors(n)])(len(df_agg)), 'spacing': 0.1, 'borderWidth': 1, 'borderColor': 'white'}]
    return json.dumps({'datasets': datasets})

def preparar_dados_distribuicao_tipo_projeto(resumo: dict) -> str:
    # (Código inalterado)
    labels = ['Gastos em Projetos Exclusivos', 'Gastos em Projetos Compartilhados']
    data_values = [resumo.get("gastos_ano_exclusivo", 0), resumo.get("gastos_ano_compartilhado", 0)]
    data = {
        "labels": labels,
        "datasets": [{'label': 'Distribuição de Gastos', 'data': data_values, 'backgroundColor': _get_colors(2)}]
    }
    return json.dumps(data)

def preparar_dados_para_grafico_cluster(df_clusters: dict) -> str:
    """Prepara os dados de cluster para o gráfico de bolhas do Chart.js."""
    # (Código inalterado da versão anterior)
    datasets, colors = [], ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)']
    for i, (nome_cluster, df) in enumerate(df_clusters.items()):
        color, data_points = colors[i % len(colors)], []
        for _, row in df.iterrows():
            freq = row['Qtd. Lançamentos (Ano)'] if row['Qtd. Lançamentos (Ano)'] > 0 else 0.1
            valor = row['Valor Total (Ano)'] if row['Valor Total (Ano)'] > 0 else 0.1
            data_points.append({'x': freq, 'y': valor, 'r': (row['Coeficiente de Variação (CV)'] * 20) + 8, 'label': row['Agrupamento Contábil (Nível 4)']})
        datasets.append({'label': nome_cluster, 'data': data_points, 'backgroundColor': color})
    return json.dumps({'datasets': datasets})

