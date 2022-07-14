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

from discord.guild import Guild

from .utils import EventEmitter, RESTClient
from .intents import Intents, get_number
from .user import User


class GatewayEvents(IntEnum):
    """
    Contains constants for the gateway opcodes.
    """
    DISPATCH = 0
    """An event was dispatched."""
    HEARTBEAT = 1
    """Sent at regular intervals by the client to keep the gateway connection alive."""
    IDENTIFY = 2
    """Used to identify yourself with the token during the initial handshake."""
    PRESENCE = 3
    """Used to update the client's presence."""
    VOICE_STATE = 4
    """Used to join and leave voice channels."""
    VOICE_PING = 5
    RESUME = 6
    """Used to resume a disconnected session."""
    RECONNECT = 7
    """Used to reconnect to the session."""
    REQUEST_MEMBERS = 8
    """Used to request information about guild members when there are too many for """
    INVALIDATE_SESSION = 9
    """Means that the session is invalid. When this is received, you must reconnect and re-identify."""
    HELLO = 10
    """Acknowledgement of gateway connection."""
    HEARTBEAT_ACK = 11
    """Acknowledgement of gateway heartbeat."""
    GUILD_SYNC = 12


class ClientCache:
    """
    A cache for the client.
    """
    def __init__(self):
        self.users = {}
        self._guilds = {}
        self._user: User

    def update_user(self, user: User):
        self.users[user.id] = user

    def get_user(self, id: str) -> Optional[User]:
        """
        Get a user from the cache.
        """
        return self.users.get(id)

    def get_guild(self, id: str) -> Optional[Guild]:
        """
        Get a guild from the cache.
        """
        return self._guilds.get(id)

    def update_guild(self, guild: Guild):
        self._guilds[guild.id] = guild
    
    @property
    def guilds(self) -> list:
        """
        Get a list of all guilds in the cache.
        """
        return list(self._guilds.values())
    
    @property
    def user(self) -> User:
        """The cached `discord.user.User` associated with the client."""
        return self._user

    @user.setter
    def user(self, user: User):
        self._user = user


