# analise_despesa/comunicacao/email.py (VERSÃO FINAL COMPLETA)

import pandas as pd
import logging, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List
from . import graficos_html
import json

logger = logging.getLogger(__name__)
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def gerar_corpo_email_analise(unidade_gestora: str, data_relatorio: str, resumo: dict,
                              df_orcamento_exclusivo: pd.DataFrame, df_orcamento_compartilhado: pd.DataFrame,
                              df_mes_agregado: pd.DataFrame, link_relatorio_detalhado: str) -> str:
    """Gera o corpo do e-mail SUMARIZADO."""
    template = env.get_template('relatorio_analise.html')
    
    def robust_currency_formatter(value):
        if pd.isna(value) or (isinstance(value, (int, float)) and value == 0): return "-"
        if isinstance(value, str): return value
        return f"R$ {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def robust_percent_formatter(value):
        if isinstance(value, str): return value
        if pd.isna(value): return "N/A"
        return f"{value:.0%}"

    itens_resumo = [
        {"indicador": "Total Gasto (Realizado)", "mes": robust_currency_formatter(resumo.get("valor_total_mes")), "ano": robust_currency_formatter(resumo.get("valor_total_ano")), "is_total": True},
        {"indicador": "&nbsp;&nbsp;↳ Gastos - Iniciativas exclusivas", "mes": robust_currency_formatter(resumo.get("gastos_mes_exclusivo")), "ano": robust_currency_formatter(resumo.get("gastos_ano_exclusivo")), "is_total": False},
        {"indicador": "&nbsp;&nbsp;↳ Gastos - Iniciativas compartilhadas", "mes": robust_currency_formatter(resumo.get("gastos_mes_compartilhado")), "ano": robust_currency_formatter(resumo.get("gastos_ano_compartilhado")), "is_total": False},
        {"indicador": "Orçamento Planejado (a+b)", "mes": robust_currency_formatter(resumo.get("orcamento_mes_referencia")), "ano": robust_currency_formatter(resumo.get("orcamento_planejado_ano")), "is_total": True},
        {"indicador": "&nbsp;&nbsp;↳ Orçamento - Iniciativas exclusivas (a)", "mes": robust_currency_formatter(resumo.get("orcamento_mes_exclusivo")), "ano": robust_currency_formatter(resumo.get("orcamento_total_exclusivo")), "is_total": False},
        {"indicador": "&nbsp;&nbsp;↳ Orçamento - Iniciativas compartilhadas (b)", "mes": robust_currency_formatter(resumo.get("orcamento_mes_compartilhado")), "ano": robust_currency_formatter(resumo.get("orcamento_total_compartilhado")), "is_total": False},
        {"indicador": "Total de Lançamentos", "mes": resumo.get("qtd_lancamentos_mes"), "ano": resumo.get("qtd_lancamentos_ano"), "is_total": True},
    ]
    resumo_formatado = {"numero_unidade": resumo.get("numero_unidade"), "mes_referencia": resumo.get("mes_referencia")}
    formatters = {'projeto': {'Criticidade': lambda x: x, 'Orçado': robust_currency_formatter, 'Realizado': robust_currency_formatter, '% Execução': robust_percent_formatter}, 'mes': {'Mês': lambda x: x, 'Realizado (Exclusivo)': robust_currency_formatter, 'Realizado (Compartilhado)': robust_currency_formatter, 'Sinalização da IA': lambda x: x}}
    tabelas_html = {
        'tabela_orc_exclusivo': df_orcamento_exclusivo.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['projeto']),
        'tabela_orc_compartilhado': df_orcamento_compartilhado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['projeto']),
        'tabela_mes_agregado': df_mes_agregado.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['mes']),
    }
    return template.render(unidade_gestora=unidade_gestora, data_relatorio=data_relatorio, resumo=resumo_formatado, itens_resumo=itens_resumo, tem_exclusivos=not df_orcamento_exclusivo.empty, tem_compartilhados=not df_orcamento_compartilhado.empty, link_relatorio_detalhado=link_relatorio_detalhado, **tabelas_html)

