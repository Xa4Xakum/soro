from websockets import ClientConnection
import asyncio

from framework.types import EventMessage
from framework.app import WebSocketFramework


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


    async def notify(self, server: WebSocketFramework, event_type: str, event: dict):
        """Уведомляем всех подписчиков о событии."""
        # Создаем задачи для всех подписчиков, которых нужно уведомить
        tasks = []
        for socket, subscriptions in self.clients.items():
            if event_type in subscriptions:
                tasks.append(
                    server.send_response(
                        socket,
                        EventMessage(
                            event_type=event_type,
                            data=event
                        )
                    )
                )
        result = await asyncio.gather(*tasks, return_exceptions=True)
        return result
