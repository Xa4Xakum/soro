from loguru import logger
from server import server
from time import perf_counter
from framework.types import IncomingMessage


@server.middleware
async def log_request(message: IncomingMessage, call_next, socket):
    start_time = perf_counter()
    logger.info(f"Получено {message.path} {message.event_type} {message.uid}")
    response = await call_next(message, socket)
    logger.info(f"Обработано {message.path} {message.event_type} {message.uid} за {round(perf_counter() - start_time, 3)} секунд")
    return response
