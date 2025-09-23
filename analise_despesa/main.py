# analise_despesa/main.py
import logging
import datetime
import os
import re # <-- 1. IMPORTAMOS a biblioteca 're' para limpar nomes de arquivos

# Imports do seu projeto (permanecem os mesmos)
from .logging_config import setup_logging
from . import extracao, database, exportacao
from .processamento import limpeza, enriquecimento
from .analise import agregacao, insights_ia
from .visualizacao import graficos
from .comunicacao import email
from .config import MAPA_GESTORES # <-- 2. IMPORTAMOS o nosso mapa

setup_logging()
logger = logging.getLogger(__name__)

# --- 3. A FUNÇÃO PRINCIPAL AGORA TEM UM NOVO PROPÓSITO ---
def executar_analise_distribuida():
    """
    Orquestra o pipeline, executando uma análise personalizada para cada
    Unidade Gestora definida no MAPA_GESTORES e enviando um e-mail para
    o gestor responsável.
    """
    logger.info("🚀 Iniciando pipeline DISTRIBUÍDO de análise de despesas.")
    ano_corrente = datetime.date.today().year

    # --- 4. O LOOP PRINCIPAL QUE MUDA TUDO ---
    # Iteramos sobre cada unidade e e-mail definidos no config.py
    for unidade, email_gestor in MAPA_GESTORES.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        
        try:
            # --- 5. EXTRAÇÃO DIRECIONADA ---
            # Passamos a unidade como parâmetro para a query SQL
            df_unidade = extracao.buscar_dados(
                "BaseDespesas",
                params={"ano": ano_corrente, "unidade_gestora": unidade}
            )

            if df_unidade.empty:
                logger.warning(f"Nenhum dado encontrado para a unidade '{unidade}'. Pulando para a próxima.")
                continue # Pula para a próxima unidade no loop

            # --- O RESTO DO PIPELINE, AGORA RODANDO APENAS NA "FATIA" DE DADOS ---
            # (O código aqui é o mesmo que você já tinha, mas usando 'df_unidade')
            
            # 2. TRANSFORMAÇÃO (T)
            df_limpo = limpeza.tratar_dados_nulos(df_unidade)
            df_enriquecido = enriquecimento.adicionar_colunas_de_data(df_limpo)

            # 3. ANÁLISE & IA (A)
            df_final = insights_ia.detectar_anomalias_de_valor(df_enriquecido)
            df_top_fornecedores = agregacao.agregar_despesas_por_fornecedor(df_final)
            anomalias = df_final[df_final['ANOMALIA'] == 'Anomalia'].sort_values('UNIFICAVALOR', ascending=False)
            
            # --- 6. SAÍDAS PERSONALIZADAS PARA CADA UNIDADE ---
            # Criamos um nome de arquivo seguro a partir do nome da unidade
            nome_arquivo_unidade = re.sub(r'[^a-zA-Z0-9_]', '', unidade.replace(" ", "_"))

            # 4. VISUALIZAÇÃO (V)
            caminho_grafico = os.path.join('outputs', 'graficos', f'top_10_fornecedores_{nome_arquivo_unidade}.png')
            graficos.plotar_top_fornecedores(df_top_fornecedores, caminho_salvar=caminho_grafico)

            # 5. COMUNICAÇÃO (VIA OUTLOOK)
            corpo_email_html = email.gerar_corpo_email_analise(
                df_completo=df_final,
                df_top_fornecedores=df_top_fornecedores,
                df_anomalias=anomalias
            )
            # Assunto e destinatário agora são dinâmicos
            assunto = f"Análise de Despesas - {unidade} - {datetime.date.today().strftime('%d/%m/%Y')}"
            
            email.enviar_email_via_outlook(
                assunto=assunto,
                corpo_html=corpo_email_html,
                destinatario=email_gestor, # <-- MUDANÇA CRÍTICA
                caminho_anexo=caminho_grafico
            )
            
            # 6. EXPORTAÇÃO E CARGA
            caminho_relatorio_anomalias = os.path.join('outputs', 'relatorios', f'relatorio_anomalias_{nome_arquivo_unidade}.csv')
            exportacao.exportar_para_csv(anomalias, caminho_relatorio_anomalias)
            
            # Opcional: Salvar o resultado de cada unidade em uma tabela separada ou com uma coluna de identificação
            # database.salvar_dataframe(...)
            
            logger.info(f"✅ Análise da unidade '{unidade}' concluída e e-mail enviado para {email_gestor}.")

        except Exception as e:
            # Se uma unidade falhar, o log registra o erro e o loop continua para a próxima
            logger.critical(f"❌ Ocorreu um erro fatal no processamento da unidade '{unidade}': {e}", exc_info=True)

    logger.info("✅ Pipeline distribuído finalizado com sucesso!")

# --- 7. ATUALIZAMOS A CHAMADA PRINCIPAL ---
if __name__ == "__main__":
    executar_analise_distribuida()

