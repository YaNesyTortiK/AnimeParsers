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

try:
    from . import errors # Импорт если библиотека установлена
except ImportError:
    import errors # Импорт если библиотека не установлена и файл лежит локально

class KodikParser:
    """
    Парсер для плеера Kodik
    """
    def __init__(self, token: str|None = None, use_lxml: bool = False, validate_token: bool = True) -> None:
        """
        :token: токен kodik для поиска по его базе. Если не указан будет произведена попытка автоматического получения токена
        :use_lxml: использовать lxml парсер (в некоторых случаях lxml может не работать)
        :validate_token: валидация токена (по умолчанию True). Проверяет все функции парсера на наличие ошибки по токену.
        """
        if token is None:
            try:
                token = self.get_token()
            except Exception as ex:
                raise errors.ServiceError(f'Произошла ошибка при попытке автоматического получения токена kodik. Ошибка: {ex}')
        self.TOKEN = token
        if not LXML_WORKS and use_lxml:
            raise ImportWarning('Параметр use_lxml установлен в true, однако при попытке импорта lxml произошла ошибка')
        self.USE_LXML = use_lxml
        self._crypt_step = None
        if validate_token and not self.validate_token():
            raise errors.TokenError("Ошибка валидации токена. Одна или несколько функций недоступны с данным токеном. "\
                                    "Чтобы пропустить валидацию, укажите параметр validate_token=False")

    def api_request(self, endpoint: str, filters: dict = {}, parameters: dict = {}) -> dict:
        """
        Запрос к апи кодика по указанным фильтрам и параметрам. Требует токен.
        Более полная документация в файле KODIK_API.md (см. репозиторий https://github.com/YaNesyTortiK/AnimeParsers)
        
        :endpoint: Эндпоинт для запроса (search, list, translations)
        :filters: Фильтры (по умолчанию {})
        :parameters: Дополнительные параметры (по умолчанию {})

        Возвращает неизмененный ответ сервера.
        """
        if endpoint not in ['search', 'list', 'translations']:
            raise errors.PostArgumentsError(f'Неизвестный эндпоинт. Ожидался один из "search", "list", "translations". Получен: "{endpoint}"')
        if self.TOKEN is None:
            raise errors.TokenError('Токен kodik не указан')
        
        payload = {"token": self.TOKEN}
        for item, val in filters.items():
            payload[item] = val
        for item, val in parameters.items():
            payload[item] = val

        url = f"https://kodikapi.com/{endpoint}"
        data = requests.post(url, data=payload)
        
        try:
            data = data.json()
        except Exception as ex:
            if data.status_code != 200:
                raise errors.ServiceError(f'Произошла ошибка при запросе к kodik api. Ожидался код "200", получен: "{data.status_code}"')
            raise errors.ServiceError(f"Произошла ошибка при запросе к kodik api. Ожидался ответ json, при попытке получения произошла непредвиденная ошибка: {ex}")
        
        if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
            raise errors.TokenError('Отсутствует или неверный токен')
        elif 'error' in data.keys():
            raise errors.ServiceError(f"Произошла ошибка при запросе к kodik api. Ошибка: {data['error']}")
        
        if data['total'] == 0:
            raise errors.NoResults('Сервер вернул ответ с пустым списком результатов.')
        return data

    def base_search(self, title: str, limit: int = 50, include_material_data: bool = True, anime_status: str|None = None, strict: bool = False) -> dict:
        """
        ### Для использования требуется токен kodik
        Прямой запрос к базе кодика без дополнительных преобразований

        :title: Название аниме / фильма / сериала
        :limit: Верхнее ограничение количества ответов
        :include_material_data: Добавлять в ответ дополнительные данные о сериале
        :anime_status: Статус выхода аниме (доступно: released, ongoing, None - если ищется не аниме или любой статус)
        :strict: Исключение названий далеких от оригинального

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
        try:
            payload = {
                "title": title + ' ' if strict else title, # Хз почему, но если не добавить этот пробел, результатов не будет. \_(=-=)_/
                "limit": limit,
                "with_material_data": 'true' if include_material_data else 'false',
                "strict": 'true' if strict else 'false'
            }
            if anime_status in ['released', 'ongoing']:
                payload['anime_status'] = anime_status
            data = self.api_request(
                'search',
                payload
            )
        except errors.NoResults:
            raise errors.NoResults(f'По запросу "{title}" ничего не найдено')
        return data
    
    def base_search_by_id(self, id: str, id_type: str, limit: int = 50, include_material_data: bool = True) -> dict:
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
        if id_type not in ['shikimori', 'kinopoisk', 'imdb']:
            raise errors.PostArgumentsError(f'Поддерживаются только id shikimori, kinopoisk, imdb. Получено: {id_type}')
        try:
            data = self.api_request(
                'search',
                {
                    f"{id_type}_id": id,
                    "limit": limit,
                    "with_material_data": 'true' if include_material_data else 'false'
                }
            )
        except errors.NoResults:
            raise errors.NoResults(f'По id {id_type} "{id}" ничего не найдено')
        return data
    
    def get_list(self, limit_per_page: int = 50, pages_to_parse: int = 1, include_material_data: bool = True, anime_status: str|None = None, only_anime: bool = False, start_from: str|None = None) -> tuple[list[dict],str]:
        """
        Получение случайного списка аниме от кодика (скорее всего это будут онгоинги)
        ### Для использования требуется токен kodik

        :limit_per_page: Ограничение на количество результатов на запрос(страницу), не все элементы в списке будут аниме (по умолчанию 50)
        :pages_to_parse: Ограничение на количество страниц для обработки (каждая страница - отдельный запрос) (по умолчанию 1)
        :include_material_data: Добавление дополнительных данных (необязательно, по умолчанию True)
        :anime_status: Статус выхода аниме (доступно: released, ongoing, None - если ищется не аниме или любой статус)
        :only_anime: Возвращать только варианты аниме (тип anime или anime-serial) (по умолчанию False)
        :start_from: Поиск следующих страниц по заданному id (id возвращается вторым элементом кортежа) (по умолчанию None)

        Возвращает кортеж из списка словарей и id страницы:
        (
            [
            {
                "title": "Название",
                "type": "тип мультимедиа (anime, film, ...)",
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
            ],
            "next_page_id": "id следующей страницы (для последовательного парсинга нескольких страниц) (может быть None, если след. страниц нет)"
        )
        """
        results = []
        next_page = start_from
        payload = {
            "token": self.TOKEN,
            "limit": limit_per_page,
            "with_material_data": 'true' if include_material_data else 'false'
        }
        if anime_status in ['released', 'ongoing']:
            payload['anime_status'] = anime_status
        for _ in range(pages_to_parse):
            if next_page != None:
                payload['next'] = next_page
            try:
                data = self.api_request(
                    'list',
                    payload
                )
            except errors.NoResults:
                data = {'results': []}
            if 'next_page' in data.keys():
                next_page = data['next_page'][data['next_page'].rfind('=')+1:]
            else:
                next_page = None
            results += data['results']
        return (self._prettify_data(results, only_anime=only_anime), next_page)
    
    def search(self, title: str, limit: int|None = None, include_material_data: bool = True, anime_status: str|None = None, strict: bool = False, only_anime: bool = False) -> list:
        """
        ### Для использования требуется токен kodik
        Получение только самых основных данных о сериале.
        Для получения всех данных воспользуйтесь функцией base_search

        :title: Название аниме / фильма / сериала
        :limit: Верхнее ограничение количества ответов для base_search (необязательно)
        :include_material_data: Добавление дополнительных данных (необязательно, по умолчанию True)
        :anime_status: Статус выхода аниме (доступно: released, ongoing, None - если ищется не аниме или любой статус)
        :strict: Исключение названий далеких от оригинального
        :only_anime: Возвращать только варианты аниме (тип anime или anime-serial) (по умолчанию False)

        Возвращает список словарей в следующем виде:
        [
        {
            "title": "Название",
            "type": "тип мультимедиа (anime, film, ...)",
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
            search_data = self.base_search(title, include_material_data=include_material_data, anime_status=anime_status, strict=strict)
        else:
            search_data = self.base_search(title, limit, include_material_data=include_material_data, anime_status=anime_status, strict=strict)
        return self._prettify_data(search_data['results'], only_anime=only_anime)
    
    def search_by_id(self, id: str, id_type: str, limit: int|None = None) -> list:
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
            "type": "тип мультимедиа (anime, film, ...)",
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
        if type(id) == int:
            id = str(id)
        elif type(id) != str:
            raise ValueError(f'Для id ожидался тип str, получен "{type(id)}"')

        if limit is None:
            search_data = self.base_search_by_id(id, id_type, include_material_data=True)
        else:
            search_data = self.base_search_by_id(id, id_type, limit, include_material_data=True)
        return self._prettify_data(search_data['results'])
    
    def _prettify_data(self, results: list[dict], only_anime: bool = False) -> list[dict]:
        """
        Превращает полученные данные от запроса кодику в удобный вариант словаря

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
    
    def translations(self, id: str, id_type: str) -> list:
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
        return self.get_info(id, id_type)['translations']
    
    def series_count(self, id: str, id_type: str) -> int:
        """
        ### Для использования требуется токен kodik
        Возвращает количество серий для медиафайла по id.

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)
        """
        return self.get_info(id, id_type)['series_count']

    def _link_to_info(self, id: str, id_type: str, https: bool = True) -> str:
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
        data = requests.get(serv)
        try:
            data = data.json()
        except Exception as ex:
            if data.status_code != 200:
                raise errors.ServiceError(f'Произошла ошибка при запросе к kodik api. Ожидался код "200", получен: "{data.status_code}"')
            raise errors.ServiceError(f"Произошла ошибка при запросе к kodik api. Ожидался ответ json, при попытке получения произошла непредвиденная ошибка: {ex}")
        
        if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
            raise errors.TokenError('Отсутствует или неверный токен')
        elif 'error' in data.keys():
            raise errors.ServiceError(f"Произошла ошибка при запросе к kodik api. Ошибка: {data['error']}")
        if not data['found']:
            raise errors.NoResults(f'Нет данных по {id_type} id "{id}"')
        return 'https:'+data['link'] if https else 'http:'+data['link']
    
    def get_info(self, id: str, id_type: str) -> dict:
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
        if type(id) == int:
            id = str(id)
        elif type(id) != str:
            raise ValueError(f'Для id ожидался тип str, получен "{type(id)}"')
    
        link = self._link_to_info(id, id_type)
        data = requests.get(link)
        try:
            data = data.text
        except Exception as ex:
            if data.status_code != 200:
                raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
            raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ текстового вида, при попытке получения произошла непредвиденная ошибка: {ex}")
        
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
            raise errors.UnexpectedBehavior('Ссылка на данные не была распознана как ссылка на сериал или фильм')
    
    def _is_serial(self, iframe_url: str) -> bool:
        return True if iframe_url[iframe_url.find(".info/")+6] == "s" else False

    def _is_video(self, iframe_url: str) -> bool:
        return True if iframe_url[iframe_url.find(".info/")+6] == "v" else False
    
    def _generate_translations_dict(self, translations_div: Soup) -> dict:
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

    def get_link(self, id: str, id_type: str, seria_num: int, translation_id: str) -> tuple[str, int]:
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
        # Проверка переданных параметров на правильность типа
        if type(id) == int:
            id = str(id)
        elif type(id) != str:
            raise ValueError(f'Для id ожидался тип str, получен "{type(id)}"')
        if type(seria_num) == str and seria_num.isdigit():
            seria_num = int(seria_num)
        elif type(seria_num) != int:
            raise ValueError(
                f'Для seria_num ожидался тип int, получен "{type(seria_num)}"'
            )
        if type(translation_id) == int:
            translation_id = str(translation_id)
        elif type(translation_id) != str:
            raise ValueError(
                f'Для translation_id ожидался тип str, получен "{type(translation_id)}"'
            )

        link = self._link_to_info(id, id_type)
        data = requests.get(link)
        if data.status_code != 200:
            raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
        try:
            data = data.text
        except Exception as ex:
            raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ текстового вида, при попытке получения произошла непредвиденная ошибка: {ex}")
        
        soup = Soup(data, "lxml") if self.USE_LXML else Soup(data, "html.parser")
        urlParams = data[data.find("urlParams") + 13 :]
        urlParams = json.loads(urlParams[: urlParams.find(";") - 1])
        if (
            translation_id != "0" and seria_num != 0
        ):  # Обычный сериал с известной озвучкой на более чем 1 серию
            container = soup.find("div", {"class": "serial-translations-box"}).find(
                "select"
            )
            media_hash = None
            media_id = None
            for translation in container.find_all("option"):
                if translation.get_attribute_list("data-id")[0] == translation_id:
                    media_hash = translation.get_attribute_list("data-media-hash")[0]
                    media_id = translation.get_attribute_list("data-media-id")[0]
                    break
            url = f"https://kodik.info/serial/{media_id}/{media_hash}/720p?min_age=16&first_url=false&season=1&episode={seria_num}"
            data = requests.get(url)
            if data.status_code != 200:
                raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
            try:
                data = data.text
            except Exception as ex:
                raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ текстового вида, при попытке получения произошла непредвиденная ошибка: {ex}")
            
            soup = Soup(data, "lxml") if self.USE_LXML else Soup(data, "html.parser")
        elif (
            translation_id != "0" and seria_num == 0
        ):  # Фильм/одна серия с несколькими переводами
            container = soup.find("div", {"class": "movie-translations-box"}).find(
                "select"
            )
            media_hash = None
            media_id = None
            for translation in container.find_all("option"):
                if translation.get_attribute_list("data-id")[0] == translation_id:
                    media_hash = translation.get_attribute_list("data-media-hash")[0]
                    media_id = translation.get_attribute_list("data-media-id")[0]
                    break
            url = f"https://kodik.info/video/{media_id}/{media_hash}/720p?min_age=16&first_url=false&season=1&episode={seria_num}"
            data = requests.get(url)
            if data.status_code != 200:
                raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
            try:
                data = data.text
            except Exception as ex:
                raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ текстового вида, при попытке получения произошла непредвиденная ошибка: {ex}")
            soup = Soup(data, "lxml") if self.USE_LXML else Soup(data, "html.parser")
        script_url = soup.find_all("script")[1].get_attribute_list("src")[0]

        hash_container = soup.find_all("script")[4].text
        video_type = hash_container[hash_container.find(".type = '") + 9 :]
        video_type = video_type[: video_type.find("'")]
        video_hash = hash_container[hash_container.find(".hash = '") + 9 :]
        video_hash = video_hash[: video_hash.find("'")]
        video_id = hash_container[hash_container.find(".id = '") + 7 :]
        video_id = video_id[: video_id.find("'")]

        link_data, max_quality = self._get_link_with_data(video_type, video_hash, video_id, urlParams, script_url)

        download_url = str(link_data).replace("https:", "")
        download_url = download_url[: download_url.rfind("/") + 1]
        return download_url, max_quality

    def _get_link_with_data(self, video_type: str, video_hash: str, video_id: str, urlParams: dict, script_url: str):
        params = {
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

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        post_link = self._get_post_link(script_url)
        data = requests.post(f"https://kodik.info{post_link}", data=params, headers=headers)
        try:
            data = data.json()
        except Exception as ex:
            if data.status_code != 200:
                raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
            raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ json, при попытке получения произошла непредвиденная ошибка: {ex}")
        
        if 'error' in data.keys() and data['error'] == 'Отсутствует или неверный токен':
            raise errors.TokenError('Отсутствует или неверный токен')
        elif 'error' in data.keys():
            raise errors.ServiceError(f"Произошла ошибка при запросе. Ошибка: {data['error']}")
        
        data_url = data["links"]["360"][0]["src"]
        url = data_url if "mp4:hls:manifest" in data_url else self._convert(data_url)
        max_quality = max([int(x) for x in data["links"].keys()])

        return url, max_quality
    
    def get_m3u8_playlist_link(self, id: str, id_type: str, seria_num: int, translation_id: str, quality: int = 720) -> str:
        """
        Возвращает ссылку на m3u8 плейлист.
        Пример: https://cloud.kodik-storage.com/.../.../720.mp4:hls:manifest.m3u8

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)
        :seria_num: номер серии (если фильм или одно видео, укажите 0)
        :translation_id: id перевода (прим: Anilibria = 610, если неизвестно - 0)
        :quality: Желаемое качество (360, 480, 720). Если указанное качество будет больше, чем максимально доступное, вернется ссылка с максимально доступным качеством. По умолчанию: 720
        """
        link_data = self.get_link(id, id_type, seria_num, translation_id)
        selected_quality = str(min(quality, link_data[1]) if quality in [360, 480, 720] else link_data[1])
        return "https:"+link_data[0]+selected_quality+".mp4:hls:manifest.m3u8"
    
    def get_m3u8_playlist(self, id: str, id_type: str, seria_num: int, translation_id: str, quality: int = 720) -> str:
        """
        Возвращает m3u8 плейлист в виде содержания файла.
        Прим: 
        #EXTM3U
        #EXT-X-TARGETDURATION:6
        #EXT-X-ALLOW-CACHE:YES
        #EXT-X-PLAYLIST-TYPE:VOD
        #EXT-X-VERSION:3
        #EXT-X-MEDIA-SEQUENCE:1
        #EXTINF:6.000,
        https://.../720.mp4:hls:seg-1-v1-a1.ts
        #EXTINF:6.000,
        https://.../720.mp4:hls:seg-2-v1-a1.ts
        #EXTINF:6.000,
        https://.../720.mp4:hls:seg-3-v1-a1.ts

        :id: id медиа
        :id_type: тип id (возможные: shikimori, kinopoisk, imdb)
        :seria_num: номер серии (если фильм или одно видео, укажите 0)
        :translation_id: id перевода (прим: Anilibria = 610, если неизвестно - 0)
        :quality: Желаемое качество (360, 480, 720). Если указанное качество будет больше, чем максимально доступное, вернется содержимое файла с максимально доступным качеством. По умолчанию: 720
        """
        link_data = self.get_link(id, id_type, seria_num, translation_id)
        selected_quality = str(min(quality, link_data[1]) if quality in [360, 480, 720] else link_data[1])
        
        link = "https:"+link_data[0]+selected_quality+".mp4:hls:manifest.m3u8"
        data = requests.get(link)
        if data.status_code == 404:
            raise errors.NoResults(f"Плейлист не найден. Попробуйте сменить качество.")
        elif data.status_code != 200:
            raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
        try:
            data = data.text
        except Exception as ex:
            raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ текстового вида, при попытке получения произошла непредвиденная ошибка: {ex}")

        return data.replace('./'+selected_quality+'.mp4', "https:"+link_data[0]+selected_quality+'.mp4')

    def _convert_char(self, char: str, num):
        low = char.islower()
        alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if char.upper() in alph:
            ch = alph[(alph.index(char.upper()) + num) % len(alph)]
            if low:
                return ch.lower()
            else:
                return ch
        else:
            return char

    def _convert(self, string: str):
        # Декодирование строки со ссылкой

        if self._crypt_step:
            crypted_url = "".join([self._convert_char(i, self._crypt_step) for i in string])
            padding = (4 - (len(crypted_url) % 4)) % 4
            crypted_url += "=" * padding
            try:
                result = b64decode(crypted_url).decode("utf-8")
                if "mp4:hls:manifest" in result:
                    return result
            except UnicodeDecodeError:
                pass
        
        for rot in range(0, 26):
            crypted_url = "".join([self._convert_char(i, rot) for i in string])
            padding = (4 - (len(crypted_url) % 4)) % 4
            crypted_url += "=" * padding
            try:
                result = b64decode(crypted_url).decode("utf-8")
                if "mp4:hls:manifest" in result:
                    self._crypt_step = rot
                    return result
            except UnicodeDecodeError:
                continue
        else:
            raise errors.DecryptionFailure

    def _get_post_link(self, script_url: str):
        data = requests.get("https://kodik.info" + script_url)
        if data.status_code != 200:
            raise errors.ServiceError(f'Произошла ошибка при запросе. Ожидался код "200", получен: "{data.status_code}"')
        try:
            data = data.text
        except Exception as ex:
            raise errors.ServiceError(f"Произошла ошибка при запросе. Ожидался ответ текстового вида, при попытке получения произошла непредвиденная ошибка: {ex}")
        
        url = data[data.find("$.ajax") + 30 : data.find("cache:!1") - 3]
        return b64decode(url.encode()).decode()

    @staticmethod
    def get_token() -> str:
        """
        ! ВНИМАНИЕ ! Токен полученный с помощью этой функции может не работать для некоторых 
            запросов к апи из-за, предположительно, удаления данного токена из валидных.
        Попытка получения токена.
        Обратите внимание, что эта функция может не работать из-за изменений кодиком ссылок.
        """
        # Попытка получения полного токена
        """
        Используется токен из репозитория https://github.com/nb557/plugins
        За помощь и написание функций спасибо https://github.com/deathnoragami
        """
        def js_hash_str(s: str) -> str:
            """Эквивалент JS-хэша из плагина: ((h<<5) - h + code) >>> 0, затем приводим к signed 32-bit и в строку."""
            h = 0
            for ch in s:
                h = ((h << 5) - h + ord(ch)) & 0xFFFFFFFF
            if h & 0x80000000:  # signed 32-bit
                h = -((~h & 0xFFFFFFFF) + 1)
            return str(h)

        def decode_secret(nums, password: str) -> str:
            h = js_hash_str(password)
            return ''.join(chr(n ^ ord(h[i % len(h)])) for i, n in enumerate(nums))

        def get_secret():
            link = 'https://raw.githubusercontent.com/nb557/plugins/refs/heads/main/online_mod.js'
            data = requests.get(link).text
            start_pos = data.rfind("var embed = 'https://kodikapi.com/search';")
            
            line = data[data.find("Utils.decodeSecret([", start_pos)+20:data.find("],", start_pos)]
            secret = [int(x) for x in line.split(', ')]
            return secret
        
        try:
            token = decode_secret(get_secret(), 'kodik')
        except:
            pass
        else:
            return token

        # Получение токена который не работает для поиска и списков
        script_url = 'https://kodik-add.com/add-players.min.js?v=2'
        data = requests.get(script_url).text
        token = data[data.find('token=')+7:]
        token = token[:token.find('"')]
        return token
    
    def validate_token(self) -> bool:
        if self.TOKEN:
            res = True
            try:
                self.base_search("Кулинарные скитания", limit=1, include_material_data=False)
            except errors.TokenError:
                print("[Token validation] Токен неверен для функции base_search")
                res = False
            except Exception as ex:
                raise errors.UnexpectedBehavior(f"[Token validation] Произошла непредвиденная ошибка при валидации токена: {ex}")
            try:
                self.base_search_by_id("53446", "shikimori", limit=1, include_material_data=False)
            except errors.TokenError:
                print("[Token validation] Токен неверен для функции base_search_by_id")
                res = False
            except Exception as ex:
                raise errors.UnexpectedBehavior(f"[Token validation] Произошла непредвиденная ошибка при валидации токена: {ex}")
            try:
                self.get_info("53446", "shikimori")
            except errors.TokenError:
                print("[Token validation] Токен неверен для функции get_info")
                res = False
            except Exception as ex:
                raise errors.UnexpectedBehavior(f"[Token validation] Произошла непредвиденная ошибка при валидации токена: {ex}")
            try:
                self.get_list(limit_per_page=1, pages_to_parse=1, include_material_data=False)
            except errors.TokenError:
                print("[Token validation] Токен неверен для функции get_list")
                res = False
            except Exception as ex:
                raise errors.UnexpectedBehavior(f"[Token validation] Произошла непредвиденная ошибка при валидации токена: {ex}")
            try:
                self.get_link("53446", "shikimori", 1, "610")
            except errors.TokenError:
                print("[Token validation] Токен неверен для функции get_link")
                res = False
            except Exception as ex:
                raise errors.UnexpectedBehavior(f"[Token validation] Произошла непредвиденная ошибка при валидации токена: {ex}")
            return res
        else:
            raise errors.TokenError(f"Для валидации токена он должен быть указан при инициализации или получен автоматически. Текущий токен: {self.TOKEN}")
