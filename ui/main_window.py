# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5 import QtCore
from .video_player_widget import VideoPlayerWidget
from .vod_list_widget import VODListWidget
from utils.scraper import scrape_vods
from utils.downloader import download_m3u8
from utils.logger import setup_logger
import sys
import os

# Configuração do logger
logger = setup_logger('MainWindow')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Inicializando a MainWindow.")
        self.setWindowTitle("VODPlayer")
        self.setGeometry(100, 100, 800, 600)  # Define o tamanho da janela

        # Widgets
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Digite o nome do streamer")
        self.search_button = QPushButton("Buscar")
        self.vod_list = VODListWidget()
        self.video_player = VideoPlayerWidget()

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.search_field)
        layout.addWidget(self.search_button)
        layout.addWidget(self.vod_list)
        layout.addWidget(self.video_player)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Signals
        self.search_button.clicked.connect(self.search_vods)
        self.vod_list.itemClicked.connect(self.play_vod)
        logger.info("MainWindow inicializada com sucesso.")

    def search_vods(self):
        streamer_name = self.search_field.text().strip()
        logger.debug(f"Usuário iniciou a busca pelo streamer: '{streamer_name}'")
        if not streamer_name:
            logger.warning("Campo de busca vazio. Nenhuma ação tomada.")
            QMessageBox.warning(self, "Aviso", "Por favor, digite o nome de um streamer.")
            return

        try:
            # Chamar função de scraping para obter os VODs
            vods = scrape_vods(streamer_name)
            logger.info(f"Encontrados {len(vods)} VODs para o streamer '{streamer_name}'.")
            if vods:
                self.vod_list.populate_vods(vods)
            else:
                logger.info(f"Nenhum VOD encontrado para o streamer '{streamer_name}'.")
                QMessageBox.information(self, "Resultados da Busca", "Nenhum VOD encontrado para o streamer informado.")
        except Exception as e:
            logger.exception(f"Erro ao buscar VODs para o streamer '{streamer_name}'.")
            QMessageBox.critical(self, "Erro", "Ocorreu um erro ao buscar os VODs. Verifique os logs para mais detalhes.")

    def play_vod(self, item):
        vod_url = item.data(QtCore.Qt.UserRole)
        logger.debug(f"Usuário selecionou o VOD com URL: {vod_url}")
        if vod_url:
            try:
                # Chamar função de download e reproduzir o VOD
                cache_dir = os.path.join(os.getcwd(), 'data', 'cache', 'm3u8_files')
                os.makedirs(cache_dir, exist_ok=True)
                m3u8_path = download_m3u8(vod_url, cache_dir)
                logger.info(f"Arquivo .m3u8 baixado em: {m3u8_path}")
                self.video_player.play(m3u8_path)
                logger.info(f"Reprodução iniciada para o VOD: {m3u8_path}")
            except Exception as e:
                logger.exception(f"Erro ao reproduzir o VOD com URL: {vod_url}")
                QMessageBox.critical(self, "Erro", "Ocorreu um erro ao reproduzir o VOD. Verifique os logs para mais detalhes.")
