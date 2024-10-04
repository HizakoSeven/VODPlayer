# tests/test_main.py

import pytest
from unittest.mock import patch
from main import main

@patch('PyQt5.QtWidgets.QApplication.exec_')
def test_main_initialization(mock_exec):
    """
    Testa se a aplicação inicializa sem erros, mockando exec_.
    """
    mock_exec.return_value = 0  # Simula que exec_ retorna 0
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() levantou uma exceção: {e}")
    mock_exec.assert_called_once()
