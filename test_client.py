import asyncio
import websockets
import json


# def new_message(id: int):
#     pass

# process = {
#     'event_type': new_message
# }

# def handle(event: dict):
#     data = event['event_type'].split(' ')
#     event_type = data[0]
#     id = data[1]
#     func = process[event_type]
#     func(id)



class Requests():

    def post(self, path: str, event_type: str, data: dict):
        return {
            "path": path,  # Путь маршрута
            "event_type": event_type,
            "data": data,  # Данные, которые отправляем
        }


routes = ['echo', 'subscribe', 'unsubscribe', 'notify']


async def handle_ping(websocket):
    """Обработчик пинга от сервера"""
    while True:
        try:
            message = await websocket.recv()
            if is_valid_json(message): message = json.loads(message)
            if (
                isinstance(message, dict) and
                'data' in message and
                (not isinstance(message['data'], dict)) and
                message['data'].lower() == 'ping'
            ):
                await websocket.send('pong')
            else:
                if message != 'pong':
                    print(f">> {message}")
        except websockets.ConnectionClosed:
            break  # Выход из цикла, если соединение закрыто


async def send_ping(websocket):
    """Отправка пинга серверу каждые 5 секунд"""
    while True:
        try:
            await websocket.send('ping')
            await asyncio.sleep(5)  # Пинг каждую 5 секунд
        except websockets.ConnectionClosed:
            break  # Выход из цикла, если соединение закрыто


def is_valid_json(string: str) -> bool:
        try:
            json.loads(string)
            return True
        except json.JSONDecodeError:
            return False


async def read_console_input(websocket):
    """Чтение ввода с консоли и отправка на сервер"""
    r = Requests()
    while True:
        try:
            text = await asyncio.to_thread(input)  # Чтение ввода асинхронно

            text = text.split(maxsplit=2)
            path = text[0]
            event_type = text[1]
            data = text[2] if len(text) > 2 else None

            await websocket.send(
                json.dumps(
                    r.post(path, event_type, data)
                )
            )  # Отправляем сообщение на сервер
        except websockets.ConnectionClosed:
            break  # Если соединение закрыто, выходим из цикла
        # except Exception as e:
        #     print(f'Ошибка {e}')


async def main():
    uri = "ws://192.168.117.137:8002"

    try:
        # Подключаемся к WebSocket-серверу с дополнительными заголовками (включая авторизацию)
        async with websockets.connect(uri) as websocket:
            # Запускаем все нужные задачи
            asyncio.create_task(handle_ping(websocket))  # Обработка пингов
            asyncio.create_task(send_ping(websocket))  # Пингование сервера
            await read_console_input(websocket)  # Обработка ввода с консоли

    except Exception as e:
        print(f"Error: {e}")

# Запуск клиента
asyncio.run(main())
