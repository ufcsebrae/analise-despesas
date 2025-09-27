# analise/agregacao.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def agregar_despesas_por_fornecedor(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Agrupa as DESPESAS (valores positivos) por fornecedor, limpa categorias
    genéricas e retorna os top N maiores.
    """
    logger.info(f"Agregando despesas e buscando os top {top_n} fornecedores...")
    
    # --- 1. FILTRAR APENAS DESPESAS (valores positivos) ---
    # Isso evita que créditos/reversões (valores negativos) influenciem o ranking.
    df_despesas = df[df['UNIFICAVALOR'] > 0].copy()
    
    if df_despesas.empty:
        logger.warning("Nenhum registro de despesa (valor positivo) encontrado para esta unidade.")
        return pd.DataFrame(columns=['FORNECEDOR', 'UNIFICAVALOR'])
    
    logger.info(f"Analisando {len(df_despesas)} registros de despesas (valores positivos).")

    # --- 2. LISTA DE CATEGORIAS GENÉRICAS A SEREM EXCLUÍDAS DA ANÁLISE ---
    placeholders_para_excluir = ['Não Informado', 'Fornecedor Não Encontrado']
    
    df_filtrado = df_despesas[~df_despesas['FORNECEDOR'].isin(placeholders_para_excluir)]
    
    if df_filtrado.empty:
        logger.warning("Nenhum fornecedor nomeado encontrado após a filtragem. Retornando DataFrame vazio.")
        return pd.DataFrame(columns=['FORNECEDOR', 'UNIFICAVALOR'])

    # --- 3. AGRUPAR, SOMAR E CALCULAR O TOP N ---
    top_fornecedores = df_filtrado.groupby('FORNECEDOR')['UNIFICAVALOR'].sum()
    top_fornecedores = top_fornecedores.nlargest(top_n).reset_index()
    
    logger.info("Agregação por fornecedor concluída.")
    return top_fornecedores
