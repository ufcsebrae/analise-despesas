# analise_despesa/visualizacao/graficos.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

logger = logging.getLogger(__name__)

def plotar_top_fornecedores(df_top: pd.DataFrame, caminho_salvar: str):
    """Cria e salva um gráfico de barras com os top fornecedores."""
    logger.info(f"Gerando gráfico de Top Fornecedores em '{caminho_salvar}'...")
    
    plt.figure(figsize=(12, 8))
    
    # --- CORREÇÃO DO WARNING ---
    # Atribuímos a variável 'y' ('FORNECEDOR') ao parâmetro 'hue' para ter uma cor diferente
    # para cada barra e adicionamos legend=False para não mostrar a legenda redundante.
    sns.barplot(
        x='UNIFICAVALOR', 
        y='FORNECEDOR', 
        data=df_top, 
        palette='viridis', 
        hue='FORNECEDOR',  # Adicionado conforme a sugestão
        legend=False       # Adicionado conforme a sugestão
    )
    
    plt.title('Top 10 Fornecedores por Valor de Despesa', fontsize=16)
    plt.xlabel('Valor Total da Despesa (R$)', fontsize=12)
    plt.ylabel('Fornecedor', fontsize=12)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
    plt.savefig(caminho_salvar)
    plt.close()
    logger.info("Gráfico salvo com sucesso.")
