import websockets
from websockets import ClientConnection
from loguru import logger

from server.router import Router
from server.middleware import MiddlewareManager
from server.client import ClientHandler


class WebSocketServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.router = Router()
        self.middleware = MiddlewareManager()
        self.auth_handler = None
        self.on_connect_handler = lambda ws: None
        self.on_disconnect_handler = lambda ws: None

    def on_connect(self, func): self.on_connect_handler = func; return func
    def on_disconnect(self, func): self.on_disconnect_handler = func; return func

    def add_router(self, router: Router):
        for k, v in router.routes.items():
            self.router.routes[k] = v

    async def run(self, on_startup):
        if on_startup:
            await on_startup
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        server = await websockets.serve(
            self._client_entrypoint,
            self.host,
            self.port,
        )
        await server.serve_forever()

    async def _client_entrypoint(self, websocket: ClientConnection):
        handler = ClientHandler(websocket, self)
        await handler.handle()
