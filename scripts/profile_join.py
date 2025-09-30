# profile_joins.py
import pandas as pd
from sqlalchemy import create_engine, text
from analise_despesa.config import PARAMETROS_ANALISE, CONEXOES

def profile_join_keys():
    """
    Investiga a relação real entre CODGERENCIAL e CODCCUSTO para
    entender por que o JOIN está falhando.
    """
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        print(f"--- ANÁLISE PROFUNDA DAS CHAVES DE JOIN (ANO {ano}) ---")
    except KeyError:
        print("❌ A chave 'ANO_REFERENCIA' não foi encontrada em PARAMETROS_ANALISE no config.py.")
        return

    try:
        # Conexão
        info_conexao = CONEXOES["SPSVSQL39_HubDados"]
        odbc_str = (f"DRIVER={{{info_conexao['driver']}}};SERVER={info_conexao['servidor']};"
                    f"DATABASE={info_conexao['banco']};Trusted_Connection=yes;")
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={odbc_str}")

        with engine.connect() as connection:
            # 1. Obter 5 códigos gerenciais de exemplo de 2024
            print("\nPASSO 1: Obtendo 5 códigos gerenciais de exemplo de 2024...")
            codigos_query = text("""
                SELECT DISTINCT TOP 5
                    crt.CODGERENCIAL
                FROM HUBDADOS.CorporeRM.CLANCA cln
                INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC crt ON crt.LCTREF = cln.LCTREF
                WHERE YEAR(cln.[DATA]) = :ano AND crt.CODGERENCIAL IS NOT NULL AND crt.CODGERENCIAL <> '';
            """)
            df_codigos = pd.read_sql(codigos_query, connection, params={"ano": ano})
            
            if df_codigos.empty:
                print("\nERRO CRÍTICO: Não foi possível encontrar nenhum CODGERENCIAL em 2024. O problema é anterior a este join.")
                return

            codigos_encontrados = df_codigos['CODGERENCIAL'].tolist()
            print("Códigos encontrados:", codigos_encontrados)

            # 2. Para cada código, procurar por correspondências na tabela GCCUSTO
            print("\nPASSO 2: Procurando por esses códigos (ou partes deles) na tabela GCCUSTO...")
            for cod_gerencial in codigos_encontrados:
                print(f"\n--- Investigando Código Gerencial: '{cod_gerencial}' ---")
                
                chave_join = cod_gerencial[-16:] if len(cod_gerencial) >= 16 else cod_gerencial
                print(f"Chave de join que estávamos usando (RIGHT, 16): '{chave_join}'")

                # Query de busca na GCCUSTO
                busca_query = text("SELECT CODCCUSTO, NOME FROM HUBDADOS.CorporeRM.GCCUSTO WHERE CODCCUSTO LIKE :padrao")
                
                # Busca pela chave exata
                df_busca = pd.read_sql(busca_query, connection, params={"padrao": f"%{chave_join}%"})
                
                if not df_busca.empty:
                    print("✅ ENCONTRADO! A chave de join foi encontrada na tabela GCCUSTO:")
                    print(df_busca)
                else:
                    print("❌ FALHA: A chave de join NÃO foi encontrada na tabela GCCUSTO.")
                    print("   Isso confirma que a lógica 'RIGHT(crt.CODGERENCIAL, 16)' está incorreta para os dados de 2024.")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante a análise: {e}")

if __name__ == "__main__":
    profile_join_keys()
