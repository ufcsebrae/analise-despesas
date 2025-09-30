# diagnosticar_dados.py
import pandas as pd
import logging
from analise_despesa.config import PARAMETROS_ANALISE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Lê o arquivo CSV e faz um perfil completo das colunas críticas (VALOR e UNIDADE)
    para diagnosticar problemas de tipo de dado e conteúdo.
    """
    try:
        caminho_csv = PARAMETROS_ANALISE["ARQUIVO_CSV_LOCAL"]
        logging.info(f"Analisando o arquivo: {caminho_csv}")

        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig', low_memory=False)

        logging.info("\n\n--- PASSO 1: INFORMAÇÕES GERAIS DO DATAFRAME ---")
        print("O comando df.info() nos mostra o tipo de dado de cada coluna.")
        print("Procure pelas colunas 'VALOR' e 'UNIDADE'. Elas deveriam ser 'float64' e 'object', respectivamente.")
        print("Se 'VALOR' estiver como 'object', encontramos o problema.")
        print("--------------------------------------------------")
        df.info()
        print("--------------------------------------------------")

        # --- PASSO 2: AMOSTRA DOS DADOS DA COLUNA 'VALOR' ---
        if 'VALOR' in df.columns:
            logging.info("\n\n--- PASSO 2: AMOSTRA DOS DADOS DA COLUNA 'VALOR' ---")
            print("Abaixo estão os 10 primeiros valores da coluna 'VALOR' exatamente como o Python os lê.")
            print("Procure por símbolos (R$), separadores de milhar (,) ou outros caracteres não numéricos.")
            print("--------------------------------------------------")
            print(df['VALOR'].head(10).to_string())
            print("--------------------------------------------------")
        else:
            logging.error("\nERRO CRÍTICO: A coluna 'VALOR' não foi encontrada no CSV.")

    except FileNotFoundError:
        logging.error(f"ERRO CRÍTICO: O arquivo '{caminho_csv}' não foi encontrado.")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}", exc_info=True)

if __name__ == "__main__":
    main()
