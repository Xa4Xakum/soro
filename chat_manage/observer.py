from websockets import ClientConnection
# import asyncio

# from server.types import EventMessage, IncomingMessage
# from server.server import WebSocketServer


class Observer:
    def __init__(self):
        self.clients = {}  # Словарь с подключениями и их подписками


    def subscribe(self, websocket: ClientConnection, event_type: str):
        """Подписываем клиент на событие."""
        if websocket not in self.clients:
            self.clients[websocket] = []
        self.clients[websocket].append(event_type)


    def unsubscribe(self, websocket: ClientConnection, event_type: str):
        """Отписываем клиента от события."""
        if websocket in self.clients and event_type in self.clients[websocket]:
            self.clients[websocket].remove(event_type)


    def remove(self, socket: ClientConnection):
        '''Удалить все подписки сокета'''
        if socket in self.clients:
            del self.clients[socket]


    # async def notify(self, server: WebSocketServer, msg: IncomingMessage):
    #     """Уведомляем всех подписчиков о событии."""
    #     # Создаем задачи для всех подписчиков, которых нужно уведомить
    #     tasks = []
    #     for socket, subscriptions in self.clients.items():
    #         if msg.event_type in subscriptions:
    #             tasks.append(
    #                 server.send_response(
    #                     socket,
    #                     EventMessage(
    #                         event_type=msg.event_type,
    #                         data=msg.data,
    #                         event_uid=msg.uid
    #                     )
    #                 )
    #             )
    #     result = await asyncio.gather(*tasks, return_exceptions=True)
    #     return result
