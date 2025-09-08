# analise_despesa/queries.py
"""
Define e organiza as consultas pré-definidas do projeto.
"""
from typing import Dict

# Importações agora são relativas ao pacote 'analise_despesa'
from .utils import carregar_sql
from .config import CONEXOES

# Caminho simplificado para a pasta 'sql' na raiz do projeto.
SQL_DIR = 'sql/'

class Consulta:
    """Representa uma definição de consulta (SQL ou MDX)."""
    def __init__(self, titulo: str, sql_filename: str, tipo: str, conexao: str):
        self.titulo = titulo
        self.sql_filename = sql_filename
        self.tipo = tipo.lower()
        self.conexao = conexao

        if conexao not in CONEXOES:
            raise ValueError(f"Conexão '{conexao}' não definida em config.py")

        self.info_conexao = CONEXOES[conexao]

    @property
    def sql(self) -> str:
        """Propriedade que carrega o conteúdo SQL/MDX do arquivo sob demanda."""
        caminho_completo = SQL_DIR + self.sql_filename
        return carregar_sql(caminho_completo)

# Dicionário de consultas pré-definidas
consultas: Dict[str, Consulta] = {
    "BaseDespesas": Consulta(
        titulo="Base de Despesas Completa",
        tipo="sql",
        sql_filename="bd.sql",
        conexao="SPSVSQL39_HubDados"
    )
}
