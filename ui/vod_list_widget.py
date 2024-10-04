# ui/vod_list_widget.py (versão atualizada para asyncio)

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from utils.logger import setup_logger
import asyncio

# Configuração do logger
logger = setup_logger("VODListWidget")


class VODListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(
            QtCore.QSize(100, 56)
        )  # Define o tamanho do ícone das miniaturas
        logger.debug("VODListWidget inicializado.")

    def populate_vods(self, vods):
        """
        Popula a lista de VODs de forma assíncrona.

        :param vods: Lista de dicionários contendo 'title', 'link' e 'thumbnail'
        """
        asyncio.create_task(self.async_populate_vods(vods))

    async def async_populate_vods(self, vods):
        logger.debug("Populando a lista de VODs.")
        self.clear()
        for vod in vods:
            await asyncio.sleep(0)  # Yield para manter a interface responsiva
            item = QListWidgetItem()
            item.setText(vod["title"])
            item.setData(
                QtCore.Qt.UserRole, vod["link"]
            )  # Armazena o link do VOD no dado do item
            if vod["thumbnail"]:
                try:
                    # Se o thumbnail for uma URL, você pode baixar a imagem ou usar diretamente se suportado
                    item.setIcon(QIcon(vod["thumbnail"]))
                except Exception as e:
                    logger.warning(
                        f"Falha ao definir o ícone para o VOD '{vod['title']}': {e}"
                    )
            else:
                # Opcional: Definir um ícone padrão se não houver miniatura
                item.setIcon(QIcon("resources/icons/default_thumbnail.png"))
            self.addItem(item)
        logger.info(f"{len(vods)} VODs adicionados à lista.")
