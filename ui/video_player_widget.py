 # ui/video_player_widget.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import vlc
import sys

class VideoPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Integrar o player com o widget
        if sys.platform.startswith('linux'):  # para Linux usando X Server
            self.player.set_xwindow(self.winId())
        elif sys.platform == "win32":  # para Windows
            self.player.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # para MacOS
            self.player.set_nsobject(int(self.winId()))

    def play(self, media_path):
        media = self.instance.media_new(media_path)
        self.player.set_media(media)
        self.player.play()

