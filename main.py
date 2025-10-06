# main.py (VERSÃO FINAL COM GERAÇÃO DE ANEXO CSV)

import logging
import datetime
import pandas as pd
from analise_despesa.logging_config import setup_logging
from analise_despesa.extracao import buscar_dados_realizado, buscar_dados_orcamento
from analise_despesa.analise import agregacao, insights_ia
from analise_despesa.comunicacao import email
from analise_despesa.config import PARAMETROS_ANALISE, MAPA_GESTORES, PROJETOS_FOLHA_PAGAMENTO, MES_ANALISE_SOBRESCRITA, OUTPUT_DIR
from analise_despesa.processamento import enriquecimento
import os

setup_logging()
logger = logging.getLogger(__name__)

def executar_analise_distribuida():
    logger.info("🚀 Iniciando pipeline completo...")
    try:
        ano = PARAMETROS_ANALISE["ANO_REFERENCIA"]
        id_periodo = PARAMETROS_ANALISE["ID_PERIODO_ORCAMENTO"]
        df_realizado_bruto = buscar_dados_realizado(ano=ano)
        df_orcado = buscar_dados_orcamento(id_periodo=id_periodo)
        if df_realizado_bruto.empty: return
        df_orcado_anual = df_orcado.groupby('CODCCUSTO')['VALOR_ORCADO'].sum().reset_index()
        df_realizado_enriquecido = enriquecimento.adicionar_colunas_de_data(df_realizado_bruto)
        contagem_unidades_por_projeto = df_realizado_enriquecido.groupby('PROJETO')['UNIDADE'].nunique().reset_index(name='contagem_unidades')
        contagem_unidades_por_projeto['tipo_projeto'] = contagem_unidades_por_projeto['contagem_unidades'].apply(lambda x: 'Exclusivo' if x == 1 else 'Compartilhado')
        df_realizado_enriquecido = pd.merge(df_realizado_enriquecido, contagem_unidades_por_projeto[['PROJETO', 'tipo_projeto']], on='PROJETO', how='left')
        df_realizado_enriquecido['CODCCUSTO_JUNCAO'] = df_realizado_enriquecido['CC'].str.slice(0, 12)
        df_real_agg = df_realizado_enriquecido.groupby(['UNIDADE', 'PROJETO', 'tipo_projeto', 'CODCCUSTO_JUNCAO']).agg(VALOR_REALIZADO=('VALOR', 'sum')).reset_index()
        df_integrado = pd.merge(df_real_agg, df_orcado_anual, left_on='CODCCUSTO_JUNCAO', right_on='CODCCUSTO', how='left', suffixes=('', '_orcado'))
        df_integrado['VALOR_ORCADO'] = df_integrado['VALOR_ORCADO'].fillna(0)
        df_integrado.drop(columns=['CODCCUSTO'], inplace=True, errors='ignore')

    except Exception as e:
        logger.critical(f"❌ Falha na carga/integração inicial. Erro: {e}", exc_info=True)
        return

    df_analise_principal = df_realizado_enriquecido.copy()
    if MES_ANALISE_SOBRESCRITA:
        logger.warning(f" MODO DE SOBRESCRITA ATIVADO: A análise será limitada aos dados até o mês {MES_ANALISE_SOBRESCRITA}. ")
        df_analise_principal = df_analise_principal[df_analise_principal['MES'] <= MES_ANALISE_SOBRESCRITA].copy()

    for unidade, email_gestor in MAPA_GESTORES.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        try:
            df_unidade_bruto = df_analise_principal[df_analise_principal['UNIDADE'].str.strip() == unidade].copy()
            if df_unidade_bruto.empty: continue
            df_unidade_integrado = df_integrado[df_integrado['UNIDADE'].str.strip() == unidade].copy()
            
            cod_unidade_analisada = "N/A"
            if not df_unidade_bruto.empty:
                cod_unidade_analisada = df_unidade_bruto['CC'].str[-3:].iloc[0]
            
            mes_referencia_num = df_unidade_bruto['MES'].max()
            resumo = agregacao.gerar_resumo_executivo(df_unidade_bruto, df_unidade_integrado, mes_referencia_num)
            resumo['numero_unidade'] = cod_unidade_analisada
            
            df_unidade_exclusivos = df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Exclusivo'].copy()
            df_clusters, resumo_clusters = {}, {}
            if not df_unidade_exclusivos.empty:
                df_clusters, resumo_clusters = insights_ia.segmentar_contas_por_comportamento(df_unidade_exclusivos)

            df_integrado_exclusivo = df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Exclusivo']
            df_integrado_compartilhado = df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Compartilhado']
            
            df_ocorrencias_atipicas = insights_ia.detectar_anomalias_de_contexto(df_unidade_exclusivos)
            
            df_orcamento_exclusivo = agregacao.agregar_realizado_vs_orcado_por_projeto(df_integrado_exclusivo, df_ocorrencias_atipicas)
            df_orcamento_compartilhado = agregacao.agregar_realizado_vs_orcado_por_projeto(df_integrado_compartilhado, df_ocorrencias_atipicas)
            df_fornecedores_exclusivo = agregacao.agregar_despesas_por_fornecedor(df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Exclusivo'], top_n=5)
            df_fornecedores_compartilhado = agregacao.agregar_despesas_por_fornecedor(df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Compartilhado'], top_n=5)
            df_mes_agregado = agregacao.agregar_despesas_por_mes(df_unidade_bruto)
            
            meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
            resumo['mes_referencia'] = meses_map.get(mes_referencia_num, "N/A")
            
            df_ocorrencias_filtradas = df_ocorrencias_atipicas[df_ocorrencias_atipicas['DATA'].dt.month == mes_referencia_num].copy()
            df_ocorrencias_investigadas = insights_ia.investigar_causa_raiz_ocorrencia(df_ocorrencias_filtradas, df_unidade_bruto)
            if not df_ocorrencias_investigadas.empty:
                df_ocorrencias_investigadas.rename(columns={'VALOR': 'Realizado'}, inplace=True)

            corpo_html = email.gerar_corpo_email_analise(
                unidade_gestora=unidade, data_relatorio=datetime.date.today().strftime('%d/%m/%Y'), resumo=resumo,
                df_orcamento_exclusivo=df_orcamento_exclusivo, df_orcamento_compartilhado=df_orcamento_compartilhado,
                df_fornecedores_exclusivo=df_fornecedores_exclusivo, df_fornecedores_compartilhado=df_fornecedores_compartilhado,
                df_mes_agregado=df_mes_agregado, df_ocorrencias_atipicas=df_ocorrencias_investigadas,
                df_clusters_folha=df_clusters, resumo_clusters_folha=resumo_clusters
            )
            
            # --- CORREÇÃO 1: AJUSTE DO TÍTULO DO E-MAIL ---
            unidade_para_assunto = unidade.replace("SP - ", "")
            assunto = f"Análise de Despesas - {unidade_para_assunto} - Ref {resumo['mes_referencia']}/{ano}"

            # --- CORREÇÃO 2: GERAÇÃO DO ARQUIVO CSV PARA ANEXO ---
            unidade_para_arquivo = unidade_para_assunto.replace(" ", "_")
            nome_arquivo_csv = f"despesa_{ano}{resumo['mes_referencia']}_{unidade_para_arquivo}.csv"
            caminho_anexo = OUTPUT_DIR / nome_arquivo_csv
            
            logger.info(f"Gerando arquivo de despesas para anexo em: {caminho_anexo}")
            df_unidade_bruto.to_csv(caminho_anexo, index=False, sep=';', encoding='utf-8-sig')

            email.enviar_email_via_smtp(assunto, corpo_html, email_gestor, caminho_anexo=str(caminho_anexo))
            logger.info(f"✅ Análise da unidade '{unidade}' concluída e e-mail enviado com anexo.")

        except Exception as e:
            logger.critical(f"❌ Erro no processamento da unidade '{unidade}': {e}", exc_info=True)
    logger.info("✅ Pipeline finalizado com sucesso.")

if __name__ == "__main__":
    executar_analise_distribuida()
