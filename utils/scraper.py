# utils/scraper.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from utils.logger import setup_logger
import time

# Configuração do logger
logger = setup_logger('Scraper')

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
            return realizar_scraping(streamer_name)
        except Exception as e:
            logger.exception(f"Erro na tentativa {attempt} para scraping: {e}")
            time.sleep(5)  # Aguarda antes de tentar novamente

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
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url)
        logger.debug("Página de pesquisa carregada.")

        # Aguardar até que os elementos de canal estejam presentes
        try:
            page.wait_for_selector("a[href*='/channels/@']", timeout=10000)
            logger.debug("Elementos de canal encontrados na página de pesquisa.")
        except:
            logger.warning("Tempo limite atingido ao aguardar os elementos de canal na página de pesquisa.")
            browser.close()
            return []

        # Obter o HTML da página de pesquisa
        search_page_html = page.content()
        logger.debug("Obtido HTML da página de pesquisa.")
        browser.close()

    # Passo 2: Extrair o link do canal
    try:
        search_soup = BeautifulSoup(search_page_html, 'html.parser')
        channel_link_tag = search_soup.find('a', href=lambda href: href and "/channels/@" in href)
        if not channel_link_tag:
            logger.warning(f"Nenhum canal encontrado para o streamer '{streamer_name}'.")
            return []
        channel_url = f"https://vodvod.top{channel_link_tag['href']}"
        logger.info(f"Encontrado canal: {channel_url}")
    except Exception as e:
        logger.exception(f"Erro ao extrair o link do canal na página de pesquisa: {e}")
        return []

    # Passo 3: Acessar a página do canal e extrair os VODs
    logger.debug(f"Acessando página do canal: {channel_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(channel_url)
        logger.debug("Página do canal carregada.")

        # Aguardar até que os VODs estejam presentes
        try:
            page.wait_for_selector("div.vod-item", timeout=10000)
            logger.debug("Elementos de VOD encontrados na página do canal.")
        except:
            logger.warning("Tempo limite atingido ao aguardar os elementos de VOD na página do canal.")
            browser.close()
            return []

        # Obter o HTML da página do canal
        channel_page_html = page.content()
        logger.debug("Obtido HTML da página do canal.")
        browser.close()

    # Analisar a página do canal para extrair os VODs
    try:
        channel_soup = BeautifulSoup(channel_page_html, 'html.parser')
        vods = []
        for vod in channel_soup.find_all('div', class_='vod-item'):
            title_tag = vod.find('h3')
            link_tag = vod.find('a', href=True)
            thumbnail_tag = vod.find('img', src=True)
            if not title_tag or not link_tag:
                logger.debug("VOD sem título ou link encontrado. Ignorando.")
                continue
            title = title_tag.get_text(strip=True)
            link = f"https://vodvod.top{link_tag['href']}"
            thumbnail = thumbnail_tag['src'] if thumbnail_tag else None
            vods.append({
                'title': title,
                'link': link,
                'thumbnail': thumbnail
            })
        logger.info(f"Encontrados {len(vods)} VODs na página do canal.")
        return vods
    except Exception as e:
        logger.exception(f"Erro ao processar o conteúdo da página do canal: {e}")
        return []