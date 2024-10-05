# main.py

import sys
import os

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.logger import setup_logger
from utils.scraper import Scraper

import qasync
import asyncio

# Reconfigura o stdout para usar 'utf-8'
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Configuração do logger com nível de log obtido da variável de ambiente
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

logger = setup_logger("MainApp", log_file="logs/main_app.log", level=log_level)


async def main_async():
    """
    Função principal assíncrona que inicializa a aplicação VODPlayer.
    """
    logger.info("Inicializando a aplicação VODPlayer.")
    app = QApplication(sys.argv)

    # Integração do loop de eventos do asyncio com o loop do Qt
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    logger.debug("QApplication inicializada com sucesso.")

    # Inicializar o Scraper
    scraper = Scraper()
    try:
        await scraper.initialize()
    except Exception as e:
        logger.exception("Falha ao inicializar o Scraper.")
        sys.exit(1)

    # Cria a janela principal da aplicação
    window = MainWindow(scraper)  # Passar o scraper para a janela
    logger.debug("Janela principal criada com sucesso.")
    window.show()
    logger.debug("Janela principal exibida.")

    # Cria um evento para aguardar até que a aplicação seja encerrada
    app_exit_event = asyncio.Event()

    def on_exit():
        logger.debug("Sinal de encerramento recebido. Iniciando processo de limpeza.")
        app_exit_event.set()

    app.aboutToQuit.connect(on_exit)

    # Aguarda até que a aplicação seja encerrada
    await app_exit_event.wait()

    # Após o evento ser acionado, realizar a limpeza
    logger.info("Iniciando limpeza após encerramento da aplicação.")
    try:
        await scraper.close()
        logger.info("Scraper fechado com sucesso.")
    except Exception as e:
        logger.exception("Erro ao fechar o Scraper.")


def main():
    """
    Função principal síncrona que inicia a aplicação.
    """
    # Ponto de entrada do script
    logger.debug("Ponto de entrada do script.")
    try:
        qasync.run(main_async())
    except Exception as e:
        logger.exception("Exceção não tratada no loop principal.")


if __name__ == "__main__":
    main()
