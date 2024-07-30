try:
    import aiohttp
    import asyncio
except ImportError:
    CAN_WORK = False
else:
    CAN_WORK = True

import json
import anime_parsers_ru.errors as errors

class Response:
    """
    Класс для удобства использования AsyncSession
    Параметры:
    status, text
    """
    def __init__(self, status, text) -> None:
        self.status = status
        self.text = text

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
            return Response(
                status=response.status,
                text=await response.text()
            )
    
    async def post(self, url: str, **kwargs) -> Response:
        async with aiohttp.request(method='post', url=url, **kwargs) as response:
            return Response(
                status=response.status,
                text=await response.text()
            )