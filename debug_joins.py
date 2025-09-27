# debug_joins.py (VERSÃO FINAL E CORRIGIDA)
import pandas as pd
from sqlalchemy import create_engine, text
from analise_despesa.config import PARAMETROS_ANALISE, CONEXOES

def testar_joins_passo_a_passo():
    """Executa a query em etapas para identificar qual JOIN está falhando."""
    
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        unidade_teste = "SP - Finanças e Controladoria"
        print(f"--- INICIANDO TESTE DE JOINS PARA O ANO {ano} ---")
    except KeyError:
        print("❌ A chave 'ANO_REFERENCIA' não foi encontrada em PARAMETROS_ANALISE no config.py.")
        return

    try:
        # Conexão
        info_conexao = CONEXOES["SPSVSQL39_HubDados"]
        odbc_str = (f"DRIVER={{{info_conexao['driver']}}};SERVER={info_conexao['servidor']};"
                    f"DATABASE={info_conexao['banco']};Trusted_Connection=yes;")
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={odbc_str}")

        # As 6 queries de teste. Cada uma adiciona um passo à lógica.
        queries = {
            "Passo 1: Contagem na Tabela Principal (CLANCA)": """
                SELECT COUNT(*) AS total FROM HUBDADOS.CorporeRM.CLANCA WHERE YEAR([DATA]) = :ano
            """,
            "Passo 2: Adicionando INNER JOIN com TMOV": """
                SELECT COUNT(*) AS total FROM HUBDADOS.CorporeRM.CLANCA cln
                INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
                WHERE YEAR(cln.[DATA]) = :ano
            """,
            "Passo 3: Adicionando INNER JOIN com CRATEIOLC": """
                SELECT COUNT(*) AS total FROM HUBDADOS.CorporeRM.CLANCA cln
                INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
                INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC crt ON crt.LCTREF = cln.LCTREF
                WHERE YEAR(cln.[DATA]) = :ano
            """,
            "Passo 4: Adicionando LEFT JOIN com Centros de Custo (subquery)": """
                SELECT COUNT(*) AS total FROM HUBDADOS.CorporeRM.CLANCA cln
                INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
                INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC crt ON crt.LCTREF = cln.LCTREF
                LEFT JOIN (
                    SELECT NivelAcao.CODCCUSTO, NivelUnidade.NOME AS UNIDADE FROM HUBDADOS.CorporeRM.GCCUSTO AS NivelAcao
                    LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelUnidade ON LEFT(NivelAcao.CODCCUSTO, 2) = NivelUnidade.CODCCUSTO
                    WHERE LEN(NivelAcao.CODCCUSTO) > 15
                ) AS cc ON RIGHT(crt.CODGERENCIAL, 16) = cc.CODCCUSTO
                WHERE YEAR(cln.[DATA]) = :ano
            """,
            "Passo 5: Filtrando Onde a Unidade NÃO é Nula": """
                SELECT COUNT(*) AS total FROM HUBDADOS.CorporeRM.CLANCA cln
                INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
                INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC crt ON crt.LCTREF = cln.LCTREF
                LEFT JOIN (
                    SELECT NivelAcao.CODCCUSTO, NivelUnidade.NOME AS UNIDADE FROM HUBDADOS.CorporeRM.GCCUSTO AS NivelAcao
                    LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelUnidade ON LEFT(NivelAcao.CODCCUSTO, 2) = NivelUnidade.CODCCUSTO
                    WHERE LEN(NivelAcao.CODCCUSTO) > 15
                ) AS cc ON RIGHT(crt.CODGERENCIAL, 16) = cc.CODCCUSTO
                WHERE YEAR(cln.[DATA]) = :ano AND cc.UNIDADE IS NOT NULL
            """,
            "Passo 6: Filtrando Pela Unidade Específica": """
                SELECT COUNT(*) AS total FROM HUBDADOS.CorporeRM.CLANCA cln
                INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
                INNER JOIN HUBDADOS.CorporeRM.CRATEIOLC crt ON crt.LCTREF = cln.LCTREF
                LEFT JOIN (
                    SELECT NivelAcao.CODCCUSTO, NivelUnidade.NOME AS UNIDADE FROM HUBDADOS.CorporeRM.GCCUSTO AS NivelAcao
                    LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelUnidade ON LEFT(NivelAcao.CODCCUSTO, 2) = NivelUnidade.CODCCUSTO
                    WHERE LEN(NivelAcao.CODCCUSTO) > 15
                ) AS cc ON RIGHT(crt.CODGERENCIAL, 16) = cc.CODCCUSTO
                WHERE YEAR(cln.[DATA]) = :ano AND cc.UNIDADE = :unidade
            """
        }

        with engine.connect() as connection:
            for nome, query in queries.items():
                params_dict = {"ano": ano}
                if "Passo 6" in nome:
                    params_dict["unidade"] = unidade_teste
                
                print(f"\nExecutando -> {nome}...")
                df = pd.read_sql(text(query), connection, params=params_dict)
                print(f"Resultado: {df.iloc[0]['total']} linhas encontradas.")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante o teste: {e}")

if __name__ == "__main__":
    testar_joins_passo_a_passo()
