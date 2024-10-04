# utils/scraper.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from utils.logger import setup_logger
import re
import time
import threading
import random
import logging

# Configuração do logger
logger = setup_logger('Scraper')

# Adiciona um FileHandler com codificação UTF-8 para suportar caracteres especiais
file_handler = logging.FileHandler('scraper.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def scrape_vods_async(streamer_name, callback, retries=3):
    """
    Realiza scraping dos VODs de um streamer específico de forma assíncrona.

    :param streamer_name: Nome do streamer a ser pesquisado.
    :param callback: Função de callback a ser chamada com os resultados do scraping.
    :param retries: Número de tentativas em caso de falha.
    """
    def run_scraper():
        logger.debug(f"Iniciando scraping assíncrono para o streamer '{streamer_name}'.")
        result = scrape_vods(streamer_name, retries)
        logger.debug(f"Scraping assíncrono concluído para o streamer '{streamer_name}'. Chamando callback.")
        callback(result)
    
    # Cria um thread daemon para executar o scraping em segundo plano
    thread = threading.Thread(target=run_scraper, daemon=True)
    logger.debug("Iniciando thread para scraping assíncrono.")
    thread.start()

def scrape_vods(streamer_name, retries=3):
    """
    Realiza scraping dos VODs de um streamer específico no site vodvod.top.

    :param streamer_name: Nome do streamer a ser pesquisado.
    :param retries: Número de tentativas em caso de falha.
    :return: Lista de dicionários com informações dos VODs.
    """
    for attempt in range(1, retries + 1):
        logger.info(f"Tentativa {attempt} de {retries} para scraping do streamer '{streamer_name}'.")
        try:
            # Tenta realizar o scraping
            result = realizar_scraping(streamer_name)
            logger.debug(f"Scraping realizado com sucesso para o streamer '{streamer_name}' na tentativa {attempt}.")
            return result
        except Exception as e:
            # Captura qualquer exceção e faz uma nova tentativa após um tempo de espera
            logger.exception(f"Erro na tentativa {attempt} para scraping: {e}")
            sleep_time = random.uniform(1, 5) * (2 ** (attempt - 1))  # Estratégia de backoff exponencial
            logger.info(f"Aguardando {sleep_time:.2f} segundos antes de tentar novamente.")
            time.sleep(sleep_time)  # Aguarda antes de tentar novamente

    # Se todas as tentativas falharem, registra um erro
    logger.error(f"Falha ao realizar scraping para o streamer '{streamer_name}' após {retries} tentativas.")
    return []

def realizar_scraping(streamer_name):
    """
    Realiza o processo de scraping para um streamer específico.

    :param streamer_name: Nome do streamer a ser pesquisado.
    :return: Lista de dicionários com informações dos VODs.
    """
    logger.info(f"Iniciando scraping para o streamer: '{streamer_name}'.")
    search_url = f"https://vodvod.top/search/{streamer_name}"
    logger.debug(f"Acessando URL de pesquisa: {search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Inicia o navegador em modo headless
        page = browser.new_page()
        try:
            page.goto(search_url)  # Navega até a URL de pesquisa
            logger.debug("Página de pesquisa carregada.")

            # Aguardar até que os elementos de canal estejam presentes
            page.wait_for_selector("a[href*='/channels/@']", timeout=10000)
            logger.debug("Elementos de canal encontrados na página de pesquisa.")

            # Obter o HTML da página de pesquisa
            search_page_html = page.content()
            logger.debug("Obtido HTML da página de pesquisa.")
        except PlaywrightTimeoutError:
            # Trata o caso de tempo limite ao esperar pelos elementos
            logger.warning("Tempo limite atingido ao aguardar os elementos de canal na página de pesquisa.")
            return []
        except Exception as e:
            # Captura qualquer outra exceção durante a navegação
            logger.exception(f"Erro inesperado ao aguardar os elementos de canal: {e}")
            return []
        finally:
            # Garante que o navegador será fechado
            logger.debug("Fechando o navegador após a busca pelo canal.")
            browser.close()

    # Passo 2: Extrair o link do canal
    try:
        logger.debug("Iniciando extração do link do canal.")
        search_soup = BeautifulSoup(search_page_html, 'html.parser')  # Analisa o HTML da página de pesquisa
        channel_link_tag = search_soup.find('a', href=lambda href: href and "/channels/@" in href)
        if not channel_link_tag:
            # Se nenhum canal for encontrado, registra um aviso
            logger.warning(f"Nenhum canal encontrado para o streamer '{streamer_name}'.")
            return []
        channel_url = f"https://vodvod.top{channel_link_tag['href']}"
        logger.info(f"Encontrado canal: {channel_url}")
    except Exception as e:
        # Captura qualquer exceção durante a extração do link do canal
        logger.exception(f"Erro ao extrair o link do canal na página de pesquisa: {e}")
        return []

    # Passo 3: Acessar a página do canal e extrair os VODs
    logger.debug(f"Acessando página do canal: {channel_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Inicia o navegador em modo headless
        page = browser.new_page()
        try:
            page.goto(channel_url)  # Navega até a página do canal
            logger.debug("Página do canal carregada.")

            # Aguardar até que os VODs estejam presentes
            page.wait_for_selector("a[href*='.m3u8']", timeout=10000)
            logger.debug("Elementos de VOD encontrados na página do canal.")

            # Obter o HTML da página do canal
            channel_page_html = page.content()
            logger.debug("Obtido HTML da página do canal.")
        except PlaywrightTimeoutError:
            # Trata o caso de tempo limite ao esperar pelos VODs
            logger.warning("Tempo limite atingido ao aguardar os elementos de VOD na página do canal.")
            return []
        except Exception as e:
            # Captura qualquer outra exceção durante a navegação
            logger.exception(f"Erro inesperado ao aguardar os elementos de VOD: {e}")
            return []
        finally:
            # Garante que o navegador será fechado
            logger.debug("Fechando o navegador após acessar a página do canal.")
            browser.close()

    # Analisar a página do canal para extrair os VODs
    try:
        logger.debug("Iniciando análise do HTML da página do canal.")
        channel_soup = BeautifulSoup(channel_page_html, 'html.parser')  # Analisa o HTML da página do canal
        vods = {}  # Dicionário para armazenar VODs únicos

        # Encontrar todos os links que correspondem ao padrão .m3u8
        m3u8_links = channel_soup.find_all('a', href=re.compile(r'https://api\.vodvod\.top/m3u8/\d+/\d+/index\.m3u8'))
        logger.debug(f"Encontrados {len(m3u8_links)} links de VOD.")

        for link in m3u8_links:
            href = link['href']
            title = link.get_text(strip=True) or "Sem Título"  # Extrai o título do VOD ou define como 'Sem Título'
            vods[href] = {
                'title': title,
                'link': href,
                'thumbnail': None  # Atualize se as miniaturas puderem ser extraídas
            }
            logger.debug(f"Adicionado VOD: {title}, URL: {href}")

        vod_list = list(vods.values())  # Converte o dicionário de VODs em uma lista
        logger.info(f"Encontrados {len(vod_list)} VODs na página do canal.")
        return vod_list
    except Exception as e:
        # Captura qualquer exceção durante a análise da página do canal
        logger.exception(f"Erro ao processar o conteúdo da página do canal: {e}")
        return []