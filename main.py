# main.py (na raiz)
import logging
from analise_despesa.main import executar_analise_distribuida

# Configuração centralizada do logging para todo o projeto.
# Isso garante que todos os 'logger.info/error' nos outros módulos funcionem.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    logging.info(">>> Iniciando a análise de despesas...")
    executar_analise_distribuida()
    logging.info(">>> Análise concluída com sucesso!")
