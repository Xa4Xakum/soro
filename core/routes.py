from loguru import logger
from framework.types import IncomingMessage, OutgoingMessage
from websockets import ClientConnection
from server import server, obs
import traceback


# Регистрация маршрутов и функций
@server.route("echo")
async def echo_handler(message: IncomingMessage, socket: ClientConnection):
    """Пример маршрута echo"""
    logger.info(f"Echo route called with method: {message.path} with event_type: {message.event_type} and data: {message.data}")
    await server.send_response(
        socket,
        OutgoingMessage(
            data={"message": f"uuid={message.uid} path={message.path} event_type={message.event_type} data={message.data}"}
        )
    )


@server.route("subscribe")
async def subscribe(message: IncomingMessage, socket: ClientConnection):
    obs.subscribe(socket, message.event_type)
    await server.send_response(socket, OutgoingMessage(uid=message.uid))


@server.route("unsubscribe")
async def unsubscribe(message: IncomingMessage, socket: ClientConnection):
    obs.unsubscribe(socket, message.event_type)
    await server.send_response(socket, OutgoingMessage(uid=message.uid))


# @server.route('mail')
# async def mail(message: IncomingMessage, socket: ClientConnection):
#     clis = server.clients


@server.route('notify')
async def notify(message: IncomingMessage, socket: ClientConnection):
    await server.send_response(socket, OutgoingMessage(data='started', uid=message.uid))
    logger.debug('started')
    results = await obs.notify(server, message.event_type, message.data)
    errors = []
    if results:
        for result in results:
            if isinstance(result, Exception):
                errors.append(result.__str__())
                stack_trace = traceback.format_exc()  # Получаем полный стек вызовов
                caller_info = traceback.extract_stack(limit=3)[0]  # Информация о месте вызова функции
                error_origin = traceback.extract_stack(limit=3)[-2]  # Откуда вызвали проблемную функцию

                logger.error(
                    f"Ошибка: {repr(Exception)}\n"
                    f"(файл: {caller_info.filename}, строка: {caller_info.lineno})\n"
                    f"Функция вызвана из '{error_origin.name}' "
                    f"(файл: {error_origin.filename}, строка: {error_origin.lineno})\n"
                    f"Трассировка стека:\n{stack_trace}"
                )
    await server.send_response(socket, OutgoingMessage(data={'errors': errors}, uid=message.uid))
