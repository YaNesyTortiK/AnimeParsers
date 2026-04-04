import html
import json
import re
from urllib.parse import quote
from bs4 import BeautifulSoup

try:
    from . import errors                        # Импорт при установленной библиотеке
    from .internal_tools import AsyncSession    # Обёртка над aiohttp
except ImportError:
    import errors                               # Импорт при локальном запуске
    from internal_tools import AsyncSession


class AniboomPlayerAsync:
    """
    Асинхронный парсер плеера Aniboom (aniboom.one) + AnimeGO.

    Отвечает исключительно за работу с плеером Aniboom:
    - search()               — поиск аниме на AnimeGO
    - get_voices()           — получение доступных озвучек
    - get_stream_for_voice() — получение потока для озвучки использующей Aniboom-плеер.
                               Если эпизод отдаётся через CVH — бросает UnexpectedBehavior.
    - get_stream()           — низкоуровневый метод: поток напрямую по embed-ссылке Aniboom

    Пример использования:
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
    async def main():
        async with AniboomPlayerAsync() as parser:
            results = await parser.search("Баскетбол Куроко")
            info = await parser.get_voices(results[0])
            stream = await parser.get_stream_for_voice(
                voice_entry=info["voices"][0],
                season=1, episode=1,
                anime=results[0]
            )
            print(stream)
            subprocess.run(["mpv", f"--user-agent={USER_AGENT}", stream['url']])
    """

    # Базовый домен AnimeGO
    _ANIMEGO_BASE = "https://animego.org"

    # Заголовки для XHR-запросов к API плеера AnimeGO
    _PLAYER_HEADERS = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://animego.org/",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
    }

    # Заголовки для запросов к embed-странице на aniboom.one
    _EMBED_HEADERS = {
        "Referer": "https://animego.org/",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
    }

    # Заголовки для скачивания MPD-файла с CDN
    _DASH_HEADERS = {
        "Origin": "https://aniboom.one",
        "Referer": "https://aniboom.one/",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
    }

    def __init__(self) -> None:
        # Собственная HTTP-сессия — никаких внешних зависимостей на другие парсеры
        self._session = AsyncSession()

    async def search(self, query: str) -> list:
        """
        Поиск аниме по названию на animego.org.
        :query: Строка поиска (название аниме)

        Возвращает список словарей вида:
        [
            {
                "id": "Числовой ID аниме на animego.org",
                "slug": "slug-из-url (прим: naruto-shippuuden)",
                "title": "Название аниме"
            },
            ...
        ]

        Исключения:
        - errors.ServiceError — HTTP-ошибка или блокировка Cloudflare
        - errors.NoResults    — поиск не дал результатов
        """
        url = f"{self._ANIMEGO_BASE}/search/anime?q={quote(query)}"
        resp = await self._session.get(url, headers={
            "User-Agent": self._PLAYER_HEADERS["User-Agent"]
        })

        # Cloudflare блокировка — 403/503 или JS-challenge в теле ответа
        if resp.status_code in (403, 503) or "Cloudflare" in resp.text:
            raise errors.ServiceError(
                f'AnimeGO вернул статус {resp.status_code} при поиске. '
                f'Возможна блокировка Cloudflare. Попробуйте позже.'
            )
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при поиске на AnimeGO. '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        for item in soup.select("div.ani-grid__item"):
            # AnimeGO использует несколько вариантов разметки для ссылки на аниме
            link = (
                item.select_one("a.ani-grid__item-body") or
                item.select_one("div.ani-grid__item-title a") or
                item.select_one("a[href*='/anime/']")
            )
            if not link:
                continue

            href = link.get("href", "").strip("/")
            if not href.startswith("anime/"):
                continue

            # Ссылки имеют формат /anime/slug-ЧИСЛОВОЙ_ID
            path = href[len("anime/"):]
            m = re.match(r"^(.+)-(\d+)$", path)
            if not m:
                continue

            slug, anime_id = m.group(1), m.group(2)
            title_tag = item.select_one("div.ani-grid__item-title a")
            title = (
                title_tag.get_text(strip=True) if title_tag
                else slug.replace("-", " ").title()
            )
            results.append({"id": anime_id, "slug": slug, "title": title})

        if not results:
            raise errors.NoResults(
                f'По запросу "{query}" на AnimeGO ничего не найдено.'
            )

        return results

    async def get_voices(self, anime: dict) -> dict:
        """
        Получает список доступных озвучек и общее число эпизодов.
        :anime: Словарь из результатов search() — обязательно содержит поле "id"
        Возвращает словарь вида:
        {
            "voices": [
                {
                    "label": "Название озвучки",
                    "translation_id": "ID для передачи в get_stream_for_voice()"
                },
                ...
            ],
            "total_episodes": 12  # None если не удалось определить
        }

        Исключения:
        - errors.ServiceError       — HTTP-ошибка или блокировка Cloudflare
        - errors.NoResults          — аниме не найдено или нет переводов
        - errors.UnexpectedBehavior — ответ сервера не содержит ожидаемых данных
        """
        anime_id = anime["id"]
        url = f"{self._ANIMEGO_BASE}/player/{anime_id}"

        resp = await self._session.get(url, headers=self._PLAYER_HEADERS)

        if resp.status_code in (403, 503) or "Cloudflare" in resp.text:
            raise errors.ServiceError(
                f'AnimeGO вернул статус {resp.status_code} при запросе плеера (id={anime_id}). '
                f'Возможна блокировка Cloudflare.'
            )
        if resp.status_code == 404:
            raise errors.NoResults(
                f'Аниме с id={anime_id} не найдено на AnimeGO (404).'
            )
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при запросе плеера AnimeGO (id={anime_id}). '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        # Сервер возвращает JSON, HTML плеера лежит в data.content
        try:
            data = resp.json()
            content = html.unescape(data.get("data", {}).get("content", ""))
        except Exception as ex:
            raise errors.UnexpectedBehavior(
                f'Не удалось разобрать JSON ответа плеера AnimeGO (id={anime_id}). '
                f'Ошибка: {ex}'
            )

        soup = BeautifulSoup(content, "html.parser")

        # Кнопки озвучки содержат атрибут data-translation с её ID
        buttons = soup.find_all("button", {"data-translation": True})
        if not buttons:
            raise errors.NoResults(
                f'Кнопки выбора озвучки не найдены для аниме id={anime_id}. '
                f'Возможно, переводы отсутствуют или структура страницы изменилась.'
            )

        voices = []
        for btn in buttons:
            translation_id = btn.get("data-translation")
            span = btn.find("span", {"class": "text-truncate"})
            name = span.text.strip() if span else None
            if translation_id and name:
                # Убираем суффикс "(ошибка)" — так AnimeGO помечает нерабочие озвучки
                label = name.replace(" (ошибка)", "").strip()
                voices.append({"label": label, "translation_id": translation_id})

        # Максимальный номер эпизода из элементов с data-episode
        ep_nums = []
        for el in soup.find_all(attrs={"data-episode": True}):
            try:
                ep_nums.append(int(el.text.strip()))
            except ValueError:
                pass
        total_episodes = max(ep_nums) if ep_nums else None

        return {"voices": voices, "total_episodes": total_episodes}

    async def get_stream_for_voice(
        self,
        voice_entry: dict,
        season: int,
        episode: int,
        anime: dict
    ) -> dict:
        """
        Получает поток Aniboom для конкретной озвучки и эпизода.
        Если AnimeGO отдаёт этот эпизод через CVH, а не Aniboom —
        бросает errors.UnexpectedBehavior. В этом случае используйте CVHPlayerAsync.

        :voice_entry: Элемент из списка voices (из get_voices()), содержит "translation_id"
        :season:      Номер сезона (обычно 1)
        :episode:     Номер эпизода
        :anime:       Словарь из результатов search() — обязательно содержит "id"

        Возвращает словарь:
          MPD: {"content": "<содержимое MPD-файла>", "kind": "MPD"}
          HLS: {"url": "https://.../.m3u8",          "kind": "HLS"}

        Исключения:
        - errors.ServiceError       — HTTP-ошибка при запросе
        - errors.UnexpectedBehavior — эпизод не использует Aniboom-плеер
        """
        anime_id = anime["id"]
        translation_id = voice_entry["translation_id"]

        # Получаем HTML плеера для данного эпизода и озвучки
        player_html = await self._get_player_html(anime_id, episode, translation_id)

        # Ищем признаки Aniboom — URL embed-плеера в атрибуте data-player
        m = re.search(r'data-player="([^"]*aniboom[^"]*)"', player_html)
        if not m:
            raise errors.UnexpectedBehavior(
                f'Плеер Aniboom не найден для '
                f'anime_id={anime_id}, S{season:02d}E{episode:02d}, '
                f'translation_id={translation_id}. '
                f'Возможно, этот эпизод использует CVH — попробуйте CVHPlayerAsync.'
            )

        raw_url = html.unescape(m.group(1))
        # URL может приходить без схемы (начинается с "//")
        embed_url = "https:" + raw_url if raw_url.startswith("//") else raw_url

        # Подставляем корректный номер эпизода в URL плеера
        if "episode=" in embed_url:
            embed_url = re.sub(r'episode=\d+', f'episode={episode}', embed_url)
        elif "?" in embed_url:
            embed_url += f"&episode={episode}"
        else:
            embed_url += f"?episode={episode}"

        return await self.get_stream(embed_url)

    async def get_stream(self, embed_url: str) -> dict:
        """
        Получает поток (MPD или HLS) напрямую по embed-ссылке плеера Aniboom.
        Низкоуровневый метод — можно вызывать самостоятельно если embed-URL уже известен.
        Внутри вызывается из get_stream_for_voice().

        :embed_url: Прямая ссылка на embed-плеер Aniboom
                    (прим: https://aniboom.one/embed/VIDEO_ID)

        Возвращает словарь одного из двух видов:

        MPD (приоритетный формат):
        {
            "content": "<содержимое MPD-файла с абсолютными URL сегментов>",
            "kind": "MPD"
        }

        HLS (fallback, если MPD недоступен):
        {
            "url": "https://.../.m3u8",
            "kind": "HLS"
        }

        Исключения:
        - errors.ServiceError       — HTTP-ошибка
        - errors.NoResults          — плеер или data-parameters не найдены
        - errors.UnexpectedBehavior — ни MPD, ни HLS нет в data-parameters
        """
        # Шаг 1: Скачиваем embed-страницу Aniboom
        resp = await self._session.get(embed_url, headers=self._EMBED_HEADERS)
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при запросе embed-страницы Aniboom. '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        # Шаг 2: Ищем тег <video id="video"> — в нём лежат параметры потоков
        soup = BeautifulSoup(resp.text, "html.parser")
        video_tag = soup.find("video", {"id": "video"})
        if not video_tag:
            raise errors.NoResults(
                f'Тег <video id="video"> не найден на странице: {embed_url}. '
                f'Возможно, структура плеера изменилась.'
            )

        # Шаг 3: data-parameters — HTML-encoded JSON со ссылками на потоки
        raw_params = video_tag.get("data-parameters")
        if not raw_params:
            raise errors.NoResults(
                f'Атрибут data-parameters отсутствует в теге <video>: {embed_url}'
            )

        data = json.loads(html.unescape(raw_params))

        # Шаг 4: MPD (DASH) — приоритетный формат
        if "dash" in data:
            try:
                mpd_url = json.loads(data["dash"])["src"]

                resp_mpd = await self._session.get(mpd_url, headers=self._DASH_HEADERS)
                if resp_mpd.status_code != 200:
                    raise errors.ServiceError(
                        f'Ошибка при скачивании MPD-файла. '
                        f'Ожидался код 200, получен: {resp_mpd.status_code}'
                    )

                playlist = resp_mpd.text

                # MPD содержит относительные пути сегментов — заменяем на абсолютные URL
                if "<MPD" in playlist:
                    filename = mpd_url[mpd_url.rfind('/') + 1 : mpd_url.rfind('.')]
                    server_path = mpd_url[: mpd_url.rfind('.')]
                    playlist = playlist.replace(filename, server_path)

                return {"url": mpd_url, "content": playlist, "kind": "MPD"}

            except errors.ServiceError:
                raise
            except Exception:
                # MPD недоступен — откатываемся на HLS
                pass

        # Шаг 5: HLS — fallback
        if "hls" in data:
            try:
                hls_url = json.loads(data["hls"])["src"]
                return {"url": hls_url, "kind": "HLS"}
            except Exception as ex:
                raise errors.ServiceError(
                    f'Не удалось разобрать HLS поток из data-parameters. '
                    f'Ошибка: {ex}'
                )

        raise errors.UnexpectedBehavior(
            f'В data-parameters плеера Aniboom не найдено ни "dash", ни "hls". '
            f'Содержимое: {data}'
        )

    async def _get_player_html(
        self,
        anime_id: str,
        episode: int,
        translation_id: str
    ) -> str:
        """
        Запрашивает HTML содержимое плеера AnimeGO для конкретного эпизода/озвучки.
        Возвращает декодированную HTML-строку для определения типа плеера.

        Исключения:
        - errors.ServiceError       — HTTP-ошибка или блокировка Cloudflare
        - errors.UnexpectedBehavior — JSON ответа не содержит поля data.content
        """
        url = (
            f"{self._ANIMEGO_BASE}/player/{anime_id}"
            f"?episode={episode}&translation={translation_id}"
        )

        resp = await self._session.get(url, headers=self._PLAYER_HEADERS)

        if resp.status_code in (403, 503) or "Cloudflare" in resp.text:
            raise errors.ServiceError(
                f'AnimeGO вернул статус {resp.status_code} при запросе плеера эпизода '
                f'(anime_id={anime_id}, episode={episode}, translation={translation_id}). '
                f'Возможна блокировка Cloudflare.'
            )
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при запросе HTML плеера AnimeGO. '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        try:
            data = resp.json()
            return html.unescape(data["data"]["content"])
        except Exception as ex:
            raise errors.UnexpectedBehavior(
                f'Не удалось извлечь content из JSON ответа плеера AnimeGO. '
                f'(anime_id={anime_id}, episode={episode}). Ошибка: {ex}'
            )

    async def close(self) -> None:
        """Закрывает внутреннюю HTTP-сессию."""
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
