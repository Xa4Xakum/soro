from collections import defaultdict
from typing import Callable


class Router:
    def __init__(self):
        self.routes = defaultdict(dict)

    def route(self, path: str):
        def decorator(func: Callable):
            self.routes[path] = func
            return func
        return decorator

    def get_handler(self, path: str):
        return self.routes.get(path)