def gerar_relatorio_detalhado(unidade_gestora: str, data_relatorio: str, resumo: dict,
                               df_unidade_bruto: pd.DataFrame,
                               df_orcamento_exclusivo: pd.DataFrame,
                               df_fornecedores_exclusivo: pd.DataFrame,
                               df_ocorrencias_atipicas: pd.DataFrame,
                               df_clusters: Dict[str, pd.DataFrame],
                               resumo_clusters: Dict[str, Dict[str, Any]]) -> str:
    logger.info("Gerando corpo do relatório detalhado interativo...")
    template = env.get_template('relatorio_detalhado.html')
    
    chart_data = {
        'orcamento': graficos_html.preparar_dados_execucao_orcamentaria(df_orcamento_exclusivo),
        'tendencia': graficos_html.preparar_dados_tendencia_mensal(resumo.get('df_mes_agregado_raw', pd.DataFrame())),
        'fornecedores': graficos_html.preparar_dados_top_fornecedores(df_fornecedores_exclusivo),
        'ocorrencias': graficos_html.preparar_dados_ocorrencias_por_justificativa(df_ocorrencias_atipicas),
        'treemap': graficos_html.preparar_dados_treemap_contas(df_unidade_bruto),
        'distribuicao': graficos_html.preparar_dados_distribuicao_tipo_projeto(resumo),
        'cluster': graficos_html.preparar_dados_para_grafico_cluster(df_clusters)
    }

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

    resumo_clusters_formatado = {}
    for name, data in resumo_clusters.items():
        resumo_clusters_formatado[name] = {
            'valor_total': robust_currency_formatter(data.get('valor_total')),
            'frequencia': robust_int_formatter(data.get('frequencia')),
            'coef_variacao': robust_percent_formatter(data.get('coef_variacao')),
            'description': data.get('description', 'Descrição não disponível.')
        }
    
    formatters = {
        'ocorrencia': {'Realizado': robust_currency_formatter, 'Justificativa IA': lambda x: x},
        'cluster': {'Agrupamento Contábil (Nível 4)': lambda x: x, 'Valor Total (Ano)': robust_currency_formatter, 'Qtd. Lançamentos (Ano)': robust_int_formatter, 'Coeficiente de Variação (CV)': robust_percent_formatter}
    }
    
    tabela_ocorrencias_html = df_ocorrencias_atipicas.to_html(index=False, na_rep='N/A', classes='table', formatters=formatters['ocorrencia'])
    clusters_html = {name: df.to_html(index=False, na_rep='-', classes='table', formatters=formatters['cluster']) for name, df in df_clusters.items()}
    
    return template.render(
        unidade_gestora=unidade_gestora, data_relatorio=data_relatorio, resumo=resumo,
        tem_ocorrencias_atipicas=not df_ocorrencias_atipicas.empty,
        tem_clusters_folha=bool(df_clusters),
        tabela_ocorrencias_atipicas=tabela_ocorrencias_html,
        clusters_folha=clusters_html,
        resumo_clusters_folha=resumo_clusters_formatado,
        chart_data_json=json.dumps(chart_data)
    )


def enviar_email_via_smtp(assunto: str, corpo_html: str, destinatario: str, caminhos_anexos: List[str] = None):
    logger.info(f"Iniciando envio de e-mail para {destinatario} via SMTP...")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        logger.error("Credenciais SMTP não configuradas. O e-mail não pode ser enviado.")
        return
    try:
        msg = MIMEMultipart()
        msg['Subject'] = assunto
        msg['From'] = smtp_user
        msg['To'] = destinatario
        msg.attach(MIMEText(corpo_html, 'html'))
        
        if caminhos_anexos:
            for caminho_anexo in caminhos_anexos:
                if not os.path.exists(caminho_anexo):
                    logger.warning(f"Arquivo de anexo não encontrado: {caminho_anexo}. Pulando.")
                    continue

                filename = os.path.basename(caminho_anexo)
                logger.info(f"Anexando arquivo: {filename}")
                
                ctype = 'application/octet-stream'
                if filename.lower().endswith('.csv'):
                    ctype = 'text/csv'
                elif filename.lower().endswith('.pptx'):
                    ctype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                
                maintype, subtype = ctype.split('/', 1)

                if maintype == 'text':
                    with open(caminho_anexo, 'r', encoding='utf-8-sig') as attachment:
                        part = MIMEText(attachment.read(), subtype, 'utf-8')
                else:
                    with open(caminho_anexo, 'rb') as attachment:
                        part = MIMEBase(maintype, subtype)
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)
                logger.info(f"Arquivo '{filename}' anexado com o tipo MIME '{ctype}'.")

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"✅ E-mail para '{destinatario}' enviado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail via SMTP. Erro: {e}", exc_info=True)
        raise
