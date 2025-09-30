# exportar_view.py
import logging
import time
import os
import pandas as pd

# Importa apenas o que é necessário para a conexão
from analise_despesa.database import obter_conexao
from analise_despesa.config import PARAMETROS_ANALISE

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def exportar_view_para_csv():
    """
    Conecta-se ao banco de dados, lê o conteúdo completo da VIEW 'vw_AnaliseDespesas'
    para um ano específico e salva em um arquivo CSV para verificação.
    """
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        # --- NOME CORRETO DA VIEW ---
        nome_view = 'vw_AnaliseDespesas' 
        caminho_csv = PARAMETROS_ANALISE["ARQUIVO_CSV_LOCAL"]
        logger.info(f"Iniciando exportação da VIEW '{nome_view}' para o ano {ano}...")
    except KeyError as e:
        logger.error(f"Parâmetro '{e}' não encontrado no arquivo de configuração.")
        return

    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

    inicio = time.perf_counter()
    engine = obter_conexao("SPSVSQL39_FINANCA")
    
    sql_query = f"""
        SELECT * 
        FROM {nome_view}
        WHERE YEAR([DATA]) = {ano}
    """

    try:
        logger.info("Executando a consulta na VIEW...")
        df = pd.read_sql(sql_query, engine)
        
        fim_leitura = time.perf_counter()
        logger.info(f"Leitura da VIEW concluída em {fim_leitura - inicio:.2f}s. "
                    f"Foram encontradas {len(df)} linhas.")

        if df.empty:
            logger.warning("A VIEW não retornou dados. Nenhum arquivo CSV será gerado.")
            return

        logger.info(f"Salvando os dados em: '{caminho_csv}'")
        
        df.to_csv(
            caminho_csv,
            index=False,
            sep=';',
            encoding='utf-8-sig'
        )
        
        fim_total = time.perf_counter()
        logger.info(f"SUCESSO! Arquivo CSV gerado em {fim_total - inicio:.2f}s.")
        logging.warning("Por favor, abra o arquivo CSV e verifique os nomes das colunas e os valores na coluna 'UNIDADE'.")

    except Exception as e:
        logging.error(f"Falha crítica durante a exportação. Erro: {e}", exc_info=True)

if __name__ == "__main__":
    exportar_view_para_csv()
