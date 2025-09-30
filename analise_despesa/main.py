# analise_despesa/main.py
# VERSÃO FINAL: Corrigido para passar o DataFrame da unidade para as agregações.

import logging
import datetime
import os
import re

from .logging_config import setup_logging
from .extracao import buscar_dados_completos
from .processamento import limpeza, enriquecimento
from .analise import agregacao, insights_ia
from .comunicacao import email
from .config import PARAMETROS_ANALISE, MAPA_GESTORES

setup_logging()
logger = logging.getLogger(__name__)

def executar_analise_distribuida():
    logger.info("🚀 Iniciando pipeline DISTRIBUÍDO de análise de despesas.")
    
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        data_inicio_str = f"{ano}-01-01"
        data_fim_str = f"{ano}-12-31"
        logger.info(f"Ano de referência para a análise: {ano}")
        
        params_extracao = {"data_inicio": data_inicio_str, "data_fim": data_fim_str}
        df_completo = buscar_dados_completos(params=params_extracao)
        
        if df_completo.empty:
            logger.warning("A extração de dados não retornou nenhuma linha. Encerrando.")
            return

    except Exception as e:
        logger.critical(f"❌ Falha crítica na extração de dados. O pipeline não pode continuar. Erro: {e}", exc_info=True)
        return

    for unidade, email_gestor in MAPA_GESTORES.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        
        try:
            df_unidade = df_completo[df_completo['UNIDADE'] == unidade].copy()
            
            if df_unidade.empty:
                logger.warning(f"Nenhum dado encontrado para a unidade '{unidade}'. Pulando para a próxima.")
                continue

            df_limpo = limpeza.tratar_dados_nulos(df_unidade)
            df_enriquecido = enriquecimento.adicionar_colunas_de_data(df_limpo)
            df_final = insights_ia.detectar_anomalias_de_valor(df_enriquecido)
            anomalias = df_final[df_final['ANOMALIA'] == 'Anomalia'].sort_values('VALOR', ascending=False)
            
            # ==============================================================================
            # ||                        CORREÇÃO CRÍTICA AQUI                             ||
            # ==============================================================================
            # As funções de agregação agora recebem o df_final, que contém
            # apenas os dados da unidade que está sendo processada no loop.
            df_top_fornecedores = agregacao.agregar_despesas_por_fornecedor(df_final)
            df_por_projeto = agregacao.agregar_despesas_por_projeto(df_final)
            df_por_mes = agregacao.agregar_despesas_por_mes(df_final)
            # ==============================================================================

            # Geração de gráfico foi removida
            
            corpo_email_html = email.gerar_corpo_email_analise(
                df_completo=df_final,
                df_top_fornecedores=df_top_fornecedores,
                df_anomalias=anomalias,
                df_por_projeto=df_por_projeto,
                df_por_mes=df_por_mes
            )
            assunto = f"Análise de Despesas - {unidade} - {datetime.date.today().strftime('%d/%m/%Y')}"
            
            email.enviar_email_via_outlook(
                assunto=assunto, 
                corpo_html=corpo_email_html,
                destinatario=email_gestor
            )
            
            logger.info(f"✅ Análise da unidade '{unidade}' concluída e e-mail enviado para {email_gestor}.")

        except Exception as e:
            logger.critical(f"❌ Ocorreu um erro fatal no processamento da unidade '{unidade}': {e}", exc_info=True)

    logger.info("✅ Pipeline distribuído finalizado com sucesso!")

if __name__ == "__main__":
    executar_analise_distribuida()
