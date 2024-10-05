# utils/downloader.py

import asyncio
import os
import aiohttp
from utils.logger import setup_logger

# Configuração do logger
logger = setup_logger("Downloader")


async def download_m3u8(vod_link, cache_dir):
    """
    Baixa o arquivo .m3u8 de forma assíncrona e o salva no diretório de cache.

    :param vod_link: Link do arquivo .m3u8 a ser baixado.
    :param cache_dir: Diretório de cache onde o arquivo será salvo.
    :return: Caminho do arquivo baixado.
    """
    logger.info(f"Iniciando download do arquivo .m3u8: {vod_link}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(vod_link, timeout=10) as response:
                response.raise_for_status()
                logger.debug(
                    f"Resposta HTTP para o download recebida com status code {response.status}"
                )

                filename = os.path.basename(vod_link)
                if not filename:
                    logger.warning(
                        f"Não foi possível determinar o nome do arquivo a partir da URL: {vod_link}"
                    )
                    filename = f"download_{int(asyncio.get_event_loop().time())}.m3u8"
                filepath = os.path.join(cache_dir, filename)
                os.makedirs(cache_dir, exist_ok=True)

                with open(filepath, "wb") as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

                logger.info(f"Arquivo .m3u8 salvo em: {filepath}")
                return filepath
    except aiohttp.ClientError as e:
        logger.exception(f"Erro ao baixar o arquivo .m3u8 de '{vod_link}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Erro ao salvar o arquivo .m3u8 de '{vod_link}': {e}")
        raise
