# utils/scraper.py

import asyncio
import logging
import random
import re
from bs4 import BeautifulSoup
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from utils.logger import setup_logger
from utils.performance_monitor import async_timeit  # Importar o decorador

# Configuração do logger
logger = setup_logger("Scraper")


class Scraper:
    def __init__(self):
        self.playwright = None
        self.browser = None

    @async_timeit
    async def initialize(self):
        logger.info("Inicializando Playwright e lançando o navegador.")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.debug("Navegador Playwright lançado com sucesso.")

    @async_timeit
    async def close(self):
        logger.info("Fechando o navegador Playwright.")
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @async_timeit
    async def scrape_vods_async(self, streamer_name, retries=3):
        """
        Realiza scraping dos VODs de um streamer específico de forma assíncrona.

        :param streamer_name: Nome do streamer a ser pesquisado.
        :param retries: Número de tentativas em caso de falha.
        :return: Lista de dicionários com informações dos VODs.
        """
        for attempt in range(1, retries + 1):
            logger.info(
                f"Tentativa {attempt} de {retries} para scraping do streamer '{streamer_name}'."
            )
            try:
                # Tenta realizar o scraping
                result = await self.realizar_scraping(streamer_name)
                logger.debug(
                    f"Scraping realizado com sucesso para o streamer '{streamer_name}' na tentativa {attempt}."
                )
                return result
            except Exception as e:
                # Captura qualquer exceção e faz uma nova tentativa após um tempo de espera
                logger.exception(f"Erro na tentativa {attempt} para scraping: {e}")
                sleep_time = random.uniform(1, 5) * (
                    2 ** (attempt - 1)
                )  # Estratégia de backoff exponencial
                logger.info(
                    f"Aguardando {sleep_time:.2f} segundos antes de tentar novamente."
                )
                await asyncio.sleep(sleep_time)  # Aguarda antes de tentar novamente

        # Se todas as tentativas falharem, registra um erro
        logger.error(
            f"Falha ao realizar scraping para o streamer '{streamer_name}' após {retries} tentativas."
        )
        return []

    @async_timeit
    async def realizar_scraping(self, streamer_name):
        """
        Realiza o processo de scraping para um streamer específico.

        :param streamer_name: Nome do streamer a ser pesquisado.
        :return: Lista de dicionários com informações dos VODs.
        """
        logger.info(f"Iniciando scraping para o streamer: '{streamer_name}'.")
        search_url = f"https://vodvod.top/search/{streamer_name}"
        logger.debug(f"Acessando URL de pesquisa: {search_url}")

        page = await self.browser.new_page()
        try:
            await page.goto(search_url)  # Navega até a URL de pesquisa
            logger.debug("Página de pesquisa carregada.")

            # Aguardar até que os elementos de canal estejam presentes
            await page.wait_for_selector("a[href*='/channels/@']", timeout=10000)
            logger.debug("Elementos de canal encontrados na página de pesquisa.")

            # Obter o HTML da página de pesquisa
            search_page_html = await page.content()
            logger.debug("Obtido HTML da página de pesquisa.")
        except PlaywrightTimeoutError:
            # Trata o caso de tempo limite ao esperar pelos elementos
            logger.warning(
                "Tempo limite atingido ao aguardar os elementos de canal na página de pesquisa."
            )
            return []
        except Exception as e:
            # Captura qualquer outra exceção durante a navegação
            logger.exception(f"Erro inesperado ao aguardar os elementos de canal: {e}")
            return []
        finally:
            await page.close()
            logger.debug("Página de pesquisa fechada.")

        # Passo 2: Extrair o link do canal
        try:
            logger.debug("Iniciando extração do link do canal.")
            search_soup = BeautifulSoup(
                search_page_html, "html.parser"
            )  # Analisa o HTML da página de pesquisa
            channel_link_tag = search_soup.find(
                "a", href=lambda href: href and "/channels/@" in href
            )
            if not channel_link_tag:
                # Se nenhum canal for encontrado, registra um aviso
                logger.warning(
                    f"Nenhum canal encontrado para o streamer '{streamer_name}'."
                )
                return []
            channel_url = f"https://vodvod.top{channel_link_tag['href']}"
            logger.info(f"Encontrado canal: {channel_url}")
        except Exception as e:
            # Captura qualquer exceção durante a extração do link do canal
            logger.exception(
                f"Erro ao extrair o link do canal na página de pesquisa: {e}"
            )
            return []

        # Passo 3: Acessar a página do canal e extrair os VODs
        logger.debug(f"Acessando página do canal: {channel_url}")
        channel_page_html = await self._get_channel_page_html(channel_url)
        if not channel_page_html:
            return []

        # Analisar a página do canal para extrair os VODs
        try:
            logger.debug("Iniciando análise do HTML da página do canal.")
            channel_soup = BeautifulSoup(
                channel_page_html, "html.parser"
            )  # Analisa o HTML da página do canal
            vods = {}  # Dicionário para armazenar VODs únicos

            # Encontrar todos os links que correspondem ao padrão .m3u8
            m3u8_links = channel_soup.find_all(
                "a",
                href=re.compile(r"https://api\.vodvod\.top/m3u8/\d+/\d+/index\.m3u8"),
            )
            logger.debug(f"Encontrados {len(m3u8_links)} links de VOD.")

            for link in m3u8_links:
                href = link["href"]
                title = (
                    link.get_text(strip=True) or "Sem Título"
                )  # Extrai o título do VOD ou define como 'Sem Título'
                vods[href] = {
                    "title": title,
                    "link": href,
                    "thumbnail": None,  # Atualize se as miniaturas puderem ser extraídas
                }
                logger.debug(f"Adicionado VOD: {title}, URL: {href}")

            vod_list = list(vods.values())  # Converte o dicionário de VODs em uma lista
            logger.info(f"Encontrados {len(vod_list)} VODs na página do canal.")
            return vod_list
        except Exception as e:
            # Captura qualquer exceção durante a análise da página do canal
            logger.exception(f"Erro ao processar o conteúdo da página do canal: {e}")
            return []

    @async_timeit
    async def _get_channel_page_html(self, channel_url):
        """
        Navega até a página do canal e retorna o HTML.

        :param channel_url: URL da página do canal.
        :return: HTML da página do canal ou None em caso de falha.
        """
        page = await self.browser.new_page()
        try:
            await page.goto(channel_url)  # Navega até a página do canal
            logger.debug("Página do canal carregada.")

            # Aguardar até que os VODs estejam presentes
            await page.wait_for_selector("a[href*='.m3u8']", timeout=10000)
            logger.debug("Elementos de VOD encontrados na página do canal.")

            # Obter o HTML da página do canal
            channel_page_html = await page.content()
            logger.debug("Obtido HTML da página do canal.")
            return channel_page_html
        except PlaywrightTimeoutError:
            # Trata o caso de tempo limite ao esperar pelos VODs
            logger.warning(
                "Tempo limite atingido ao aguardar os elementos de VOD na página do canal."
            )
            return None
        except Exception as e:
            # Captura qualquer outra exceção durante a navegação
            logger.exception(f"Erro inesperado ao aguardar os elementos de VOD: {e}")
            return None
        finally:
            await page.close()
            logger.debug("Página do canal fechada.")
