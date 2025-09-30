# comunicacao/email.py
import pandas as pd
import logging
import os
import win32com.client as win32
from datetime import datetime

logger = logging.getLogger(__name__)

def enviar_email_via_outlook(assunto: str, corpo_html: str, destinatario: str, caminho_anexo: str = None):
    """Cria e envia um e-mail através do Outlook, com anexo opcional."""
    logger.info(f"Iniciando criação de e-mail para {destinatario} via Outlook...")
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = destinatario
        mail.Subject = assunto
        mail.HTMLBody = corpo_html

        if caminho_anexo and os.path.exists(caminho_anexo):
            caminho_absoluto_anexo = os.path.abspath(caminho_anexo)
            mail.Attachments.Add(caminho_absoluto_anexo)
        
        mail.Send()
        logger.info("✅ E-mail enviado com sucesso através do Outlook!")
    except Exception as e:
        logger.error("❌ Falha ao tentar controlar o Outlook.", exc_info=True)
        raise

def gerar_corpo_email_analise(df_completo: pd.DataFrame, df_top_fornecedores: pd.DataFrame, 
                              df_anomalias: pd.DataFrame, df_por_projeto: pd.DataFrame, 
                              df_por_mes: pd.DataFrame) -> str:
    """Gera o corpo do e-mail em HTML com todas as novas tabelas de agregação."""
    logger.info("Gerando corpo do e-mail de análise com múltiplas agregações...")

    total_despesa = df_completo[df_completo['VALOR'] > 0]['VALOR'].sum()
    transacoes_total = len(df_completo)
    periodo_inicio = pd.to_datetime(df_completo['DATA']).min().strftime('%d/%m/%Y')
    periodo_fim = pd.to_datetime(df_completo['DATA']).max().strftime('%d/%m/%Y')
    
    # --- Lógica robusta para cada tabela ---
    principal_fornecedor_str = "N/A" if df_top_fornecedores.empty else df_top_fornecedores.iloc[0]['FORNECEDOR']
    resumo_anomalias = "Nenhuma anomalia detectada." if df_anomalias.empty else f"Detectadas {len(df_anomalias)} despesas anômalas."

    def formatar_tabela_html(df, titulo):
        if df.empty:
            return f"<h2>{titulo}</h2><p><i>Não há dados para exibir.</i></p>"
        # Formata a coluna de valor como moeda
        df_copy = df.copy()
        if 'VALOR' in df_copy.columns:
            df_copy['VALOR'] = df_copy['VALOR'].map('R$ {:,.2f}'.format)
        return f"<h2>{titulo}</h2>" + df_copy.to_html(index=False, justify='left', border=0, classes='dataframe')

    tabela_top_fornecedores_html = formatar_tabela_html(df_top_fornecedores, "Top 10 Fornecedores por Valor")
    tabela_anomalias_html = formatar_tabela_html(df_anomalias[['DATA', 'FORNECEDOR', 'COMPLEMENTO', 'VALOR']].head(), "Principais Despesas Anômalas")
    tabela_por_projeto_html = formatar_tabela_html(df_por_projeto, "Despesas Consolidadas por Projeto")
    tabela_por_mes_html = formatar_tabela_html(df_por_mes, "Despesas Consolidadas por Mês")

    # --- Montagem do Corpo do E-mail ---
    corpo_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Calibri, sans-serif; font-size: 11pt; }}
            h1 {{ color: #003366; }}
            h2 {{ color: #004080; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 25px; }}
            .summary-box {{ background-color: #f0f8ff; border: 1px solid #d4eaf7; padding: 15px; margin-bottom: 20px; }}
            .dataframe {{ border-collapse: collapse; width: 95%; margin-bottom: 20px; font-size: 9pt; }}
            .dataframe th {{ background-color: #eaf5ff; text-align: left; padding: 8px; border-bottom: 2px solid #a_id_02; }}
            .dataframe td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>Análise de Despesas - Relatório Automático</h1>
        <p>Este é um resumo gerado automaticamente sobre as despesas do período de <strong>{periodo_inicio}</strong> a <strong>{periodo_fim}</strong>.</p>
        
        <div class="summary-box">
            <h2>Resumo Executivo da Unidade</h2>
            <ul>
                <li><strong>Total de Despesas (Gastos):</strong> R$ {total_despesa:,.2f}</li>
                <li><strong>Número Total de Transações:</strong> {transacoes_total:,}</li>
                <li><strong>Principal Fornecedor (por despesa):</strong> {principal_fornecedor_str}</li>
                <li><strong>Análise de Risco:</strong> {resumo_anomalias}</li>
            </ul>
        </div>

        {tabela_por_projeto_html}
        {tabela_por_mes_html}
        {tabela_top_fornecedores_html}
        {tabela_anomalias_html}
        
        <hr style="margin-top: 30px;">
        <p><em>Este é um e-mail automático gerado pelo pipeline de Análise de Despesas.</em></p>
    </body>
    </html>
    """
    return corpo_html
