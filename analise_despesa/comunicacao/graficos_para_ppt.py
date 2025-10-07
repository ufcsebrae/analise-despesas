# analise_despesa/comunicacao/graficos_para_ppt.py

import logging
import matplotlib.pyplot as plt
import numpy as np
import os

logger = logging.getLogger(__name__)

def _configurar_plot():
    """Configurações visuais padrão para os gráficos."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rc('font', family='Calibri')
    fig, ax = plt.subplots(figsize=(10, 5))
    return fig, ax

def criar_grafico_score(caminho_saida: str):
    """Cria um gráfico de barras conceitual para o Score de Criticidade."""
    fig, ax = _configurar_plot()
    projetos = ['Projeto A', 'Projeto B', 'Projeto C', 'Projeto D']
    execucao = [0.95, 0.80, 0.85, 0.50]
    cores = ['#d9534f', '#f0ad4e', '#d9534f', '#5cb85c'] # Vermelho, Amarelo, Vermelho, Verde
    
    bars = ax.barh(projetos, execucao, color=cores)
    ax.set_title('Exemplo Visual: Score de Criticidade', fontsize=16, weight='bold')
    ax.set_xlabel('% Execução Orçamentária', fontsize=12)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.text(execucao[1], 1, '  Ocorrência Atípica', va='center', color='#c9302c', weight='bold')
    ax.text(execucao[2], 2, '  Ocorrência Atípica', va='center', color='#c9302c', weight='bold')
    
    plt.tight_layout()
    plt.savefig(caminho_saida)
    plt.close(fig)
    logger.debug(f"Gráfico de Score salvo em {caminho_saida}")
    return caminho_saida

def criar_grafico_tendencia(caminho_saida: str):
    """Cria um gráfico de linha conceitual para a Sinalização de Tendência."""
    fig, ax = _configurar_plot()
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    valores = [100, 110, 105, 250, 115, 120]
    
    ax.plot(meses, valores, marker='o', linestyle='-', color='#0275d8')
    ax.plot(3, 250, 'o', markersize=15, color='#d9534f', alpha=0.8) # Destaque no pico
    ax.annotate('Pico Atípico', xy=(3, 250), xytext=(3.5, 240),
                arrowprops=dict(facecolor='black', shrink=0.05), fontsize=12, weight='bold')
    ax.set_title('Exemplo Visual: Sinalização de Tendência Mensal', fontsize=16, weight='bold')
    ax.set_ylabel('Gasto Total da Unidade (R$)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(caminho_saida)
    plt.close(fig)
    logger.debug(f"Gráfico de Tendência salvo em {caminho_saida}")
    return caminho_saida

def criar_grafico_contexto(caminho_saida: str):
    """Cria um gráfico de dispersão conceitual para a Análise de Contexto."""
    fig, ax = _configurar_plot()
    np.random.seed(42)
    # Simula dados normais
    freq_forn = np.random.randint(10, 100, 50)
    z_score = np.random.randn(50) * 0.5
    ax.scatter(freq_forn, z_score, alpha=0.6, label='Lançamentos Normais')
    
    # Simula anomalias
    ax.scatter([5, 80], [0.2, 3.5], color='#d9534f', s=150, label='Ocorrências Atípicas', edgecolors='black')
    ax.text(6, 0.3, "Fornecedor Raro", fontsize=11, weight='bold')
    ax.text(81, 3.6, "Valor Atípico (Z-Score Alto)", fontsize=11, weight='bold')

    ax.set_title('Exemplo Visual: Detecção de Ocorrências de Contexto', fontsize=16, weight='bold')
    ax.set_xlabel('Familiaridade do Fornecedor (Frequência)', fontsize=12)
    ax.set_ylabel('Anomalia de Valor (Z-Score)', fontsize=12)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(caminho_saida)
    plt.close(fig)
    logger.debug(f"Gráfico de Contexto salvo em {caminho_saida}")
    return caminho_saida
