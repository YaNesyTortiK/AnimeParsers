import base64
import json
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True

try:
    from . import errors                        # Импорт при установленной библиотеке
    from .internal_tools import TTLCache
except ImportError:
    import errors                               # Импорт при локальном запуске
    from internal_tools import TTLCache


class DreamcastParser:
    """
    Парсер сайта фандаб-студии DreamCast (dreamerscast.com). Плеер Playerjs, видео в HLS/DASH (AV1 + AAC/Opus).
    """

    # Базовый домен DreamCast
    _DREAMCAST_BASE = "https://dreamerscast.com"

    # Заголовки для запросов к сайту
    _HEADERS = {
        "Referer": "https://dreamerscast.com/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) "
            "Gecko/20100101 Firefox/140.0"
        ),
    }

    # Ссылка на релиз: /home/release/<id>-<slug> (без slug сайт отдает 404)
    _RELEASE_RE = re.compile(r"/home/release/(\d+)-([A-Za-z0-9-]+)")
    # Настройки плеера на странице релиза: new Playerjs("#2<base64>")
    _PLAYERJS_RE = re.compile(r'new Playerjs\("#2([A-Za-z0-9+/=]+)"\)')
    # Мусорные вставки в base64: "//" + base64 от 64 букв и цифр. Lookahead — вставки могут перекрываться
    _JUNK_RE = re.compile(r"(?=//([A-Za-z0-9+/]{86}==))")
    _JUNK_TEXT_RE = re.compile(rb"[A-Za-z0-9]{64}")
    _EPISODE_RE = re.compile(r"(\d+(?:[.,]\d+)?)")
    _RESOLUTION_RE = re.compile(r"RESOLUTION=\d+x(\d+)")

    def __init__(self, mirror: str | None = None, proxy: str | None = None, use_lxml: bool = False, use_cache: bool = True, cache_maxsize: int = 300, cache_ttl: int = 900) -> None:
        """
        :mirror: Зеркало сайта если dreamerscast.com заблокирован (по умолчанию None)
        :proxy: прокси для обхода блокировки, применяется ко всем запросам парсера (`http://host:port` или 'socks5://user:pass@host:port') (по умолчанию None)
        :use_lxml: Использовать lxml парсер для html (По умолчанию False)
        :use_cache: Использование кеширования страниц релизов, рекомендуется (По умолчанию True)
        :cache_maxsize: Максимальный размер кеша (по умолчанию 300)
        :cache_ttl: Время жизни кеша (по умолчанию 900 сек = 15 минут, у онгоингов часто добавляются серии)
        """
        if not LXML_WORKS and use_lxml:
            raise ImportWarning('Параметр use_lxml установлен в true, однако при попытке импорта lxml произошла ошибка')
        self.use_lxml = use_lxml
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        if mirror:
            self._DREAMCAST_BASE = f"https://{mirror}"
        self.use_cache = use_cache
        self._page_cache = TTLCache(cache_maxsize, cache_ttl) if use_cache else {}

    def search(self, query: str, page: int = 1) -> list:
        """
        Поиск аниме по названию на dreamerscast.com (ищет по русскому и оригинальному названию).
        :query: Строка поиска (название аниме, сайт ищет от 4 символов)
        :page: Номер страницы выдачи (на странице до 16 результатов)

        Возвращает список словарей вида:
        [
            {
                "id": "Числовой ID релиза на dreamerscast.com (прим: 209)",
                "slug": "slug релиза (прим: 209-sousou-no-frieren)",
                "link": "Ссылка на страницу релиза",
                "title": "Название аниме",
                "original_title": "Оригинальное название (если есть, иначе None)",
                "image": "Ссылка на постер (если есть, иначе None)",
                "type": "Тип (прим: TV, OVA/ONA)",
                "year": Год выхода (int или None),
                "season": "Сезон выхода (прим: Осень) или None",
                "genres": ["Жанр 1", "Жанр 2"],
                "studio": "Студия или None",
                "episodes": Всего серий (int или None),
                "released_episodes": Вышло серий в озвучке (int или None),
                "voice_actors": ["Актер озвучки 1", "Актер озвучки 2"],
                "timing": ["Таймер 1"],
                "rating": "Оценка на сайте (прим: 4,8) или None"
            },
            ...
        ]

        Исключения:
        - errors.ServiceError — HTTP-ошибка или блокировка Cloudflare
        - errors.UnexpectedBehavior — сервер прислал не JSON
        - errors.NoResults — поиск не дал результатов
        """
        resp = requests.post(
            f"{self._DREAMCAST_BASE}/",
            data={"search": query, "pageNumber": page, "pageSize": 16},
            headers={**self._HEADERS, "X-Requested-With": "XMLHttpRequest"},
            proxies=self.proxies,
        )
        self._check_status(resp, "при поиске")
        try:
            releases = resp.json().get("releases") or []
        except (ValueError, AttributeError) as ex:
            raise errors.UnexpectedBehavior(f'DreamCast вернул не JSON при поиске "{query}". Ошибка: {ex}')

        results = []
        for item in releases:
            found = self._RELEASE_RE.search(str(item.get("url") or ""))
            if not found:
                continue
            results.append({
                "id": found.group(1),
                "slug": f"{found.group(1)}-{found.group(2)}",
                "link": urljoin(self._DREAMCAST_BASE, found.group(0)),
                "title": (item.get("russian") or "").strip(),
                "original_title": (item.get("original") or "").strip() or None,
                "image": self._https(item.get("image")),
                "type": item.get("type"),
                "year": item.get("dateissue") if isinstance(item.get("dateissue"), int) else None,
                "season": item.get("season") or None,
                "genres": self._split(item.get("genres")),
                "studio": item.get("studio") or None,
                "episodes": item.get("series") if isinstance(item.get("series"), int) and item.get("series") > 0 else None,
                "released_episodes": item.get("currentSeries") if isinstance(item.get("currentSeries"), int) else None,
                "voice_actors": self._split(item.get("dubbers")),
                "timing": self._split(item.get("timers")),
                "rating": item.get("rating") or None,
            })
        if not results:
            raise errors.NoResults(f'По запросу "{query}" ничего не найдено.')
        return results

    def anime_info(self, link: str) -> dict:
        """
        Информация об аниме со страницы релиза.
        :link: Ссылка на страницу релиза или его slug (прим: https://dreamerscast.com/home/release/209-sousou-no-frieren или 209-sousou-no-frieren)

        Возвращает словарь вида:
        {
            "id": "Числовой ID релиза",
            "link": "Ссылка на страницу релиза",
            "title": "Название аниме",
            "original_title": "Оригинальное название (если есть, иначе None)",
            "poster": "Ссылка на постер (если есть, иначе None)",
            "year": Год выхода (int или None),
            "season": "Сезон выхода или None",
            "studio": "Студия или None",
            "episodes": Всего серий (int или None),
            "released_episodes": Вышло серий в озвучке (int или None),
            "genres": ["Жанр 1", "Жанр 2"],
            "voice_actors": ["Актер озвучки 1", "Актер озвучки 2"],
            "timing": ["Таймер 1"],
            "description": "Описание"
        }

        Исключения:
        - errors.ServiceError — HTTP-ошибка или блокировка Cloudflare
        - errors.NoResults — релиз не найден
        - errors.UnexpectedBehavior — изменилась верстка страницы
        """
        link = self._release_link(link)
        page = self._get_page(link)
        soup = BeautifulSoup(page, "lxml") if self.use_lxml else BeautifulSoup(page, "html.parser")
        info = soup.find("div", {"class": "postInfo"})
        if info is None or info.find("h3") is None:
            raise errors.UnexpectedBehavior(f'Не найден блок с информацией об аниме по ссылке "{link}". Возможно изменилась верстка страницы.')

        title = info.find("h3").get_text(strip=True)
        original_title = None
        if " / " in title:
            title, original_title = (part.strip() for part in title.split(" / ", 1))

        fields = {}
        for item in info.find_all("div", {"class": "postItem"}):
            label = item.find("span")
            if label is None:
                continue
            name = label.get_text(strip=True).rstrip(":")
            links = [a.get_text(strip=True) for a in item.find_all("a")]
            desc = item.find("div", {"class": "postDesc"})
            if desc is not None:
                fields[name] = desc.get_text("\n", strip=True)
            elif links:
                fields[name] = links
            else:
                spans = item.find_all("span")
                fields[name] = spans[-1].get_text(strip=True) if len(spans) > 1 else ""

        released, total = None, None
        counter = re.match(r"\s*(\d+)\s*из\s*(\d+)", str(fields.get("Эпизодов") or ""))
        if counter:
            released, total = int(counter.group(1)), int(counter.group(2))
        year = (fields.get("Год") or [None])[0]
        poster = soup.find("meta", {"property": "og:image"})

        return {
            "id": self._RELEASE_RE.search(link).group(1),
            "link": link,
            "title": title,
            "original_title": original_title,
            "poster": self._https(poster.get("content") if poster else None),
            "year": int(year) if year and str(year).isdigit() else None,
            "season": (fields.get("Сезон") or [None])[0],
            "studio": (fields.get("Студия") or [None])[0],
            "episodes": total,
            "released_episodes": released,
            "genres": fields.get("Жанр") or [],
            "voice_actors": fields.get("Озвучивание") or [],
            "timing": fields.get("Тайминг") or [],
            "description": fields.get("Описание") or "",
        }

    def get_episodes(self, link: str) -> list:
        """
        Список вышедших серий релиза со ссылками на видео.
        :link: Ссылка на страницу релиза или его slug

        Возвращает список словарей вида (отсортирован по номеру серии):
        [
            {
                "episode": Номер серии (int, у спешлов бывает float, прим: 12.5),
                "title": "Название серии на сайте (прим: Серия 1)",
                "hls": "Ссылка на master.m3u8 (все качества)",
                "dash": "Ссылка на manifest.mpd или None",
                "thumbnails": "Ссылка на .vtt с превью кадров или None",
                "embed": "Ссылка на встраиваемый плеер или None"
            },
            ...
        ]
        Если у релиза один файл (фильм, OVA или первая серия онгоинга), он будет серией 1.

        Исключения:
        - errors.ServiceError — HTTP-ошибка или блокировка Cloudflare
        - errors.NoResults — релиз не найден или в нем пока нет серий
        - errors.UnexpectedBehavior — на странице нет плеера
        - errors.DecryptionFailure — не удалось расшифровать настройки плеера (сайт изменил формат)
        """
        link = self._release_link(link)
        config = self.decode_player(self._get_page(link))
        files = config.get("file")
        if isinstance(files, str):
            items = [config]
        elif isinstance(files, list):
            items = [f for f in files if isinstance(f, dict)]
        else:
            items = []

        episodes = {}
        for index, item in enumerate(items, start=1):
            streams = self._split_streams(item.get("file"))
            if not streams["hls"] and not streams["dash"]:
                continue
            title = item.get("title") or f"Серия {index}"
            number = self._EPISODE_RE.search(title) if item is not config else None
            if number:
                value = float(number.group(1).replace(",", "."))
                episode = int(value) if value.is_integer() else value
            else:
                episode = index
            episodes.setdefault(episode, {
                "episode": episode,
                "title": title,
                "hls": streams["hls"],
                "dash": streams["dash"],
                "thumbnails": item.get("thumbnails") or None,
                "embed": item.get("embed") or None,
            })
        if not episodes:
            raise errors.NoResults(f'В релизе "{link}" пока нет серий.')
        return sorted(episodes.values(), key=lambda x: x["episode"])

    def get_stream(self, link: str, episode: int | float = 1) -> dict:
        """
        Ссылки на видео серии.
        :link: Ссылка на страницу релиза или его slug
        :episode: Номер серии (по умолчанию 1)

        Возвращает словарь вида:
        {
            "HLS": "https://.../master.m3u8", // или None
            "DASH": "https://.../manifest.mpd" // или None
        }

        Исключения: как у get_episodes, плюс errors.NoResults — серия не найдена
        """
        for item in self.get_episodes(link):
            if item["episode"] == episode:
                return {"HLS": item["hls"], "DASH": item["dash"]}
        raise errors.NoResults(f'Серия {episode} не найдена в релизе "{link}".')

    def get_qualities(self, hls_link: str) -> dict:
        """
        Доступные качества по ссылке на master.m3u8 (из get_episodes или get_stream).
        :hls_link: Ссылка на master.m3u8

        Возвращает словарь вида:
        {
            "1080": "ссылка на m3u8 плейлист с качеством 1080p (видео и звук вместе)",
            "720": "...",
            "480": "..."
        }
        Видео на DreamCast в кодеке AV1 — для воспроизведения нужен плеер с его поддержкой.

        Исключения:
        - errors.ServiceError — HTTP-ошибка
        - errors.NoResults — в плейлисте нет видео
        """
        resp = requests.get(hls_link, headers=self._HEADERS, proxies=self.proxies)
        self._check_status(resp, "при получении плейлиста")
        lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
        qualities = {}
        for i, line in enumerate(lines[:-1]):
            height = self._RESOLUTION_RE.search(line) if line.startswith("#EXT-X-STREAM-INF") else None
            if height and not lines[i + 1].startswith("#"):
                qualities.setdefault(height.group(1), urljoin(resp.url, lines[i + 1]))
        if not qualities:
            raise errors.NoResults(f'В плейлисте "{hls_link}" нет видео.')
        return dict(sorted(qualities.items(), key=lambda x: int(x[0]), reverse=True))

    @classmethod
    def decode_player(cls, page: str) -> dict:
        """
        Расшифровывает настройки плеера Playerjs со страницы релиза.
        :page: HTML страницы релиза

        Настройки записаны как "#2" + base64, в который вставлены мусорные куски "//" + base64(64 буквы и цифры).
        Вставки бывают вложенными (следующая попадает внутрь предыдущей), поэтому убираем их по одной,
        каждый раз ищем первую целую.

        Возвращает словарь настроек Playerjs (ключ "file" — ссылка или список серий)

        Исключения:
        - errors.UnexpectedBehavior — на странице нет плеера
        - errors.DecryptionFailure — не удалось расшифровать настройки
        """
        found = cls._PLAYERJS_RE.search(page)
        if not found:
            raise errors.UnexpectedBehavior("На странице релиза не найден плеер Playerjs. Возможно изменилась верстка страницы.")
        data = found.group(1)
        for _ in range(50):  # Вставок на странице 5, больше — значит формат изменился
            for match in cls._JUNK_RE.finditer(data):
                try:
                    is_junk = cls._JUNK_TEXT_RE.fullmatch(base64.b64decode(match.group(1)))
                except ValueError:
                    is_junk = None
                if is_junk:
                    start = match.start()
                    data = data[:start] + data[start + 2 + len(match.group(1)):]
                    break
            else:
                break
        try:
            return json.loads(base64.b64decode(data + "=" * (-len(data) % 4)))
        except ValueError as ex:
            raise errors.DecryptionFailure(f"Не удалось расшифровать настройки плеера DreamCast. Возможно сайт изменил формат. Ошибка: {ex}")

    def _release_link(self, link: str) -> str:
        """Ссылка на релиз из ссылки или slug. Сторонние домены не принимаем."""
        link = str(link or "").strip()
        if re.fullmatch(r"\d+-[A-Za-z0-9-]+", link):
            return f"{self._DREAMCAST_BASE}/home/release/{link}"
        found = self._RELEASE_RE.search(link)
        host = self._DREAMCAST_BASE.split("://", 1)[1]
        allowed = tuple(f"{scheme}://{prefix}{domain}/" for scheme in ("http", "https") for prefix in ("", "www.") for domain in {"dreamerscast.com", host}) + ("/home/release/",)
        if not found or not link.startswith(allowed):
            raise errors.PostArgumentsError(f'Ожидалась ссылка на релиз DreamCast вида "{self._DREAMCAST_BASE}/home/release/209-sousou-no-frieren" или slug "209-sousou-no-frieren". Получено: "{link}"')
        return f"{self._DREAMCAST_BASE}{found.group(0)}"

    def _get_page(self, link: str) -> str:
        if self.use_cache and link in self._page_cache:
            return self._page_cache[link]
        resp = requests.get(link, headers=self._HEADERS, proxies=self.proxies)
        if resp.status_code == 404:
            raise errors.NoResults(f'Релиз по ссылке "{link}" не найден.')
        self._check_status(resp, "при получении страницы релиза")
        if self.use_cache:
            self._page_cache[link] = resp.text
        return resp.text

    @staticmethod
    def _check_status(resp, action: str) -> None:
        if resp.status_code in (403, 503):
            raise errors.ServiceError(f'DreamCast вернул статус {resp.status_code} {action}. Возможна блокировка Cloudflare. Попробуйте позже или используйте прокси.')
        if resp.status_code != 200:
            raise errors.ServiceError(f'Ошибка {action} на DreamCast. Ожидался код 200, получен: {resp.status_code}')

    @staticmethod
    def _https(url) -> str | None:
        """Ссылки на картинки бывают без схемы ("//cache...") или с http — приводим к https."""
        return re.sub(r"^(?:https?:)?//", "https://", url) if url else None

    @staticmethod
    def _split(value) -> list:
        return [part.strip() for part in str(value or "").split(",") if part.strip()]

    @staticmethod
    def _split_streams(value) -> dict:
        """В поле file — "ссылка на DASH or ссылка на HLS"."""
        streams = {"hls": None, "dash": None}
        for part in str(value or "").split(" or "):
            part = part.strip()
            path = part.split("?", 1)[0]
            if part.startswith("http") and path.endswith(".m3u8"):
                streams["hls"] = part
            elif part.startswith("http") and path.endswith(".mpd"):
                streams["dash"] = part
        return streams
