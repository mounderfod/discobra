import asyncio
from types import NoneType
from typing import Coroutine

class EventEmitter():
    def __init__(self):
        self.listeners = {}

    def add_listener(self, event_name: str, func: Coroutine):
        if not self.listeners.get(event_name, None):
            self.listeners[event_name] = {func}
        else:
            self.listeners[event_name].add(func)

    def remove_listener(self, event_name: str, func: Coroutine):
        self.listeners[event_name].remove(func)
        if len(self.listeners[event_name]) == 0:
            del self.listeners[event_name]

    def emit(self, event_name: str, args_required=False, *args, **kwargs):
        listeners = self.listeners.get(event_name, [])
        for func in listeners:
            if args_required:
                if len(args) == 0:
                    raise TypeError('event registered must have arguments')
                else:
                    asyncio.create_task(func(*args, **kwargs))
            else:
                asyncio.create_task(func(*args, **kwargs))
