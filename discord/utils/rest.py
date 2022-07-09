import aiohttp
import asyncio

from discord.utils.exceptions import APIException


async def get(token, url):
    async with aiohttp.ClientSession(headers={
        "Authorization": f"Bot {token}",
        "User-Agent": f"DiscordBot (https://github.com/mounderfod/discobra 0.0.1)"
    }) as session:
        async with session.get(url='https://discord.com/api/v10' + url) as r:
            data = await r.json()
            match r.status:
                case 200:
                    return data
                case other:
                    raise APIException(data['message'])


async def post(token, url, data):
    async with aiohttp.ClientSession(headers={
        "Authorization": f"Bot {token}",
        "User-Agent": f"DiscordBot (https://github.com/mounderfod/discobra 0.0.1)"
    }) as session:
        async with session.post(url='https://discord.com/api/v10' + url, data=data) as r:
            data = await r.json()
            match r.status:
                case 200 | 204:
                    return data
                case other:
                    raise APIException(data['message'])


async def patch(token, url, data):
    async with aiohttp.ClientSession(headers={
        "Authorization": f"Bot {token}",
        "User-Agent": f"DiscordBot (https://github.com/mounderfod/discobra 0.0.1)"
    }) as session:
        async with session.patch(url='https://discord.com/api/v10' + url, data=data) as r:
            data = await r.json()
            match r.status:
                case 200 | 204:
                    return data
                case other:
                    raise APIException(data['message'])


async def delete(token, url):
    async with aiohttp.ClientSession(headers={
        "Authorization": f"Bot {token}",
        "User-Agent": f"DiscordBot (https://github.com/mounderfod/discobra 0.0.1)"
    }) as session:
        async with session.delete(url='https://discord.com/api/v10' + url) as r:
            data = await r.json()
            match r.status:
                case 200:
                    return data
                case other:
                    raise APIException(data['message'])
