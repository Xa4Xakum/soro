from typing import Callable


class MiddlewareManager:
    def __init__(self):
        self.middlewares = []

    def __call__(self, func: Callable):
        self.middlewares.append(func)
        return func

    def build_chain(self, final_handler: Callable):
        async def call_next_wrapper(message, middlewares, *args, **kwargs):
            if not middlewares:
                return await final_handler(message, *args, **kwargs)
            current = middlewares[0]

            async def call_next(msg, *args, **kwargs):
                return await call_next_wrapper(msg, middlewares[1:], *args, **kwargs)

            return await current(message, call_next, *args, **kwargs)

        return lambda msg, *args, **kwargs: call_next_wrapper(msg, self.middlewares, *args, **kwargs)
