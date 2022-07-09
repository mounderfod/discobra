import asyncio
import json
import sys
import threading
from typing import Optional, Coroutine, Any, Callable
import websockets

from .utils import EventEmitter
from .utils.rest import get
from .intents import Intents, get_number
from .user import User


class Client:
    _token: str

    @property
    async def user(self):
        data = await get(self._token, '/users/@me')
        return User(data)

    def __init__(self, intents: list[Intents]):
        self.gateway = None
        self.loop = asyncio.get_event_loop()
        self.code = get_number(intents)
        self.event_emitter = EventEmitter()

    async def connect(self, token: str, intent_code: int):
        async with websockets.connect("wss://gateway.discord.gg/?v=10&encoding=json") as gateway:
            hello = await gateway.recv()
            self.gateway = gateway
            threading.Thread(target=self.loop.run_forever).start()
            heartbeat = asyncio.run_coroutine_threadsafe(
                self.heartbeat(gateway, json.loads(hello)['d']['heartbeat_interval']), self.loop)
            identify = {
                "op": 2,
                "d": {
                    "token": token,
                    "intents": intent_code,
                    "properties": {
                        "os": sys.platform,
                        "browser": "discobra",
                        "device": "discobra"
                    }
                }
            }
            await gateway.send(json.dumps(identify))
            ready = await gateway.recv()
            self.event_emitter.emit('on_ready')
    
    async def send(self, data: dict):
        """
        Send data to the gateway.
        """
        await self.gateway.send(json.dumps(data))
    
    async def recv(self, msg):
        """
        Receive data from the gateway.
        """
        pass

    async def close(self):
        """
        Close the client.
        """
        self.loop.stop()
        await self.gateway.close()

    async def poll_events(self):
        pass

    async def heartbeat(self, gateway: websockets.WebSocketClientProtocol, interval: int):
        while True:
            await asyncio.sleep(interval / 1000)
            heartbeat = {
                "op": 1,
                "d": None
            }
            await gateway.send(json.dumps(heartbeat))
            ack = await gateway.recv()

    def event(self, coro: Optional[Callable[..., Coroutine[Any, Any, Any]]]=None, /) -> Optional[Callable[..., Coroutine[Any, Any, Any]]]:
        """
        Registers a coroutine to be called when an event is emitted.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a coroutine function')
        self.event_emitter.add_listener(coro.__name__, coro)
        return coro

    def run(self, token: str):
        """
        Run the client.
        """
        self._token = token
        asyncio.run(self.connect(token, self.code))
