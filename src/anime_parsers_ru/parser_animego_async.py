import html
import json
import re
from urllib.parse import quote
from bs4 import BeautifulSoup

try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True

try:
    from . import errors                        # Импорт при установленной библиотеке
    from .internal_tools import AsyncSession, TTLCache
except ImportError:
    import errors                               # Импорт при локальном запуске
    from internal_tools import AsyncSession, TTLCache


class AnimegoParserAsync:
    """
    Асинхронный парсер плеера AnimeGO.

    Отвечает исключительно за получение данных с сайта AnimeGO:
    - search               — поиск аниме на AnimeGO
    - get_voices           — получение доступных озвучек и embed ссылок на плееры
    - aniboom_get_stream_for_voice — Получение mpd плейлиста (и его содержания) указав anime id, translation id и номер серии
    - aniboom_get_stream — Получение mpd плейлиста (и его содержания) указав embed link (можно получить из функции get_voices)
    """

    # Базовый домен AnimeGO
    _ANIMEGO_BASE = "https://animego.org"
    # Базовый URL API плеера CVH
    _CVH_API_BASE = "https://plapi.cdnvideohub.com/api/v1/player/sv"

    # Параметры идентификации издателя и агрегатора для animego.org
    _PUB = "747"
    _AGGR = "mali"

    # Заголовки для запросов к CVH API
    _CVH_HEADERS = {
        "Referer": "https://animego.org/",
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
    }

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

    def __init__(self, mirror: str | None, proxy: str | None = None, use_lxml: bool = False, use_cache: bool = True, cache_maxsize: int = 300, cache_ttl: int = 36000) -> None:
        """
        :mirror: Зеркало сайта если animego.org заблокирован (по умолчанию None)
        :proxy: прокси для обхода блокировки, применяется ко всем запросам парсера (`http://host:port` или 'socks5://user:pass@host:port') (по умолчанию None)
        :use_lxml: Использовать lxml парсер для html (По умолчанию False)
        :use_cache: Использование кеширования, рекомендуется (По умолчанию True)
        :cache_maxsize: Максимальный размер кеша (по умолчанию 300)
        :cache_ttl: Время жизни кеша (по умолчанию 36000 сек = 10 часов)
        """
        if not LXML_WORKS and use_lxml:
            raise ImportWarning('Параметр use_lxml установлен в true, однако при попытке импорта lxml произошла ошибка')
        self.use_lxml = use_lxml
        self._session = AsyncSession(proxy=proxy)
        if mirror:
            self._ANIMEGO_BASE = f"https://{mirror}"
        self.use_cache = use_cache
        self._player_url_cache = TTLCache(cache_maxsize, cache_ttl) if use_cache else {}


    async def search(self, query: str) -> list:
        """
        Поиск аниме по названию на animego.org.
        :query: Строка поиска (название аниме)

        Возвращает список словарей вида:
        [
            {
                "link": "Ссылка на страницу аниме",
                "id": "Числовой ID аниме на animego.org",
                "slug": "slug-из-url (прим: naruto-shippuuden)",
                "title": "Название аниме",
                "original_title": "Оригинальное название (если есть, иначе None)",
                "image": "Ссылка на постер (если есть, иначе None)",
                "rating": "Оценка аниме (если есть, иначе None)"
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

        soup = BeautifulSoup(resp.text, "lxml") if self.use_lxml else BeautifulSoup(resp.text, "html.parser")
        results = []

        for item in soup.select("div.ani-grid__item"):
            res = {}
            # AnimeGO использует несколько вариантов разметки для ссылки на аниме
            link = (
                item.select_one("a.ani-grid__item-body") or
                item.select_one("div.ani-grid__item-title a") or
                item.select_one("a[href*='/anime/']")
            )
            if not link:
                continue

            href = link.get("href", "").strip("/")
            res['link'] = self._ANIMEGO_BASE+'/'+href
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
            res['id'] = anime_id
            res['slug'] = slug
            res['title'] = title

            rating = item.find('div', {'class': 'rating-badge'})
            res['rating'] = rating.text.strip() if rating else None

            img = item.find('img')
            res['image'] = img.get('src') if img else None
            orig_title = item.find('div', {'class': 'ani-grid__item-body'})
            res['original_title'] = x.text.strip() if orig_title and (x:=orig_title.find('div', {'class': 'fw-lighter'})) else None

            res['year'] = None
            res['type'] = None
            for extra in item.find_all('span', {'class': 'ani-grid__item-genres__link'}):
                if extra.text.isdigit():
                    res['year'] = int(extra.text)
                    continue
                if extra.text != '/':
                    res['type'] = extra.text
            results.append(res)

        if not results:
            raise errors.NoResults(
                f'По запросу "{query}" на AnimeGO ничего не найдено.'
            )

        return results
    
    async def anime_info(self, url: str) -> dict:
        """
        Возвращает данные об аниме.
        :url: Ссылка на страницу аниме на animego (прим: https://animego.me/anime/kulinarnyye-skitaniya-v-parallel-nom-mire-2-3261)

        Возвращает словарь вида:
{'aired_at': 'даты выхода',
 'anime_season': 'аниме сезон',
 'author': 'автор',
 'description': 'Описание',
 'director': 'Режиссёр',
 'duration': 'длительность',
 'episodes': 'эпизодов (если онгоинг, то вышло / всего)',
 'genres': ['список жанров'],
 'image': 'ссылка на картинку',
 'main_characters': [{'character': 'Персонаж',
                      'voice_actor': 'Актер озвучки в оригинале'}],
 'minimal_age': 'минимальный возраст зрителя',
 'mpaa_rating': 'рейтинг MPAA',
 'next_episode': 'дата выхода следующего эпизода (если онгоинг)',
 'original_source': 'первоисточник',
 'other_titles': 'другие названия',
 'related': [{'image': 'Ссылка на картинку',
              'link': 'Ссылка на animego',
              'relation': 'связь (предыстория, продолжение...)',
              'title': 'Название',
              'type': 'Тип',
              'year': 'Год выхода'}],
 'score': 'Оценка на анимего',
 'screenshots': ['список ссылок на скриншоты'],
 'status': 'Статус (Вышел, Онгоинг...)',
 'studio': 'Студия анимации',
 'theme': 'Тема',
 'title': 'Название',
 'translations': ['Список студий озвучки'],
 'type': 'Тип'}
        """
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

        soup = BeautifulSoup(resp.text, "lxml") if self.use_lxml else BeautifulSoup(resp.text, "html.parser")

        item = soup.find('div', {'class': 'entity'})
        if not item:
            raise errors.UnexpectedBehavior(f"Не найден родительский элемент для получения данных об аниме по ссылке \"{url}\". Возможно изменилась верстка страницы.")
        
        res = {}
        res['title'] = x.text.strip() if (x := item.find('div', {'class': 'entity__title'})) else None
        res['other_titles'] = x.text.strip() if (x := item.find('div', {'class': 'entity__title-synonyms'})) else None
        res['image'] = x.get('src') if (x := item.find('img', {'class': 'image__img'})) else None
        res['score'] = x.text if (x := item.find('span', {'class': 'entity-rating__value'})) else None

        res['type'] = res['studio'] = res['status'] = res['original_source'] = res['next_episode'] = res['mpaa_rating'] = res['theme'] = res['anime_season'] =\
            res['minimal_age'] = res['episodes'] = res['duration'] = res['director'] = res['aired_at'] = res['author'] = None # Добавляем все поля, чтобы избежать KeyError
        res['translations'] = res['related'] = res['main_characters'] = res['genres'] = []
        fields = item.find('div', {'class': 'entity-field'}).find_all('div')
        for el in range(0, len(fields), 2):
            k = fields[el].text.strip()
            v = fields[el+1].text.strip()
            if k == 'Тип':
                res['type'] = v
            elif k == 'Эпизоды':
                res['episodes'] = v
            elif k == 'Жанры':
                res['genres'] = []
                for a in fields[el+1].find_all('a'):
                    res['genres'].append(a.text)
            elif k == 'Тема':
                res['theme'] = v
            elif k == 'Первоисточник':
                res['original_source'] = v
            elif k == 'Сезон':
                res['anime_season'] = v
            elif k == 'Статус':
                res['status'] = v
            elif k == 'Выпуск':
                res['aired_at'] = v
            elif k == 'Рейтинг':
                res['mpaa_rating'] = v
            elif k == 'Возраст':
                res['minimal_age'] = v
            elif k == 'Длительность':
                res['duration'] = v
            elif k == 'Студия':
                res['studio'] = v
            elif k == 'Озвучка':
                res['translations'] = []
                for a in fields[el+1].find_all('a'):
                    res['translations'].append(a.text)
            elif k == 'Автор':
                res['author'] = v
            elif k == 'Главные герои':
                res['main_characters'] = []
                for a in fields[el+1].find_all('a', recursive=False):
                    res['main_characters'].append({'character': a.text, 'voice_actor': None})
                for i, sp in enumerate(fields[el+1].find_all('span')):
                    res['main_characters'][i]['voice_actor'] = sp.text.strip('() ')
            elif k == 'Следующий эпизод':
                res['next_episode'] = v
            elif k == 'Режиссёр':
                res['director'] = v
        
        res['description'] = x.text.strip() if (x := item.find('div', {'class': 'description'})) else None

        screenshots_cont = item.find('div', {'class': 'screenshots'})
        res['screenshots'] = []
        if screenshots_cont:
            for img in screenshots_cont.find_all('img'):
                res['screenshots'].append(img.get('src'))

        related_cont = item.find('div', {'class': 'seasons'})
        res['related'] = []
        if related_cont:
            for rel in related_cont.find_all('div', {'class': 'seasons-item'}):
                a = rel.find('a')
                img = rel.find('img')
                info = rel.find('div', {'class': 'seasons__info'})
                spans = info.find_all('span') if info else None
                relation = info.find_all('div')[-1] if info else None
                res['related'].append({
                    'title': a.text.strip(),
                    'link': self._ANIMEGO_BASE+a.get('href'),
                    'image': img.get('src') if img else None,
                    'type': spans[0].text.strip() if spans else None,
                    'year': spans[-1].text.strip() if spans else None,
                    'relation': relation.text.strip() if relation else None
                })

        return res

    async def get_episodes_info(self, anime_id: str) -> list:
        """
        Получение информации по эпизодам для аниме

        :anime_id: id аниме на animego

        Возвращает список словарей вида:
        [
            {
                'air_date': 'дата выхода',
                'is_released': вышло или нет (bool),
                'seria': номер серии,
                'title': 'Название серии (или --- если не указано)'
            }
        ]
        """
        url = f"https://animego.me/anime/{anime_id}/9999999/schedule/load"
        resp = await self._session.get(url, headers={
            "User-Agent": self._PLAYER_HEADERS["User-Agent"],
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://animego.me"
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

        # Сервер возвращает JSON, HTML плеера лежит в data.content
        try:
            data = resp.json()
            data = html.unescape(data.get("data", {}).get("content", ""))
        except Exception as ex:
            raise errors.UnexpectedBehavior(
                f'Не удалось разобрать JSON ответа плеера AnimeGO (url=\"{url}\"). '
                f'Ошибка: {ex}'
            )
        soup = BeautifulSoup(data, "lxml") if self.use_lxml else BeautifulSoup(data, "html.parser")

        res = []
        divs = soup.find_all('div', recursive=False)
        for div_i in range(0, len(divs), 4):
            num = int(divs[div_i].get('data-label').strip('. '))
            title = divs[div_i+1].text.strip()
            date = divs[div_i+2].text.strip()
            is_released = True if divs[div_i+3].find('div') else False
            res.append({"seria": num, "title": title, "air_date": date, "is_released": is_released})
        return sorted(res, key=lambda x: x['seria'])
    
    async def _get_main_page(self) -> BeautifulSoup:
        """
        Получение информации с домашней страницы, возвращает объект BeautifulSoup
        """

        resp = await self._session.get(self._ANIMEGO_BASE, headers={
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
                f'Ошибка при запросе на AnimeGO. '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        return BeautifulSoup(resp.text, "lxml") if self.use_lxml else BeautifulSoup(resp.text, "html.parser")
    
    async def get_schedule(self) -> dict:
        """
        Возвращает расписание на текущую неделю.

        Возвращает словарь вида:
        {
            'schedule': {
                'Понедельник': [
                    {   'episode': 'Номер эпизода',
                        'image': 'Ссылка на картинку',
                        'link': 'Ссылка на аниме на animego',
                        'time': 'Время выхода',
                        'title': 'Название'
                    },
                    ...
                ],
                'Вторник': ...
            },
            'schedule_dates': {
                'Понедельник': 'дата (либо: Сегодня, Завтра)',
                'Вторник': ...
            }
        }
        """
        soup = await self._get_main_page()
        res = {}
        res['schedule'] = {'Понедельник': [], 'Вторник': [], 'Среда': [], 'Четверг': [], 'Пятница': [], 'Суббота': [], 'Воскресенье': []}
        res['schedule_dates'] = {'Понедельник': None, 'Вторник': None, 'Среда': None, 'Четверг': None, 'Пятница': None, 'Суббота': None, 'Воскресенье': None}

        for day in soup.find_all('div', {'class': 'aw-day'}):
            day_title = day.find('span', {'class': 'schedule-day'}).text.strip()
            day_date = day.find('span', {'class': re.compile(r'schedule-(tomorrow|date|today)')}).text.strip()
            data = self._get_entries_from_container(day.find('div', {'class': 'collapse'}))
            res['schedule'][day_title] = data
            res['schedule_dates'][day_title] = day_date
        return res
    
    async def get_anime_updates(self) -> list:
        """
        Возвращает список последних обновлений аниме на сайте.

        Возвращает список вида:
        [
            {
                'episode': 'номер эпизода',
                'image': 'Ссылка на картинку',
                'link': 'Ссылка на аниме на animego',
                'time': 'Время',
                'title': 'Название',
                'translation': 'Студия озвучки/субтитры'
            },
            ...
        ]
        """
        soup = await self._get_main_page()
        return self._get_entries_from_updates_container(soup.find('div', {'class': 'updates-body'}))
    
    async def get_anime_from_current_season(self) -> list:
        """
        Возвращает список аниме из текущего сезона.

        Возвращает список вида:
        [
            {
                'image': 'Ссылка на картинку',
                'link': 'Ссылка на аниме на animego',
                'other_title': 'Другое (оригинальное) название',
                'score': 'Оценка',
                'title': 'Название'
            },
        ]
        """
        soup = await self._get_main_page()
        season_section = soup.find('section', {'class': 'season-section'})
        res = []
        if season_section:
            for el in season_section.find_all('div', {'class': 'ani-grid__item'}):
                try:
                    a = el.find('a')
                    res.append({
                        'title': x.text.strip() if (x := el.find('div', {'class': 'ani-grid__item-title'})) else None,
                        'other_title': x.text.strip() if (x := el.find('div', {'class': 'fw-lighter'})) else None,
                        'image': x.get('src') if (x := a.find('img')) else None,
                        'link': self._ANIMEGO_BASE+a.get('href'),
                        'score': x.text.strip() if (x := el.find('div', {'class': 'rating-badge'})) else None
                    })
                except:
                    pass
        return res
    
    def _get_entries_from_container(self, container: BeautifulSoup) -> list:
        res = []
        for el in container.find_all('a', {'class': 'aw-item'}):
            try:
                meta = x.text.strip() if (x := el.find('div', {'class': 'aw-meta'})) else None 
                res.append({
                    'link': self._ANIMEGO_BASE+el.get('href'),
                    'image': x.get('src') if (x := el.find('img')) else None,
                    'title': x.text.strip() if (x := el.find('div', {'class': 'aw-name'})) else None,
                    'episode': meta[meta.find('Серия')+5:(meta.find('(из') if '(из' in meta else meta.find('—'))].strip() if meta and 'Серия' in meta else None,
                    'time': meta[meta.rfind('—')+1:].strip() if meta else None
                })
            except:
                pass
        return res
    
    def _get_entries_from_updates_container(self, container: BeautifulSoup) -> list:
        res = []
        for el in container.find_all('a', {'class': 'aw-item'}):
            try:
                meta = x.text.strip() if (x := el.find('div', {'class': 'aw-meta'})) else None 
                res.append({
                    'link': self._ANIMEGO_BASE+el.get('href').replace('#player', ''),
                    'image': x.get('src') if (x := el.find('img')) else None,
                    'title': x.text.strip() if (x := el.find('div', {'class': 'aw-name'})) else None,
                    'episode': meta[meta.find('Серия')+5:meta.find('·')].strip() if meta and 'Серия' in meta else None,
                    'time': meta[meta.rfind('—')+1:].strip() if meta else None,
                    'translation': meta[meta.find('· ')+2:meta.find('—')].strip() if meta and 'Серия' in meta else None,
                })
            except:
                pass
        return res
    
    @staticmethod
    def get_id_from_link(link: str) -> str:
        """
        Возвращает id из ссылки
        """
        return link[link.rfind('-')+1:]

    async def get_voices(self, anime_id: str, episode: int = 1) -> dict:
        """
        Получает список доступных озвучек и общее число эпизодов.
        :anime_id: animego id аниме 
        Возвращает словарь вида:
        {
            "voices": [
                {
                    "label": "Название озвучки",
                    "translation_id": "ID для передачи в get_stream_for_voice()",
                    "player": "Тип плеера (kodik, aniboom, cvh, ...)"
                    "embed": "Ссылка на embed",
                    "cvh_id": "id для получения плейлиста CVH (только для cvh-плеера, иначе None)"
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
        
        url = await self._get_player_url_for_episode(anime_id, episode)
        content = await self._get_player_html(url)

        soup = BeautifulSoup(content, "lxml") if self.use_lxml else BeautifulSoup(content, "html.parser")

        # Кнопки озвучки содержат атрибут data-translation с её ID
        buttons = soup.find('div', {'id': 'provider'}).find_all("button")

        if not buttons:
            raise errors.NoResults(
                f'Кнопки выбора озвучки не найдены для аниме id={anime_id}. '
                f'Возможно, переводы отсутствуют или структура страницы изменилась.'
            )

        voices = []
        for btn in buttons:
            translation_id = btn.get("data-ptranslation")
            provider = btn.get('data-provider-title')
            embed = 'https:'+btn.get('data-player')
            name = btn.get("data-translation-title")
            if translation_id and name:
                # Убираем суффикс "(ошибка)" — так AnimeGO помечает нерабочие озвучки
                label = name.replace(" (ошибка)", "").strip()
                voices.append({"label": label, "translation_id": translation_id, "player": provider, "embed": embed, 
                               "cvh_id": embed[embed.find("cdn-iframe/")+11:embed.find("/", embed.find("cdn-iframe/")+11)] if provider == "CVH" else None})

        # Максимальный номер эпизода из элементов с data-episode
        ep_nums = []
        for el in soup.find_all(attrs={"data-episode": True}):
            try:
                ep_nums.append(int(el.text.strip()))
            except ValueError:
                pass
        total_episodes = max(ep_nums) if ep_nums else None

        return {"voices": voices, "total_episodes": total_episodes}
    
    async def _get_player_url_for_episode(self, anime_id: str, episode: int = 1) -> str:
        if episode == 1:
            return f"{self._ANIMEGO_BASE}/player/{anime_id}"
        
        cache_key = f"{anime_id}_ep_{episode}"
        if self.use_cache and cache_key in self._player_url_cache:
            return self._player_url_cache[cache_key]
        
        content = await self._get_player_html(f"{self._ANIMEGO_BASE}/player/{anime_id}")
        
        soup = BeautifulSoup(content, "lxml") if self.use_lxml else BeautifulSoup(content, "html.parser")
        
        res = None
        for el in soup.find_all(attrs={"data-episode": True}):
            try:
                num = int(el.get('data-episode-number').strip())
                if self.use_cache:
                    url = f"{self._ANIMEGO_BASE}/player/videos/{el.get('data-episode')}"
                    self._player_url_cache[f"{anime_id}_ep_{num}"] = url
                    if num == episode:
                        res = url
                else:
                    if num == episode:
                        return f"{self._ANIMEGO_BASE}/player/videos/{el.get('data-episode')}"
            except ValueError:
                pass
        
        if res:
            return res
        raise ValueError(f"Указанный эпизод ({episode}) отсутствует в списке эпизодов.")


    async def aniboom_get_stream_for_voice(
        self,
        translation_id: str,
        episode: int,
        anime_id: str
    ) -> dict:
        """
        Получает поток Aniboom для конкретной озвучки и эпизода.
        Если AnimeGO отдаёт этот эпизод через CVH, а не Aniboom —
        бросает errors.UnexpectedBehavior. В этом случае используйте CVHPlayerAsync.

        :translation_id: Id перевода
        :episode: Номер эпизода
        :anime_id: Id аниме

        Возвращает словарь:
        {
            "url": "https://.../.mpd" или "https://.../.m3u8",
            "content": "Содержимое файла"
        }

        Исключения:
        - errors.ServiceError       — HTTP-ошибка при запросе
        - errors.UnexpectedBehavior — эпизод не использует Aniboom-плеер
        """
        data = await self.get_voices(anime_id, episode)
        for v in data['voices']:
            if v['translation_id'] == translation_id and v['player'] == 'AniBoom':
                return await self.aniboom_get_stream(v['embed'])
        raise errors.UnexpectedBehavior(f"Для аниме с id \"{anime_id}\", translation_id \"{translation_id}\" и episode={episode} не найдено aniboom плеера.")

    async def aniboom_get_stream(self, embed_url: str) -> dict:
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

    async def cvh_get_playlist(self, cvh_id: str) -> list:
        """
        Получает список эпизодов (items) для заданного cvh_id.
        :cvh_id: ID медиа в системе CdnVideoHub (передаётся AnimeGO в HTML плеера)
        Возвращает список словарь вида:
        {
            season_number: {
                episode_number: [
                    {
                        'cvh_id': '019d...11',
                        'episode': номер эпизода,
                        'season': номер сезона,
                        'name': 'Название серии (обычно пустое)',
                        'vkId': 'ID видео в системе CVH, нужен для получения ссылок на потоки через cvh_get_stream()',
                        'voiceStudio': 'Название студии озвучки (напр. AnilibriaTV)',
                        'voiceType': 'Тип озвучки/субтитры'
                    }
                ]
            }
        }

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
        
        res = {}
        for item in items:
            season = item["season"]
            episode = item["episode"]
            if season not in res.keys():
                res[season] = {}
            if episode not in res[season].keys():
                res[season][episode] = []
            res[season][episode].append(item)

        return res
    
    async def cvh_get_stream(self, cvh_id: str, season: int, episode: int, translation: str) -> dict:
        """
        Получает ссылку на поток конкретного видео по cvh_id.
        :cvh_id: ID медиа в системе CVH
        :season: Номер сезона (если в результате вернется только один сезон, это значение будет проигнорировано)
        :episode: Номер эпизода
        :translation: Название озвучки

        Возвращает словарь вида:
        {
            "HLS": "https://.../.m3u8" или None,
            "DASH": "https://.../.mpd" или None,
            "MP4s": ["https://.../360p.mp4", "https://.../720p.mp4"] или []
        }
        Исключения:
        - errors.ServiceError — HTTP-ошибка или невалидный JSON
        - errors.NoResults    — ни одного рабочего URL в ответе или не найдено совпадение для озвучки
        """
        playlist = await self.cvh_get_playlist(cvh_id)
        if len(playlist) == 1:
            season = list(playlist.keys())[0]
        if season not in playlist.keys():
            raise errors.NoResults(f'Сезон {season} не найден в плейлисте CVH для cvh_id={cvh_id}.')
        if episode not in playlist[season].keys():
            raise errors.NoResults(f'Эпизод {episode} не найден в сезоне {season} плейлиста CVH для cvh_id={cvh_id}.')
        _cvh_studios = []
        for ep in playlist[season][episode]:
            if ep['voiceStudio'] not in _cvh_studios:
                _cvh_studios.append(ep['voiceStudio'])

        matched_studio = self._match_cvh_studio(translation, _cvh_studios)
        if not matched_studio:
            raise errors.NoResults(
                f'Не найдено совпадение для озвучки "{translation}" в CVH. '
                f'Доступные студии для сезона {season} эпизода {episode}: {_cvh_studios}.'
            )
        for ep in playlist[season][episode]:
            if ep['voiceStudio'] == matched_studio:
                return await self.cvh_get_stream_by_id(ep['vkId'])

    async def cvh_get_stream_by_id(self, vk_id: str) -> dict:
        """
        Получает ссылку на поток конкретного видео по vk_id.
        :vk_id: ID видео в системе CVH (поле "vkId" из элемента плейлиста)

        Возвращает словарь вида:
        {
            "HLS": "https://.../.m3u8" или None,
            "DASH": "https://.../.mpd" или None,
            "MP4s": ["https://.../360p.mp4", "https://.../720p.mp4"] или []
        }

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
        if hls is None and dash is None and not mp4s:
            raise errors.NoResults(
                f'CVH не вернул ни одной рабочей ссылки для vk_id={vk_id}. '
                f'Содержимое sources: {sources}'
            )
        return {
            "HLS": hls if hls else None,
            "DASH": dash if dash else None,
            "MP4s": mp4s
        }
        
    
    async def _get_player_html(self, url: str) -> str:
        resp = await self._session.get(url, headers=self._PLAYER_HEADERS)

        if resp.status_code in (403, 503) or "Cloudflare" in resp.text:
            raise errors.ServiceError(
                f'AnimeGO вернул статус {resp.status_code} при запросе плеера (url=\"{url}\"). '
                f'Возможна блокировка Cloudflare.'
            )
        if resp.status_code == 404:
            raise errors.NoResults(
                f'Плеер с url=\"{url}\" не найдено на AnimeGO (404).'
            )
        if resp.status_code != 200:
            raise errors.ServiceError(
                f'Ошибка при запросе плеера AnimeGO (url=\"{url}\"). '
                f'Ожидался код 200, получен: {resp.status_code}'
            )

        # Сервер возвращает JSON, HTML плеера лежит в data.content
        try:
            data = resp.json()
            return html.unescape(data.get("data", {}).get("content", ""))
        except Exception as ex:
            raise errors.UnexpectedBehavior(
                f'Не удалось разобрать JSON ответа плеера AnimeGO (url=\"{url}\"). '
                f'Ошибка: {ex}'
            )

    async def close(self) -> None:
        """Закрывает внутреннюю HTTP-сессию."""
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
