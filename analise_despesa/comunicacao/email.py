import pandas as pd
import logging
import os
import win32com.client as win32 # Importa a biblioteca de automação COM
from datetime import datetime

logger = logging.getLogger(__name__)

def enviar_email_via_outlook(assunto: str, corpo_html: str, destinatario: str, caminho_anexo: str):
    """
    Cria e envia um e-mail através do aplicativo Microsoft Outlook instalado na máquina.
    Usa a sessão já autenticada do usuário.
    """
    logger.info(f"Iniciando criação de e-mail para {destinatario} via Outlook...")
    
    try:
        # Conecta-se ao aplicativo Outlook
        outlook = win32.Dispatch('outlook.application')
        # Cria um novo item de e-mail (0 é o código para MailItem)
        mail = outlook.CreateItem(0)

        # Preenche os detalhes do e-mail
        mail.To = destinatario
        mail.Subject = assunto
        mail.HTMLBody = corpo_html # Usamos HTMLBody para manter a formatação

        # Anexa o gráfico. O caminho precisa ser absoluto.
        caminho_absoluto_anexo = os.path.abspath(caminho_anexo)
        mail.Attachments.Add(caminho_absoluto_anexo)
        
        # --- ESCOLHA UMA DAS OPÇÕES ABAIXO ---
        
        # Opção 1: Enviar o e-mail diretamente (totalmente automático)
        mail.Send()
        logger.info("✅ E-mail enviado com sucesso através do Outlook!")
        
        # Opção 2: Salvar na caixa de Rascunhos para revisão (semi-automático)
        # mail.Save()
        # logger.info("✅ E-mail salvo na sua caixa de 'Rascunhos' do Outlook para revisão.")

        # Opção 3: Mostrar o e-mail na tela para o usuário enviar (interativo)
        # mail.Display(True) # O 'True' torna a janela modal
        # logger.info("✅ E-mail exibido na tela para envio manual.")

    except Exception as e:
        logger.error("❌ Falha ao tentar controlar o Outlook. Verifique se ele está instalado.", exc_info=True)
        logger.error("Dica: Se o Outlook não estiver aberto, o processo pode rodar em segundo plano, mas é recomendado que ele esteja aberto.")
        raise

# A função para gerar o corpo do e-mail permanece exatamente a mesma de antes.
def gerar_corpo_email_analise(df_completo: pd.DataFrame, df_top_fornecedores: pd.DataFrame, df_anomalias: pd.DataFrame) -> str:
    logger.info("Gerando corpo do e-mail de análise...")

    total_despesa = df_completo['UNIFICAVALOR'].sum()
    transacoes_total = len(df_completo)
    periodo_inicio = pd.to_datetime(df_completo['DATA']).min().strftime('%d/%m/%Y')
    periodo_fim = pd.to_datetime(df_completo['DATA']).max().strftime('%d/%m/%Y')
    
    tabela_top_fornecedores_html = df_top_fornecedores.to_html(index=False, justify='left', border=0, classes='dataframe')
    tabela_anomalias_html = df_anomalias[['DATA', 'FORNECEDOR', 'COMPLEMENTO', 'UNIFICAVALOR']].head().to_html(index=False, justify='left', border=0, classes='dataframe')

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
                <li><strong>Valor Total das Despesas:</strong> R$ {total_despesa:,.2f}</li>
                <li><strong>Número Total de Transações:</strong> {transacoes_total:,}</li>
                <li><strong>Principal Fornecedor (por valor):</strong> {df_top_fornecedores.iloc[0]['FORNECEDOR']}</li>
            </ul>
        </div>

        <h2>Top 10 Fornecedores por Valor</h2>
        {tabela_top_fornecedores_html}
        
        <h2>Principais Despesas Anômalas Detectadas (por Valor)</h2>
        <p>As seguintes despesas foram sinalizadas como potenciais anomalias devido ao seu alto valor em comparação com a média.</p>
        {tabela_anomalias_html}

        <h2>Gráfico - Top 10 Fornecedores</h2>
        <p>O gráfico abaixo ilustra a distribuição de despesas entre os principais fornecedores.</p>
        
        <hr>
        <p><em>Este é um e-mail automático gerado pelo pipeline de Análise de Despesas.</em></p>
    </body>
    </html>
    """
    return corpo_html
