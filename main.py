# main.py

import sys
import atexit
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import setup_logger
from logging.handlers import RotatingFileHandler
import logging
import os

# Configuração do logger com nível de log obtido da variável de ambiente
log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()  # Obtém o nível de log da variável de ambiente, padrão para 'DEBUG'
logger = setup_logger('MainApp')  # Cria um logger para a aplicação principal

# Adicionar um handler de arquivo para persistir logs
file_handler = RotatingFileHandler('logs/main_app.log', maxBytes=10*1024*1024, backupCount=3)  # Configura um handler de arquivo com rotação para limitar o tamanho do log
file_handler.setLevel(getattr(logging, log_level, logging.DEBUG))  # Define o nível do handler baseado na configuração
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Formato do log com timestamp, nome do logger, nível e mensagem
file_handler.setFormatter(formatter)  # Define o formato do log para o handler
logger.addHandler(file_handler)  # Adiciona o handler de arquivo ao logger

def cleanup():
    """
    Função de limpeza chamada ao encerrar a aplicação.
    """
    logger.info("Encerrando a aplicação.")
    print("Encerrando a aplicação.")  # Debug print
    # Adicionar operações de limpeza adicionais, como liberar recursos ou salvar o estado da aplicação
    # Exemplo: Salvar estado da aplicação em um arquivo
    # save_application_state()

def main():
    """
    Função principal que inicializa a aplicação VODPlayer.
    """
    logger.info("Inicializando a aplicação VODPlayer.")
    print("Inicializando a aplicação VODPlayer.")  # Debug print
    try:
        app = QApplication(sys.argv)  # Cria uma instância da aplicação Qt
        logger.debug("QApplication inicializada com sucesso.")
        print("QApplication inicializada com sucesso.")  # Debug print
    except Exception as e:
        # Captura exceções durante a inicialização da QApplication e registra o erro
        logger.exception("Erro ao inicializar QApplication: %s", e)
        print(f"Erro ao inicializar QApplication: {e}")  # Debug print
        sys.exit(1)  # Sai do programa com código de erro
    
    # Cria a janela principal da aplicação
    window = MainWindow()
    logger.debug("Janela principal criada com sucesso.")
    print("Janela principal criada com sucesso.")  # Debug print
    window.show()  # Mostra a janela principal
    logger.debug("Janela principal exibida.")
    print("Janela principal exibida.")  # Debug print
    
    # Registra a função de limpeza para ser chamada ao encerrar a aplicação
    atexit.register(cleanup)
    logger.debug("Função de limpeza registrada com sucesso.")
    print("Função de limpeza registrada com sucesso.")  # Debug print
    
    try:
        # Executa a aplicação e aguarda até que seja fechada
        return_code = app.exec_()  # Executa o loop principal do Qt
        logger.info(f"Aplicação encerrada com código de retorno: {return_code}")
        print(f"Aplicação encerrada com código de retorno: {return_code}")  # Debug print
        sys.exit(return_code)  # Sai do programa com o código de retorno da aplicação
    except SystemExit:
        # Se houver uma chamada explícita para sys.exit(), apenas re-levanta a exceção
        logger.debug("SystemExit chamado explicitamente.")
        print("SystemExit chamado explicitamente.")  # Debug print
        raise
    except (OSError, RuntimeError, ValueError) as e:
        # Captura exceções inesperadas durante a execução da aplicação e registra o erro
        logger.exception("Erro inesperado durante a execução da aplicação: %s", e)
        print(f"Erro inesperado durante a execução da aplicação: {e}")  # Debug print
        sys.exit(1)  # Sai do programa com código de erro

if __name__ == '__main__':
    # Ponto de entrada do script
    logger.debug("Ponto de entrada do script.")
    print("Ponto de entrada do script.")  # Debug print
    main()