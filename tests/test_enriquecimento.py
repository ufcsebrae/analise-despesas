# tests/test_enriquecimento.py
import pandas as pd
from analise_despesa.processamento import enriquecimento

def test_adicionar_colunas_de_data():
    # Dado (Arrange)
    data = {'DATA': pd.to_datetime(['2025-01-15', '2025-03-20'])}
    df_teste = pd.DataFrame(data)

    # Quando (Act)
    df_resultado = enriquecimento.adicionar_colunas_de_data(df_teste)

    # Então (Assert)
    assert 'MES' in df_resultado.columns
    assert 'ANO' in df_resultado.columns
    assert df_resultado['MES'].tolist() == [1, 3]
    assert df_resultado['ANO'].tolist() == [2025, 2025]
