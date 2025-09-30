# tests/test_agregacao.py
import pandas as pd
import pytest
from analise_despesa.analise import agregacao

@pytest.fixture
def dados_teste() -> pd.DataFrame:
    """Cria um DataFrame de exemplo para ser usado nos testes."""
    return pd.DataFrame({
        'LCTREF': [1, 1, 2, 3, 4, 5],  # Lançamento 1 está duplicado
        'FORNECEDOR': ['Forn-A', 'Forn-A', 'Forn-B', 'Forn-A', 'Forn-C', 'Forn-C'],
        'PROJETO': ['PROJ-X', 'PROJ-X', 'PROJ-Y', 'PROJ-X', 'PROJ-Y', 'PROJ-Z'],
        'VALOR': [1000, 1000, 500, 200, -150, 0] # Inclui valor duplicado, negativo e zero
    })

def test_apenas_despesas_filtra_corretamente(dados_teste):
    """Garante que valores negativos e nulos sejam removidos."""
    df_filtrado = agregacao.apenas_despesas(dados_teste)
    
    assert len(df_filtrado) == 3  # Deve manter apenas as 3 linhas com valor > 0
    assert (df_filtrado['VALOR'] > 0).all()

def test_agregacao_por_fornecedor_evita_duplicatas(dados_teste):
    """
    Verifica se a agregação por fornecedor ignora lançamentos duplicados (LCTREF)
    e retorna o top N corretamente.
    """
    df_agregado = agregacao.agregar_despesas_por_fornecedor(dados_teste, top_n=2)
    
    # A soma de Forn-A deve ser 1200 (1000 do LCTREF 1 + 200 do LCTREF 3).
    # A soma de Forn-B deve ser 500.
    # O LCTREF 1 duplicado (valor 1000) deve ser ignorado.
    
    assert len(df_agregado) == 2
    assert df_agregado.iloc[0]['FORNECEDOR'] == 'Forn-A'
    assert df_agregado.iloc[0]['VALOR'] == 1200
    assert df_agregado.iloc[1]['FORNECEDOR'] == 'Forn-B'
    assert df_agregado.iloc[1]['VALOR'] == 500
