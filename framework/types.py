from typing import Optional
from pydantic import BaseModel


class IncomingMessage(BaseModel):
    """Класс для представления входящего сообщения от клиента."""
    path: str  # Обозначение метода, который нужно выполнить
    event_type: str  # тип_ивента
    data: Optional[dict | str] = None  # Данные ответа (например, {"message": "success"})
    uid: Optional[str] = None  # чтобы различить можно было


class OutgoingMessage(BaseModel):
    """Класс для представления исходящего сообщения (ответа от сервера)."""
    statuscode: int = 200  # HTTP-статус код (например, 200)
    data: Optional[dict | str] = 'success'  # Данные ответа (например, {"message": "success"})
    uid: Optional[str] = None  # чтобы различить можно было


class EventMessage(BaseModel):
    """Класс для представления исходящего сообщения (сообщения от сервера)."""
    event_type: str  # HTTP-статус код (например, 200)
    data: Optional[dict | str]  # данные от одного из подключений


class IncomingMessageException(Exception):
    def __init__(self, status_code: int, error: dict | str, uid: str = None):
        self.status_code = status_code
        self.error = error
        self.uid = uid

    def __str__(self):
        return (
            f'IncomingMessageException('
            f'status_code={self.status_code}, '
            f'error={self.error}, '
            f'uid={self.uid})'
        )
