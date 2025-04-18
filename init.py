from server.server import WebSocketServer
from chat_manage.observer import Observer

from config import conf

obs = Observer()
server = WebSocketServer(
    host=conf.host,
    port=conf.port,
)
