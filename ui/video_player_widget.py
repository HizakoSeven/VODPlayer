# ui/video_player_widget.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import vlc
import sys
from utils.logger import setup_logger

# Configuração do logger
logger = setup_logger('VideoPlayerWidget')

class VideoPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug("Inicializando VideoPlayerWidget.")
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Integrar o player com o widget
        if sys.platform.startswith('linux'):  # para Linux usando X Server
            self.player.set_xwindow(self.winId())
        elif sys.platform == "win32":  # para Windows
            self.player.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # para MacOS
            self.player.set_nsobject(int(self.winId()))

        logger.debug("VideoPlayerWidget configurado com sucesso.")

    def play(self, media_path):
        logger.info(f"Reproduzindo mídia: {media_path}")
        try:
            media = self.instance.media_new(media_path)
            self.player.set_media(media)
            self.player.play()
            logger.debug("Mídia iniciada com sucesso.")
        except Exception as e:
            logger.exception(f"Erro ao reproduzir mídia '{media_path}': {e}")
