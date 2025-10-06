# main.py (VERSÃO FINAL COM HIGIENIZAÇÃO DO NOME DO ANEXO)

import logging
import datetime
import pandas as pd
import sys
import re
from analise_despesa.logging_config import setup_logging
from analise_despesa.extracao import buscar_dados_realizado, buscar_dados_orcamento, buscar_unidades_disponiveis
from analise_despesa.analise import agregacao, insights_ia
from analise_despesa.comunicacao import email
from analise_despesa.config import PARAMETROS_ANALISE, MAPA_GESTORES, PROJETOS_FOLHA_PAGAMENTO, OUTPUT_DIR
from analise_despesa.processamento import enriquecimento
import os

setup_logging()
logger = logging.getLogger(__name__)

def obter_parametros_interativos():
    # (Código inalterado)
    if not sys.stdout.isatty():
        logger.info("Terminal não interativo detectado. Pulando para o modo automático.")
        return None, None, [], ""
    try:
        print("\n--- Modo de Execução Interativa ---")
        print("Pressione Enter para usar os valores padrão do config.py.")
        ano_str = input(f"Digite o ano da análise (padrão: {PARAMETROS_ANALISE['ANO_REFERENCIA']}): ")
        ano_interativo = int(ano_str) if ano_str else None
        mes_str = input("Digite o mês de referência (1-12) (padrão: último mês dos dados): ")
        mes_interativo = int(mes_str) if mes_str else None
        if not ano_str and not mes_str:
            print("Nenhum parâmetro fornecido. Iniciando modo automático...")
            return None, None, [], ""
        unidades_disponiveis = buscar_unidades_disponiveis()
        if not unidades_disponiveis:
            print("Não foi possível buscar a lista de unidades.")
            return ano_interativo, mes_interativo, {}, ""
        print("\nUnidades de Negócio Disponíveis:")
        for i, unidade in enumerate(unidades_disponiveis): print(f"  {i+1}: {unidade}")
        print("  Deixe em branco para analisar TODAS as unidades do mapa padrão.")
        selecao_str = input("Digite o número da(s) unidade(s), separados por vírgula (ex: 1,3,5): ")
        unidades_selecionadas, email_destino = [], ""
        if selecao_str:
            try:
                indices = [int(i.strip()) for i in selecao_str.split(',')]
                unidades_selecionadas = [unidades_disponiveis[i-1] for i in indices if 0 < i <= len(unidades_disponiveis)]
                if unidades_selecionadas:
                    email_destino = input("Digite o e-mail para receber o(s) relatório(s): ")
                    if not email_destino:
                        print("E-mail de destino é obrigatório no modo de seleção. Abortando.")
                        return None, None, None, None
            except (ValueError, IndexError):
                print("Seleção de unidade inválida. Abortando.")
                return None, None, None, None
        return ano_interativo, mes_interativo, unidades_selecionadas, email_destino
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        return None, None, None, None
    except Exception as e:
        print(f"Ocorreu um erro durante a entrada de dados: {e}")
        return None, None, None, None

# --- NOVA FUNÇÃO PARA HIGIENIZAR NOMES DE ARQUIVO ---
def slugify(text):
    """
    Converte um texto em um formato seguro para nomes de arquivo (ASCII).
    """
    text = str(text).lower()
    # Substituições manuais para caracteres comuns em português
    text = text.replace(' ', '_')
    text = text.replace('ç', 'c')
    text = text.replace('ã', 'a').replace('á', 'a').replace('à', 'a').replace('â', 'a')
    text = text.replace('é', 'e').replace('ê', 'e')
    text = text.replace('í', 'i')
    text = text.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
    text = text.replace('ú', 'u')
    # Remove qualquer caractere que não seja letra, número, underscore ou hífen
    text = re.sub(r'[^\w-]', '', text)
    return text

