import asyncio
import json
import sys
import threading
import warnings
from typing import Optional, Coroutine, Any, Callable
import websockets

from .utils import EventEmitter
from .utils.rest import get
from .intents import Intents, get_number
from .user import User


class Client:
    """
    Represents a Discord client (i.e. a bot).
    You need to initialise one of these and then use `run()` with a token to login.
    """
    _token: str

    @property
    async def user(self):
        """The `discord.user.User` associated with the client."""
        data = await get(self._token, '/users/@me')
        return User(data)

    def __init__(self, intents: list[Intents]):
        self.gateway = None
        self.loop = asyncio.get_event_loop()
        if Intents.MESSAGE_CONTENT in intents:
            warnings.warn("Message Content will become a privileged intent in August 2022. You must enable it in the "
                          "Discord developer portal.")
        if Intents.GUILD_MEMBERS in intents or Intents.GUILD_PRESENCES in intents:
            warnings.warn("You are using one or more privileged intent (Guild Members and/or Guild Presences). You "
                          "must enable them in the Discord developer portal.") 
        self.code = get_number(intents)
        self.event_emitter = EventEmitter()

    async def connect(self, token: str, intent_code: int):
        """
        Connects to the Discord gateway and begins sending heartbeats.
        This should not be called manually.

        **Parameters:**
        - token: Your bot token.
        - intent_code: The number which represents the `discord.intents.Intents` being used.
        """
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

        **Parameters:**
        - data: The data to send to the gateway.
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
        """
        Sends a heartbeat through the gateway to keep the connection active.
        This should not be called manually.

        **Parameters:**
        - gateway: The gateway to keep open.
        - interval: How often to send a heartbeat. This is given by the gateway in a Hello packet.
        """
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

        **Parameters:**
        - coro: The coroutine to be registered.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a coroutine function')
        self.event_emitter.add_listener(coro.__name__, coro)
        return coro

    def run(self, token: str):
        """
        Run the client.

        **Parameters:**
        - token: Your bot token. Do not share this with anyone!
        """
        self._token = token
        asyncio.run(self.connect(token, self.code))
