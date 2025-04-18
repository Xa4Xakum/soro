import json
import traceback
from loguru import logger
from websockets import ConnectionClosed
from server.types import OutgoingMessage, IncomingMessageException, IncomingMessage


class ClientHandler:
    def __init__(self, websocket, server):
        self.websocket = websocket
        self.server = server

    async def handle(self):
        await self.server.on_connect_handler(self.websocket)

        try:
            async for raw in self.websocket:
                await self.process_event(raw)
        except ConnectionClosed:
            pass
        finally:
            await self.server.on_disconnect_handler(self.websocket)

    async def process_event(self, raw: str):
        try:
            message = IncomingMessage.model_validate(json.loads(raw))
            handler = self.server.router.get_handler(message.path)

            if handler:
                chain = self.server.middleware.build_chain(handler)
                await chain(message, self)
            else:
                response = OutgoingMessage(type='Error', data="Path not found")
                await self.send_response(response)

        except IncomingMessageException as e:
            logger.warning(f'Invalid message: {e}')
            await self.send_response(OutgoingMessage(type='Error', data=e.error))
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Unexpected error: {e}\n{stack_trace}")
            await self.send_response(OutgoingMessage(
                type='Error',
                data=str(e)
            ))

    async def send_response(self, response: OutgoingMessage):
        try:
            await self.websocket.send(json.dumps(response.model_dump(), ensure_ascii=False))
        except ConnectionClosed:
            logger.warning('Connection closed while trying to send message')
