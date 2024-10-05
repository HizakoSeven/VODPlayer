# tests/test_shutdown.py

import pytest
import asyncio
from PyQt5.QtWidgets import QApplication
from main import main_async
from utils.logger import setup_logger

logger = setup_logger("TestShutdown")


@pytest.mark.asyncio
async def test_application_shutdown(qtbot):
    """
    Testa se a aplicação VODPlayer encerra corretamente ao fechar a janela principal.
    """
    # Iniciar a aplicação de forma assíncrona
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Definir nível de log para DEBUG para mais detalhes durante o teste
    logger.setLevel("DEBUG")

    # Iniciar a função assíncrona principal sem bloquear o teste
    task = asyncio.create_task(main_async())

    # Aguarde um curto período para garantir que a aplicação inicializou
    await asyncio.sleep(2)

    # Encontrar a janela principal
    main_window = None
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            main_window = widget
            break

    assert main_window is not None, "Janela principal não foi encontrada."

    # Simular o fechamento da janela principal
    qtbot.mouseClick(main_window.closeButton(), QtCore.Qt.LeftButton)

    # Alternativamente, podemos chamar diretamente o método close()
    main_window.close()

    # Aguarde um curto período para permitir que a aplicação processe o fechamento
    await asyncio.sleep(2)

    # Verificar se todas as tarefas assíncronas foram finalizadas
    assert task.done(), "A tarefa principal não foi finalizada após fechar a aplicação."

    # Verificar se o QApplication está encerrado
    assert not app.topLevelWidgets(), "A aplicação ainda possui janelas abertas após o fechamento."

