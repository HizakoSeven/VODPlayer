# main.py

import sys
import atexit
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import setup_logger

# Configuração do logger
logger = setup_logger('MainApp')

def cleanup():
    logger.info("Encerrando a aplicação.")

def main():
    logger.info("Inicializando a aplicação VODPlayer.")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    atexit.register(cleanup)
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception("Erro inesperado durante a execução da aplicação.")
        sys.exit(1)

if __name__ == '__main__':
    main()
