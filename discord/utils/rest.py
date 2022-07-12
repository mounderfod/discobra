import aiohttp

from discord.utils.exceptions import APIException


class RESTClient:
    """
    Utility class to make it easier to make HTTP requests to Discord's API. This should not be used manually,
    as it only works with Discord's API and the library should cover anything that can be requested from it. Any
    requests to other APIs should use `aiohttp`.
    """
    def __init__(self, token: str, session: aiohttp.ClientSession):
        self.token = token
        self._session = session

    @property
    def session(self) -> aiohttp.ClientSession:
        """
        Returns the _session used by the client.
        """
        return self._session

    async def get(self, url: str):
        """
        Makes a GET request to Discord's API.

        **Parameters:**
        - url: The part of the request URL that goes after `https://discord.com/api/v10`
        """
        async with self._session.get(url='https://discord.com/api/v10' + url) as r:
            data = await r.json()
            match r.status:
                case 200:
                    return data
                case other:
                    raise APIException(data['message'])

    async def post(self, url: str, data):
        """
        Makes a POST request to Discord's API.

        **Parameters:**
        - url: The part of the request URL that goes after `https://discord.com/api/v10`
        - data: The data to post.
        """
        async with self._session.post(url='https://discord.com/api/v10' + url, data=data) as r:
            data = await r.json()
            match r.status:
                case 200 | 204 | 201:
                    return data
                case other:
                    raise APIException(data['message'])

    async def patch(self, url, data):
        """
        Makes a PATCH request to Discord's API.

        **Parameters:**
        - url: The part of the request URL that goes after `https://discord.com/api/v10`
        - data: The data to patch.
        """
        async with self._session.patch(url='https://discord.com/api/v10' + url, data=data) as res:
            data = await res.json()
            match res.status:
                case 200 | 204:
                    return data
                case other:
                    raise APIException(data['message'])

    async def delete(self, url):
        """
        Makes a POST request to Discord's API.

        **Parameters:**
        - url: The part of the request URL that goes after `https://discord.com/api/v10`
        """
        async with self._session.delete(url='https://discord.com/api/v10' + url) as r:
            data = await r.json()
            match r.status:
                case 200:
                    return data
                case other:
                    raise APIException(data['message'])
