# utils/performance_monitor.py

import time
import asyncio
import functools
from utils.logger import setup_logger

logger = setup_logger("PerformanceMonitor")


def async_timeit(func):
    """
    Decorador para medir o tempo de execução de funções assíncronas.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            logger.info(
                f"Função '{func.__name__}' executada em {elapsed:.4f} segundos."
            )

    return wrapper


def timeit_sync(func):
    """
    Decorador para medir o tempo de execução de funções síncronas.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            logger.info(
                f"Função '{func.__name__}' executada em {elapsed:.4f} segundos."
            )

    return wrapper
