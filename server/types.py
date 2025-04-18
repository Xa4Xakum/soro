from typing import Optional
from pydantic import BaseModel


class IncomingMessage(BaseModel):
    """Класс для представления входящего сообщения от клиента."""
    path: str
    data: Optional[dict | str] = None
    uid: Optional[str] = None


class OutgoingMessage(BaseModel):
    """Класс для представления исходящего сообщения (ответа от сервера)."""
    type: str = 'unexpected'
    data: Optional[dict | str] = 'success'
    uid: Optional[str] = None


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
