# comunicacao/email.py
import pandas as pd
import logging
import os
import win32com.client as win32
from datetime import datetime

logger = logging.getLogger(__name__)

def enviar_email_via_outlook(assunto: str, corpo_html: str, destinatario: str, caminho_anexo: str):
    """
    Cria e envia um e-mail através do aplicativo Microsoft Outlook.
    (Esta função permanece a mesma)
    """
    logger.info(f"Iniciando criação de e-mail para {destinatario} via Outlook...")
    
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = destinatario
        mail.Subject = assunto
        mail.HTMLBody = corpo_html

        # Anexa o gráfico, somente se o arquivo existir.
        if caminho_anexo and os.path.exists(caminho_anexo):
            caminho_absoluto_anexo = os.path.abspath(caminho_anexo)
            mail.Attachments.Add(caminho_absoluto_anexo)
        else:
            logger.warning(f"Arquivo de anexo não encontrado em '{caminho_anexo}'. O e-mail será enviado sem anexo.")
        
        mail.Send()
        logger.info("✅ E-mail enviado com sucesso através do Outlook!")
        
    except Exception as e:
        logger.error("❌ Falha ao tentar controlar o Outlook. Verifique se ele está instalado.", exc_info=True)
        raise

# ==============================================================================
# ||              FUNÇÃO DE GERAÇÃO DE E-MAIL ATUALIZADA E ROBUSTA            ||
# ==============================================================================
def gerar_corpo_email_analise(df_completo: pd.DataFrame, df_top_fornecedores: pd.DataFrame, df_anomalias: pd.DataFrame) -> str:
    """
    Gera o corpo do e-mail em HTML, tratando de forma inteligente os casos
    em que não há dados de top fornecedores ou anomalias.
    """
    logger.info("Gerando corpo do e-mail de análise...")

    total_despesa = df_completo['UNIFICAVALOR'].sum()
    transacoes_total = len(df_completo)
    periodo_inicio = pd.to_datetime(df_completo['DATA']).min().strftime('%d/%m/%Y')
    periodo_fim = pd.to_datetime(df_completo['DATA']).max().strftime('%d/%m/%Y')
    
    # --- LÓGICA ROBUSTA PARA TOP FORNECEDORES ---
    if df_top_fornecedores.empty:
        principal_fornecedor_str = "N/A (nenhuma despesa relevante encontrada)"
        tabela_top_fornecedores_html = "<p><i>Não há dados de Top Fornecedores para exibir para esta unidade.</i></p>"
    else:
        principal_fornecedor_str = df_top_fornecedores.iloc[0]['FORNECEDOR']
        tabela_top_fornecedores_html = df_top_fornecedores.to_html(index=False, justify='left', border=0, classes='dataframe')

    # --- LÓGICA ROBUSTA PARA ANOMALIAS ---
    if df_anomalias.empty:
        tabela_anomalias_html = "<p><i>Nenhuma anomalia de valor foi detectada para esta unidade.</i></p>"
        resumo_anomalias = "Nenhuma anomalia detectada."
    else:
        # Pega as 5 primeiras anomalias para o e-mail, mas garante que não quebre se houver menos de 5.
        tabela_anomalias_html = df_anomalias[['DATA', 'FORNECEDOR', 'COMPLEMENTO', 'UNIFICAVALOR']].head().to_html(index=False, justify='left', border=0, classes='dataframe')
        resumo_anomalias = f"Detectadas {len(df_anomalias)} despesas anômalas."

    # --- MONTAGEM FINAL DO CORPO DO E-MAIL ---
    corpo_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Calibri, sans-serif; }}
            h1 {{ color: #003366; }}
            h2 {{ color: #004080; border-bottom: 1px solid #ccc; padding-bottom: 5px;}}
            .summary-box {{ background-color: #f0f8ff; border: 1px solid #d4eaf7; padding: 15px; margin-bottom: 20px; }}
            .dataframe {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            .dataframe th {{ background-color: #eaf5ff; text-align: left; padding: 8px; }}
            .dataframe td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>Análise de Despesas - Relatório Automático</h1>
        <p>Este é um resumo gerado automaticamente sobre as despesas do período de <strong>{periodo_inicio}</strong> a <strong>{periodo_fim}</strong>.</p>
        
        <div class="summary-box">
            <h2>Resumo Executivo</h2>
            <ul>
                <li><strong>Valor Total Analisado:</strong> R$ {total_despesa:,.2f}</li>
                <li><strong>Número Total de Transações:</strong> {transacoes_total:,}</li>
                <li><strong>Principal Fornecedor (por valor de despesa):</strong> {principal_fornecedor_str}</li>
                <li><strong>Análise de Risco:</strong> {resumo_anomalias}</li>
            </ul>
        </div>

        <h2>Top 10 Fornecedores por Valor de Despesa</h2>
        {tabela_top_fornecedores_html}
        
        <h2>Principais Despesas Anômalas Detectadas (por Valor)</h2>
        {tabela_anomalias_html}

        <h2>Gráfico - Top 10 Fornecedores</h2>
        <p>O gráfico abaixo ilustra a distribuição de despesas entre os principais fornecedores (se aplicável).</p>
        
        <hr>
        <p><em>Este é um e-mail automático gerado pelo pipeline de Análise de Despesas.</em></p>
    </body>
    </html>
    """
    return corpo_html

