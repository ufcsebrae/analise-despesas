# analise_despesa/analise/agregacao.py (VERSÃO COM A CORREÇÃO FINAL)
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def apenas_despesas(df: pd.DataFrame) -> pd.DataFrame:
    df_despesas = df[df['VALOR'] > 0].copy()
    if df_despesas.empty: logger.warning("Nenhum registro de despesa (valor positivo) encontrado.")
    return df_despesas

def agregar_despesas_por_fornecedor(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    # CORREÇÃO: Conta cada LCTREF apenas uma vez.
    df_corrigido = df.drop_duplicates(subset=['LCTREF'])
    df_despesas = apenas_despesas(df_corrigido)
    
    if df_despesas.empty: return pd.DataFrame(columns=['FORNECEDOR', 'VALOR'])
    placeholders = ['Não Informado', 'Fornecedor Não Encontrado']
    df_filtrado = df_despesas[~df_despesas['FORNECEDOR'].isin(placeholders)]
    if df_filtrado.empty: return pd.DataFrame(columns=['FORNECEDOR', 'VALOR'])
    return df_filtrado.groupby('FORNECEDOR')['VALOR'].sum().nlargest(top_n).reset_index()

def calcular_total_projetos_global(df_completo: pd.DataFrame) -> pd.DataFrame:
    # CORREÇÃO: Conta cada LCTREF apenas uma vez para o total global.
    df_corrigido = df_completo.drop_duplicates(subset=['LCTREF'])
    df_despesas = apenas_despesas(df_corrigido)

    if df_despesas.empty: return pd.DataFrame(columns=['PROJETO', 'VALOR_TOTAL_PROJETO'])
    df_total = df_despesas.groupby('PROJETO')['VALOR'].sum().reset_index()
    return df_total.rename(columns={'VALOR': 'VALOR_TOTAL_PROJETO'})

def agregar_despesas_por_projeto(df_unidade: pd.DataFrame, df_total_projetos: pd.DataFrame) -> pd.DataFrame:
    # CORREÇÃO: Conta cada LCTREF apenas uma vez antes de somar para o projeto da unidade.
    df_corrigido = df_unidade.drop_duplicates(subset=['LCTREF'])
    df_despesas_unidade = apenas_despesas(df_corrigido)

    if df_despesas_unidade.empty: return pd.DataFrame()
    df_agregado_unidade = df_despesas_unidade.groupby('PROJETO')['VALOR'].sum().reset_index()
    
    df_contextual = pd.merge(df_agregado_unidade, df_total_projetos, on='PROJETO', how='left')
    
    df_contextual['PARTICIPACAO_%'] = df_contextual.apply(
        lambda row: (row['VALOR'] / row['VALOR_TOTAL_PROJETO']) * 100 if row.get('VALOR_TOTAL_PROJETO') and row['VALOR_TOTAL_PROJETO'] != 0 else 0,
        axis=1
    )
    df_contextual = df_contextual.rename(columns={'VALOR': 'VALOR_UNIDADE'})
    return df_contextual[['PROJETO', 'VALOR_UNIDADE', 'VALOR_TOTAL_PROJETO', 'PARTICIPACAO_%']].sort_values('VALOR_UNIDADE', ascending=False)

def agregar_despesas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    # CORREÇÃO: Conta cada LCTREF apenas uma vez.
    df_corrigido = df.drop_duplicates(subset=['LCTREF'])
    df_despesas = apenas_despesas(df_corrigido)

    if df_despesas.empty: return pd.DataFrame(columns=['MÊS', 'VALOR'])
    if 'MES' not in df_despesas.columns: return pd.DataFrame(columns=['MÊS', 'VALOR'])
    df_por_mes = df_despesas.groupby('MES')['VALOR'].sum().reset_index()
    meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
    df_por_mes['MES'] = df_por_mes['MES'].map(meses_map)
    return df_por_mes.rename(columns={'MES': 'MÊS'}).sort_values('VALOR', ascending=False)