def executar_analise_distribuida():
    ano_interativo, mes_interativo, unidades_selecionadas, email_destino = obter_parametros_interativos()
    if ano_interativo is None and mes_interativo is None and not unidades_selecionadas and not email_destino: pass
    elif unidades_selecionadas is None: return
    if unidades_selecionadas:
        logger.info(f"--- MODO INTERATIVO ATIVADO ---")
        logger.info(f"Unidades selecionadas: {unidades_selecionadas}")
        logger.info(f"E-mail de destino: {email_destino}")
        mapa_execucao = {unidade: email_destino for unidade in unidades_selecionadas}
    else:
        logger.info(f"--- MODO AUTOMÁTICO ATIVADO ---")
        logger.info("Usando o mapa de gestores do arquivo config.py.")
        mapa_execucao = MAPA_GESTORES
    logger.info("🚀 Iniciando pipeline completo...")
    try:
        ano = ano_interativo if ano_interativo is not None else PARAMETROS_ANALISE["ANO_REFERENCIA"]
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
        df_analise_principal = df_realizado_enriquecido.copy()
        if mes_interativo:
            logger.warning(f" MODO DE SOBRESCRITA ATIVADO: A análise será limitada aos dados até o mês {mes_interativo}. ")
            df_analise_principal = df_analise_principal[df_analise_principal['MES'] <= mes_interativo].copy()
        df_todos_exclusivos = df_analise_principal[df_analise_principal['tipo_projeto'] == 'Exclusivo'].copy()
        df_clusters_global, resumo_clusters_global = {}, {}
        if not df_todos_exclusivos.empty:
            df_clusters_global, resumo_clusters_global = insights_ia.segmentar_contas_por_comportamento(df_todos_exclusivos)
    except Exception as e:
        logger.critical(f"❌ Falha na carga/integração inicial. Erro: {e}", exc_info=True)
        return
    for unidade, email_gestor_final in mapa_execucao.items():
        logger.info(f"================== PROCESSANDO UNIDADE: {unidade} ==================")
        try:
            df_unidade_bruto = df_analise_principal[df_analise_principal['UNIDADE'].str.strip() == unidade].copy()
            if df_unidade_bruto.empty: 
                logger.warning(f"Nenhum dado encontrado para a unidade '{unidade}' no período selecionado. Pulando.")
                continue
            df_unidade_integrado = df_integrado[df_integrado['UNIDADE'].str.strip() == unidade].copy()
            cod_unidade_analisada = "N/A"
            if not df_unidade_bruto.empty:
                cod_unidade_analisada = df_unidade_bruto['CC'].str[-3:].iloc[0]
            mes_referencia_num = df_unidade_bruto['MES'].max()
            resumo = agregacao.gerar_resumo_executivo(df_unidade_bruto, df_unidade_integrado, mes_referencia_num)
            resumo['numero_unidade'] = cod_unidade_analisada
            df_clusters_unidade = {}
            if df_clusters_global:
                contas_da_unidade = df_unidade_bruto['DESC_NIVEL_4'].unique()
                for nome_cluster, df_cluster in df_clusters_global.items():
                    df_filtrado = df_cluster[df_cluster['Agrupamento Contábil (Nível 4)'].isin(contas_da_unidade)]
                    if not df_filtrado.empty:
                        df_clusters_unidade[nome_cluster] = df_filtrado
            df_unidade_exclusivos = df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Exclusivo']
            df_ocorrencias_atipicas_ano = insights_ia.detectar_anomalias_de_contexto(df_unidade_exclusivos)
            df_orcamento_exclusivo = agregacao.agregar_realizado_vs_orcado_por_projeto(df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Exclusivo'], df_ocorrencias_atipicas_ano)
            df_orcamento_compartilhado = agregacao.agregar_realizado_vs_orcado_por_projeto(df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Compartilhado'], df_ocorrencias_atipicas_ano)
            df_fornecedores_exclusivo = agregacao.agregar_despesas_por_fornecedor(df_unidade_exclusivos, top_n=5)
            df_fornecedores_compartilhado = agregacao.agregar_despesas_por_fornecedor(df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Compartilhado'], top_n=5)
            df_mes_agregado = agregacao.agregar_despesas_por_mes(df_unidade_bruto)
            meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
            resumo['mes_referencia'] = meses_map.get(mes_referencia_num, "N/A")
            df_ocorrencias_filtradas = df_ocorrencias_atipicas_ano[df_ocorrencias_atipicas_ano['DATA'].dt.month == mes_referencia_num].copy()
            df_ocorrencias_investigadas = insights_ia.investigar_causa_raiz_ocorrencia(df_ocorrencias_filtradas, df_unidade_bruto)
            if not df_ocorrencias_investigadas.empty:
                df_ocorrencias_investigadas.rename(columns={'VALOR': 'Realizado'}, inplace=True)
            corpo_html = email.gerar_corpo_email_analise(unidade_gestora=unidade, data_relatorio=datetime.date.today().strftime('%d/%m/%Y'), resumo=resumo, df_orcamento_exclusivo=df_orcamento_exclusivo, df_orcamento_compartilhado=df_orcamento_compartilhado, df_fornecedores_exclusivo=df_fornecedores_exclusivo, df_fornecedores_compartilhado=df_fornecedores_compartilhado, df_mes_agregado=df_mes_agregado, df_ocorrencias_atipicas=df_ocorrencias_investigadas, df_clusters_folha=df_clusters_unidade, resumo_clusters_folha=resumo_clusters_global)
            unidade_para_assunto = unidade.replace("SP - ", "")
            assunto = f"Análise de Despesas - {unidade_para_assunto} - Ref {resumo['mes_referencia']}/{ano}"
            
            # --- CORREÇÃO: Higienização do nome do arquivo ---
            unidade_para_arquivo = slugify(unidade_para_assunto)
            nome_arquivo_csv = f"despesa_{ano}{resumo['mes_referencia']}_{unidade_para_arquivo}.csv"
            caminho_anexo = OUTPUT_DIR / nome_arquivo_csv
            
            logger.info(f"Gerando arquivo de despesas para anexo em: {caminho_anexo}")
            df_unidade_bruto.to_csv(caminho_anexo, index=False, sep=';', encoding='utf-8-sig')
            
            email.enviar_email_via_smtp(assunto, corpo_html, email_gestor_final, caminho_anexo=str(caminho_anexo))
            logger.info(f"✅ Análise da unidade '{unidade}' concluída e e-mail enviado com anexo para '{email_gestor_final}'.")
        except Exception as e:
            logger.critical(f"❌ Erro no processamento da unidade '{unidade}': {e}", exc_info=True)
    logger.info("✅ Pipeline finalizado com sucesso.")

if __name__ == "__main__":
    executar_analise_distribuida()
