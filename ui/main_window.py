# ui/main_window.py 

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget
from .video_player_widget import VideoPlayerWidget
from .vod_list_widget import VODListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VODPlayer")

        # Widgets
        self.search_field = QLineEdit()
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

    def search_vods(self):
        streamer_name = self.search_field.text()
        # Chamar função de scraping e atualizar a lista de VODs
        pass

    def play_vod(self, item):
        vod_url = item.data(0)
        # Chamar função de download e reproduzir o VOD
        pass
 
