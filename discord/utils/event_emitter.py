import asyncio
from typing import Optional, Coroutine, Any, Callable, Dict


class EventEmitter:
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.listeners: Dict[str, Optional[Callable[..., Coroutine[Any, Any, Any]]]] = {}
        self.loop = loop if loop else asyncio.get_event_loop()

    def add_listener(self, event_name: str, func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None):
        if not self.listeners.get(event_name, None):
            self.listeners[event_name] = {func}
        else:
            self.listeners[event_name].add(func)

    def remove_listener(self, event_name: str, func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None):
        self.listeners[event_name].remove(func)
        if len(self.listeners[event_name]) == 0:
            del self.listeners[event_name]

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        listeners = self.listeners.get(event_name, [])
        for func in listeners:
            asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self.loop)
