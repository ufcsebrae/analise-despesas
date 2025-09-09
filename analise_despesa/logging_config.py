# analise_despesa/logging_config.py
import logging
import os

def setup_logging():
    """Configura o sistema de logging para console e arquivo."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Define o nível de log para DEBUG para capturar mais detalhes, se necessário.
    # Em produção, você pode mudar para logging.INFO.
    log_level = logging.INFO 

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        # Removido o 'handlers' daqui para evitar duplicação com os handlers abaixo.
        # Isso garante que cada log não apareça duas vezes.
    )

    # Limpa handlers existentes para evitar logs duplicados em re-execuções (comum em notebooks)
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()

    # Handler para o console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    
    # Handler para o arquivo, com a codificação UTF-8
    file_handler = logging.FileHandler(
        os.path.join(log_dir, "analise_despesas.log"), 
        encoding='utf-8'  # <--- ESTA É A CORREÇÃO PRINCIPAL
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Adiciona os handlers ao logger raiz
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# Chamar setup_logging() no início de main.py
