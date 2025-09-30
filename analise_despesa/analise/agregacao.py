# analise/agregacao.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def apenas_despesas(df: pd.DataFrame) -> pd.DataFrame:
    """Função auxiliar para filtrar apenas despesas (valores positivos)."""
    df_despesas = df[df['VALOR'] > 0].copy()
    if df_despesas.empty:
        logger.warning("Nenhum registro de despesa (valor positivo) encontrado.")
    else:
        logger.info(f"Analisando {len(df_despesas)} registros de despesas (valores positivos).")
    return df_despesas

def agregar_despesas_por_fornecedor(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Agrupa as despesas por fornecedor e retorna os top N maiores."""
    logger.info(f"Agregando despesas por fornecedor (Top {top_n})...")
    df_despesas = apenas_despesas(df)
    if df_despesas.empty:
        return pd.DataFrame(columns=['FORNECEDOR', 'VALOR'])

    placeholders_para_excluir = ['Não Informado', 'Fornecedor Não Encontrado']
    df_filtrado = df_despesas[~df_despesas['FORNECEDOR'].isin(placeholders_para_excluir)]
    
    if df_filtrado.empty:
        logger.warning("Nenhum fornecedor nomeado encontrado para o Top N.")
        return pd.DataFrame(columns=['FORNECEDOR', 'VALOR'])

    top_fornecedores = df_filtrado.groupby('FORNECEDOR')['VALOR'].sum()
    top_fornecedores = top_fornecedores.nlargest(top_n).reset_index()
    
    logger.info("Agregação por fornecedor concluída.")
    return top_fornecedores

def agregar_despesas_por_projeto(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa as despesas totais por projeto."""
    logger.info("Agregando despesas por projeto...")
    df_despesas = apenas_despesas(df)
    if df_despesas.empty:
        return pd.DataFrame(columns=['PROJETO', 'VALOR'])
        
    # Agrupa por 'PROJETO', soma os valores, e ordena do maior para o menor
    df_por_projeto = df_despesas.groupby('PROJETO')['VALOR'].sum().reset_index()
    df_por_projeto = df_por_projeto.sort_values('VALOR', ascending=False)
    
    logger.info("Agregação por projeto concluída.")
    return df_por_projeto

def agregar_despesas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa as despesas totais por mês."""
    logger.info("Agregando despesas por mês...")
    df_despesas = apenas_despesas(df)
    if df_despesas.empty:
        return pd.DataFrame(columns=['MÊS', 'VALOR'])

    # Garante que a coluna 'MES' exista (criada no passo de enriquecimento)
    if 'MES' not in df_despesas.columns:
        logger.error("A coluna 'MES' não foi encontrada. Execute o enriquecimento de data primeiro.")
        return pd.DataFrame(columns=['MÊS', 'VALOR'])
        
    # Agrupa por 'MES', soma os valores, e ordena pelo mês
    df_por_mes = df_despesas.groupby('MES')['VALOR'].sum().reset_index()
    df_por_mes = df_por_mes.sort_values('MES')
    
    # Opcional: Mapeia o número do mês para o nome para melhor legibilidade
    meses_map = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 
                 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    df_por_mes['MÊS'] = df_por_mes['MES'].map(meses_map)
    df_por_mes = df_por_mes.rename(columns={'MES': 'MÊS'})

    logger.info("Agregação por mês concluída.")
    return df_por_mes
