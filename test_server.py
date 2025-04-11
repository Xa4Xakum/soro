import asyncio
from loguru import logger
from misc import set_loggers
from server import server
from core import base, middlewares, routes


async def on_startup():
    set_loggers()
    logger.info('server started')


if __name__ == "__main__":
    asyncio.run(server.run(on_startup=on_startup()))
