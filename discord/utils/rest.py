import aiohttp

from discord.utils.exceptions import APIException

class RESTClient:
    def __init__(self, token: str, session: aiohttp.ClientSession):
        self.token = token
        self.session = session

    async def get(self, url: str):
        async with self.session.get(url='https://discord.com/api/v10' + url) as r:
            data = await r.json()
            match r.status:
                case 200:
                    return data
                case other:
                    raise APIException(data['message'])


    async def post(self, url: str, data):
        async with self.session.post(url='https://discord.com/api/v10' + url, data=data) as r:
            data = await r.json()
            match r.status:
                case 200 | 204:
                    return data
                case other:
                    raise APIException(data['message'])


    async def patch(self, url, data):
        async with self.session.patch(url='https://discord.com/api/v10' + url, data=data) as res:
            data = await res.json()
            match res.status:
                case 200 | 204:
                    return data
                case other:
                    raise APIException(data['message'])


    async def delete(self, url):
        async with self.session.delete(url='https://discord.com/api/v10' + url) as r:
            data = await r.json()
            match r.status:
                case 200:
                    return data
                case other:
                    raise APIException(data['message'])
