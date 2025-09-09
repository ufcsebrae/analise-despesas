# analise_despesa/exceptions.py
"""Módulo de exceções customizadas do projeto."""

class AnaliseDespesaError(Exception):
    """Classe base para erros da aplicação."""
    pass

class QueryNaoEncontradaError(AnaliseDespesaError):
    """Lançado quando uma query não é encontrada no dicionário."""
    def __init__(self, nome_query: str):
        super().__init__(f"A query '{nome_query}' não existe em queries.py")

class FalhaDeConexaoError(AnaliseDespesaError):
    """Lançado quando a conexão com o banco de dados falha."""
    pass
