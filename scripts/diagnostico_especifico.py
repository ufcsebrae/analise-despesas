import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# O caminho do arquivo que o main.py gera
caminho_csv = r'C:\temp\RelatoriosSQL\base_completa_extraida_hoje.csv'

# Os nomes exatos que estamos investigando
unidade_alvo = "SP - Finanças e Controladoria"
projeto_alvo = "Gestão Operacional - Remuneração de Recursos Humanos - Custeio Administrativo"

try:
    logger.info(f"Analisando o arquivo em '{caminho_csv}'...")
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig', low_memory=False)
    logger.info(f"Arquivo carregado com {len(df)} linhas.")

    # PASSO 1: Isolar a Unidade (limpando espaços em branco por segurança)
    df_unidade = df[df['UNIDADE'].str.strip() == unidade_alvo].copy()

    # PASSO 2: Isolar o Projeto
    df_projeto = df_unidade[df_unidade['PROJETO'].str.strip() == projeto_alvo].copy()

    # PASSO 3: Aplicar o filtro de "apenas_despesas" (VALOR > 0)
    df_final_para_soma = df_projeto[df_projeto['VALOR'] > 0]

    soma_python = df_final_para_soma['VALOR'].sum()

    print("\n" + "="*80)
    logger.info(f"O Python está somando as {len(df_final_para_soma)} linhas abaixo para o projeto '{projeto_alvo}'.")
    logger.info(f"Soma calculada pelo Python: {soma_python:,.2f}")
    logger.info("Soma esperada (do Excel): 5,587,725.50")
    print("="*80)

    if df_final_para_soma.empty:
        logger.warning("Nenhuma linha encontrada para estes filtros. Verifique os nomes da unidade e projeto.")
    else:
        # Mostra as linhas que estão sendo somadas
        print("\n>>> ESTAS SÃO AS LINHAS QUE O PYTHON ESTÁ SOMANDO:\n")
        print(df_final_para_soma.to_string())

except FileNotFoundError:
    logger.error(f"Arquivo não encontrado em '{caminho_csv}'. Execute o 'main.py' para gerá-lo primeiro.")
except Exception as e:
    logger.error(f"Um erro ocorreu: {e}", exc_info=True)

