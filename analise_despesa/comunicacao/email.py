# analise_despesa/comunicacao/email.py (VERSÃO FINAL COM FORMATADORES INTELIGENTES)

import pandas as pd
import logging, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def gerar_corpo_email_analise(unidade_gestora: str, data_relatorio: str, resumo: dict,
                              df_orcamento_exclusivo: pd.DataFrame, df_orcamento_compartilhado: pd.DataFrame,
                              df_fornecedores_exclusivo: pd.DataFrame, df_fornecedores_compartilhado: pd.DataFrame,
                              df_mes_agregado: pd.DataFrame,
                              df_anomalias_exclusivo: pd.DataFrame, df_anomalias_compartilhado: pd.DataFrame) -> str:
    logger.info("Gerando corpo de e-mail para a unidade...")
    template = env.get_template('relatorio_analise.html')
    
    # --- MUDANÇA PRINCIPAL: Formatadores que verificam o tipo de dado ---
    def robust_currency_formatter(value):
        """Formata o valor como moeda se for um número, senão, retorna o valor como está."""
        if isinstance(value, str):
            return value
        if pd.isna(value):
            return "N/A"
        return f"R$ {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def robust_percent_formatter(value):
        """Formata o valor como percentual se for um número, senão, retorna o valor como está."""
        if isinstance(value, str):
            return value
        if pd.isna(value):
            return "N/A"
        return f"{value:.0%}"

    resumo_formatado = {k: (robust_currency_formatter(v) if 'valor' in k else v) for k, v in resumo.items()}
    if 'numero_unidade' in resumo:
        resumo_formatado['numero_unidade'] = resumo['numero_unidade']

    formatters = {
        'projeto': {'Orçado': robust_currency_formatter, 'Realizado': robust_currency_formatter, '% Execução': robust_percent_formatter},
        'fornecedor': {'Realizado (Ano)': robust_currency_formatter},
        'anomalia': {'Realizado': robust_currency_formatter},
        'mes': {
            'Valor (Exclusivo)': robust_currency_formatter, 'Acumulado (Exclusivo)': robust_currency_formatter,
            'Valor (Compartilhado)': robust_currency_formatter, 'Acumulado (Compartilhado)': robust_currency_formatter
        }
    }

    # Usamos escape=False para permitir que o HTML de negrito (<b>) seja renderizado
    tabelas_html = {
        'tabela_orc_exclusivo': df_orcamento_exclusivo.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['projeto'], escape=False),
        'tabela_orc_compartilhado': df_orcamento_compartilhado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['projeto'], escape=False),
        'tabela_forn_exclusivo': df_fornecedores_exclusivo.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['fornecedor']),
        'tabela_forn_compartilhado': df_fornecedores_compartilhado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['fornecedor']),
        'tabela_mes_agregado': df_mes_agregado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['mes']),
        'tabela_anom_exclusivo': df_anomalias_exclusivo.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['anomalia']),
        'tabela_anom_compartilhado': df_anomalias_compartilhado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['anomalia']),
    }

    return template.render(
        unidade_gestora=unidade_gestora, data_relatorio=data_relatorio, resumo=resumo_formatado,
        tem_exclusivos=not df_orcamento_exclusivo.empty, tem_compartilhados=not df_orcamento_compartilhado.empty,
        tem_anomalias_exclusivas=not df_anomalias_exclusivo.empty, tem_anomalias_compartilhadas=not df_anomalias_compartilhado.empty,
        **tabelas_html
    )

def enviar_email_via_smtp(assunto: str, corpo_html: str, destinatario: str):
    logger.info(f"Iniciando envio de e-mail para {destinatario} via SMTP...")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        logger.error("Credenciais SMTP não configuradas no arquivo .env. O e-mail não pode ser enviado.")
        raise ValueError("Variáveis de ambiente SMTP (HOST, PORT, USER, PASSWORD) não definidas.")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = smtp_user
        msg['To'] = destinatario
        part_html = MIMEText(corpo_html, 'html')
        msg.attach(part_html)
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"✅ E-mail para '{destinatario}' enviado com sucesso via SMTP!")
    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail via SMTP para '{destinatario}'. Erro: {e}", exc_info=True)
        raise
