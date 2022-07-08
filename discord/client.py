import asyncio
import json
import sys
import threading
import websockets
from typing import Coroutine
from discord.intents import Intents, gen_number

class Client:
    def __init__(self, intents: list[Intents]):
        self.gateway = None
        self.loop = asyncio.get_event_loop()
        self.code = gen_number(intents)

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
            if (hasattr(self, 'on_ready')):
                await getattr(self, 'on_ready')()

    async def heartbeat(self, gateway: websockets.WebSocketClientProtocol, interval: int):
        while True:
            await asyncio.sleep(interval / 1000)
            heartbeat = {
                "op": 1,
                "d": None
            }
            await gateway.send(json.dumps(heartbeat))
            ack = await gateway.recv()

    def event(self, coro: Coroutine, /) -> Coroutine:
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a coroutine function')

        setattr(self, coro.__name__, coro)
        return coro

    def run(self, token: str):
        self.token = token
        asyncio.run(self.connect(self.token, self.code))
