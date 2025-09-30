import pandas as pd
import logging

# Configuração para mostrar mensagens claras
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- CAMINHO CORRIGIDO ---
caminho_csv = r'C:\temp\RelatoriosSQL\base_completa_extraida_hoje.csv'

try:
    logger.info(f"Analisando o arquivo em '{caminho_csv}'...")
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig')
    logger.info(f"Arquivo carregado. Total de {len(df)} linhas.")

    # Acha TODAS as linhas que são 100% idênticas a pelo menos uma outra linha.
    df_repetidas = df[df.duplicated(keep=False)]

    print("\n" + "="*50)
    if df_repetidas.empty:
        logger.warning("RESULTADO FINAL: NENHUMA LINHA 100% IDÊNTICA FOI ENCONTRADA NO ARQUIVO.")
    else:
        logger.info("RESULTADO FINAL: ENCONTRADAS AS SEGUINTES LINHAS 100% IDÊNTICAS:")
        # Ordena para agrupar visualmente as linhas idênticas
        print(df_repetidas.sort_values(by=list(df.columns)).to_string())
    print("="*50 + "\n")

except FileNotFoundError:
    logger.error(f"Arquivo não encontrado em '{caminho_csv}'. Execute o 'main.py' para gerá-lo primeiro.")
except Exception as e:
    logger.error(f"Um erro ocorreu: {e}", exc_info=True)
