# analise_despesa/utils.py
"""
Módulo de funções utilitárias para o projeto.
"""
import os

def carregar_sql(caminho_arquivo: str) -> str:
    """
    Lê e retorna o conteúdo de um arquivo de texto (SQL/MDX).

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo de query não encontrado em: '{caminho_arquivo}'")

    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return f.read()
