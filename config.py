from enum import Enum

from dotenv import load_dotenv


class Config():
    '''Настройки бота'''

    def __init__(self) -> None:
        load_dotenv()


    @property
    def db_conneciton(self) -> str:
        return 'postgresql+asyncpg://sct:102938@localhost:5432/sct'

    @property
    def minio_conneciton(self) -> str:
        return f'{self.host}:9000'

    @property
    def mime_ext(self) -> dict:
        return {
            'application/pdf': 'pdf',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/png': 'png',
            'text/plain': 'txt',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
            'application/x-rar-compressed': 'rar',
            'application/zip': 'zip',
            'image/vnd.microsoft.icon': 'ico',
            'application/msword': 'doc',
        }

    @property
    def minio_login(self) -> str:
        return 'minioadmin'

    @property
    def minio_password(self) -> str:
        return 'minioadmin'

    @property
    def user_photo_folder(self) -> str:
        return 'user_photo'

    @property
    def chat_photo_folder(self) -> str:
        return 'chat_photo'

    @property
    def attachments_folder(self) -> str:
        return 'attachments'

    @property
    def bucket(self) -> str:
        return 'sct'

    @property
    def host(self) -> str:
        return '192.168.117.137'

    @property
    def port(self) -> int:
        return 8765


class UserStatuses(Enum):
    '''Пользователей'''
    online = 'Онлайн'
    deleted = 'Удален'
    offline = 'Офлайн'


conf = Config()
