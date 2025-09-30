# main.py (VERSÃO FINAL E LIMPA)
import logging
import datetime
from analise_despesa.logging_config import setup_logging
from analise_despesa.extracao import buscar_dados_completos
from analise_despesa.processamento import limpeza, enriquecimento
from analise_despesa.analise import agregacao, insights_ia
from analise_despesa.comunicacao import email
from analise_despesa import exportacao
from analise_despesa.config import PARAMETROS_ANALISE, MAPA_GESTORES

setup_logging()
logger = logging.getLogger(__name__)

def executar_analise_distribuida():
    logger.info("🚀 Iniciando pipeline de análise de despesas.")
    
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        logger.info(f"Ano de referência: {ano}")
        
        df_completo = buscar_dados_completos(params={"ano": ano})
        
        if df_completo.empty:
            logger.warning("A extração não retornou dados. Encerrando.")
            return

        colunas_necessarias = ['VALOR', 'UNIDADE', 'LCTREF', 'PROJETO']
        if not all(col in df_completo.columns for col in colunas_necessarias):
            raise KeyError(f"Colunas essenciais não encontradas. Verifique a VIEW. Colunas: {df_completo.columns.tolist()}")

        caminho_verificacao = PARAMETROS_ANALISE.get("ARQUIVO_CSV_VERIFICACAO")
        if caminho_verificacao:
            exportacao.exportar_dataframe_para_csv(df_completo, caminho_verificacao, "Verificação da VIEW Completa")
        
        # A função em agregacao.py agora é responsável pela correção.
        df_total_projetos_global = agregacao.calcular_total_projetos_global(df_completo)

    except Exception as e:
        logger.critical(f"❌ Falha na fase de carga. Pipeline interrompido. Erro: {e}", exc_info=True)
        return

    for unidade, email_gestor in MAPA_GESTORES.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        try:
            df_unidade = df_completo[df_completo['UNIDADE'].str.strip() == unidade].copy()
            
            if df_unidade.empty:
                logger.warning(f"Nenhum dado para a unidade '{unidade}'. Pulando.")
                continue

            df_limpo = limpeza.tratar_dados_nulos(df_unidade)
            df_enriquecido = enriquecimento.adicionar_colunas_de_data(df_limpo)
            
            # As funções de agregação agora recebem os dados e são responsáveis pela correção.
            df_por_projeto = agregacao.agregar_despesas_por_projeto(df_enriquecido, df_total_projetos_global)
            df_por_mes = agregacao.agregar_despesas_por_mes(df_enriquecido)
            df_top_fornecedores = agregacao.agregar_despesas_por_fornecedor(df_enriquecido)
            
            # A detecção de anomalias é feita nos dados já corrigidos para consistência.
            df_final_anomalia = insights_ia.detectar_anomalias_de_valor(df_enriquecido.drop_duplicates(subset=['LCTREF']))
            anomalias = df_final_anomalia[df_final_anomalia['ANOMALIA'] == 'Anomalia'].sort_values('VALOR', ascending=False)

            corpo_email_html = email.gerar_corpo_email_analise(
                df_completo=df_final_anomalia, df_top_fornecedores=df_top_fornecedores,
                df_anomalias=anomalias, df_por_projeto=df_por_projeto,
                df_por_mes=df_por_mes
            )
            assunto = f"Análise de Despesas - {unidade} - {datetime.date.today().strftime('%d/%m/%Y')}"
            
            email.enviar_email_via_outlook(assunto, corpo_email_html, email_gestor)
            
            logger.info(f"✅ Análise da unidade '{unidade}' concluída.")
        except Exception as e:
            logger.critical(f"❌ Erro no processamento da unidade '{unidade}': {e}", exc_info=True)

    logger.info("✅ Pipeline finalizado.")

if __name__ == "__main__":
    executar_analise_distribuida()
