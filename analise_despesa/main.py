import logging
import datetime
import os

from .logging_config import setup_logging
from . import extracao
from . import database

from .processamento import limpeza, enriquecimento
from .analise import agregacao, insights_ia
from .visualizacao import graficos
from . import exportacao # <-- Importamos o novo módulo

setup_logging()
logger = logging.getLogger(__name__)

def executar_analise():
    """
    Orquestra o fluxo completo: Extração, Transformação, Análise, Visualização, Exportação e Carga.
    """
    logger.info("🚀 Iniciando o pipeline completo de análise de despesas.")
    
    try:
        # ... (Etapas 1, 2 e 3 permanecem as mesmas) ...
        # 1. EXTRAÇÃO
        ano_corrente = datetime.date.today().year
        params = {"ano": ano_corrente}
        df_bruto = extracao.buscar_dados("BaseDespesas", params=params)

        if df_bruto.empty:
            return

        # 2. TRANSFORMAÇÃO
        df_limpo = limpeza.tratar_dados_nulos(df_bruto)
        df_enriquecido = enriquecimento.adicionar_colunas_de_data(df_limpo)

        # 3. ANÁLISE & IA
        df_final = insights_ia.detectar_anomalias_de_valor(df_enriquecido)
        df_top_fornecedores = agregacao.agregar_despesas_por_fornecedor(df_final)
        
        anomalias = df_final[df_final['ANOMALIA'] == 'Anomalia'].sort_values('UNIFICAVALOR', ascending=False)
        print("\n--- Top 10 Fornecedores ---")
        print(df_top_fornecedores)
        print("\n--- Possíveis Despesas Anômalas (Valores mais altos) ---")
        print(anomalias[['DATA', 'FORNECEDOR', 'COMPLEMENTO', 'UNIFICAVALOR']].head())
        
        # 4. VISUALIZAÇÃO
        caminho_grafico = os.path.join('outputs', 'graficos', 'top_10_fornecedores.png')
        graficos.plotar_top_fornecedores(df_top_fornecedores, caminho_salvar=caminho_grafico)

        # --- 5. EXPORTAÇÃO (NOVA ETAPA) ---
        logger.info("Iniciando a fase de Exportação de Relatórios...")
        caminho_relatorio_anomalias = os.path.join('outputs', 'relatorios', 'relatorio_anomalias.csv')
        exportacao.exportar_para_csv(anomalias, caminho_relatorio_anomalias)
        
        # --- 6. CARGA (L) ---
        logger.info("Iniciando a fase de Carga...")
        nome_tabela_destino = "analise_despesas_resultado"
        nome_conexao_destino = "SPSVSQL39_FINANCA"
        database.salvar_dataframe(df=df_final, nome_tabela=nome_tabela_destino, nome_conexao=nome_conexao_destino)

        logger.info("✅ Pipeline completo executado com sucesso!")

    except Exception as e:
        logger.critical(f"❌ Ocorreu um erro fatal no pipeline: {e}", exc_info=True)

if __name__ == "__main__":
    executar_analise()