class Client:
    """
    Represents a Discord client (i.e. a bot).
    You need to initialise one of these and then use `run()` with a token to login.
    """
    _token: str
    rest_client: RESTClient
    client_cache: ClientCache = ClientCache()

    async def user(self):
        """The `discord.user.User` associated with the client."""
        data = await self.rest_client.get('/users/@me')
        user = User(data)
        self.client_cache.user = user
        return user

    @property
    def cache(self) -> ClientCache:
        """The cache for the client."""
        return self.client_cache
    
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

    async def connect(self):
        """
        Connects to the Discord gateway and begins sending heartbeats.
        This should not be called manually.

        **Parameters:**
        - token: Your bot token.
        - intent_code: The number which represents the `discord.intents.Intents` being used.
        """
        timeout = aiohttp.ClientTimeout(total=60)
        self.rest_client = RESTClient(self._token, aiohttp.ClientSession(headers={
            "Authorization": f"Bot {self._token}",
            "User-Agent": "DiscordBot (https://github.com/mounderfod/discobra 0.0.1)"
        }, timeout=timeout))
        async with self.rest_client.session.ws_connect("wss://gateway.discord.gg/?v=10&encoding=json") as gateway:
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
        await self.gateway.send_str(json.dumps(data))

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

        if opcode != GatewayEvents.DISPATCH:
            if opcode == GatewayEvents.RECONNECT:
                return await self.close()

            if opcode == GatewayEvents.HELLO:
                self.heartbeat_interval = data['heartbeat_interval']
                asyncio.run_coroutine_threadsafe(self.heartbeat(self.heartbeat_interval), self.loop)
                return await self.identify()

            if opcode == GatewayEvents.HEARTBEAT_ACK:
                return await self.heartbeat(self.heartbeat_interval)

            if opcode == GatewayEvents.HEARTBEAT:
                return await self.heartbeat(self.heartbeat_interval)

        event = msg['t']

        print(f"{event}")

        match(event):
            case 'READY':
                self.ready = True
                self.client_cache.user = User(data['user'])
                return self.event_emitter.emit('on_ready')
            case 'APPLICATION_COMMAND_PERMISSIONS_UPDATE':
                return self.event_emitter.emit('on_application_command_permissions_update')
            case 'CHANNEL_CREATE':
                return self.event_emitter.emit('on_channel_create', data)
            case 'CHANNEL_DELETE':
                return self.event_emitter.emit('on_channel_delete', data)
            case 'CHANNEL_UPDATE':
                return self.event_emitter.emit('on_channel_update', data)
            case 'CHANNEL_PINS_ACK':
                return self.event_emitter.emit('on_channel_pins_ack', data)
            case 'CHANNEL_PINS_UPDATE':
                return self.event_emitter.emit('on_channel_pins_update', data)
            case 'GUILD_CREATE':
                self.client_cache.update_guild(Guild(data))
                return self.event_emitter.emit('on_guild_create', Guild(data))
            case 'GUILD_DELETE':
                return self.event_emitter.emit('on_guild_delete', data)
            case 'GUILD_UPDATE':
                return self.event_emitter.emit('on_guild_update', data)
            case 'GUILD_BAN_ADD':
                return self.event_emitter.emit('on_guild_ban_add', data)
            case 'GUILD_BAN_REMOVE':
                return self.event_emitter.emit('on_guild_ban_remove', data)
            case 'GUILD_EMOJIS_UPDATE':
                return self.event_emitter.emit('on_guild_emojis_update', data)
            case 'GUILD_INTEGRATIONS_UPDATE':
                return self.event_emitter.emit('on_guild_integrations_update', data)
            case 'GUILD_MEMBER_ADD':
                return self.event_emitter.emit('on_guild_member_add', data)
            case 'GUILD_MEMBER_REMOVE':
                return self.event_emitter.emit('on_guild_member_remove', data)
            case 'GUILD_MEMBER_UPDATE':
                return self.event_emitter.emit('on_guild_member_update', data)
            case 'GUILD_MEMBERS_CHUNK':
                return self.event_emitter.emit('on_guild_members_chunk', data)
            case 'GUILD_ROLE_CREATE':
                return self.event_emitter.emit('on_guild_role_create', data)
            case 'GUILD_ROLE_DELETE':
                return self.event_emitter.emit('on_guild_role_delete', data)
            case 'GUILD_ROLE_UPDATE':
                return self.event_emitter.emit('on_guild_role_update', data)
            case 'GUILD_SYNC':
                return self.event_emitter.emit('on_guild_sync', data)
            case 'GUILD_MEMBERS_CHUNK':
                return self.event_emitter.emit('on_guild_members_chunk', data)
            case 'MESSAGE_CREATE':
                return self.event_emitter.emit('on_message_create', data)
            case 'MESSAGE_DELETE':
                return self.event_emitter.emit('on_message_delete', data)
            case 'MESSAGE_DELETE_BULK':
                return self.event_emitter.emit('on_message_delete_bulk', data)
            case 'MESSAGE_UPDATE':
                return self.event_emitter.emit('on_message_update', data)
            case 'MESSAGE_REACTION_ADD':
                return self.event_emitter.emit('on_message_reaction_add', data)
            case 'MESSAGE_REACTION_REMOVE':
                return self.event_emitter.emit('on_message_reaction_remove', data)
            case 'MESSAGE_REACTION_REMOVE_ALL':
                return self.event_emitter.emit('on_message_reaction_remove_all', data)
            case 'MESSAGE_REACTION_REMOVE_EMOJI':
                return self.event_emitter.emit('on_message_reaction_remove_emoji', data)
            case 'PRESENCE_UPDATE':
                return self.event_emitter.emit('on_presence_update', data)
            case 'TYPING_START':
                return self.event_emitter.emit('on_typing_start', data)
            case 'USER_UPDATE':
                return self.event_emitter.emit('on_user_update', data)
            case 'VOICE_STATE_UPDATE':
                return self.event_emitter.emit('on_voice_state_update', data)
            case 'VOICE_SERVER_UPDATE':
                return self.event_emitter.emit('on_voice_server_update', data)
            case 'WEBHOOKS_UPDATE':
                return self.event_emitter.emit('on_webhooks_update', data)

    async def close(self):
        """
        Close the client.
        """
        self.loop.stop()
        await self.gateway.close()

    async def poll_event(self):
        async for msg in self.gateway:
            if msg.type in (aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY):
                await self.recv(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break

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
        await self.send(heartbeat)

    async def identify(self):
        """
        Identify the client.
        """
        identify = {
            "op": GatewayEvents.IDENTIFY.value,
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
        await self.send(identify)

    def event(self, coro: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None, /) -> Optional[
        Callable[..., Coroutine[Any, Any, Any]]]:
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
