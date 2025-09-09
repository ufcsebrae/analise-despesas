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
    sns.barplot(x='UNIFICAVALOR', y='FORNECEDOR', data=df_top, palette='viridis')
    plt.title('Top 10 Fornecedores por Valor de Despesa', fontsize=16)
    plt.xlabel('Valor Total da Despesa (R$)', fontsize=12)
    plt.ylabel('Fornecedor', fontsize=12)
    plt.tight_layout() # Ajusta o layout para não cortar os nomes
    
    # Garante que o diretório de saída exista
    os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
    plt.savefig(caminho_salvar)
    plt.close() # Libera a memória da figura
    logger.info("Gráfico salvo com sucesso.")
