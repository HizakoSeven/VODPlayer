# utils/downloader.py

import requests
import os
from utils.logger import setup_logger

# Configuração do logger
logger = setup_logger('Downloader')

def download_m3u8(vod_link, cache_dir):
    logger.info(f"Iniciando download do arquivo .m3u8: {vod_link}")
    try:
        response = requests.get(vod_link, stream=True, timeout=10)
        response.raise_for_status()
        logger.debug(f"Resposta HTTP para o download recebida com status code {response.status_code}.")
    except requests.RequestException as e:
        logger.exception(f"Erro ao baixar o arquivo .m3u8 de '{vod_link}': {e}")
        raise

    filename = os.path.basename(vod_link)
    filepath = os.path.join(cache_dir, filename)

    try:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"Arquivo .m3u8 salvo em: {filepath}")
        return filepath
    except Exception as e:
        logger.exception(f"Erro ao salvar o arquivo .m3u8 em '{filepath}': {e}")
        raise
