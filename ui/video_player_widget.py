# ui/video_player_widget.py

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore
import vlc
from utils.logger import setup_logger
import sys
import os
import asyncio

# Configuração do logger
logger = setup_logger("VideoPlayerWidget")


class VideoPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Inicializando VideoPlayerWidget.")
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Integrar o player com o widget
        try:
            if sys.platform.startswith("linux"):  # para Linux usando X Server
                self.player.set_xwindow(self.winId())
            elif sys.platform == "win32":  # para Windows
                self.player.set_hwnd(self.winId())
            elif sys.platform == "darwin":  # para MacOS
                self.player.set_nsobject(int(self.winId()))
            else:
                logger.error(
                    "Sistema operacional não suportado para integração com VLC."
                )
        except Exception as e:
            logger.exception(f"Erro ao configurar o video output: {e}")

        logger.debug("VideoPlayerWidget configurado com sucesso.")

        # Adicionar event manager para capturar eventos de VLC
        self.events = self.player.event_manager()
        self.events.event_attach(
            vlc.EventType.MediaPlayerEncounteredError, self.handle_error
        )
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.handle_end)

        # Inicializar variáveis para gerenciamento de tarefas
        self.check_state_task = None
        self._stop_flag = False

    def play(self, media_path):
        logger.info(f"Reproduzindo mídia: {media_path}")
        # Cancelar qualquer reprodução anterior antes de iniciar uma nova
        self.stop()
        self.check_state_task = asyncio.create_task(self.async_play(media_path))

    async def async_play(self, media_path):
        try:
            if not os.path.exists(media_path):
                logger.error(f"O arquivo de mídia não existe: {media_path}")
                return

            media = self.instance.media_new(media_path)
            self.player.set_media(media)
            self.player.play()
            logger.debug("Mídia iniciada com sucesso.")

            # Verificar se o player está realmente reproduzindo
            await asyncio.sleep(1)  # Aguarda um tempo para iniciar a reprodução
            state = self.player.get_state()
            logger.debug(f"Estado inicial do player após play(): {state}")

            # Adicionar verificação periódica do estado do player
            self.check_state_task = asyncio.create_task(self.check_player_state())
        except Exception as e:
            logger.exception(f"Erro ao reproduzir mídia '{media_path}': {e}")

    async def check_player_state(self):
        try:
            while not self._stop_flag:
                await asyncio.sleep(
                    5
                )  # Espera alguns segundos antes de verificar o estado
                state = self.player.get_state()
                logger.debug(f"Estado do player após 5 segundos: {state}")
                if state == vlc.State.Error:
                    logger.error(
                        "Erro detectado no player após tentativa de reprodução."
                    )
                elif state == vlc.State.Ended:
                    logger.info("Reprodução da mídia encerrada.")
                elif state == vlc.State.Playing:
                    logger.debug("Mídia está sendo reproduzida.")
                else:
                    logger.warning(f"Estado inesperado do player: {state}")
        except asyncio.CancelledError:
            logger.debug("Tarefa check_player_state cancelada.")
        except Exception as e:
            logger.exception(f"Erro na tarefa check_player_state: {e}")

    def stop(self):
        """
        Método para parar a reprodução e cancelar tarefas assíncronas relacionadas.
        """
        if self.player.is_playing():
            self.player.stop()
            logger.info("Playback interrompido.")

        # Sinalizar para a tarefa de verificação de estado que deve parar
        self._stop_flag = True

        # Cancelar a tarefa de verificação de estado, se existir
        if self.check_state_task and not self.check_state_task.done():
            self.check_state_task.cancel()
            logger.debug("Tarefa check_player_state foi cancelada.")

    def handle_error(self, event):
        logger.error("Erro encontrado durante a reprodução da mídia.")
        # Opcional: Implementar diálogo ou notificação na UI

    def handle_end(self, event):
        logger.info("Reprodução da mídia encerrada.")
        # Opcional: Resetar o player ou atualizar a UI
