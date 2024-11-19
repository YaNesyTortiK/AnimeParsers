try:
    import aiohttp
    import asyncio
except ImportError:
    CAN_WORK = False
else:
    CAN_WORK = True

import json

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
    def __init__(self) -> None:
        if not CAN_WORK:
            raise ImportError("Невозможно получить доступ к библиотекам \"aiohttp\" и/или \"asyncio\". Проверьте правильность установки библиотеки.")

    async def get(self, url: str, **kwargs) -> Response:
        async with aiohttp.request(method='get', url=url, **kwargs) as response:
            text = await response.text()
            res = Response(
                status=response.status,
                text=text,
                url=response.url.human_repr()
            ) 
        return res
    
    async def post(self, url: str, **kwargs) -> Response:
        async with aiohttp.request(method='post', url=url, **kwargs) as response:
            text = await response.text()
            res = Response(
                status=response.status,
                text=text,
                url=response.url.human_repr()
            )
        return res