# analise_despesa/main.py
# VERSÃO FINAL E CORRIGIDA

import logging
import datetime
import os
import re

from .logging_config import setup_logging
# --- IMPORTAÇÕES CORRIGIDAS ---
from .extracao import buscar_dados_completos
from .processamento import limpeza, enriquecimento
from .analise import agregacao, insights_ia
from .visualizacao import graficos
from .comunicacao import email
from . import exportacao # <-- A LINHA QUE FALTAVA
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
        
        # --- CARREGAMENTO ÚNICO ---
        params_extracao = {"data_inicio": data_inicio_str, "data_fim": data_fim_str}
        df_completo = buscar_dados_completos(params=params_extracao)
        
        if df_completo.empty:
            logger.warning("A extração de dados não retornou nenhuma linha. Encerrando.")
            return

    except Exception as e:
        logger.critical(f"❌ Falha crítica na extração de dados. O pipeline não pode continuar. Erro: {e}", exc_info=True)
        return

    # --- LOOP DE ANÁLISE ---
    for unidade, email_gestor in MAPA_GESTORES.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        
        try:
            # --- FATIAMENTO EM MEMÓRIA ---
            df_unidade = df_completo[df_completo['UNIDADE'] == unidade].copy()
            
            if df_unidade.empty:
                logger.warning(f"Nenhum dado encontrado para a unidade '{unidade}'. Pulando para a próxima.")
                continue

            # ... (O resto do seu pipeline continua exatamente o mesmo) ...
            df_limpo = limpeza.tratar_dados_nulos(df_unidade)
            df_enriquecido = enriquecimento.adicionar_colunas_de_data(df_limpo)
            df_final = insights_ia.detectar_anomalias_de_valor(df_enriquecido)
            df_top_fornecedores = agregacao.agregar_despesas_por_fornecedor(df_final)
            anomalias = df_final[df_final['ANOMALIA'] == 'Anomalia'].sort_values('UNIFICAVALOR', ascending=False)
            
            nome_arquivo_unidade = re.sub(r'[^a-zA-Z0-9_]', '', unidade.replace(" ", "_"))
            
            caminho_grafico = os.path.join('outputs', 'graficos', f'top_10_fornecedores_{nome_arquivo_unidade}.png')
            graficos.plotar_top_fornecedores(df_top_fornecedores, caminho_salvar=caminho_grafico)
            
            corpo_email_html = email.gerar_corpo_email_analise(
                df_completo=df_final,
                df_top_fornecedores=df_top_fornecedores,
                df_anomalias=anomalias
            )
            assunto = f"Análise de Despesas - {unidade} - {datetime.date.today().strftime('%d/%m/%Y')}"
            
            email.enviar_email_via_outlook(
                assunto=assunto, corpo_html=corpo_email_html,
                destinatario=email_gestor, caminho_anexo=caminho_grafico
            )
            
            # Exportação do relatório de anomalias
            caminho_relatorio_anomalias = os.path.join('outputs', 'relatorios', f'relatorio_anomalias_{nome_arquivo_unidade}.csv')
            exportacao.exportar_para_csv(anomalias, caminho_relatorio_anomalias) # <-- ESTA LINHA AGORA FUNCIONARÁ
            
            logger.info(f"✅ Análise da unidade '{unidade}' concluída e e-mail enviado para {email_gestor}.")

        except Exception as e:
            logger.critical(f"❌ Ocorreu um erro fatal no processamento da unidade '{unidade}': {e}", exc_info=True)

    logger.info("✅ Pipeline distribuído finalizado com sucesso!")

if __name__ == "__main__":
    executar_analise_distribuida()
