# debug_final.py
import pandas as pd
from sqlalchemy import create_engine, text
from analise_despesa.config import PARAMETROS_ANALISE, CONEXOES

def teste_final_de_acesso():
    """Executa a query mais simples possível para verificar se há dados em 2024."""
    
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        print(f"--- TESTE FINAL ---")
        print(f"Buscando as 10 primeiras linhas de 'CLANCA' para o ano: {ano}")
    except KeyError:
        print("❌ A chave 'ANO_REFERENCIA' não foi encontrada em PARAMETROS_ANALISE no config.py.")
        return

    try:
        # Conexão (mesma lógica de antes)
        info_conexao = CONEXOES["SPSVSQL39_HubDados"]
        odbc_str = (
            f"DRIVER={{{info_conexao['driver']}}};"
            f"SERVER={info_conexao['servidor']};"
            f"DATABASE={info_conexao['banco']};"
            f"Trusted_Connection=yes;"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={odbc_str}")

        # A "Query Burra": sem JOINs, sem lógica complexa.
        query_sql = text("""
            SELECT TOP 10
                [DATA],
                VALOR,
                COMPLEMENTO
            FROM HUBDADOS.CorporeRM.CLANCA
            WHERE YEAR([DATA]) = :ano;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(query_sql, connection, params={"ano": ano})
            
            print("\n--- RESULTADO DA BUSCA DIRETA ---")
            if df.empty:
                print("!!! ALERTA: A query mais simples possível NÃO RETORNOU DADOS.")
                print("Isso sugere um problema de permissão ou de ambiente, não de SQL.")
            else:
                print("✅ SUCESSO! O Python consegue ver os dados. O problema está nos JOINs da query principal.")
                print("Amostra de dados encontrados:")
                print(df)
            print("----------------------------------")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    teste_final_de_acesso()

