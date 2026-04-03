try:
    import aiohttp
    import asyncio
except ImportError:
    CAN_WORK = False
else:
    CAN_WORK = True

import json
import time
from collections import OrderedDict

class TTLCache:
    """
    Простой LRU-кэш с ограничением по времени жизни (TTL) и максимальному размеру (maxsize).
    Используется для кэширования данных в библиотеке, чтобы избежать утечек памяти в долгоживущих процессах.
    """
    def __init__(self, maxsize: int = 100, ttl: float = 3600) -> None:
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl

    def __contains__(self, key) -> bool:
        if key not in self.cache:
            return False
        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return False
        return True

    def __getitem__(self, key):
        value, timestamp = self.cache.pop(key)
        if time.time() - timestamp > self.ttl:
            raise KeyError(key)
        self.cache[key] = (value, timestamp)
        return value

    def __setitem__(self, key, value) -> None:
        if key in self.cache:
            del self.cache[key]
        self.cache[key] = (value, time.time())
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self):
        self.cache.clear()

class Response:
    """
    Класс для удобства использования AsyncSession
    Параметры:
    status, status_code, text, url
    """
    def __init__(self, status, text, url) -> None:
        self.status = status
        self.status_code = status
        self.text = text
        self.url = url

    def json(self):
        return json.loads(self.text)

class AsyncSession:
    """
    Класс-обертка для удобства использования асинхронных запросов
    """
    def __init__(self, proxy=None) -> None:
        if not CAN_WORK:
            raise ImportError("Невозможно получить доступ к библиотекам \"aiohttp\" и/или \"asyncio\". Проверьте правильность установки библиотеки.")
        self.proxy = proxy
        self._session = None

    async def _get_session(self):
        if self._session is None:
            if self.proxy and self.proxy.startswith('socks'):
                try:
                    from aiohttp_socks import ProxyConnector
                except ImportError:
                    raise ImportError("Для работы с proxy-серверами SOCKS требуется библиотека 'aiohttp_socks'. Установите ее с помощью 'pip install aiohttp_socks'")
                connector = ProxyConnector.from_url(self.proxy)
                self._session = aiohttp.ClientSession(connector=connector)
            else:
                self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, method: str, url: str, **kwargs) -> Response:
        session = await self._get_session()
        
        if self.proxy and not self.proxy.startswith('socks'):
            kwargs['proxy'] = self.proxy
            
        async with session.request(method=method, url=url, **kwargs) as response:
            return Response(response.status, await response.text(), str(response.url))

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get(self, url: str, **kwargs) -> Response:
        return await self._request('get', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Response:
        return await self._request('post', url, **kwargs)
    
    async def sleep(time: float): # Чтобы потом не импортировать asyncio отдельно
        await asyncio.sleep(time)