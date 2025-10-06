# analise_despesa/analise/agregacao.py (VERSÃO FINAL COM NOVA TERMINOLOGIA)

import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

def agregar_realizado_vs_orcado_por_projeto(df_integrado: pd.DataFrame, df_ocorrencias_atipicas: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega dados de orçamento e realizado, e calcula o Score de Criticidade para cada projeto.
    """
    if df_integrado.empty:
        return pd.DataFrame()
    
    logger.info("Agregando Orçado vs. Realizado e calculando Score de Criticidade...")
    df_agregado = df_integrado.groupby('PROJETO').agg(
        VALOR_REALIZADO=('VALOR_REALIZADO', 'sum'), 
        VALOR_ORCADO=('VALOR_ORCADO', 'sum')
    ).reset_index()

    df_agregado['%_EXECUCAO'] = (df_agregado['VALOR_REALIZADO'] / df_agregado['VALOR_ORCADO']).replace([np.inf, -np.inf], 0).fillna(0)
    
    df_final = df_agregado.rename(columns={
        'PROJETO': 'Iniciativa', 'VALOR_ORCADO': 'Orçado', 
        'VALOR_REALIZADO': 'Realizado', '%_EXECUCAO': '% Execução'
    })

    projetos_com_ocorrencias = []
    if not df_ocorrencias_atipicas.empty and 'PROJETO' in df_ocorrencias_atipicas.columns:
        projetos_com_ocorrencias = df_ocorrencias_atipicas['PROJETO'].unique().tolist()
        logger.info(f"Projetos com ocorrências atípicas considerados para criticidade: {projetos_com_ocorrencias}")

    def calcular_criticidade(row):
        tem_ocorrencia_atipica = row['Iniciativa'] in projetos_com_ocorrencias
        execucao = row['% Execução']
        
        if execucao > 0.90 or (tem_ocorrencia_atipica and execucao > 0.75):
            return '↑ Alto'
        elif execucao > 0.75 or tem_ocorrencia_atipica:
            return '→ Médio'
        else:
            return '↓ Baixo'

    df_final['Criticidade'] = df_final.apply(calcular_criticidade, axis=1)
    
    df_final = df_final[['Criticidade', 'Iniciativa', 'Orçado', 'Realizado', '% Execução']]

    if not df_final.empty:
        total_orcado = df_final['Orçado'].sum()
        total_realizado = df_final['Realizado'].sum()
        total_execucao = (total_realizado / total_orcado) if total_orcado > 0 else 0
        total_row = pd.DataFrame([{
            'Criticidade': '-', 'Iniciativa': 'Total Geral', 
            'Orçado': total_orcado, 'Realizado': total_realizado, '% Execução': total_execucao
        }])
        df_final = pd.concat([df_final, total_row], ignore_index=True)
        
    return df_final

def agregar_despesas_por_fornecedor(df_bruto: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df_bruto.empty: return pd.DataFrame()
    df_agregado = df_bruto.groupby('FORNECEDOR')['VALOR'].sum().reset_index()
    df_agregado['VALOR_ABS'] = df_agregado['VALOR'].abs()
    placeholders = ['Não Informado', 'Fornecedor Não Encontrado']
    df_filtrado = df_agregado[~df_agregado['FORNECEDOR'].isin(placeholders)]
    df_top = df_filtrado.nlargest(top_n, 'VALOR_ABS')[['FORNECEDOR', 'VALOR']]
    return df_top.rename(columns={'FORNECEDOR': 'Fornecedor', 'VALOR': 'Realizado (Ano)'})

def agregar_despesas_por_mes(df_bruto: pd.DataFrame) -> pd.DataFrame:
    if df_bruto.empty or 'tipo_projeto' not in df_bruto.columns: return pd.DataFrame()
    df_exclusivo = df_bruto[df_bruto['tipo_projeto'] == 'Exclusivo']
    df_compartilhado = df_bruto[df_bruto['tipo_projeto'] == 'Compartilhado']
    df_mes_exclusivo = df_exclusivo.groupby('MES')['VALOR'].sum().reset_index().rename(columns={'VALOR': 'Realizado (Exclusivo)'})
    df_mes_compartilhado = df_compartilhado.groupby('MES')['VALOR'].sum().reset_index().rename(columns={'VALOR': 'Realizado (Compartilhado)'})
    if not df_mes_exclusivo.empty and not df_mes_compartilhado.empty:
        df_final = pd.merge(df_mes_exclusivo, df_mes_compartilhado, on='MES', how='outer')
    elif not df_mes_exclusivo.empty:
        df_final = df_mes_exclusivo
    else:
        df_final = df_mes_compartilhado
    df_final = df_final.fillna(0).sort_values('MES')
    df_final['Acumulado (Exclusivo)'] = df_final['Realizado (Exclusivo)'].cumsum() if 'Realizado (Exclusivo)' in df_final.columns else 0
    df_final['Acumulado (Compartilhado)'] = df_final['Realizado (Compartilhado)'].cumsum() if 'Realizado (Compartilhado)' in df_final.columns else 0
    meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
    df_final['MES'] = df_final['MES'].map(meses_map)
    colunas_finais = ['MES', 'Realizado (Exclusivo)', 'Acumulado (Exclusivo)', 'Realizado (Compartilhado)', 'Acumulado (Compartilhado)']
    colunas_existentes = [col for col in colunas_finais if col in df_final.columns]
    return df_final[colunas_existentes].rename(columns={'MES': 'Mês'})

def gerar_resumo_executivo(
    df_unidade_bruto: pd.DataFrame, 
    df_unidade_integrado: pd.DataFrame, 
    mes_referencia_num: int
) -> dict:
    """Calcula todas as métricas detalhadas para o Resumo Executivo e contexto da Tabela 4."""
    logger.info("Gerando Resumo Executivo e estatísticas de referência...")
    if df_unidade_bruto.empty: return {}

    df_mes_bruto = df_unidade_bruto[df_unidade_bruto['MES'] == mes_referencia_num]
    
    resumo = {
        "valor_total_mes": df_mes_bruto['VALOR'].sum(),
        "valor_total_ano": df_unidade_bruto['VALOR'].sum(),
        "qtd_lancamentos_mes": len(df_mes_bruto),
        "qtd_lancamentos_ano": len(df_unidade_bruto),
    }

    orc_total_ano = df_unidade_integrado['VALOR_ORCADO'].sum()
    orc_exclusivo_ano = df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Exclusivo']['VALOR_ORCADO'].sum()
    orc_compartilhado_ano = df_unidade_integrado[df_unidade_integrado['tipo_projeto'] == 'Compartilhado']['VALOR_ORCADO'].sum()
    
    resumo.update({
        "orcamento_planejado_ano": orc_total_ano,
        "orcamento_total_exclusivo": orc_exclusivo_ano,
        "orcamento_total_compartilhado": orc_compartilhado_ano,
        "orcamento_mes_referencia": orc_total_ano / 12 if orc_total_ano else 0,
        "orcamento_mes_exclusivo": orc_exclusivo_ano / 12 if orc_exclusivo_ano else 0,
        "orcamento_mes_compartilhado": orc_compartilhado_ano / 12 if orc_compartilhado_ano else 0,
    })

    def get_stats_de_valor(df_historico_tipo, df_mes_tipo):
        stats = {}
        if not df_historico_tipo.empty:
            stats.update({
                "media_ano": df_historico_tipo['VALOR'].mean(),
                "mediana_ano": df_historico_tipo['VALOR'].median(),
                "maior_ano": df_historico_tipo['VALOR'].max(),
                "menor_ano": df_historico_tipo['VALOR'].min(),
            })
        
        if not df_mes_tipo.empty and df_mes_tipo['VALOR'].nunique() > 1:
            stats["valor_mediano_mes"] = df_mes_tipo['VALOR'].median()
            
            model = IsolationForest(contamination=0.02, random_state=42)
            predictions = model.fit_predict(df_mes_tipo[['VALOR']])
            inliers = df_mes_tipo[predictions == 1]
            
            if not inliers.empty:
                stats["min_normal_mes"] = inliers['VALOR'].min()
                stats["max_normal_mes"] = inliers['VALOR'].max()
        return stats

    stats_exclusivo = get_stats_de_valor(
        df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Exclusivo'],
        df_mes_bruto[df_mes_bruto['tipo_projeto'] == 'Exclusivo']
    )
    for key, val in stats_exclusivo.items():
        resumo[f"{key}_exclusivo"] = val

    stats_compartilhado = get_stats_de_valor(
        df_unidade_bruto[df_unidade_bruto['tipo_projeto'] == 'Compartilhado'],
        df_mes_bruto[df_mes_bruto['tipo_projeto'] == 'Compartilhado']
    )
    for key, val in stats_compartilhado.items():
        resumo[f"{key}_compartilhado"] = val

    logger.info("Resumo e estatísticas gerados com sucesso.")
    return resumo
