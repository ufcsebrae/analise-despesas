# verify_units.py
import pandas as pd
from sqlalchemy import create_engine, text
from analise_despesa.config import PARAMETROS_ANALISE, CONEXOES

def verify_unit_names_for_year():
    """
    Executa a query principal para um ano, mas sem filtrar por unidade,
    para listar todas as unidades que a query encontra.
    """
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        print(f"--- VERIFICANDO NOMES DE UNIDADE PARA O ANO {ano} ---")
    except KeyError:
        print("❌ A chave 'ANO_REFERENCIA' não foi encontrada em PARAMETROS_ANALISE no config.py.")
        return

    try:
        # Conexão
        info_conexao = CONEXOES["SPSVSQL39_HubDados"]
        odbc_str = (f"DRIVER={{{info_conexao['driver']}}};SERVER={info_conexao['servidor']};"
                    f"DATABASE={info_conexao['banco']};Trusted_Connection=yes;")
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={odbc_str}")

        # A nossa query final, mas com a última linha do WHERE comentada.
        query_sql = text("""
            SELECT
                COALESCE(REPLACE(unidade.NOME, CHAR(22), ''), 'Unidade Não Encontrada') AS NOME_DA_UNIDADE_ENCONTRADA,
                COUNT(*) AS QTD_LANCAMENTOS
            FROM 
                HUBDADOS.CorporeRM.CLANCA AS cln
            INNER JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
            INNER JOIN CorporeRM.CCONTA AS pc ON pc.CODCONTA = cln.CREDITO
            INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC AS crt ON crt.LCTREF = cln.LCTREF
            LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS cc
                ON RIGHT(crt.CODGERENCIAL, 16) = cc.CODCCUSTO
            LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS unidade 
                ON LEFT(cc.CODCCUSTO, 2) = unidade.CODCCUSTO
            WHERE 
                cln.[DATA] BETWEEN :data_inicio AND :data_fim
            GROUP BY
                COALESCE(REPLACE(unidade.NOME, CHAR(22), ''), 'Unidade Não Encontrada')
            ORDER BY
                QTD_LANCAMENTOS DESC;
        """)

        data_inicio = f"{ano}-01-01"
        data_fim = f"{ano}-12-31"

        with engine.connect() as connection:
            df = pd.read_sql(query_sql, connection, params={"data_inicio": data_inicio, "data_fim": data_fim})
            
            print(f"\n--- Unidades e contagem de lançamentos encontrados para {ano} ---")
            if df.empty:
                print("NENHUM DADO RETORNADO. A lógica de JOIN ainda está falhando em algum ponto anterior.")
            else:
                print(df.to_string())
            print("---------------------------------------------------------------")
            print("\nCompare os nomes da coluna 'NOME_DA_UNIDADE_ENCONTRADA' com as chaves do seu MAPA_GESTORES.")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante a verificação: {e}")

if __name__ == "__main__":
    verify_unit_names_for_year()
