# analise_despesa/utils.py
# VERSÃO CORRIGIDA: Usa pathlib para encontrar os arquivos a partir da raiz do projeto.

import logging
from pathlib import Path  # NOVO: Importa a biblioteca para lidar com caminhos

logger = logging.getLogger(__name__)

# NOVO: Define o diretório raiz do projeto de forma dinâmica.
# Path(__file__) é o caminho para este arquivo (utils.py).
# .parent vai para a pasta 'analise_despesa'.
# .parent vai novamente para a raiz do projeto ('analise-despesas').
BASE_DIR = Path(__file__).resolve().parent.parent

def carregar_sql(caminho_relativo: str) -> str:
    """
    Lê e retorna o conteúdo de um arquivo de texto (SQL/MDX).
    Agora constrói um caminho absoluto a partir da raiz do projeto, tornando-o infalível.
    """
    # MODIFICADO: Constrói o caminho completo e absoluto para o arquivo SQL.
    # Ex: BASE_DIR / 'sql/extracao_realizado.sql'
    caminho_absoluto = BASE_DIR / caminho_relativo
    
    logger.debug(f"Carregando query do caminho absoluto: {caminho_absoluto}")
    
    try:
        # MODIFICADO: Usa o novo caminho absoluto para abrir o arquivo.
        with open(caminho_absoluto, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # A mensagem de erro agora mostrará o caminho relativo, que é mais limpo.
        logger.error(f"Arquivo de query não encontrado no caminho: '{caminho_absoluto}'")
        raise FileNotFoundError(f"Arquivo de query não encontrado em: '{caminho_relativo}'")
    except Exception as e:
        logger.error(f"Erro inesperado ao ler o arquivo de query '{caminho_absoluto}': {e}")
        raise
