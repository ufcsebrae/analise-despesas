# diagnosticar_csv.py
import pandas as pd
import logging
from analise_despesa.config import PARAMETROS_ANALISE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Lê o arquivo CSV e lista todos os nomes de unidade únicos encontrados,
    junto com a contagem de quantos registros cada um tem.
    """
    try:
        caminho_csv = PARAMETROS_ANALISE["ARQUIVO_CSV_LOCAL"]
        logging.info(f"Analisando o arquivo: {caminho_csv}")

        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig')

        coluna_unidade = 'CLASSIFICA' # O nome da coluna que contém a unidade

        if coluna_unidade not in df.columns:
            logging.error(f"ERRO: A coluna '{coluna_unidade}' não foi encontrada no CSV!")
            logging.info(f"Colunas encontradas: {df.columns.tolist()}")
            return

        contagem_unidades = df[coluna_unidade].value_counts().reset_index()
        contagem_unidades.columns = ['NOME_DA_UNIDADE_NO_CSV', 'QTD_REGISTROS']

        logging.info("--- NOMES DE UNIDADE ÚNICOS ENCONTRADOS NO ARQUIVO CSV ---")
        
        # Imprime a tabela completa de forma legível
        pd.set_option('display.max_rows', None)
        print(contagem_unidades)
        
        logging.info("-------------------------------------------------------------")
        logging.warning("Compare os nomes da coluna 'NOME_DA_UNIDADE_NO_CSV' com as chaves do seu 'MAPA_GESTORES'.")
        logging.warning("Eles devem ser IDÊNTICOS (incluindo espaços, maiúsculas/minúsculas e caracteres especiais).")

    except FileNotFoundError:
        logging.error(f"ERRO CRÍTICO: O arquivo '{caminho_csv}' não foi encontrado.")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}", exc_info=True)

if __name__ == "__main__":
    main()
