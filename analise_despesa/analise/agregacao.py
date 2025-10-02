# analise_despesa/analise/agregacao.py (VERSÃO COM FORMATAÇÃO DE NEGRIO NOS TOTAIS)

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def agregar_realizado_vs_orcado_por_projeto(df_integrado: pd.DataFrame) -> pd.DataFrame:
    if df_integrado.empty: return pd.DataFrame()
    df_agregado = df_integrado.groupby('PROJETO').agg(VALOR_REALIZADO=('VALOR_REALIZADO', 'sum'), VALOR_ORCADO=('VALOR_ORCADO', 'sum')).reset_index()
    df_agregado['%_EXECUCAO'] = (df_agregado['VALOR_REALIZADO'] / df_agregado['VALOR_ORCADO']).replace([np.inf, -np.inf], 0).fillna(0)
    df_final = df_agregado.rename(columns={'PROJETO': 'Iniciativa', 'VALOR_ORCADO': 'Orçado', 'VALOR_REALIZADO': 'Realizado', '%_EXECUCAO': '% Execução'}).sort_values('Realizado', ascending=False)
    
    if not df_final.empty:
        total_orcado = df_final['Orçado'].sum()
        total_realizado = df_final['Realizado'].sum()
        total_execucao = (total_realizado / total_orcado) if total_orcado > 0 else 0
        
        # MUDANÇA 4: Formata os valores do total como strings em negrito
        total_row = pd.DataFrame([{
            'Iniciativa': '<b>Total Geral</b>',
            'Orçado': f"<b>R$ {total_orcado:,.0f}</b>".replace(",", "X").replace(".", ",").replace("X", "."),
            'Realizado': f"<b>R$ {total_realizado:,.0f}</b>".replace(",", "X").replace(".", ",").replace("X", "."),
            '% Execução': f"<b>{total_execucao:.0%}</b>"
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
    if df_bruto.empty or 'tipo_projeto' not in df_bruto.columns:
        return pd.DataFrame()
    df_exclusivo = df_bruto[df_bruto['tipo_projeto'] == 'Exclusivo']
    df_compartilhado = df_bruto[df_bruto['tipo_projeto'] == 'Compartilhado']
    df_mes_exclusivo = df_exclusivo.groupby('MES')['VALOR'].sum().reset_index().rename(columns={'VALOR': 'Valor (Exclusivo)'})
    df_mes_compartilhado = df_compartilhado.groupby('MES')['VALOR'].sum().reset_index().rename(columns={'VALOR': 'Valor (Compartilhado)'})
    if not df_mes_exclusivo.empty and not df_mes_compartilhado.empty:
        df_final = pd.merge(df_mes_exclusivo, df_mes_compartilhado, on='MES', how='outer')
    elif not df_mes_exclusivo.empty:
        df_final = df_mes_exclusivo
    elif not df_mes_compartilhado.empty:
        df_final = df_mes_compartilhado
    else:
        return pd.DataFrame()
    df_final = df_final.fillna(0).sort_values('MES')
    df_final['Acumulado (Exclusivo)'] = df_final['Valor (Exclusivo)'].cumsum() if 'Valor (Exclusivo)' in df_final.columns else 0
    df_final['Acumulado (Compartilhado)'] = df_final['Valor (Compartilhado)'].cumsum() if 'Valor (Compartilhado)' in df_final.columns else 0
    meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
    df_final['MES'] = df_final['MES'].map(meses_map)
    colunas_finais = ['MES', 'Valor (Exclusivo)', 'Acumulado (Exclusivo)', 'Valor (Compartilhado)', 'Acumulado (Compartilhado)']
    colunas_existentes = [col for col in colunas_finais if col in df_final.columns]
    return df_final[colunas_existentes].rename(columns={'MES': 'Mês'})
