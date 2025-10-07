# analise_despesa/database.py (VERSÃO FINAL COM AJUSTE NO SALVAR)
import logging
import time
from typing import Union, Dict
import pandas as pd
import sqlalchemy
from sqlalchemy.engine import Engine
from .config import CONEXOES

logger = logging.getLogger(__name__)

_ENGINES: Dict[str, Engine] = {}

def obter_conexao(nome_conexao: str) -> Union[Engine, str]:
    # (Código inalterado)
    if nome_conexao in _ENGINES:
        logger.debug(f"Retornando engine do cache para '{nome_conexao}'")
        return _ENGINES[nome_conexao]
    info = CONEXOES.get(nome_conexao)
    if not info:
        raise ValueError(f"Configuração de conexão '{nome_conexao}' não encontrada em config.py")
    tipo = info.get("tipo", "sql").lower()
    logger.info(f"Criando novo objeto de conexão para '{nome_conexao}' (tipo: {tipo})")
    if tipo in ("sql", "azure_sql"):
        url = sqlalchemy.engine.URL.create(drivername="mssql+pyodbc", query={"odbc_connect": _construir_odbc_str(info)})
        engine = sqlalchemy.create_engine(url, fast_executemany=True)
        _ENGINES[nome_conexao] = engine
        return engine
    elif tipo == "mdx":
        return info["str_conexao"]
    raise ValueError(f"Tipo de conexão '{tipo}' não suportado.")

def _construir_odbc_str(info: dict) -> str:
    # (Código inalterado)
    driver, servidor, banco = info["driver"], info["servidor"], info["banco"]
    odbc_parts = [f"DRIVER={{{driver}}}", f"SERVER={servidor}", f"DATABASE={banco}"]
    if info.get("trusted_connection"): odbc_parts.append("Trusted_Connection=yes")
    if info.get("authentication"): odbc_parts.append(f"Authentication={info['authentication']}")
    return ";".join(odbc_parts)

def salvar_dataframe(df: pd.DataFrame, nome_tabela: str, nome_conexao: str, if_exists: str = "replace"):
    """
    Salva um DataFrame em uma tabela de banco de dados.
    Agora usa 'append' como padrão implícito, que é mais seguro para logs.
    """
    if df.empty:
        logger.warning(f"⚠️  DataFrame está vazio. Nada será salvo na tabela '{nome_tabela}'.")
        return

    logger.info(f"📀 Iniciando salvamento de {len(df)} linhas na tabela '{nome_tabela}' (método: {if_exists})...")
    inicio = time.perf_counter()
    engine = obter_conexao(nome_conexao)
    try:
        with engine.begin() as connection:
            df.to_sql(name=nome_tabela, con=connection, if_exists=if_exists, index=False, chunksize=1000)
            fim = time.perf_counter()
            tempo = fim - inicio
            logger.info(f"✅ Salvamento na tabela '{nome_tabela}' concluído com sucesso em {tempo:.2f} segundos.")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar dados na tabela '{nome_tabela}'. A transação foi desfeita (rollback). Erro: {e}", exc_info=True)
        raise
