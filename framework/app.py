import asyncio
from datetime import datetime
import traceback
import json
import websockets
from loguru import logger
from websockets import ClientConnection
from framework.types import IncomingMessage, OutgoingMessage, EventMessage, IncomingMessageException
from collections import defaultdict
from time import perf_counter
from typing import Callable, Awaitable, Coroutine, List


class WebSocketFramework:
    def __init__(
            self,
            host='localhost',
            port=8765,
            ping_timeout: int = 20,
            ping_interval: int = 5
    ):
        self.host = host
        self.port = port
        self.ping_timeout = ping_timeout
        self.ping_interval = ping_interval
        self.routes = defaultdict(dict)
        self.middlewares = []
        self.flood: dict[ClientConnection, int] = {}
        self.clients: dict[ClientConnection, float] = {}  # клиент: прошедшее время с последнего понга
        self.pings: dict[ClientConnection, List[float]] = {}
        self._global_ping_task = None
        self.auth_handler = None
        self.process_request_handler = None  # Для хранения пользовательского обработчика


    def process_request(self, func: Callable):
        """Регистрирует пользовательскую функцию для обработки запроса."""
        self.process_request_handler = func
        return func

    def middleware(self, func: Callable):
        """Регистрирует middleware-функцию"""
        self.middlewares.append(func)
        return func

    def route(self, path: str):
        def decorator(func: Callable):
            self.routes[path] = func
            return func
        return decorator

    def on_connect(self, func): self.on_connect_handler = func; return func
    def on_disconnect(self, func): self.on_disconnect_handler = func; return func
    def on_auth(self, func: Callable[[str, str], bool | Awaitable[bool]]): self.auth_handler = func; return func

    async def process_connect(self, websocket: ClientConnection):
        self.clients[websocket] = perf_counter()
        self.pings[websocket] = []
        self.flood[websocket] = 0
        await self.on_connect_handler(websocket)

    async def receive_raw_message(self, websocket: ClientConnection):
        return await asyncio.wait_for(websocket.recv(), timeout=None)

    async def handle_ping_pong(self, raw: str, websocket: ClientConnection) -> bool:
        """Обработка ping/pong. Возвращает True, если ответ уже отправлен и обработка завершена."""
        lower = raw.lower()
        if lower == 'ping':
            await websocket.send('pong')
            return True

        elif lower == 'pong':
            logger
            now = perf_counter()
            if len(self.pings[websocket]) == 0:
                if self.flood[websocket] > 30:
                    await self.send_response(
                        websocket,
                        OutgoingMessage(
                            403,
                            'to much pongs stop it, please'
                        )
                    )

                logger.warning(f'socket {websocket.remote_address[0]}:{websocket.remote_address[1]} too much pongs')
                self.flood[websocket] += 1
                raise IncomingMessageException(400, 'to much pongs stop it, please')

            pong_at = self.pings[websocket].pop(0)
            delta = round(now - pong_at, 3)
            lag = str(delta * 1000) + 'ms' if delta <= 1 else str(delta) + 's'

            logger.debug(
                f'{websocket.remote_address[0]}:{websocket.remote_address[1]} - {lag}'
            )
            self.clients[websocket] = now

            return True
        return False

    def is_valid_json(self, string: str) -> bool:
        try:
            json.loads(string)
            return True
        except json.JSONDecodeError:
            return False

    def parse_message(self, raw: str) -> IncomingMessage:
        if not self.is_valid_json(raw):
            raise IncomingMessageException(400, 'Message must be a valid json string')
        data = json.loads(raw)
        msg = IncomingMessage(**data)
        return msg

    async def handle_message(self, message: IncomingMessage, *args, **kwargs) -> OutgoingMessage:
        async def actual_handler(msg: IncomingMessage, *args, **kwargs) -> OutgoingMessage:
            if msg.path in self.routes:
                handler = self.routes[msg.path]
                return await handler(msg, *args, **kwargs)
            return OutgoingMessage(statuscode=404, data="Path not found")

        handler_chain = self._build_middleware_chain(actual_handler, *args, **kwargs)
        return await handler_chain(message, *args, **kwargs)

    async def send_response(self, websocket: ClientConnection, response: OutgoingMessage | EventMessage):
        await websocket.send(
            json.dumps(
                response.model_dump(),
                ensure_ascii=False
            )
        )

    def _build_middleware_chain(self, handler, *args, **kwargs):
        """Рекурсивно оборачивает handler всеми middleware"""
        async def call_next_wrapper(message, middlewares, *args, **kwargs):
            if not middlewares:
                return await handler(message, *args, **kwargs)  # Здесь передаем message и ws
            current = middlewares[0]

            # Переход к следующей мидлваре
            async def call_next(msg, *args, **kwargs):
                return await call_next_wrapper(msg, middlewares[1:], *args, **kwargs)

            return await current(message, call_next, *args, **kwargs)  # Передаем message и websocket в current

        # Возвращаем лямбду, которая принимает только один аргумент — message
        return lambda msg, *args, **kwargs: call_next_wrapper(msg, self.middlewares, *args, **kwargs)


    async def process_disconnect(self, websocket: ClientConnection):
        await self.on_disconnect_handler(websocket)
        if websocket in self.clients: del self.clients[websocket]
        if websocket in self.pings: del self.pings[websocket]
        if websocket in self.flood: del self.flood[websocket]


    def run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


    async def process_event(self, websocket: ClientConnection):
        try:
            raw = await self.receive_raw_message(websocket)
            logger.debug(raw)
            if await self.handle_ping_pong(raw, websocket):
                return

            message = self.parse_message(raw)
            result = await self.handle_message(message, websocket)

            if isinstance(result, OutgoingMessage):
                await self.send_response(websocket, result)

        except json.JSONDecodeError:
            await self.send_response(websocket, OutgoingMessage(
                statuscode=400,
                data={"error": f"Invalid JSON format: {raw}"}
            ))
        except IncomingMessageException as e:
            logger.warning(f'idiot user with error {e}')
            await self.send_response(websocket, OutgoingMessage(
                statuscode=e.status_code,
                data={"error": e.error}
            ))


    async def connect(self, websocket: ClientConnection):
        await self.process_connect(websocket)
        while True:
            try:
                await self.process_event(websocket)

            except websockets.ConnectionClosed:
                await self.process_disconnect(websocket)
                break

            except Exception as e:
                error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # таймштамп, чтобы найти в логах
                stack_trace = traceback.format_exc()  # Получаем полный стек вызовов
                caller_info = traceback.extract_stack(limit=3)[0]  # Информация о месте вызова функции
                error_origin = traceback.extract_stack(limit=3)[-2]  # Откуда вызвали проблемную функцию

                logger.error(
                    f"Ошибка: {repr(e)}\n"
                    f"(файл: {caller_info.filename}, строка: {caller_info.lineno})\n"
                    f"Функция вызвана из '{error_origin.name}' "
                    f"(файл: {error_origin.filename}, строка: {error_origin.lineno})\n"
                    f"Трассировка стека:\n{stack_trace}"
                )

                await self.send_response(websocket, OutgoingMessage(
                    statuscode=500,
                    data={"error": f"При обработке входящего запроса в {error_time} произошла ошибка: {str(e)}"}
                ))


    async def global_ping_loop(self):
        while True:
            await asyncio.sleep(self.ping_interval)

            for websocket in list(self.clients.keys()):
                try:
                    now = perf_counter()
                    self.pings[websocket].append(now)
                    if self.flood[websocket] > 0:
                        self.flood[websocket] -= 1

                    await self.send_response(
                        websocket,
                        EventMessage(
                            event_type='check_health',
                            data='ping'
                        )
                    )
                    if now - self.clients[websocket] >= self.ping_timeout:
                        logger.warning(f"Client {websocket.remote_address[0]}:{websocket.remote_address[1]} timed out.")
                        await websocket.close()

                except websockets.ConnectionClosed:
                    await websocket.close()
                except Exception as e:
                    logger.warning(f"Ping failed for {websocket.ping}: {e}")

    async def run(self, on_startup: Coroutine):
        await on_startup
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        asyncio.create_task(self.global_ping_loop())
        server = await websockets.serve(self.connect, self.host, self.port, process_request=self.process_request_handler)
        await server.serve_forever()
