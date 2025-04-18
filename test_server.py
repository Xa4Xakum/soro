import asyncio
from loguru import logger
from misc import set_loggers
from time import perf_counter
from init import server, obs
from server.types import IncomingMessage
from websockets import ClientConnection
from server.client import ClientHandler
from core import routes


@server.middleware
async def log_request(message: IncomingMessage, call_next: callable, client: ClientHandler):
    start_time = perf_counter()
    host = f'{client.websocket.remote_address[0]}:{client.websocket.remote_address[1]}'
    logger.info(f"Получено {message.path} {message.uid} от {host}")
    response = await call_next(message, client)
    logger.info(
        f"Обработано {message.path} {message.uid} от {host} за {round(perf_counter() - start_time, 3)} секунд"
    )
    return response


@server.on_connect
async def on_connect(websocket: ClientConnection):
    """Обработка подключения"""
    address = websocket.remote_address
    logger.info(f"New connection from {address[0]}:{address[1]}")


@server.on_disconnect
async def on_disconnect(websocket: ClientConnection):
    """Обработка отключения"""
    address = websocket.remote_address
    obs.remove(websocket)
    logger.info(f"Connection closed from {address[0]}:{address[1]}")



async def on_startup():
    set_loggers()
    logger.info('server started')


if __name__ == "__main__":
    server.add_router(routes.r)
    asyncio.run(server.run(on_startup=on_startup()))
