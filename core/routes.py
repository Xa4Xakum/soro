from server.types import IncomingMessage, OutgoingMessage
from server.router import Router
from server.client import ClientHandler

r = Router()


# Регистрация маршрутов и функций
@r.route("echo")
async def echo_handler(message: IncomingMessage, client: ClientHandler):
    """Пример маршрута echo"""
    await client.send_response(
        OutgoingMessage(
            type='echo',
            data=message.data,
            uid=message.uid
        )
    )
