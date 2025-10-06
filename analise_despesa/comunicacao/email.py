# analise_despesa/comunicacao/email.py (VERSÃO FINAL COM A ETIQUETA 'is_total')

import pandas as pd
import logging, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

logger = logging.getLogger(__name__)
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def gerar_corpo_email_analise(unidade_gestora: str, data_relatorio: str, resumo: dict,
                              df_orcamento_exclusivo: pd.DataFrame, df_orcamento_compartilhado: pd.DataFrame,
                              df_fornecedores_exclusivo: pd.DataFrame, df_fornecedores_compartilhado: pd.DataFrame,
                              df_mes_agregado: pd.DataFrame,
                              df_ocorrencias_atipicas: pd.DataFrame,
                              df_clusters_folha: Dict[str, pd.DataFrame],
                              resumo_clusters_folha: Dict[str, Dict[str, Any]]) -> str:
    logger.info("Gerando corpo de e-mail com todas as análises...")
    template = env.get_template('relatorio_analise.html')
    
    def robust_currency_formatter(value):
        if pd.isna(value) or (isinstance(value, (int, float)) and value == 0): return "-"
        if isinstance(value, str): return value
        return f"R$ {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def robust_int_formatter(value):
        if pd.isna(value): return "-"
        return f"{int(value):,}".replace(",", ".")

    def robust_percent_formatter(value):
        if pd.isna(value): return "N/A"
        return f"{value:.0%}"

    # --- CORREÇÃO AQUI: Adicionando a etiqueta 'is_total' ---
    itens_resumo = [
        {"indicador": "Total Gasto (Realizado)", "mes": robust_currency_formatter(resumo.get("valor_total_mes")), "ano": robust_currency_formatter(resumo.get("valor_total_ano")), "is_total": True},
        {"indicador": "&nbsp;&nbsp;↳ Gastos - Iniciativas exclusivas", "mes": robust_currency_formatter(resumo.get("gastos_mes_exclusivo")), "ano": robust_currency_formatter(resumo.get("gastos_ano_exclusivo")), "is_total": False},
        {"indicador": "&nbsp;&nbsp;↳ Gastos - Iniciativas compartilhadas", "mes": robust_currency_formatter(resumo.get("gastos_mes_compartilhado")), "ano": robust_currency_formatter(resumo.get("gastos_ano_compartilhado")), "is_total": False},
        {"indicador": "Orçamento Planejado (a+b)", "mes": robust_currency_formatter(resumo.get("orcamento_mes_referencia")), "ano": robust_currency_formatter(resumo.get("orcamento_planejado_ano")), "is_total": True},
        {"indicador": "&nbsp;&nbsp;↳ Orçamento - Iniciativas exclusivas (a)", "mes": robust_currency_formatter(resumo.get("orcamento_mes_exclusivo")), "ano": robust_currency_formatter(resumo.get("orcamento_total_exclusivo")), "is_total": False},
        {"indicador": "&nbsp;&nbsp;↳ Orçamento - Iniciativas compartilhadas (b)", "mes": robust_currency_formatter(resumo.get("orcamento_mes_compartilhado")), "ano": robust_currency_formatter(resumo.get("orcamento_total_compartilhado")), "is_total": False},
        {"indicador": "Total de Lançamentos", "mes": resumo.get("qtd_lancamentos_mes"), "ano": resumo.get("qtd_lancamentos_ano"), "is_total": True},
    ]

    resumo_formatado = {
        "numero_unidade": resumo.get("numero_unidade"), "mes_referencia": resumo.get("mes_referencia"),
        "valor_mediano_mes_exclusivo": robust_currency_formatter(resumo.get("valor_mediano_mes_exclusivo")),
        "min_normal_mes_exclusivo": robust_currency_formatter(resumo.get("min_normal_mes_exclusivo")), "max_normal_mes_exclusivo": robust_currency_formatter(resumo.get("max_normal_mes_exclusivo")),
        "media_ano_exclusivo": robust_currency_formatter(resumo.get("media_ano_exclusivo")), "mediana_ano_exclusivo": robust_currency_formatter(resumo.get("mediana_ano_exclusivo")),
        "maior_ano_exclusivo": robust_currency_formatter(resumo.get("maior_ano_exclusivo")), "menor_ano_exclusivo": robust_currency_formatter(resumo.get("menor_ano_exclusivo")),
        "valor_mediano_mes_compartilhado": robust_currency_formatter(resumo.get("valor_mediano_mes_compartilhado")),
        "min_normal_mes_compartilhado": robust_currency_formatter(resumo.get("min_normal_mes_compartilhado")), "max_normal_mes_compartilhado": robust_currency_formatter(resumo.get("max_normal_mes_compartilhado")),
        "media_ano_compartilhado": robust_currency_formatter(resumo.get("media_ano_compartilhado")), "mediana_ano_compartilhado": robust_currency_formatter(resumo.get("mediana_ano_compartilhado")),
        "maior_ano_compartilhado": robust_currency_formatter(resumo.get("maior_ano_compartilhado")), "menor_ano_compartilhado": robust_currency_formatter(resumo.get("menor_ano_compartilhado")),
    }
    
    resumo_clusters_formatado = {name: {'valor_total': robust_currency_formatter(data.get('valor_total')), 'frequencia': robust_int_formatter(data.get('frequencia')), 'coef_variacao': robust_percent_formatter(data.get('coef_variacao')), 'description': data.get('description', 'Descrição não disponível.')} for name, data in resumo_clusters_folha.items()}

    formatters = {
        'projeto': {'Criticidade': lambda x: x, 'Orçado': robust_currency_formatter, 'Realizado': robust_currency_formatter, '% Execução': robust_percent_formatter},
        'fornecedor': {'Realizado (Ano)': robust_currency_formatter},
        'ocorrencia': {'Realizado': robust_currency_formatter, 'Justificativa IA': lambda x: x},
        'mes': {'Mês': lambda x: x, 'Realizado (Exclusivo)': robust_currency_formatter, 'Realizado (Compartilhado)': robust_currency_formatter, 'Sinalização da IA': lambda x: x},
        'folha_cluster': {'Agrupamento Contábil (Nível 4)': lambda x: x, 'Valor Total (Ano)': robust_currency_formatter, 'Qtd. Lançamentos (Ano)': robust_int_formatter, 'Coeficiente de Variação (CV)': robust_percent_formatter}
    }
    tabelas_html = {
        'tabela_orc_exclusivo': df_orcamento_exclusivo.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['projeto']),
        'tabela_orc_compartilhado': df_orcamento_compartilhado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['projeto']),
        'tabela_forn_exclusivo': df_fornecedores_exclusivo.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['fornecedor']),
        'tabela_forn_compartilhado': df_fornecedores_compartilhado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['fornecedor']),
        'tabela_mes_agregado': df_mes_agregado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['mes']),
        'tabela_ocorrencias_atipicas': df_ocorrencias_atipicas.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['ocorrencia']),
    }
    clusters_folha_html = {name: df.to_html(index=False, na_rep='-', classes='table', formatters=formatters['folha_cluster']) for name, df in df_clusters_folha.items()}
    
    return template.render(
        unidade_gestora=unidade_gestora, data_relatorio=data_relatorio, resumo=resumo_formatado, itens_resumo=itens_resumo,
        tem_exclusivos=not df_orcamento_exclusivo.empty, tem_compartilhados=not df_orcamento_compartilhado.empty,
        tem_fornecedores_exclusivos=not df_fornecedores_exclusivo.empty, tem_fornecedores_compartilhados=not df_fornecedores_compartilhado.empty,
        tem_ocorrencias_atipicas=not df_ocorrencias_atipicas.empty,
        tem_contexto_exclusivo=resumo.get("valor_mediano_mes_exclusivo") is not None, tem_contexto_compartilhado=resumo.get("valor_mediano_mes_compartilhado") is not None,
        tem_clusters_folha=bool(df_clusters_folha), clusters_folha=clusters_folha_html, resumo_clusters_folha=resumo_clusters_formatado, **tabelas_html
    )



def enviar_email_via_smtp(assunto: str, corpo_html: str, destinatario: str):
    logger.info(f"Iniciando envio de e-mail para {destinatario} via SMTP...")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        logger.error("Credenciais SMTP não configuradas. O e-mail não pode ser enviado.")
        return
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
        logger.info(f"✅ E-mail para '{destinatario}' enviado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail via SMTP. Erro: {e}", exc_info=True)
        raise
