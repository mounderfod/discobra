import asyncio
import json
import sys
import threading

import websockets

from discord.intents import Intents, gen_number

loop = asyncio.get_event_loop()


class Client:
    def __init__(self, token: str, intents: list[Intents]):
        self.gateway = None
        code = gen_number(intents)
        asyncio.run(self.connect(token, code))

    async def connect(self, token: str, intent_code: int):
        async with websockets.connect("wss://gateway.discord.gg/?v=10&encoding=json") as gateway:
            hello = await gateway.recv()
            self.gateway = gateway
            threading.Thread(target=loop.run_forever).start()
            heartbeat = asyncio.run_coroutine_threadsafe(
                self.heartbeat(gateway, json.loads(hello)['d']['heartbeat_interval']), loop)
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

    async def heartbeat(self, gateway: websockets.WebSocketClientProtocol, interval: int):
        while True:
            await asyncio.sleep(interval / 1000)
            heartbeat = {
                "op": 1,
                "d": None
            }
            await gateway.send(json.dumps(heartbeat))
            ack = await gateway.recv()
