# /exportar_relatorio.py
import os
import logging
# Vamos precisar do seu extracao.py e de alguns outros módulos
from analise_despesa.extracao import buscar_dados
from analise_despesa.exceptions import AnaliseDespesaError
from analise_despesa.config import CONTAS_PARA_ANALISE

# Configuração para vermos mensagens de progresso no terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# ÁREA DE CONFIGURAÇÃO - Altere os valores aqui conforme sua necessidade
# ==============================================================================

# 1. Defina ONDE o arquivo CSV deve ser salvo.
CAMINHO_DE_SAIDA = 'C:/Temp/RelatoriosSQL'

# 2. Defina o NOME do arquivo CSV que será gerado.
NOME_DO_ARQUIVO = 'base_completa_2025.csv'

# 3. Defina os PARÂMETROS para a consulta na Stored Procedure.
#    Para exportar TUDO, definimos 'unidade_gestora' como None.
PARAMETROS_DA_BUSCA = {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-12-31",
    "unidade_gestora": None, # <-- None para trazer todas as unidades
    "contas": CONTAS_PARA_ANALISE # <-- Usando a lista do seu config.py
}

# ==============================================================================
# LÓGICA DO SCRIPT - Não precisa alterar
# ==============================================================================

def main():
    """
    Função principal que orquestra a busca de dados e a exportação para CSV.
    """
    logging.info("Iniciando processo de exportação de relatório completo.")
    try:
        os.makedirs(CAMINHO_DE_SAIDA, exist_ok=True)
        logging.info(f"Diretório de saída '{CAMINHO_DE_SAIDA}' está pronto.")
        
        caminho_completo_csv = os.path.join(CAMINHO_DE_SAIDA, NOME_DO_ARQUIVO)

        logging.info("Buscando dados via Stored Procedure (sem filtro de unidade)...")
        
        # A função 'buscar_dados' já está preparada para chamar a Stored Procedure
        df_resultado = buscar_dados("BaseDespesas", params=PARAMETROS_DA_BUSCA)

        if df_resultado.empty:
            logging.warning("A consulta não retornou dados. O arquivo CSV não será gerado.")
            return

        logging.info(f"Busca concluída. Salvando {len(df_resultado)} linhas em CSV...")
        
        df_resultado.to_csv(
            caminho_completo_csv,
            index=False,
            sep=';',
            encoding='utf-8-sig'
        )

        logging.info(f"SUCESSO! Relatório salvo em: {caminho_completo_csv}")

    except (AnaliseDespesaError, ValueError) as e:
        logging.error(f"ERRO no processo: {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}", exc_info=True)

if __name__ == "__main__":
    main()
