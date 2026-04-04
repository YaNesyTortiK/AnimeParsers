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


class CVHPlayerAsync:
    """
    Асинхронный парсер плеера CdnVideoHub (cvh / plapi.cdnvideohub.com) + AnimeGO.

    Отвечает исключительно за работу с плеером CVH:
    - search()               — поиск аниме на AnimeGO
    - get_voices()           — получение доступных озвучек
    - get_stream_for_voice() — получение потока для озвучки использующей CVH-плеер.
                               Если эпизод отдаётся через Aniboom — бросает UnexpectedBehavior.
    - get_playlist()         — список эпизодов плейлиста CVH по cvh_id
    - get_stream()           — получение ссылки на поток по vk_id

    Пример использования:
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
    async def main():
        async with CVHPlayerAsync() as parser:
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

    # Базовый домен AnimeGO (для search и get_voices)
    _ANIMEGO_BASE = "https://animego.org"

    # Базовый URL API плеера CVH
    _CVH_API_BASE = "https://plapi.cdnvideohub.com/api/v1/player/sv"

    # Параметры идентификации издателя и агрегатора для animego.org
    _PUB = "747"
    _AGGR = "mali"

    # Заголовки для XHR-запросов к API плеера AnimeGO
    _PLAYER_HEADERS = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://animego.org/",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
    }

    # Заголовки для запросов к CVH API
    _CVH_HEADERS = {
        "Referer": "https://animego.org/",
        "Accept": "application/json",
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

    
    @staticmethod
    def _match_cvh_studio(label: str, cvh_studios: list) -> str | None:
        """
        Fuzzy-сопоставление AnimeGO-лейбла с именем CVH voiceStudio.

        Проход 1: точное совпадение (без учёта регистра)
        Проход 2: одна строка является подстрокой другой
                  (напр. "AniLibria" ↔ "AnilibriaTV")

        Возвращает точное имя CVH-студии или None если совпадение не найдено.
        """
        lo = label.lower()
        # Проход 1: точное
        for s in cvh_studios:
            if s.lower() == lo:
                return s
        # Проход 2: подстрока в любом направлении
        for s in cvh_studios:
            sl = s.lower()
            if lo in sl or sl in lo:
                return s
        return None

    async def get_matched_voices(
        self,
        anime: dict,
        season: int = 1,
        episode: int = 1,
    ) -> dict:
        """
        Возвращает только те озвучки, которые есть в плейлисте CVH для данного эпизода.
        
        Сопоставление ведется fuzzy-методом (точное совпадение → подстрока), что
        позволяет находить пары вроде "AniLibria" ↔ "AnilibriaTV".

        CVH-студии, не сопоставленные ни с одним представленным на AnimeGO, добавляются
        в конец списка с translation_id=None — поток для них можно получить
        через get_stream_for_voice(), т.к. cvh_id уже известен.

        :anime:   Словарь из результатов search()
        :season:  Номер сезона
        :episode: Номер эпизода, по которому определяются CVH-студии

        Возвращает словарь:
        {
            "voices": [
                {
                    "label":          "AniLibria",    # AnimeGO-лейбл (для отображения)
                    "translation_id": "2",            # AnimeGO translation_id (None — CVH-only)
                    "cvh_studio":     "AnilibriaTV",  # Точное имя студии в CVH-плейлисте
                    "cvh_id":         "50273",        # ID плейлиста CVH
                },
                ...
            ],
            "cvh_id":         "50273",
            "total_episodes": 12
        }

        Исключения:
        - errors.ServiceError       — HTTP-ошибка
        - errors.NoResults          — аниме/эпизод не найден или нет CVH
        - errors.UnexpectedBehavior — CVH-плеер не обнаружен на странице
        """
        # Полный список озвучек с AnimeGO
        voices_data = await self.get_voices(anime)
        ag_voices   = voices_data["voices"]
        total       = voices_data["total_episodes"]

        if not ag_voices:
            raise errors.NoResults("Нет доступных озвучек для данного аниме.")

        # cvh_id одинаков для всех озвучек — берём из первого успешного HTML
        cvh_id = None
        for v in ag_voices:
            try:
                ph = await self._get_player_html(anime["id"], episode, v["translation_id"])
            except (errors.ServiceError, errors.UnexpectedBehavior):
                continue
            for pattern in [
                r'data-id="(\d+)"[^>]*data-provider="[Cc][Vv][Hh]"',
                r'data-provider="[Cc][Vv][Hh]"[^>]*data-id="(\d+)"',
                r'cdn-iframe/(\d+)/',
            ]:
                m = re.search(pattern, ph)
                if m:
                    cvh_id = m.group(1)
                    break
            if cvh_id:
                break

        if not cvh_id:
            raise errors.UnexpectedBehavior(
                f'CVH-плеер не найден для anime_id={anime["id"]}, '
                f'S{season:02d}E{episode:02d}. '
                f'Возможно, данное аниме недоступно на CVH.'
            )

        # Получаем CVH-студии для нужного эпизода
        items    = await self.get_playlist(cvh_id)
        ep_items = [
            it for it in items
            if it.get("season") == season and it.get("episode") == episode
        ]
        if not ep_items:
            raise errors.NoResults(
                f'Эпизод S{season:02d}E{episode:02d} не найден в плейлисте CVH '
                f'(cvh_id={cvh_id}).'
            )

        cvh_studios    = list({it["voiceStudio"] for it in ep_items if it.get("voiceStudio")})
        claimed        = set()
        matched_voices = []

        # Сопоставляем каждый AnimeGO-голос с CVH-студией
        for v in ag_voices:
            studio = self._match_cvh_studio(v["label"], cvh_studios)
            if studio and studio not in claimed:
                claimed.add(studio)
                matched_voices.append({
                    "label":          v["label"],
                    "translation_id": v["translation_id"],
                    "cvh_studio":     studio,
                    "cvh_id":         cvh_id,
                })

        # CVH-студии без сопоставления — добавляем с translation_id=None
        for studio in cvh_studios:
            if studio not in claimed:
                matched_voices.append({
                    "label":          studio,   # CVH-имя как display-лейбл
                    "translation_id": None,
                    "cvh_studio":     studio,
                    "cvh_id":         cvh_id,
                })

        return {
            "voices":         matched_voices,
            "cvh_id":         cvh_id,
            "total_episodes": total,
        }

    async def get_stream_for_voice(
        self,
        voice_entry: dict,
        season: int,
        episode: int,
        anime: dict
    ) -> dict:
        """
        Получает поток CVH для конкретной озвучки и эпизода.

        voice_entry может быть:
        - из get_voices()          — содержит только "label" и "translation_id"
        - из get_matched_voices()  — содержит также "cvh_studio" и "cvh_id"
          (в этом случае HTML-запрос пропускается, cvh_studio используется
          для точного сопоставления в плейлисте)

        Если AnimeGO отдаёт этот эпизод через Aniboom —
        бросает errors.UnexpectedBehavior.

        :voice_entry: Элемент из get_voices() или get_matched_voices()
        :season:      Номер сезона (обычно 1)
        :episode:     Номер эпизода
        :anime:       Словарь из результатов search()

        Возвращает словарь (форматы по приоритету HLS > DASH > MP4):
          {"url": "https://.../.m3u8", "kind": "HLS"}
          {"url": "https://.../.mpd",  "kind": "DASH"}
          {"url": "https://.../.mp4",  "kind": "MP4"}

        Исключения:
        - errors.ServiceError       — HTTP-ошибка при запросе
        - errors.NoResults          — озвучка/эпизод не найдены в плейлисте CVH
        - errors.UnexpectedBehavior — эпизод не использует CVH-плеер
        """
        anime_id       = anime["id"]
        translation_id = voice_entry.get("translation_id")

        # Если cvh_id уже известен (из get_matched_voices) — пропускаем HTML-запрос
        cvh_id = voice_entry.get("cvh_id")
        if not cvh_id:
            if not translation_id:
                raise errors.UnexpectedBehavior(
                    "voice_entry должен содержать 'translation_id' или 'cvh_id'."
                )
            player_html = await self._get_player_html(anime_id, episode, translation_id)
            for pattern in [
                r'data-id="(\d+)"[^>]*data-provider="[Cc][Vv][Hh]"',
                r'data-provider="[Cc][Vv][Hh]"[^>]*data-id="(\d+)"',
                r'cdn-iframe/(\d+)/',
            ]:
                m = re.search(pattern, player_html)
                if m:
                    cvh_id = m.group(1)
                    break
            if not cvh_id:
                raise errors.UnexpectedBehavior(
                    f'Плеер CVH не найден для '
                    f'anime_id={anime_id}, S{season:02d}E{episode:02d}, '
                    f'translation_id={translation_id}. '
                    f'Возможно, этот эпизод использует Aniboom — попробуйте AniboomPlayerAsync.'
                )

        # Получаем плейлист; CVH хранит все студии в одном плейлисте
        items    = await self.get_playlist(cvh_id)
        ep_items = [
            it for it in items
            if it.get("season") == season and it.get("episode") == episode
        ]
        if not ep_items:
            raise errors.NoResults(
                f'Эпизод S{season:02d}E{episode:02d} не найден в плейлисте CVH '
                f'(cvh_id={cvh_id}, translation_id={translation_id}, '
                f'label={voice_entry.get("label")}).'
            )

        # Используем cvh_studio (из get_matched_voices) — иначе label
        studio_key = (voice_entry.get("cvh_studio") or voice_entry.get("label", "")).lower()

        # Проход 1: точное совпадение по voiceStudio
        matched = next(
            (it for it in ep_items if it.get("voiceStudio", "").lower() == studio_key),
            None
        )

        # Проход 2: fallback — только если в плейлисте ровно одна студия
        if matched is None:
            studios = {it.get("voiceStudio", "") for it in ep_items}
            if len(studios) == 1:
                matched = ep_items[0]
            else:
                raise errors.NoResults(
                    f'Озвучка "{voice_entry.get("label")}" не найдена в плейлисте CVH '
                    f'для эпизода S{season:02d}E{episode:02d} (cvh_id={cvh_id}). '
                    f'Доступные студии: {sorted(studios)}.'
                )

        vk_id = matched.get("vkId")
        if not vk_id:
            raise errors.NoResults(
                f'Поле vkId отсутствует в элементе плейлиста CVH '
                f'(cvh_id={cvh_id}, S{season:02d}E{episode:02d}, '
                f'studio={matched.get("voiceStudio")}).'
            )

        return await self.get_stream(vk_id)



    async def get_playlist(self, cvh_id: str) -> list:
        """
        Получает список эпизодов (items) для заданного cvh_id.
        :cvh_id: ID медиа в системе CdnVideoHub (передаётся AnimeGO в HTML плеера)
        Возвращает список словарей. Каждый элемент содержит как минимум:
        - "vkId"    — ID видео для передачи в get_stream()
        - "season"  — номер сезона
        - "episode" — номер эпизода

        Исключения:
        - errors.ServiceError — HTTP-ошибка или невалидный JSON
        - errors.NoResults    — сервер вернул пустой список
        """
        url = (
            f"{self._CVH_API_BASE}/playlist"
            f"?pub={self._PUB}&aggr={self._AGGR}&id={cvh_id}"
        )

        resp = await self._session.get(url, headers=self._CVH_HEADERS)
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при запросе плейлиста CVH (cvh_id={cvh_id}). '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        try:
            items = resp.json().get("items", [])
        except Exception as ex:
            raise errors.ServiceError(
                f'Ошибка при разборе JSON ответа плейлиста CVH (cvh_id={cvh_id}). '
                f'Ошибка: {ex}'
            )

        if not items:
            raise errors.NoResults(
                f'CVH вернул пустой список эпизодов для cvh_id={cvh_id}.'
            )

        return items

    async def get_stream(self, vk_id: str) -> dict:
        """
        Получает ссылку на поток конкретного видео по vk_id.
        :vk_id: ID видео в системе CVH (поле "vkId" из элемента плейлиста)
        Приоритет форматов: HLS > DASH > MP4.

        Возвращает словарь вида:
        {"url": "https://...", "kind": "HLS" | "DASH" | "MP4"}

        Исключения:
        - errors.ServiceError — HTTP-ошибка или невалидный JSON
        - errors.NoResults    — ни одного рабочего URL в ответе
        """
        url = f"{self._CVH_API_BASE}/video/{vk_id}"

        resp = await self._session.get(url, headers=self._CVH_HEADERS)
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при запросе видео CVH (vk_id={vk_id}). '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        try:
            data = resp.json()
        except Exception as ex:
            raise errors.ServiceError(
                f'Ошибка при разборе JSON ответа CVH (vk_id={vk_id}). '
                f'Ошибка: {ex}'
            )

        sources = data.get("sources", {})

        # Извлекаем доступные форматы
        hls = sources.get("hlsUrl")
        dash = sources.get("dashUrl") or sources.get("dashManifestUrl")

        # MP4 URL хранятся под ключами url360, url480, url720 и т.п.
        mp4s = [
            v for k, v in sources.items()
            if k.startswith("url") and isinstance(v, str) and v.startswith("http")
        ]

        # Выбираем лучший формат по приоритету: HLS > DASH > MP4
        if hls:
            return {"url": hls, "kind": "HLS"}
        elif dash:
            return {"url": dash, "kind": "DASH"}
        elif mp4s:
            # Берём последний MP4 — как правило максимальное качество
            return {"url": mp4s[-1], "kind": "MP4"}

        raise errors.NoResults(
            f'CVH не вернул ни одной рабочей ссылки для vk_id={vk_id}. '
            f'Содержимое sources: {sources}'
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
