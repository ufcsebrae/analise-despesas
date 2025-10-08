# analise_despesa/comunicacao/graficos_html.py

import json
import pandas as pd

def preparar_dados_para_grafico_cluster(df_clusters: dict) -> str:
    """
    Converte os DataFrames de cluster em uma estrutura JSON para o Chart.js.
    """
    datasets = []
    colors = [
        'rgba(255, 99, 132, 0.6)',  # Vermelho
        'rgba(54, 162, 235, 0.6)',  # Azul
        'rgba(255, 206, 86, 0.6)',  # Amarelo
        'rgba(75, 192, 192, 0.6)',  # Verde Água
        'rgba(153, 102, 255, 0.6)' # Roxo
    ]
    
    for i, (nome_cluster, df) in enumerate(df_clusters.items()):
        color = colors[i % len(colors)]
        data_points = []
        for _, row in df.iterrows():
            # Adiciona um pequeno valor para evitar o log de zero, que é infinito
            freq = row['Qtd. Lançamentos (Ano)'] if row['Qtd. Lançamentos (Ano)'] > 0 else 0.1
            valor = row['Valor Total (Ano)'] if row['Valor Total (Ano)'] > 0 else 0.1
            
            data_points.append({
                'x': freq,
                'y': valor,
                'r': (row['Coeficiente de Variação (CV)'] * 20) + 8, # Raio da bolha = CV
                'label': row['Agrupamento Contábil (Nível 4)']
            })
        
        datasets.append({
            'label': nome_cluster,
            'data': data_points,
            'backgroundColor': color
        })
        
    return json.dumps({'datasets': datasets})
