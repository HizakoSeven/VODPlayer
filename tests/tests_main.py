import pytest
from main import main  # Ajuste conforme a estrutura do seu projeto


def test_main_initialization():
    """
    Exemplo de teste para verificar se a aplicação inicializa sem erros.
    """
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() levantou uma exceção: {e}")
