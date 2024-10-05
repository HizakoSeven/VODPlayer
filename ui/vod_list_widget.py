# ui/vod_list_widget.py

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore
from utils.logger import setup_logger
import asyncio
import aiohttp
import os

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
                    # Baixar a miniatura de forma assíncrona
                    pixmap = await self.download_thumbnail(vod["thumbnail"])
                    if pixmap:
                        icon = QIcon(pixmap)
                        item.setIcon(icon)
                    else:
                        # Definir ícone padrão se o download falhar
                        item.setIcon(QIcon("resources/icons/default_thumbnail.png"))
                except Exception as e:
                    logger.warning(
                        f"Falha ao definir o ícone para o VOD '{vod['title']}': {e}"
                    )
                    item.setIcon(QIcon("resources/icons/default_thumbnail.png"))
            else:
                # Definir ícone padrão se não houver miniatura
                item.setIcon(QIcon("resources/icons/default_thumbnail.png"))
            self.addItem(item)
        logger.info(f"{len(vods)} VODs adicionados à lista.")

    async def download_thumbnail(self, url):
        """
        Baixa a imagem da miniatura e retorna um QPixmap.

        :param url: URL da imagem da miniatura.
        :return: QPixmap da imagem ou None em caso de falha.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        pixmap = QPixmap()
                        if pixmap.loadFromData(image_data):
                            return pixmap
                        else:
                            logger.warning(f"Falha ao carregar QPixmap da URL: {url}")
                    else:
                        logger.warning(
                            f"Falha ao baixar miniatura. Status: {response.status}"
                        )
        except Exception as e:
            logger.exception(f"Erro ao baixar miniatura da URL {url}: {e}")
        return None
