# main.py (VERSÃO FINAL COM RESUMO, NÚMERO DA UNIDADE E AJUSTES)

import logging
import datetime
import pandas as pd
from analise_despesa.logging_config import setup_logging
from analise_despesa.extracao import buscar_dados_realizado, buscar_dados_orcamento
from analise_despesa.analise import agregacao, insights_ia
from analise_despesa.comunicacao import email
from analise_despesa.config import PARAMETROS_ANALISE, MAPA_GESTORES, PROJETOS_A_IGNORAR_ANOMALIAS
from analise_despesa.processamento import enriquecimento

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

        df_realizado_enriquecido = enriquecimento.adicionar_colunas_de_data(df_realizado_bruto)

        logger.info("Classificando projetos como 'Exclusivo' ou 'Compartilhado'...")
        contagem_unidades_por_projeto = df_realizado_enriquecido.groupby('PROJETO')['UNIDADE'].nunique().reset_index(name='contagem_unidades')
        contagem_unidades_por_projeto['tipo_projeto'] = contagem_unidades_por_projeto['contagem_unidades'].apply(lambda x: 'Exclusivo' if x == 1 else 'Compartilhado')
        df_realizado_enriquecido = pd.merge(df_realizado_enriquecido, contagem_unidades_por_projeto[['PROJETO', 'tipo_projeto']], on='PROJETO', how='left')

        df_realizado_enriquecido['CODCCUSTO_JUNCAO'] = df_realizado_enriquecido['CC'].str.slice(0, 12)
        df_real_agg = df_realizado_enriquecido.groupby(['UNIDADE', 'PROJETO', 'tipo_projeto', 'CODCCUSTO_JUNCAO']).agg(VALOR_REALIZADO=('VALOR', 'sum')).reset_index()
        
        df_integrado = pd.merge(df_real_agg, df_orcado, left_on='CODCCUSTO_JUNCAO', right_on='CODCCUSTO', how='left', suffixes=('', '_orcado'))
        df_integrado['VALOR_ORCADO'] = df_integrado['VALOR_ORCADO'].fillna(0)
        df_integrado.drop(columns=['CODCCUSTO'], inplace=True, errors='ignore')

    except Exception as e:
        logger.critical(f"❌ Falha na carga/integração. Erro: {e}", exc_info=True)
        return

    for unidade, email_gestor in MAPA_GESTORES.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        try:
            df_unidade_integrado = df_integrado[df_integrado['UNIDADE'].str.strip() == unidade].copy()
            df_unidade_bruto = df_realizado_enriquecido[df_realizado_enriquecido['UNIDADE'].str.strip() == unidade].copy()
            if df_unidade_bruto.empty: continue

            df_bruto_exclusivo = df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Exclusivo']
            df_bruto_compartilhado = df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Compartilhado']
            df_integrado_exclusivo = df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Exclusivo']
            df_integrado_compartilhado = df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Compartilhado']

            df_orcamento_exclusivo = agregacao.agregar_realizado_vs_orcado_por_projeto(df_integrado_exclusivo)
            df_orcamento_compartilhado = agregacao.agregar_realizado_vs_orcado_por_projeto(df_integrado_compartilhado)
            df_fornecedores_exclusivo = agregacao.agregar_despesas_por_fornecedor(df_bruto_exclusivo, top_n=5)
            df_fornecedores_compartilhado = agregacao.agregar_despesas_por_fornecedor(df_bruto_compartilhado, top_n=5)
            df_mes_agregado = agregacao.agregar_despesas_por_mes(df_unidade_bruto)
            
            mes_referencia_num = df_unidade_bruto['MES'].max()
            meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
            mes_referencia_nome = meses_map.get(mes_referencia_num, "N/A")

            df_mes_bruto = df_unidade_bruto[df_unidade_bruto['MES'] == mes_referencia_num]
            df_mes_bruto_exclusivo = df_mes_bruto[df_mes_bruto['tipo_projeto'] == 'Exclusivo']
            df_mes_bruto_compartilhado = df_mes_bruto[df_mes_bruto['tipo_projeto'] == 'Compartilhado']

            df_classificado_exclusivo = insights_ia.detectar_anomalias_de_valor(df_mes_bruto_exclusivo[~df_mes_bruto_exclusivo['PROJETO'].isin(PROJETOS_A_IGNORAR_ANOMALIAS)])
            df_classificado_compartilhado = insights_ia.detectar_anomalias_de_valor(df_mes_bruto_compartilhado[~df_mes_bruto_compartilhado['PROJETO'].isin(PROJETOS_A_IGNORAR_ANOMALIAS)])
            
            anomalias_exclusivo_df = df_classificado_exclusivo[df_classificado_exclusivo['Classificacao'] == 'Lançamento Atípico'][['VALOR', 'COMPLEMENTO', 'DATA', 'FORNECEDOR', 'PROJETO']]
            anomalias_compartilhado_df = df_classificado_compartilhado[df_classificado_compartilhado['Classificacao'] == 'Lançamento Atípico'][['VALOR', 'COMPLEMENTO', 'DATA', 'FORNECEDOR', 'PROJETO']]
            # MUDANÇA 5: Renomeando a coluna
            anomalias_exclusivo_df.rename(columns={'VALOR': 'Realizado'}, inplace=True)
            anomalias_compartilhado_df.rename(columns={'VALOR': 'Realizado'}, inplace=True)

            # MUDANÇA 3: Pegar o número da unidade (últimos 3 dígitos do primeiro CC disponível)
            numero_unidade = ""
            if not df_unidade_bruto.empty and 'CC' in df_unidade_bruto.columns:
                primeiro_cc = df_unidade_bruto['CC'].iloc[0]
                if isinstance(primeiro_cc, str) and len(primeiro_cc) >= 3:
                    numero_unidade = primeiro_cc[-3:]

            # MUDANÇA 1: Bloco 'resumo' completo
            resumo = {
                "numero_unidade": numero_unidade,
                "mes_referencia": mes_referencia_nome,
                "valor_total_mes": df_mes_bruto['VALOR'].sum(), "qtd_lancamentos_mes": len(df_mes_bruto),
                "valor_total_ano": df_unidade_bruto['VALOR'].sum(), "qtd_lancamentos_ano": len(df_unidade_bruto),
                "principal_fornecedor_ano": df_fornecedores_exclusivo.iloc[0]['Fornecedor'] if not df_fornecedores_exclusivo.empty else "N/A",
                "valor_principal_fornecedor_ano": df_fornecedores_exclusivo.iloc[0]['Realizado (Ano)'] if not df_fornecedores_exclusivo.empty else 0,
            }

            corpo_html = email.gerar_corpo_email_analise(
                unidade_gestora=unidade, data_relatorio=datetime.date.today().strftime('%d/%m/%Y'), resumo=resumo,
                df_orcamento_exclusivo=df_orcamento_exclusivo, df_orcamento_compartilhado=df_orcamento_compartilhado,
                df_fornecedores_exclusivo=df_fornecedores_exclusivo, df_fornecedores_compartilhado=df_fornecedores_compartilhado,
                df_mes_agregado=df_mes_agregado,
                df_anomalias_exclusivo=anomalias_exclusivo_df, df_anomalias_compartilhado=anomalias_compartilhado_df
            )
            assunto = f"Análise de Despesas por Classificação - {unidade} - Ref {mes_referencia_nome}/{ano}"
            email.enviar_email_via_smtp(assunto, corpo_html, email_gestor)
            logger.info(f"✅ Análise da unidade '{unidade}' concluída e e-mail enviado.")

        except Exception as e:
            logger.critical(f"❌ Erro no processamento da unidade '{unidade}': {e}", exc_info=True)

    logger.info("✅ Pipeline finalizado com sucesso.")

if __name__ == "__main__":
    executar_analise_distribuida()
