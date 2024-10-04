# utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name=__name__, log_file='logs/app.log', level=logging.DEBUG):
    """
    Configura e retorna um logger.
    
    :param name: Nome do logger.
    :param log_file: Caminho para o arquivo de log.
    :param level: Nível de severidade do logger.
    :return: Configuração do logger.
    """
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicação de handlers
    if not logger.handlers:
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Handler para o arquivo de log com rotação
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        # Handler para a saída no console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
