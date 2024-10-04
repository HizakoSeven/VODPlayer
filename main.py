# main.py

import sys
import logging
import os
from logging.handlers import RotatingFileHandler

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.logger import setup_logger
from utils.scraper import Scraper  # Importar a classe Scraper

import qasync
import asyncio

# Reconfigura o stdout para usar 'utf-8'
sys.stdout.reconfigure(encoding="utf-8")

# Configuração do logger com nível de log obtido da variável de ambiente
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

logger = setup_logger("MainApp")

# Adicionar um handler de arquivo para persistir logs
file_handler = RotatingFileHandler(
    "logs/main_app.log", maxBytes=10 * 1024 * 1024, backupCount=3
)
file_handler.setLevel(getattr(logging, log_level, logging.DEBUG))
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Inicializar o Scraper
scraper = Scraper()


async def main_async():
    """
    Função principal assíncrona que inicializa a aplicação VODPlayer.
    """
    logger.info("Inicializando a aplicação VODPlayer.")
    print("Inicializando a aplicação VODPlayer.")
    app = QApplication(sys.argv)

    # Integração do loop de eventos do asyncio com o loop do Qt
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    logger.debug("QApplication inicializada com sucesso.")
    print("QApplication inicializada com sucesso.")

    # Inicializar o Scraper
    await scraper.initialize()

    # Cria a janela principal da aplicação
    window = MainWindow(scraper)  # Passar o scraper para a janela
    logger.debug("Janela principal criada com sucesso.")
    print("Janela principal criada com sucesso.")
    window.show()
    logger.debug("Janela principal exibida.")
    print("Janela principal exibida.")

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
    print("Iniciando limpeza após encerramento da aplicação.")
    await scraper.close()
    logger.info("Scraper fechado com sucesso.")
    print("Scraper fechado com sucesso.")


def main():
    """
    Função principal síncrona que inicia a aplicação.
    """
    # Ponto de entrada do script
    logger.debug("Ponto de entrada do script.")
    print("Ponto de entrada do script.")
    qasync.run(main_async())


if __name__ == "__main__":
    main()
