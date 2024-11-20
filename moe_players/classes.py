from aiohttp import ClientSession
from bs4 import BeautifulSoup
from asyncio import sleep


class Errors:
    class PageNotFound(Exception):
        pass


class Parser(object):
    def __init__(self, *args, **kwargs):
        self.base_url = None
        self.headers = {}
        self.args = args
        self.session = None
        self.proxy = None

        try:
            import lxml

            self.lxml = True
        except ImportError:
            self.lxml = False

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    async def get(self, path: str, **kwargs) -> dict | str:
        session = (
            ClientSession(
                headers=self.headers if "headers" not in kwargs else kwargs["headers"],
                proxy=self.proxy,
            )
            if not self.session or self.session.closed
            else self.session
        )
        try:
            url = (
                "" if self.base_url is None or path.startswith("http") else self.base_url
            ) + path
            async with session.get(
                url,
                params=kwargs["params"] if "params" in kwargs else None,
            ) as response:
                if response.status == 429:
                    await sleep(
                        response.headers["Retry-After"]
                        if "retry-after" in response.headers
                        else 1
                    )
                    return await self.get(path, **kwargs)
                elif response.status == 404:
                    raise Errors.AnimeNotFound(f"Page not found: {url}")
                try:
                    if "text" in kwargs.keys() and kwargs["text"]:
                        raise Exception
                    response = await response.json()
                except Exception:
                    response = await response.text()
        finally:
            if "close" in kwargs and kwargs["close"] is False:
                return response
            await session.close()
        return response

    async def soup(self, *args, **kwargs):
        return BeautifulSoup(
            *args, **kwargs, features="lxml" if self.lxml else "html.parser"
        )

    def __repr__(self):
        return f"""<{self.__class__.__name__} "{self.base_url}">"""


class Anime(object):
    def __init__(self, *args, **kwargs):
        self.orig_title = None
        self.title = None
        self.anime_id = None
        self.id_type = None
        self.url = None
        self.episodes = None
        self.total_episodes = None
        self.type = None
        self.status = None
        self.year = None
        self.parser = None
        self.translations = None
        self.data = None
        self.args = args
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def __repr__(self):
        return f"""<{self.__class__.__name__} "{self.title if len(self.title) < 30 else self.title[:30] + '...'}">"""
