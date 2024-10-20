import requests
try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True
import json
from bs4 import BeautifulSoup as Soup
from base64 import b64decode

import anime_parsers_ru.errors as errors
from anime_parsers_ru.internal_tools import AsyncSession

class KodikParserAsync:
    """
    Асинхронный парсер для плеера Kodik
    """
    def __init__(self, token: str|None = None, use_lxml: bool = False) -> None:
        """
        :token: токен kodik для поиска по его базе. Если не указан будет произведена попытка автоматического получения токена
        :use_lxml: использовать lxml парсер (в некоторых случаях lxml может не работать)
        """
        if token is None:
            try:
                token = self.get_token_sync()
            except Exception as ex:
                raise errors.ServiceError(f'Произошла ошибка при попытке автоматического получения токена kodik. Ошибка: {ex}')
        self.TOKEN = token
        if not LXML_WORKS and use_lxml:
            raise ImportWarning('Параметр use_lxml установлен в true, однако при попытке импорта lxml произошла ошибка')
        self.USE_LXML = use_lxml
        self.requests = AsyncSession()

    async def base_search(self, title: str, limit: int = 50, include_material_data: bool = True) -> dict:
        """
        ### Для использования требуется токен kodik
        Прямой запрос к базе кодика без дополнительных преобразований

        :title: Название аниме / фильма / сериала
        :limit: Верхнее ограничение количества ответов
        :include_material_data: Добавлять в ответ дополнительные данные о сериале

        Возвращает словарь следующего вида (на запрос 'Наруто'):
        Некоторые параметры могут отличаться в зависимости от типа/состояния контента
        {
            "time": "18ms",
            "total": 50,
            "results": [
                {
                    "id": "movie-20609",
                    "type": "anime",
                    "link": "//kodik.info/video/20609/e8fd5bc1190b7eb1ee1a3e1c3aec5f62/720p",
                    "title": "Наруто 4",
                    "title_orig": "Gekijô-ban Naruto shippûden",
                    "other_title": "Наруто (фильм четвёртый) - Смерть Наруто / Наруто: Ураганные Хроники - Адепты Тёмного царства",
                    "translation": {
                        "id": 767,
                        "title": "SHIZA Project",
                        "type": "voice"
                    },
                    "year": 2007,
                    "kinopoisk_id": "283418",
                    "imdb_id": "tt0988982",
                    "worldart_link": "http://www.world-art.ru/animation/animation.php?id=6476",
                    "shikimori_id": "2472",
                    "quality": "BDRip 720p",
                    "camrip": false,
                    "lgbt": false,
                    "blocked_countries": [],
                    "created_at": "2018-01-21T13:18:37Z",
                    "updated_at": "2019-11-16T22:13:46Z",
                    "screenshots": [
                        "https://i.kodik.biz/screenshots/video/20609/1.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/2.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/3.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/4.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/5.jpg"
                    ]
                },
                ...
            ],
        }
        """
        if self.TOKEN is None:
            raise errors.TokenError('Токен kodik не указан')
        payload = {
            "token": self.TOKEN,
            "title": title,
            "limit": limit,
            "with_material_data": 'true' if include_material_data else 'false'
        }
        url = "https://kodikapi.com/search"
        data = await self.requests.post(url, data=payload)
        data = data.json()
        
        if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
            raise errors.TokenError('Отсутствует или неверный токен')
        elif 'error' in data.keys():
            raise errors.ServiceError(data['error'])
        if data['total'] == 0:
            raise errors.NoResults(f'По запросу "{title}" ничего не найдено')
        return data
    
    async def base_search_by_id(self, id: str, id_type: str, limit: int = 50, include_material_data: bool = True) -> dict:
        """
        ### Для использования требуется токен kodik
        Прямой запрос к базе кодика без дополнительных преобразований

        :id: id аниме на одном из сайтов
        :id_type: с какого сайта id (Поддерживается: shikimori, kinopoisk, imdb)
        :limit: Верхнее ограничение количества ответов
        :include_material_data: Добавлять в ответ дополнительные данные о сериале

        Возвращает словарь следующего вида (на запрос 'Наруто'):
        Некоторые параметры могут отличаться в зависимости от типа/состояния контента
        {
            "time": "18ms",
            "total": 50,
            "results": [
                {
                    "id": "movie-20609",
                    "type": "anime",
                    "link": "//kodik.info/video/20609/e8fd5bc1190b7eb1ee1a3e1c3aec5f62/720p",
                    "title": "Наруто 4",
                    "title_orig": "Gekijô-ban Naruto shippûden",
                    "other_title": "Наруто (фильм четвёртый) - Смерть Наруто / Наруто: Ураганные Хроники - Адепты Тёмного царства",
                    "translation": {
                        "id": 767,
                        "title": "SHIZA Project",
                        "type": "voice"
                    },
                    "year": 2007,
                    "kinopoisk_id": "283418",
                    "imdb_id": "tt0988982",
                    "worldart_link": "http://www.world-art.ru/animation/animation.php?id=6476",
                    "shikimori_id": "2472",
                    "quality": "BDRip 720p",
                    "camrip": false,
                    "lgbt": false,
                    "blocked_countries": [],
                    "created_at": "2018-01-21T13:18:37Z",
                    "updated_at": "2019-11-16T22:13:46Z",
                    "screenshots": [
                        "https://i.kodik.biz/screenshots/video/20609/1.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/2.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/3.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/4.jpg",
                        "https://i.kodik.biz/screenshots/video/20609/5.jpg"
                    ]
                },
                ...
            ],
        }
        """
        if self.TOKEN is None:
            raise errors.TokenError('Токен kodik не указан')
        if id_type not in ['shikimori', 'kinopoisk', 'imdb']:
            raise errors.PostArgumentsError(f'Поддерживаются только id shikimori, kinopoisk, imdb. Получено: {id_type}')
        payload = {
            "token": self.TOKEN,
            f"{id_type}_id": id,
            "limit": limit,
            "with_material_data": 'true' if include_material_data else 'false'
        }
        url = "https://kodikapi.com/search"
        data = await self.requests.post(url, data=payload)
        data = data.json()
        
        if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
            raise errors.TokenError('Отсутствует или неверный токен')
        elif 'error' in data.keys():
            raise errors.ServiceError(data['error'])
        if data['total'] == 0:
            raise errors.NoResults(f'По id {id_type} "{id}" ничего не найдено')
        return data
    
    async def get_list(self, limit_per_page: int = 50, pages_to_parse: int = 1, include_material_data: bool = True, only_anime: bool = False, start_from: str|None = None) -> tuple[list[dict],str]:
        """
        Получение случайного списка аниме от кодика (скорее всего это будут онгоинги)

        :limit_per_page: Ограничение на количество результатов на запрос(страницу), не все элементы в списке будут аниме (по умолчанию 50)
        :pages_to_parse: Ограничение на количество страниц для обработки (каждая страница - отдельный запрос) (по умолчанию 1)
        :include_material_data: Добавление дополнительных данных (необязательно, по умолчанию True)
        :only_anime: Возвращать только варианты аниме (тип anime или anime-serial) (по умолчанию False)
        :start_from: Поиск следующих страниц по заданному id (id возвращается вторым элементом кортежа) (по умолчанию None)

        Возвращает кортеж из списка словарей и id страницы:
        (
            [
            {
                "title": "Название",
                "type": "тип мультимедия (anime, film, ...)",
                "year": "Год выпуска фильма",
                "screenshots": [
                    "ссылки на скриншоты"
                ],
                "shikimori_id": "Id шикимори, если нет - None",
                "kinopoisk_id": "Id кинопоиска, если нет - None",
                "imdb_id": "Id imdb, если нет - None",
                "worldart_link": "ссылка на worldart, если нет - None",
                "additional_data": {
                    "Здесь будут находится все остальные данные выданные кодиком, не связанные с отдельным переводом"
                },
                "material_data": { 
                    "Здесь будут все данные о сериале имеющиеся у кодика. (None если указан параметр include_material_data=False)
                    В том числе оценки на шикимори, статус выхода, даты анонсов, выхода, все возможные названия, жанры, студии и многое другое."
                },
                "link": "ссылка на kodik.info (Пример: //kodik.info/video/20609/e8fd5bc1190b7eb1ee1a3e1c3aec5f62/720p)"
            },
            ...
            ],
            "next_page_id": "id следующей страницы (для последовательного парсинга нескольких страниц) (может быть None, если след. страниц нет)"
        )
        """
        if self.TOKEN is None:
            raise errors.TokenError('Токен kodik не указан')
        results = []
        next_page = start_from
        payload = {
            "token": self.TOKEN,
            "limit": limit_per_page,
            "with_material_data": 'true' if include_material_data else 'false'
        }
        for _ in range(pages_to_parse):
            if next_page != None:
                payload['next'] = next_page
            url = "https://kodikapi.com/list"
            data = await self.requests.post(url, data=payload)
            data = data.json()
            
            if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
                raise errors.TokenError('Отсутствует или неверный токен')
            elif 'error' in data.keys():
                raise errors.ServiceError(data['error'])
            if data['total'] == 0:
                raise errors.NoResults(f'Ничего не найдено. Скорее всего произошла ошибка, попробуйте позже или сообщите об ошибке на гитхабе.')
            if 'next_page' in data.keys():
                next_page = data['next_page'][data['next_page'].rfind('=')+1:]
            else:
                next_page = None
            results += data['results']
        return (self._prettify_data(results, only_anime=only_anime), next_page)

    async def search(self, title: str, limit: int|None = None, include_material_data: bool = True, only_anime: bool = False) -> list:
        """
        ### Для использования требуется токен kodik
        Получение только самых основных данных о сериале.
        Для получения всех данных воспользуйтесь функцией base_search

        :title: Название аниме / фильма / сериала
        :limit: Верхнее ограничение количества ответов для base_search (необязательно)

        Возвращает список словарей в следующем виде:
        [
        {
            "title": "Название",
            "type": "тип мультимедия (anime, film, ...)",
            "year": "Год выпуска фильма",
            "screenshots": [
                "ссылки на скриншоты"
            ],
            "shikimori_id": "Id шикимори, если нет - None",
            "kinopoisk_id": "Id кинопоиска, если нет - None",
            "imdb_id": "Id imdb, если нет - None",
            "worldart_link": "ссылка на worldart, если нет - None",
            "additional_data": {
                "Здесь будут находится все остальные данные выданные кодиком, не связанные с отдельным переводом"
            },
            "material_data": { 
                "Здесь будут все данные о сериале имеющиеся у кодика. (None если указан параметр include_material_data=False)
                В том числе оценки на шикимори, статус выхода, даты анонсов, выхода, все возможные названия, жанры, студии и многое другое."
            },
            "link": "ссылка на kodik.info (Пример: //kodik.info/video/20609/e8fd5bc1190b7eb1ee1a3e1c3aec5f62/720p)"
        },
        ...
        ]
        """
        if limit is None:
            search_data = await self.base_search(title, include_material_data=include_material_data)
        else:
            search_data = await self.base_search(title, limit, include_material_data=include_material_data)
        return self._prettify_data(search_data['results'], only_anime=only_anime)
    
    async def search_by_id(self, id: str, id_type: str, limit: int|None = None) -> list:
        """
        ### Для использования требуется токен kodik
        Получение только самых основных данных о сериале.
        Для получения всех данных воспользуйтесь функцией base_search

        :id: id аниме на одном из сайтов
        :id_type: с какого сайта id (Поддерживается: shikimori, kinopoisk, imdb)
        :limit: Верхнее ограничение количества ответов для base_search (необязательно)

        Возвращает список словарей в следующем виде:
        [
        {
            "title": "Название",
            "type": "тип мультимедия (anime, film, ...)",
            "year": "Год выпуска фильма",
            "screenshots": [
                "ссылки на скриншоты"
            ],
            "shikimori_id": "Id шикимори, если нет - None",
            "kinopoisk_id": "Id кинопоиска, если нет - None",
            "imdb_id": "Id imdb, если нет - None",
            "worldart_link": "ссылка на worldart, если нет - None",
            "additional_data": {
                "Здесь будут находится все остальные данные выданные кодиком, не связанные с отдельным переводом"
            },
            "material_data": { 
                "Здесь будут все данные о сериале имеющиеся у кодика. (None если указан параметр include_material_data=False)
                В том числе оценки на шикимори, статус выхода, даты анонсов, выхода, все возможные названия, жанры, студии и многое другое."
            },
            "link": "ссылка на kodik.info (Пример: //kodik.info/video/20609/e8fd5bc1190b7eb1ee1a3e1c3aec5f62/720p)"
        },
        ...
        ]
        """
        if limit is None:
            search_data = await self.base_search_by_id(id, id_type, include_material_data=True)
        else:
            search_data = await self.base_search_by_id(id, id_type, limit, include_material_data=True)
        return self._prettify_data(search_data['results'])

    def _prettify_data(self, results: list[dict], only_anime: bool = False) -> list[dict]:
        """
        Превращает полченные данные от запроса кодику в удобный вариант словаря

        :results: список словарей (response['results'] в json'е от кодика)
        :only_anime: Возвращать только варианты аниме (тип anime или anime-serial) (по умолчанию False)
        """
        data = []
        added_titles = []
        for res in results:
            if only_anime and res['type'] not in ['anime-serial', 'anime']:
                continue
            if res['title'] not in added_titles:
                additional_data = {}
                for k, i in res.items():
                    if k not in ['title', 'type', 'year', 'screenshots', 'translation',
                                 'shikimori_id', 'kinopoisk_id', 'imdb_id', 'worldart_link',
                                 'id', 'link', 'title_orig', 'other_title', 'created_at', 
                                 'updated_at', 'quality', 'material_data', 'link']:
                        additional_data[k] = i
                
                data.append({
                    'title': res['title'],
                    'title_orig': res['title_orig'],
                    'other_title': res['other_title'] if 'other_title' in res.keys() else None,
                    'type': res['type'],
                    'year': res['year'],
                    'screenshots': res['screenshots'],
                    'shikimori_id': res['shikimori_id'] if 'shikimori_id' in res.keys() else None,
                    'kinopoisk_id': res['kinopoisk_id'] if 'kinopoisk_id' in res.keys() else None,
                    'imdb_id': res['imdb_id'] if 'imdb_id' in res.keys() else None,
                    'worldart_link': res['worldart_link'] if 'worldart_link' in res.keys() else None,
                    'additional_data': additional_data,
                    'material_data': res['material_data'] if 'material_data' in res.keys() else None,
                    'link': res['link']
                })
                added_titles.append(res['title'])
        return data
    
    async def translations(self, id: str, id_type: str) -> list:
        """
        ### Для использования требуется токен kodik
        Возвращает список переводов для медиафайла по id.

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)

        Пример возвращаемого:
        [
            {
                'id': id перевода/субтитров/озвучки
                'type': тип (voice/subtitles)
                'name': Имя автора озвучки/субтитров
            },
            ...
        ]
        """
        data = await self.get_info(id, id_type)
        return data['translations']
    
    async def series_count(self, id: str, id_type: str) -> int:
        """
        ### Для использования требуется токен kodik
        Возвращает количество серий для медиафайла по id.

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)
        """
        data = await self.get_info(id, id_type)
        return data['series_count']

    async def _link_to_info(self, id: str, id_type: str, https: bool = True) -> str:
        """
        ### Для использования требуется токен kodik
        Получить ссылку до страницы с данными.

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)

        Возвращает ссылку
        """
        if self.TOKEN is None:
            raise errors.TokenError('Токен kodik не указан')
        if id_type == "shikimori":
            serv = f"https://kodikapi.com/get-player?title=Player&hasPlayer=false&url=https%3A%2F%2Fkodikdb.com%2Ffind-player%3FshikimoriID%3D{id}&token={self.TOKEN}&shikimoriID={id}"
        elif id_type == "kinopoisk":
            serv = f"https://kodikapi.com/get-player?title=Player&hasPlayer=false&url=https%3A%2F%2Fkodikdb.com%2Ffind-player%3FkinopoiskID%3D{id}&token={self.TOKEN}&kinopoiskID={id}"
        elif id_type == "imdb":
            serv = f"https://kodikapi.com/get-player?title=Player&hasPlayer=false&url=https%3A%2F%2Fkodikdb.com%2Ffind-player%3FkinopoiskID%3D{id}&token={self.TOKEN}&imdbID={id}"
        else:
            raise ValueError("Неизвестный тип id")
        data = await self.requests.get(serv)
        data = data.json()
        if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
            raise errors.TokenError('Отсутствует или неверный токен')
        elif 'error' in data.keys():
            raise errors.ServiceError(data['error'])
        if not data['found']:
            raise errors.NoResults(f'Нет данных по {id_type} id "{id}"')
        return 'https:'+data['link'] if https else 'http:'+data['link']
    
    async def get_info(self, id: str, id_type: str) -> dict:
        """
        ### Для использования требуется токен kodik

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)
        
        Возвращает данные:
        {
            'series_count': количество серий (если серий нет/фильм значение будет 0)
            'translations': [
                {
                    'id': id перевода/субтитров/озвучки
                    'type': тип (voice/subtitles)
                    'name': Имя автора озвучки/субтитров
                },
                ...
            ]
        }
        """
        link = await self._link_to_info(id, id_type)
        data = await self.requests.get(link)
        data = data.text
        soup = Soup(data, 'lxml') if self.USE_LXML else Soup(data, 'html.parser')
        if self._is_serial(link):
            series_count = len(soup.find("div", {"class": "serial-series-box"}).find("select").find_all("option"))
            try:
                translations_div = soup.find("div", {"class": "serial-translations-box"}).find("select").find_all("option")
            except:
                translations_div = None
            return {
                'series_count': series_count,
                'translations': self._generate_translations_dict(translations_div)
            }
        elif self._is_video(link):
            series_count = 0
            try:
                translations_div = soup.find("div", {"class": "movie-translations-box"}).find("select").find_all("option")
            except AttributeError:
                translations_div = None
            return {
                'series_count': series_count,
                'translations': self._generate_translations_dict(translations_div)
            }
        else:
            raise errors.UnexpectedBehaviour('Ссылка на данные не была распознана как ссылка на сериал или фильм')
    
    def _is_serial(self, iframe_url: str) -> bool:
        return True if iframe_url[iframe_url.find(".info/")+6] == "s" else False

    def _is_video(self, iframe_url: str) -> bool:
        return True if iframe_url[iframe_url.find(".info/")+6] == "v" else False
    
    def _generate_translations_dict(self, translations_div: Soup | None) -> dict:
        if not isinstance(translations_div, Soup) and translations_div != None:
            translations = []
            for translation in translations_div:
                a = {}
                a['id'] = translation['value']
                a['type'] = translation['data-translation-type']
                if a['type'] == 'voice':
                    a['type'] = "Озвучка"
                elif a['type'] == 'subtitles':
                    a['type'] = "Субтитры"
                a['name'] = translation.text
                translations.append(a)
        else:
            translations = [{"id": "0", "type": "Неизвестно", "name": "Неизвестно"}]
        return translations

    async def get_link(self, id: str, id_type: str, seria_num: int, translation_id: str) -> tuple[str, int]:
        """
        ### Для использования требуется токен kodik
        Возвращает ссылку на видео файл.

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)
        :seria_num: номер серии (если фильм или одно видео, укажите 0)
        :translation_id: id перевода (прим: Anilibria = 610, если неизвестно - 0)

        Возвращает ссылку в стиле:
        //cloud.kodik-storage.com/useruploads/351182fc-e1ac-4521-a9e3-261303e69687/ba18e7c1a8ac055a61b0d2e528f9eb8c:2024062702/
        В конце ссылки нужно добавить качество видео: 720.mp4 / 480.mp4 / 360.mp4
        В начале ссылки нужно добавить: http: / https:

        И максимально возможное качество.
        """
        link = await self._link_to_info(id, id_type)
        data = await self.requests.get(link)
        data = data.text
        soup = Soup(data, 'lxml') if self.USE_LXML else Soup(data, 'html.parser')
        urlParams = data[data.find('urlParams')+13:]
        urlParams = json.loads(urlParams[:urlParams.find(';')-1])
        if translation_id != "0" and seria_num != 0: # Обычный сериал с известной озвучкой на более чем 1 серию
            container = soup.find('div', {'class': 'serial-translations-box'}).find('select')
            media_hash = None
            media_id = None
            for translation in container.find_all('option'):
                if translation.get_attribute_list('data-id')[0] == translation_id:
                    media_hash = translation.get_attribute_list('data-media-hash')[0]
                    media_id = translation.get_attribute_list('data-media-id')[0]
                    break
            url = f'https://kodik.info/serial/{media_id}/{media_hash}/720p?min_age=16&first_url=false&season=1&episode={seria_num}'
            data = await self.requests.get(url)
            data = data.text
            soup = Soup(data, 'lxml') if self.USE_LXML else Soup(data, 'html.parser')
        elif translation_id != "0" and seria_num == 0: # Фильм/одна серия с несколькими переводами
            container = soup.find('div', {'class': 'movie-translations-box'}).find('select')
            media_hash = None
            media_id = None
            for translation in container.find_all('option'):
                if translation.get_attribute_list('data-id')[0] == translation_id:
                    media_hash = translation.get_attribute_list('data-media-hash')[0]
                    media_id = translation.get_attribute_list('data-media-id')[0]
                    break
            url = f'https://kodik.info/video/{media_id}/{media_hash}/720p?min_age=16&first_url=false&season=1&episode={seria_num}'
            data = await self.requests.get(url)
            data = data.text
            soup = Soup(data, 'lxml') if self.USE_LXML else Soup(data, 'html.parser')
        script_url = soup.find_all('script')[1].get_attribute_list('src')[0]

        hash_container = soup.find_all('script')[4].text
        video_type = hash_container[hash_container.find('.type = \'')+9:]
        video_type = video_type[:video_type.find('\'')]
        video_hash = hash_container[hash_container.find('.hash = \'')+9:]
        video_hash = video_hash[:video_hash.find('\'')]
        video_id = hash_container[hash_container.find('.id = \'')+7:]
        video_id = video_id[:video_id.find('\'')]

        link_data, max_quality = await self._get_link_with_data(video_type, video_hash, video_id, urlParams, script_url)

        download_url = str(link_data).replace("https://", '')
        download_url = download_url[2:-26] # :hls:manifest.m3u8

        return download_url, max_quality
    
    async def _get_link_with_data(self, video_type: str, video_hash: str, video_id: str, urlParams: dict, script_url: str):
        params={
            "hash": video_hash,
            "id": video_id,
            "type": video_type,
            'd': urlParams['d'],
            'd_sign': urlParams['d_sign'],
            'pd': urlParams['pd'],
            'pd_sign': urlParams['pd_sign'],
            'ref': '',
            'ref_sign': urlParams['ref_sign'],
            'bad_user': 'true',
            'cdn_is_working': 'true',
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        post_link = await self._get_post_link(script_url)
        data = await self.requests.post(f'https://kodik.info{post_link}', data=params, headers=headers)
        data = data.json()
        url = self._convert(data['links']['360'][0]['src'])
        max_quality = max([int(x) for x in data['links'].keys()])
        try:
            return b64decode(url.encode()), max_quality
        except:
            return str(b64decode(url.encode()+b'==')).replace("https:", ''), max_quality
        
    def _convert_char(self, char: str):
        low = char.islower()
        alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if char.upper() in alph:
            ch = alph[(alph.index(char.upper())+13)%len(alph)]
            if low:
                return ch.lower()
            else:
                return ch
        else:
            return char

    def _convert(self, string: str):
        # Декодирование строки со ссылкой
        return "".join(map(self._convert_char, list(string)))
    
    async def _get_post_link(self, script_url: str):
        data = await self.requests.get('https://kodik.info'+script_url)
        data = data.text
        url = data[data.find("$.ajax")+30:data.find("cache:!1")-3]
        return b64decode(url.encode()).decode()

    @staticmethod
    async def get_token() -> str:
        """
        Попытка получения токена.
        Обратите внимание, что эта функция может не работать из-за изменений кодиком ссылок.
        """
        script_url = 'https://kodik-add.com/add-players.min.js?v=2'
        req = AsyncSession()
        data = await req.get(script_url)
        data = data.text
        token = data[data.find('token=')+7:]
        token = token[:token.find('"')]
        return token

    @staticmethod
    def get_token_sync() -> str:
        """
        Попытка получения токена.
        Обратите внимание, что эта функция может не работать из-за изменений кодиком ссылок.
        """
        script_url = 'https://kodik-add.com/add-players.min.js?v=2'
        data = requests.get(script_url)
        data = data.text
        token = data[data.find('token=')+7:]
        token = token[:token.find('"')]
        return token