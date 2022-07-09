import asyncio
from enum import IntEnum
import json
import sys
import threading
import warnings
from typing import Optional, Coroutine, Any, Callable
import zlib
import aiohttp
import websockets

from .utils import EventEmitter
from .utils.rest import RESTClient
from .intents import Intents, get_number
from .user import User

class GatewayEvents(IntEnum):
    DISPATCH           = 0
    HEARTBEAT          = 1
    IDENTIFY           = 2
    PRESENCE           = 3
    VOICE_STATE        = 4
    VOICE_PING         = 5
    RESUME             = 6
    RECONNECT          = 7
    REQUEST_MEMBERS    = 8
    INVALIDATE_SESSION = 9
    HELLO              = 10
    HEARTBEAT_ACK      = 11
    GUILD_SYNC         = 12

class Client:
    """
    Represents a Discord client (i.e. a bot).
    You need to initialise one of these and then use `run()` with a token to login.
    """
    _token: str

    @property
    async def user(self):
        """The `discord.user.User` associated with the client."""
        data = await self.rest_client.get(self._token, '/users/@me')
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
        self.code: int = get_number(intents)
        self.event_emitter = EventEmitter()
        self.buffer = bytearray()
        self.inflator = zlib.decompressobj()
        self.heartbeat_interval: int = None
        self.ready: bool = False
        self.rest_client = RESTClient(self._token, aiohttp.ClientSession(headers={
            "Authorization": f"Bot {self._token}",
            "User-Agent": "DiscordBot (https://github.com/mounderfod/discobra 0.0.1)"
        }))

    async def connect(self):
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
            while True:
                await self.poll_event()
    
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
        if type(msg) is bytes:
            self.buffer.extend(msg)
            if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
                return

            msg = self.inflator.decompress(self.buffer)
            msg.decode('utf-8')
            self.buffer = bytearray()
        msg = json.loads(msg)
        opcode = msg['op']
        data = msg['d']
        sequence = msg['s']

        if opcode != GatewayEvents.DISPATCH.value:
            if opcode == GatewayEvents.RECONNECT.value:
                return await self.close()

            if opcode == GatewayEvents.HELLO.value:
                self.heartbeat_interval = data['heartbeat_interval']
                asyncio.run_coroutine_threadsafe(self.heartbeat(self.heartbeat_interval), self.loop)
                return await self.identify()

            if opcode == GatewayEvents.HEARTBEAT_ACK.value:
                return await self.heartbeat(self.heartbeat_interval)

            if opcode == GatewayEvents.HEARTBEAT.value:
                return await self.heartbeat(self.heartbeat_interval)

        event = msg['t']

        if event == 'READY':
            print(data)

        self.event_emitter.emit('on_' + event.lower())


    async def close(self):
        """
        Close the client.
        """
        self.loop.stop()
        await self.gateway.close()

    async def poll_event(self):
        msg = await self.gateway.recv()
        await self.recv(msg)


    async def heartbeat(self, interval: int):
        """
        Sends a heartbeat through the gateway to keep the connection active.
        This should not be called manually.

        **Parameters:**
        - gateway: The gateway to keep open.
        - interval: How often to send a heartbeat. This is given by the gateway in a Hello packet.
        """
        await asyncio.sleep(interval / 1000)
        heartbeat = {
            "op": 1,
            "d": None
        }
        await self.gateway.send(json.dumps(heartbeat))

    async def identify(self):
        """
        Identify the client.
        """
        identify = {
            "op": GatewayEvents.IDENTIFY,
            "d": {
                "token": self._token,
                "intents": self.code,
                "properties": {
                    "os": sys.platform,
                    "browser": "discobra",
                    "device": "discobra"
                }
            }
        }

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
        asyncio.run(self.connect())
