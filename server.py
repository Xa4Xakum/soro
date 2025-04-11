from framework.app import WebSocketFramework
from chat_manage.observer import Observer

obs = Observer()
server = WebSocketFramework(
    host='192.168.117.137',
    port=8002,
    ping_interval=10
)
