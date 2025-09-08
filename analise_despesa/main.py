# analise_despesa/main.py
"""
Módulo principal que orquestra o fluxo completo da análise de despesas.
"""
from . import extracao
from . import database
# from . import processamento  # Futuramente, para a lógica de negócio
# from . import visualizacao   # Futuramente, para gerar relatórios

def executar_analise():
    """
    Orquestra o fluxo completo: Extração, Transformação e Carga (ETL).
    """
    # 1. Extração (E)
    df_despesas = extracao.buscar_dados("BaseDespesas")
    print("Dados extraídos com sucesso.")
    print(df_despesas.head())

    if df_despesas.empty:
        return # Interrompe se a extração falhar

    # 2. Transformação (T) - (Aqui entraria a lógica de 'processamento.py')
    # Exemplo: df_processado = processamento.analisar_despesas(df_despesas)
    
    # 3. Carga (L) - (Aqui usamos o 'database.py' para salvar os resultados)
    # Exemplo: database.salvar_dataframe(df_processado, "relatorio_final", "SPSVSQL39_FINANCA")
