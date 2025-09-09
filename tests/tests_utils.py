# tests/test_utils.py
from unittest.mock import mock_open, patch
import pytest
from analise_despesa import utils

def test_carregar_sql_sucesso():
    """Testa se a função lê e retorna o conteúdo de um arquivo mockado."""
    sql_content = "SELECT 1;"
    # Simula a existência e o conteúdo do arquivo
    with patch("builtins.open", mock_open(read_data=sql_content)) as mock_file:
        with patch("os.path.exists", return_value=True):
            resultado = utils.carregar_sql("dummy/path.sql")
            mock_file.assert_called_with("dummy/path.sql", 'r', encoding='utf-8')
            assert resultado == sql_content

def test_carregar_sql_nao_encontrado():
    """Testa se a exceção FileNotFoundError é levantada."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            utils.carregar_sql("caminho/inexistente.sql")
