# diagnosticar_view.py
import pandas as pd
import logging
import sys

# Adiciona a pasta do projeto ao path para encontrar o pacote 'analise_despesa'
# Isso resolve o ModuleNotFoundError de forma robusta.
from pathlib import Path
sys.path.append(str(Path(__file__).parent.absolute()))

from analise_despesa.database import obter_conexao
from analise_despesa.config import PARAMETROS_ANALISE, MAPA_GESTORES

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Lê os dados diretamente da VIEW e lista os valores únicos das colunas
    críticas para entender o problema de mapeamento.
    """
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        logger.info(f"Analisando a VIEW 'vw_AnaliseDespesas' para o ano {ano}...")

        engine = obter_conexao("SPSVSQL39_FINANCA")
        
        # Usamos a mesma query que o seu script main usa
        sql_query = f"SELECT * FROM vw_AnaliseDespesas WHERE YEAR([DATA]) = {ano}"
        
        logger.info("Executando consulta... Isso pode levar alguns segundos.")
        df = pd.read_sql(sql_query, engine)

        if df.empty:
            logger.error("A VIEW não retornou nenhum dado. Verifique a fonte de dados.")
            return

        logger.info(f"Consulta concluída. {len(df)} linhas recebidas.")
        
        # --- O PONTO CHAVE DO DIAGNÓSTICO ---
        
        # 1. Verificar as colunas que a VIEW está realmente retornando
        logger.info("\n--- COLUNAS RECEBIDAS PELA VIEW ---")
        print(df.columns.tolist())

        # 2. Listar valores únicos da coluna que DEVERIA ser a unidade
        if 'UNIDADE' in df.columns:
            logger.info("\n--- VALORES ÚNICOS NA COLUNA 'UNIDADE' ---")
            unidades_na_view = df['UNIDADE'].unique()
            print(unidades_na_view)
        else:
            logger.error("ERRO: A coluna 'UNIDADE' não foi encontrada no resultado da VIEW.")

        # 3. Listar valores únicos da coluna 'ACAO' (nossa suspeita)
        if 'ACAO' in df.columns:
            logger.info("\n--- VALORES ÚNICOS NA COLUNA 'ACAO' ---")
            acoes_na_view = df['ACAO'].unique()
            print(acoes_na_view)
        else:
            logger.error("ERRO: A coluna 'ACAO' não foi encontrada no resultado da VIEW.")

        # 4. Comparar com o MAPA_GESTORES
        logger.info("\n--- COMPARAÇÃO COM MAPA_GESTORES ---")
        chaves_mapa = list(MAPA_GESTORES.keys())
        print("Chaves definidas no seu config.py:", chaves_mapa)

        logger.warning(
            "\nCompare os valores únicos listados acima com as chaves do seu mapa."
            " Eles devem ser idênticos (incluindo espaços, hífens e maiúsculas/minúsculas)."
        )

    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante o diagnóstico: {e}", exc_info=True)

if __name__ == "__main__":
    main()

