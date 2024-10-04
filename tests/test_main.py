import sys
import os
import pytest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main  # Agora deve conseguir importar corretamente

def test_main_initialization():
    """
    Exemplo de teste para verificar se a aplicação inicializa sem erros.
    """
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() levantou uma exceção: {e}")
