# main.py

import sys
import atexit
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import setup_logger
from logging.handlers import RotatingFileHandler
import logging
import os

logger = setup_logger('MainApp')

file_handler = RotatingFileHandler(
    'logs/main_app.log',
    maxBytes=10 * 1024 * 1024,
    backupCount=3
)
log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
file_handler.setLevel(getattr(logging, log_level, logging.DEBUG))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def cleanup():
    logger.info("Encerrando a aplicação.")
    print("Encerrando a aplicação.")

def create_app():
    logger.info("Criando a aplicação e a janela principal.")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app

def main():
    logger.debug("Ponto de entrada do script.")
    print("Ponto de entrada do script.")
    app = create_app()
    atexit.register(cleanup)
    try:
        return_code = app.exec_()
        logger.info(f"Aplicação encerrada com código de retorno: {return_code}")
        print(f"Aplicação encerrada com código de retorno: {return_code}")
        sys.exit(return_code)
    except SystemExit:
        logger.debug("SystemExit chamado explicitamente.")
        print("SystemExit chamado explicitamente.")
        raise
    except (OSError, RuntimeError, ValueError) as e:
        logger.exception("Erro inesperado durante a execução da aplicação: %s", e)
        print(f"Erro inesperado durante a execução da aplicação: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
