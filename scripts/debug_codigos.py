# debug_codigos.py
import pandas as pd
from sqlalchemy import create_engine, text
from analise_despesa.config import PARAMETROS_ANALISE, CONEXOES

def inspecionar_codigos_gerenciais():
    """Mostra os valores de CODGERENCIAL que estão falhando no JOIN."""
    
    ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
    print(f"--- INSPECIONANDO CÓDIGOS GERENCIAIS PARA O ANO {ano} ---")

    try:
        info_conexao = CONEXOES["SPSVSQL39_HubDados"]
        odbc_str = (f"DRIVER={{{info_conexao['driver']}}};SERVER={info_conexao['servidor']};"
                    f"DATABASE={info_conexao['banco']};Trusted_Connection=yes;")
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={odbc_str}")

        # Query para ver os valores de CODGERENCIAL que estamos usando
        query_sql = text("""
            SELECT TOP 20
                cln.LCTREF,
                crt.CODGERENCIAL,
                RIGHT(crt.CODGERENCIAL, 16) AS CodigoUsadoNoJoin
            FROM HUBDADOS.CorporeRM.CLANCA cln
            INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
            INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC crt ON crt.LCTREF = cln.LCTREF
            WHERE YEAR(cln.[DATA]) = :ano
              AND crt.CODGERENCIAL IS NOT NULL;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(query_sql, connection, params={"ano": ano})
            
            print("\nAmostra dos códigos que estamos tentando usar para o JOIN:")
            print(df)
            print("\nCompare os valores de 'CodigoUsadoNoJoin' com os códigos em sua tabela 'GCCUSTO'.")
            print("A lógica `RIGHT(..., 16)` está correta? O formato parece certo?")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro: {e}")

if __name__ == "__main__":
    inspecionar_codigos_gerenciais()
