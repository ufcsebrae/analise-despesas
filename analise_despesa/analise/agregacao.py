import pandas as pd
import logging

logger = logging.getLogger(__name__)

def agregar_despesas_por_fornecedor(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Agrupa as despesas por fornecedor e retorna os top N maiores."""
    logger.info(f"Agregando despesas e buscando os top {top_n} fornecedores...")
    
    # Exclui o fornecedor 'Não Informado' da análise de top N
    df_filtrado = df[df['FORNECEDOR'] != 'Não Informado']
    
    top_fornecedores = df_filtrado.groupby('FORNECEDOR')['UNIFICAVALOR'].sum()
    top_fornecedores = top_fornecedores.nlargest(top_n).reset_index()
    
    logger.info("Agregação por fornecedor concluída.")
    return top_fornecedores
