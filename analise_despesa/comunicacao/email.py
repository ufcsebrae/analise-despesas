# comunicacao/email.py
# VERSÃO REATORADA COM JINJA2

import pandas as pd
import logging
import os
import win32com.client as win32
from jinja2 import Environment, FileSystemLoader # Importar Jinja2

logger = logging.getLogger(__name__)

# Configura o Jinja2 para buscar templates na pasta correta
# O Path(__file__).parent aponta para a pasta 'comunicacao'
# .parent.parent aponta para a raiz do projeto
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def gerar_corpo_email_analise(unidade_gestora: str, data_relatorio: str, df_top_fornecedores: pd.DataFrame, 
                              df_anomalias: pd.DataFrame, df_por_projeto: pd.DataFrame,
                              df_por_mes: pd.DataFrame) -> str:
    """Gera um corpo de e-mail HTML a partir de um template Jinja2."""
    logger.info("Gerando corpo de e-mail a partir do template 'relatorio_analise.html'...")

    template = env.get_template('relatorio_analise.html')
    
    # Prepara as tabelas HTML que serão injetadas no template
    # O argumento 'classes' pode ser usado para estilização com CSS
    tabelas_html = {
        'tabela_projetos_html': df_por_projeto.to_html(index=False, na_rep='N/A'),
        'tabela_fornecedores_html': df_top_fornecedores.to_html(index=False, na_rep='N/A'),
        'tabela_anomalias_html': df_anomalias.to_html(index=False, na_rep='N/A')
    }

    # Renderiza o template, passando as variáveis
    corpo_html = template.render(
        unidade_gestora=unidade_gestora,
        data_relatorio=data_relatorio,
        anomalias_encontradas=not df_anomalias.empty,
        **tabelas_html
    )
    return corpo_html

def enviar_email_via_outlook(assunto: str, corpo_html: str, destinatario: str, caminho_anexo: str = None):
    """Cria e envia um e-mail através do Outlook (sem alterações)."""
    logger.info(f"Iniciando criação de e-mail para {destinatario} via Outlook...")
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = destinatario
        mail.Subject = assunto
        mail.HTMLBody = corpo_html

        if caminho_anexo and os.path.exists(caminho_anexo):
            mail.Attachments.Add(os.path.abspath(caminho_anexo))
        
        mail.Send()
        logger.info(f"✅ E-mail para '{destinatario}' enviado com sucesso através do Outlook!")
    except Exception as e:
        logger.error(f"❌ Falha ao tentar controlar o Outlook para o destinatário '{destinatario}'. Erro: {e}", exc_info=True)
        raise
