from loguru import logger
from websockets import ClientConnection
from server import server, obs


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
