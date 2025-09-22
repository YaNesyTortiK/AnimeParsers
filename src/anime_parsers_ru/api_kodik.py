try:
    from . import parser_kodik # Импорт если библиотека установлена
except ImportError:
    import parser_kodik # Импорт если библиотека не установлена и файл лежит локально

try:
    from . import errors # Импорт если библиотека установлена
except ImportError:
    import errors # Импорт если библиотека не установлена и файл лежит локально

try:
    try:
        from .internal_tools import AsyncSession
        async_available = True
    except ImportError:
        from internal_tools import AsyncSession
        async_available = True
except ImportError:
    async_available = False

import requests

class _OrderList:
    asc = 'asc'
    desc = 'desc'

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [_OrderList.asc, _OrderList.desc]

class _SortList:
    year = 'year'
    created_at = 'created_at'
    updated_at = 'updated_at'
    kinopoisk_rating = 'kinopoisk_rating'
    imdb_rating = 'imdb_rating'
    shikimori_rating = 'shikimori_rating'

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [
            _SortList.year, _SortList.created_at, _SortList.updated_at,
            _SortList.kinopoisk_rating, _SortList.imdb_rating, _SortList.shikimori_rating
        ]

class _AnimeKind:
    tv = 'tv'
    tv13 = 'tv13'
    tv24 = 'tv24'
    tv48 = 'tv48'
    movie = 'movie'
    special = 'special'
    ova = 'ova'
    ona = 'ona'
    music = 'music'

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [
            _AnimeKind.tv, _AnimeKind.tv13, _AnimeKind.tv24, _AnimeKind.tv48, 
            _AnimeKind.movie, _AnimeKind.special, _AnimeKind.ova, _AnimeKind.ona, _AnimeKind.music
        ]

class _Types:
    foreign_movie = "foreign-movie"
    soviet_cartoon = "soviet-cartoon"
    foreign_cartoon = "foreign-cartoon"
    russian_cartoon = "russian-cartoon"
    anime = "anime"
    russian_movie = "russian-movie"
    cartoon_serial = "cartoon-serial"
    documentary_serial = "documentary-serial"
    russian_serial = "russian-serial"
    foreign_serial = "foreign-serial"
    anime_serial = "anime-serial"
    multi_part_film = "multi-part-film"

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [
            _Types.foreign_movie, _Types.soviet_cartoon, _Types.foreign_cartoon, _Types.russian_cartoon, _Types.anime,
            _Types.russian_movie, _Types.cartoon_serial, _Types.documentary_serial, _Types.russian_serial,
            _Types.foreign_serial, _Types.anime_serial, _Types.multi_part_film
        ]

class _MPAArating:
    g = "g" # - Нет возрастных ограничений.
    pg = "pg" # - Рекомендуется присутствие родителей.
    pg_13 = "pg-13" # - Детям до 13 лет просмотр нежелателен.
    r = "r" # - Лицам до 17 лет обязательно присутствие взрослого.
    rx = "rx" # - Хeнтай / Пoрнография

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [_MPAArating.g, _MPAArating.pg, _MPAArating.pg_13, _MPAArating.r, _MPAArating.rx]

class _Genres:
    anime = "аниме"
    drama = "драма"
    comedy = "комедия"
    cartoon = "мультфильм"
    fantasy = "фэнтези" 
    action = "боевик"
    adventures = "приключения"
    fantastika = "фантастика" # А в чем разница между фэнтези и фантастикой? даже гугл одинаково переводит 	(ノ ゜Д゜)ノ ︵

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [
            _Genres.anime, _Genres.drama, _Genres.comedy, _Genres.cartoon, _Genres.fantasy,
            _Genres.action, _Genres.adventures, _Genres.fantastika
        ]

class _AnimeGenres: 
    military = "Военное"
    drama = "Драма"
    history = "Исторический"
    action = "Экшен"
    adventures = "Приключения"
    senen = "Сёнен"
    fantasy = "Фэнтези"
    comedy = "Комедия"
    martial_arts = "Боевые искусства"
    romance = "Романтика"
    psychological = "Психологическое"
    thriller = "Триллер"
    everyday_life = "Повседневность"
    supernatural = "Сверхъестественное"
    sport = "Спорт"
    school = "Школа"
    music = "Музыка"
    fantastika = "Фантастика"
    samurai = "Самураи"

    @staticmethod
    def get_list() -> list[str]:
        """
        Возвращает список доступных параметров.
        """
        return [
            _AnimeGenres.military, _AnimeGenres.drama, _AnimeGenres.history, _AnimeGenres.action,
            _AnimeGenres.adventures, _AnimeGenres.senen, _AnimeGenres.fantasy, _AnimeGenres.comedy,
            _AnimeGenres.martial_arts, _AnimeGenres.romance, _AnimeGenres.psychological, _AnimeGenres.thriller,
            _AnimeGenres.everyday_life, _AnimeGenres.supernatural, _AnimeGenres.sport, _AnimeGenres.school, 
            _AnimeGenres.music, _AnimeGenres.fantastika, _AnimeGenres.samurai
        ]

class Response:
    class Translation:
        def __init__(self, raw_data: dict):
            self.raw_data = raw_data
            self._keys = raw_data.keys()
            self.id = raw_data['id'] if 'id' in self._keys else None
            self.title = raw_data['title'] if 'title' in self._keys else None
            self.type = raw_data['type'] if 'type' in self._keys else None
            self.is_voice = True if self.type == 'voice' else False

        def __str__(self):
            return str(self.raw_data)
        
        def __repr__(self):
            return str(self.raw_data)

    class Season:
        class Episode:
            def __init__(self, raw_data: dict):
                self.raw_data = raw_data
                if type(raw_data) == dict:
                    self.link = raw_data['link']
                    self.title = raw_data['title'] if 'title' in self.raw_data.keys() else None
                    self.screenshots = raw_data['screenshots'] if 'screenshots' in self.raw_data.keys() else None
                else:
                    self.link = raw_data
                    self.title = None
                    self.screenshots = None

        def __init__(self, raw_data: dict):
            self.raw_data = raw_data
            self.episodes = self.raw_data['episodes'] if 'episodes' in self.raw_data.keys() else None
            self.link = self.raw_data['link'] if 'link' in self.raw_data.keys() else None

        @property
        def episodes(self) -> dict[str, 'Response.Season.Episode']:
            return self._episodes
        
        @episodes.setter
        def episodes(self, value: dict | None):
            if value is None:
                self._episodes = None
            else:
                self._episodes = {}
                for k, v in value.items():
                    self._episodes[k] = Response.Season.Episode(v)

    class MaterialData:
        """
        Поле material_data. (Доступно при выполнении запроса с параметром with_material_data)
        Доступные параметры:

        * title - Название
        * anime_title - Название аниме (если есть, иначе None, обычно совпадает с title)
        * title_en - Английское название (либо транслитерация)
        * other_titles - Список других названий (если есть, иначе None)
        * other_titles_en - Список других названий на английском (если есть, иначе None)
        * other_titles_jp - Список других названий на японском (если есть, иначе None)
        * anime_kind - Тип аниме (если есть, иначе None)
        * all_status - Статус выхода
        * anime_status - Статус выхода, если аниме (обычно совпадает с all_status) (если есть, иначе None)
        * description - Описание
        * anime_description - Описание, если аниме (обычно совпадает с description) (если есть, иначе None)
        * poster_url - Ссылка на постер (если есть, иначе ссылка на картинку по умолчанию)
        * anime_poster_url - Ссылка на аниме постер (если есть, то на шикимори, иначе None)
        * screenshots - Список ссылок на скриншоты
        * duration - Продолжительность в минутах
        * all_genres - Список всех жанров (аниме жанры + обычные жанры)
        * anime_genres - Список аниме жанров (если есть, иначе None)
        * shikimori_rating - Оценка на шикимори (если есть, иначе None)
        * shikimori_votes - Количество оценок на шикимори (если есть, иначе None)
        * kinopoisk_rating - Оценка на кинопоиске (если есть, иначе None)
        * kinopoisk_votes - Количество оценок на кинопоиске (если есть, иначе None)
        * imdb_rating - Оценка на imdb (если есть, иначе None)
        * imdb_votes - Количество оценок на imdb (если есть, иначе None)
        * aired_at - Когда проходила премьера (если есть, иначе None)
        * rating_mpaa - Возрастной рейтинг mpaa
        * minimal_age - Минимальный возраст зрителя
        * episodes_total - Всего эпизодов (если есть, иначе None)
        * episodes_aired - Сколько эпизодов уже показано (если есть, иначе None)
        * year - Год выхода 
        * countries - Страны-производители (список) (если есть, иначе None)
        * genres - Список жанров
        * premiere_world - Дата премьеры в мире (если есть, иначе None)
        * actors - Список актеров (если есть, иначе None)
        * directors - Список режиссеров (если есть, иначе None)
        * writers - Список сценаристов (если есть, иначе None)
        * producers - Список продюсеров (если есть, иначе None)
        * composers - Список композиторов (если есть, иначе None)
        * editors - Список монтажеров (если есть, иначе None)
        * designers - Список дизайнеров (если есть, иначе None)
        * operators - Список операторов (если есть, иначе None)
        * licensed_by - Кем было лицензировано (если есть, иначе None)
        * anime_studios - Студии анимации аниме (если есть, иначе None)
        * released_at - Дата выхода (если есть, иначе None)
        """
        def __init__(self, raw_data: dict):
            self.raw_data = raw_data
            self._keys = self.raw_data.keys()
            self.title = self.raw_data['title'] if 'title' in self._keys else None
            self.anime_title = self.raw_data['anime_title'] if 'anime_title' in self._keys else None
            self.title_en = self.raw_data['title_en'] if 'title_en' in self._keys else None
            self.other_titles = self.raw_data['other_titles'] if 'other_titles' in self._keys else None
            self.other_titles_en = self.raw_data['other_titles_en'] if 'other_titles_en' in self._keys else None
            self.other_titles_jp = self.raw_data['other_titles_jp'] if 'other_titles_jp' in self._keys else None
            self.anime_kind = self.raw_data['anime_kind'] if 'anime_kind' in self._keys else None
            self.all_status = self.raw_data['all_status'] if 'all_status' in self._keys else None
            self.anime_status = self.raw_data['anime_status'] if 'anime_status' in self._keys else None
            self.description = self.raw_data['description'] if 'description' in self._keys else None
            self.anime_description = self.raw_data['anime_description'] if 'anime_description' in self._keys else None
            self.poster_url = self.raw_data['poster_url'] if 'poster_url' in self._keys else None
            self.anime_poster_url = self.raw_data['anime_poster_url'] if 'anime_poster_url' in self._keys else None
            self.screenshots = self.raw_data['screenshots'] if 'screenshots' in self._keys else None
            self.duration = self.raw_data['duration'] if 'duration' in self._keys else None
            self.all_genres = self.raw_data['all_genres'] if 'all_genres' in self._keys else None
            self.anime_genres = self.raw_data['anime_genres'] if 'anime_genres' in self._keys else None
            self.shikimori_rating = self.raw_data['shikimori_rating'] if 'shikimori_rating' in self._keys else None
            self.shikimori_votes = self.raw_data['shikimori_votes'] if 'shikimori_votes' in self._keys else None
            self.kinopoisk_rating = self.raw_data['kinopoisk_rating'] if 'kinopoisk_rating' in self._keys else None
            self.kinopoisk_votes = self.raw_data['kinopoisk_votes'] if 'kinopoisk_votes' in self._keys else None
            self.imdb_rating = self.raw_data['imdb_rating'] if 'imdb_rating' in self._keys else None
            self.imdb_votes = self.raw_data['imdb_votes'] if 'imdb_votes' in self._keys else None
            self.aired_at = self.raw_data['aired_at'] if 'aired_at' in self._keys else None
            self.rating_mpaa = self.raw_data['rating_mpaa'] if 'rating_mpaa' in self._keys else None
            self.minimal_age = self.raw_data['minimal_age'] if 'minimal_age' in self._keys else None
            self.episodes_total = self.raw_data['episodes_total'] if 'episodes_total' in self._keys else None
            self.episodes_aired = self.raw_data['episodes_aired'] if 'episodes_aired' in self._keys else None
            self.year = self.raw_data['year'] if 'year' in self._keys else None
            self.countries = self.raw_data['countries'] if 'countries' in self._keys else None
            self.all_genres = self.raw_data['all_genres'] if 'all_genres' in self._keys else None
            self.genres = self.raw_data['genres'] if 'genres' in self._keys else None
            self.anime_genres = self.raw_data['anime_genres'] if 'anime_genres' in self._keys else None
            self.premiere_world = self.raw_data['premiere_world'] if 'premiere_world' in self._keys else None
            self.actors = self.raw_data['actors'] if 'actors' in self._keys else None
            self.directors = self.raw_data['directors'] if 'directors' in self._keys else None
            self.writers = self.raw_data['writers'] if 'writers' in self._keys else None
            self.producers = self.raw_data['producers'] if 'producers' in self._keys else None
            self.composers = self.raw_data['composers'] if 'composers' in self._keys else None
            self.editors = self.raw_data['editors'] if 'editors' in self._keys else None
            self.designers = self.raw_data['designers'] if 'designers' in self._keys else None
            self.operators = self.raw_data['operators'] if 'operators' in self._keys else None
            self.licensed_by = self.raw_data['licensed_by'] if 'licensed_by' in self._keys else None
            self.anime_studios = self.raw_data['anime_studios'] if 'anime_studios' in self._keys else None
            self.released_at = self.raw_data['released_at'] if 'released_at' in self._keys else None

    class Element:
        """
        Описывает элемент. Доступные параметры:

        * id - Внутренний id элемента на кодике
        * type - Тип элемента
        * link - ссылка на embed (kodik.info/....)
        * title - Название на русском
        * title_orig - Оригинальное название (название на английском) (если есть, иначе None)
        * other_title - Другое название (если есть, иначе None)
        * year - Год выхода
        * last_season - Последний сезон (если есть, иначе None)
        * last_episode - Последний эпизод (если есть, иначе None)
        * episodes_count - Количество эпизодов (если есть, иначе None)
        * kinopoisk_id - id элемента на кинопоиске (если есть, иначе None)
        * shikimori_id - id элемента на шикимори (если есть, иначе None)
        * imdb_id - id элемента на imdb (если есть, иначе None)
        * mdl_id - id элемента на my drama list (если есть, иначе None)
        * quality - Качество
        * camrip - Снято ли с камеры
        * lgbt - Есть ли лгбт сцены
        * blocked_countries - Список заблокированных стран
        * blocked_seasons - Список заблокированных сезонов
        * created_at - Дата создания элемента
        * updated_at - Дата обновления элемента
        * screenshots - Список ссылок на скриншоты
        * translation - Перевод (тип Response.Translation)
        * material_data - Дополнительные параметры (тип Response.MaterialData) (если есть, иначе None)
        * seasons - Словарь сезонов (вид: '{'1': Response.Season}') (если есть, иначе None)
        """
        def __init__(self, raw_data: dict):
            self.raw_data = raw_data
            self._keys = self.raw_data.keys()
            self.id = self.raw_data['id'] if 'id' in self._keys else None
            self.type = self.raw_data['type'] if 'type' in self._keys else None
            self.link = self.raw_data['link'] if 'link' in self._keys else None
            self.title = self.raw_data['title'] if 'title' in self._keys else None
            self.title_orig = self.raw_data['title_orig'] if 'title_orig' in self._keys else None
            self.other_title = self.raw_data['other_title'] if 'other_title' in self._keys else None
            self.year = self.raw_data['year'] if 'year' in self._keys else None
            self.last_season = self.raw_data['last_season'] if 'last_season' in self._keys else None
            self.last_episode = self.raw_data['last_episode'] if 'last_episode' in self._keys else None
            self.episodes_count = self.raw_data['episodes_count'] if 'episodes_count' in self._keys else None
            self.kinopoisk_id = self.raw_data['kinopoisk_id'] if 'kinopoisk_id' in self._keys else None
            self.shikimori_id = self.raw_data['shikimori_id'] if 'shikimori_id' in self._keys else None
            self.imdb_id = self.raw_data['imdb_id'] if 'imdb_id' in self._keys else None
            self.mdl_id = self.raw_data['mdl_id'] if 'mdl_id' in self._keys else None
            self.quality = self.raw_data['quality'] if 'quality' in self._keys else None
            self.camrip = self.raw_data['camrip'] if 'camrip' in self._keys else None
            self.lgbt = self.raw_data['lgbt'] if 'lgbt' in self._keys else None
            self.blocked_countries = self.raw_data['blocked_countries'] if 'blocked_countries' in self._keys else None
            self.blocked_seasons = self.raw_data['blocked_seasons'] if 'blocked_seasons' in self._keys else None
            self.created_at = self.raw_data['created_at'] if 'created_at' in self._keys else None
            self.updated_at = self.raw_data['updated_at'] if 'updated_at' in self._keys else None
            self.screenshots = self.raw_data['screenshots'] if 'screenshots' in self._keys else None
            self.translation = Response.Translation(self.raw_data['translation']) if 'translation' in self._keys else None
            self.material_data  = self.raw_data['material_data'] if 'material_data' in self._keys else None
            self.seasons = self.raw_data['seasons'] if 'seasons' in self._keys else None
        
        @property
        def seasons(self) -> dict[str, 'Response.Season']:
            return self._seasons
        
        @seasons.setter
        def seasons(self, value: dict | None):
            if value is None:
                self._seasons = None
            else:
                self._seasons = {}
                for k, v in value.items():
                    self._seasons[k] = Response.Season(v)
        
        @property
        def material_data(self) -> 'Response.MaterialData':
            return self._material_data
        
        @material_data.setter
        def material_data(self, value: dict | None):
            if value is None:
                self._material_data = None
            else:
                self._material_data = Response.MaterialData(value)

        def get_episodes_and_translations(self, token: str | None = None) -> list[dict]:
            """
            :token: Api ключ для кодика. Не обязателен. По умолчанию None, и используется стандартный встроенный ключ.
            Возвращает список словарей с информацией о переводе.
            Пример результата:
            [
                {
                    "title": "Название озвучки",
                    "type": "Тип перевода (озвучка/субтитры)",
                    "episodes_count": количество переведенных эпизодов с этой озвучкой,
                    "translation_id": "id перевода"
                }
            ]
            """
            if self.shikimori_id:
                data = KodikSearch(token=token).limit(100).shikimori_id(self.shikimori_id).execute()
            elif self.kinopoisk_id:
                data = KodikSearch(token=token).limit(100).kinopoisk_id(self.kinopoisk_id).execute()
            elif self.imdb_id:
                data = KodikSearch(token=token).limit(100).imdb_id(self.imdb_id).execute()
            elif self.mdl_id:
                data = KodikSearch(token=token).limit(100).mdl_id(self.mdl_id).execute()
            else:
                raise ValueError('Function requires aty least one of IDs to be, but all IDs are None.')
            return self._prepare_episodes_and_translations_data(data)
        
        async def get_episodes_and_translations_async(self, token: str | None) -> list[dict]:
            """
            :token: Api ключ для кодика. Не обязателен. По умолчанию None, и используется стандартный встроенный ключ.
            Возвращает список словарей с информацией о переводе.
            Пример результата:
            [
                {
                    "title": "Название озвучки",
                    "type": "Тип перевода (озвучка/субтитры)",
                    "episodes_count": количество переведенных эпизодов с этой озвучкой,
                    "translation_id": "id перевода"
                }
            ]
            """
            if self.shikimori_id:
                data = await KodikSearch(token=token).limit(100).shikimori_id(self.shikimori_id).execute_async()
            elif self.kinopoisk_id:
                data = await KodikSearch(token=token).limit(100).kinopoisk_id(self.kinopoisk_id).execute_async()
            elif self.imdb_id:
                data = await KodikSearch(token=token).limit(100).imdb_id(self.imdb_id).execute_async()
            elif self.mdl_id:
                data = await KodikSearch(token=token).limit(100).mdl_id(self.mdl_id).execute_async()
            else:
                raise ValueError('Function requires aty least one of IDs to be, but all IDs are None.')
            return self._prepare_episodes_and_translations_data(data)
            
        def _prepare_episodes_and_translations_data(self, data: 'Response') -> list[dict]:
            return [
                {
                    "title": item.translation.title,
                    "type": item.translation.type,
                    "episodes_count": item.episodes_count,
                    "translation_id": item.translation.id
                } for item in data.results
            ]

    def __init__(self, raw_data: dict):
        self.raw_data = raw_data
        self.total = self.raw_data['total'] # Гарантируется не менее одного результата т.к. при выполнении api_request происходит проверка на наличие результатов. При их отсутствии выходит NoResults exception
        self.time = self.raw_data['time']
        self.results = self.raw_data['results']

    @property
    def results(self) -> list['Response.Element']:
        return self._results
    
    @results.setter
    def results(self, value: list):
        self._results = [Response.Element(r) for r in value]

class Api:
    class Order(_OrderList):
        """
        Параметр направления сортировки для запроса list. Доступные параметры:\n
        * asc - По возрастанию
        * desc - По убыванию
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)\n
        """
        pass

    class Sort(_SortList):
        """
        Параметры сортировки для запросов list. Доступные параметры:\n
        * year - По году
        * created_at - По дате добавления
        * updated_at - По дате обновления
        * kinopoisk_rating - По рейтингу Кинопоиска
        * imdb_rating - По рейтингу IMDb
        * shikimori_rating - По рейтингу Shikimori
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)\n
        """
        pass
    class AnimeKind(_AnimeKind):
        """
        Тип аниме по виду. Доступные фильтры:\n
        * tv - ТВ Сериал
        * tv13 - Длительность серии ~13 минут
        * tv24 - Длительность серии ~24 минут
        * tv48 - Длительность серии ~48 минут
        * movie - Фильм
        * special - Спец. выпуск
        * ova
        * ona
        * music - Музыкальный клип / Проморолик
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)\n
        """
        pass

    class Types(_Types):
        """
        Тип мультимедиа. Доступные фильтры:\n
        * foreign-movie - Иностранный фильм
        * soviet-cartoon - Советский мультфильм
        * foreign-cartoon - Иностранный мультфильм
        * russian-cartoon - Русский мультфильм
        * anime - Аниме фильм (либо одна серия)
        * russian-movie - Русский фильм
        * cartoon-serial - мульт-сериал
        * documentary-serial - документальный сериал
        * russian-serial - Русский сериал
        * foreign-serial - Иностранный сериал
        * anime-serial - Аниме сериал (все, что больше 1 серии)
        * multi-part-film - Фильм из нескольких частей
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)
        """
        pass

    class MPAArating(_MPAArating):
        """
        Возрастной рейтинг mpaa. Доступные фильтры:\n
        * g - Нет возрастных ограничений.
        * pg - Рекомендуется присутствие родителей.
        * pg-13 - Детям до 13 лет просмотр нежелателен.
        * r - Лицам до 17 лет обязательно присутствие взрослого.
        * rx - Хeнтай / Пoрнография    
        \nЧисто технически, существует рейтинг r+, но почему-то у меня не получилось отфильтровать по нему поиск (выдавался рейтинг r).
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)
        """
        pass

    class Genres(_Genres):
        """
        Жанры (отдельно от аниме жанров). Доступные фильтры:\n    
        * anime - аниме
        * drama - драма
        * comedy - комедия
        * cartoon - мультфильм
        * fantasy - фэнтези
        * action - боевик
        * adventures - приключения
        * fantastika - фантастика
        \n(Для передачи параметра напрямую, строкой, укажите его на русском, как указано выше)
        """
        pass

    class AnimeGenres(_AnimeGenres):
        """
        Аниме жанры/тематики. Доступные фильтры:\n
        * military - Военное
        * drama - Драма
        * history - Исторический
        * action - Экшен
        * adventures - Приключения
        * senen - Сёнен
        * fantasy - Фэнтези
        * comedy - Комедия
        * martial_arts - Боевые искусства
        * romance - Романтика
        * psychological - Психологическое
        * thriller - Триллер
        * everyday_life - Повседневность
        * supernatural - Сверхъестественное
        * sport - Спорт
        * school - Школа
        * music - Музыка
        * fantastika - Фантастика
        * samurai - Самураи
        \n(Для передачи параметра напрямую, строкой, укажите его на русском, как указано выше)
        """
        pass

    def __init__(self, token: str | None = None, allow_warnings: bool = True, _args: dict = {}, _endpoint: str | None = None):
        """
        :token: Указать кастомный токен для апи кодика. По умолчанию None и токен будет подставляться автоматически.
        :allow_warnings: Разрешить вывод в консоль предупреждений о неправильно/некорректно используемых параметрах. По умолчанию True.
        :_args: Используется для передачи данных между классами.
        :_parser: Используется для передачи объекта парсера между классами. (Чтобы каждый раз не инициализировать заново и не ждать автоматического поиска токена)
        :_endpoint: Указывается конец ссылки для апи (search/list/translations). По умолчанию None, т.к. для каждого эндпоинта есть свои условия, которые предусмотрены в классах Search, List соответственно. 
        """
        if token is None:
            self.token = parser_kodik.KodikParser.get_token()
        else:
            self.token = token
        if not async_available and allow_warnings:
            print('При попытке импорта внутренних инструментов библиотеки anime-parsers-ru произошла ошибка и AsyncSession не доступен. Вы не сможете использовать асинхронные функции.')
        self._args = _args
        self.allow_warnings = allow_warnings
        self._endpoint = _endpoint
        self._next_link = None
        self._prev_link = None
        self._next_page = False
        self._prev_page = False
        

    def _ret(self) -> 'Api':
        """
        Функция для создания нового класса, с новыми данными, после каждого добавленного условия. 
        (Вынесено отдельно, чтобы не загружать каждую функцию одинаковым кодом)
        """
        return Api(allow_warnings=self.allow_warnings, _args=self._args, _endpoint=self._endpoint)
    
    def title(self, title: str) -> 'Api':
        """
        Указывается название мультимедиа для поиска.
        :title: Название.
        """
        self._args['title'] = title
        return self._ret()
    
    def title_orig(self, title_orig: str) -> 'Api':
        """
        Указывается оригинальное название мультимедиа для поиска. Обычно таким считается название на английском (Даже если оригинально названо на русском).
        :title_orig: Оригинально название.
        """
        self._args['title_orig'] = title_orig
        return self._ret()
    
    def strict(self, strict: bool = True) -> 'Api':
        """
        Параметр strict отвечает за более точное совпадение запрошенного названия/оригинального названия с найденными.
        :strict: Более точное совпадение. По умолчанию True.
        """
        self._args['strict'] = strict
        return self._ret()
    
    def full_match(self, full_match: bool = True) -> 'Api':
        """
        Требует полного совпадения запрошенного названия с найденным (зависит от регистра).
        :full_match: Полное совпадение. По умолчанию True.
        """
        self._args['full_match'] = full_match
        return self._ret()
    
    def shikimori_id(self, shikimori_id: str) -> 'Api':
        """
        Поиск по id шикимори.
        :shikimori_id: id шикимори.
        
        Как узнать id:
        1. Перейдите на страницу аниме на шикимори
        2. В адресной строке сайта будет примерно следующее: 
            https://shikimori.one/animes/52991-sousou-no-frieren
        3. Строка (обычно цифры, но могут встречаться и буквы) после последнего "/" и перед первым "-" и будет являться shikimori_id
            В данном случае: 52991 
        """
        self._args['shikimori_id'] = shikimori_id
        return self._ret()
    
    def kinopoisk_id(self, kinopoisk_id: str) -> 'Api':
        """
        Поиск по id кинопоиска.
        :kinopoisk_id: id кинопоиска.
        
        Как узнать id:
        1. Перейдите на страницу фильма/сериала на кинопоиске
        2. В адресной строке сайта будет примерно следующее: 
            https://www.kinopoisk.ru/film/258687/
        3. Строка (обычно цифры, но могут встречаться и буквы) после пред-последнего "/" и перед последним "/" и будет являться kinopoisk_id
            В данном случае: 258687
        """
        self._args['kinopoisk_id'] = kinopoisk_id
        return self._ret()
    
    def imdb_id(self, imdb_id: str) -> 'Api':
        """
        Поиск по id imdb.
        :imdb_id: id imdb.
        
        Как узнать id:
        1. Перейдите на страницу фильма/сериала на imdb
        2. В адресной строке сайта будет примерно следующее: 
            https://www.imdb.com/title/tt0816692/
        3. Строка (обычно содержит в начале "tt") после пред-последнего "/" и перед последним "/" и будет являться imdb_id
            В данном случае: tt0816692
        """
        self._args['imdb_id'] = imdb_id
        return self._ret()
    
    def id(self, id: str) -> 'Api':
        """
        Поиск по внутреннему id кодика.
        :id: Внутренний id кодика.

        Как узнать id: При выполнении запроса, в каждом элементе будет находится поле id.
        """
        self._args['id'] = id
        return self._ret()

    def mdl_id(self, mdl_id: str) -> 'Api':
        """
        Поиск по id MyDramaList.
        :mdl_id: id MyDramaList.
        
        Как узнать id:
        1. Перейдите на страницу фильма/сериала на mydramalist.com
        2. В адресной строке сайта будет примерно следующее: 
            https://mydramalist.com/2570-space-battleship-yamato
        3. Строка (обычно цифры, но могут встречаться и буквы) после последнего "/" и перед первым "-" и будет являться mdl_id
            В данном случае: 2570
        """
        self._args['mdl_id'] = mdl_id
        return self._ret()
    
    def worldart_animation_id(self, worldart_animation_id: str) -> 'Api':
        """
        Поиск по id Worldart Animation.
        :worldart_animation_id: id Worldart Animation.
        
        Как узнать id:
        1. Перейдите на страницу фильма/сериала на www.world-art.ru/anime
        2. В адресной строке сайта будет примерно следующее: 
            http://www.world-art.ru/animation/animation.php?id=11466
        3. Строка (обычно цифры, но могут встречаться и буквы) после "id=" является искомым id
            В данном случае: 11466
        """
        self._args['worldart_animation_id'] = worldart_animation_id
        return self._ret()
    
    def worldart_cinema_id(self, worldart_cinema_id: str) -> 'Api':
        """
        Поиск по id Worldart Cinema.
        :worldart_cinema_id: id Worldart Cinema.
        
        Как узнать id:
        1. Перейдите на страницу фильма/сериала на www.world-art.ru/cinema
        2. В адресной строке сайта будет примерно следующее: 
            http://www.world-art.ru/cinema/cinema.php?id=36765
        3. Строка (обычно цифры, но могут встречаться и буквы) после "id=" является искомым id
            В данном случае: 36765
        """
        self._args['worldart_cinema_id'] = worldart_cinema_id
        return self._ret()
    
    def worldart_link(self, worldart_link: str) -> 'Api':
        """
        Ссылка на страницу world-art.
        :worldart_link: Ссылка на страницу world-art.

        Пример: http://www.world-art.ru/animation/animation.php?id=11466
        """
        self._args['worldart_link'] = worldart_link
        return self._ret()
    
    def limit(self, limit: int = 50) -> 'Api':
        """
        Установка предела на количество элементов в ответе.
        Допустимые пределы: 1-100 (Если меньше 1, то сервер вернет ошибку 500, если больше 100, то сервер сам ограничит количество до 100)
        :limit: Предел на количество элементов. По умолчанию 50.
        """
        if limit < 1:
            raise ValueError("Параметр limit должен быть указан в пределах 1-100! В случае если limit будет меньше одного, сервер гарантированно вернет ошибку 500.")
        elif limit > 100 and self.allow_warnings:
            print('Предупреждение! Параметр limit установлен больше 100, сервер не вернет больше 100 элементов.')
        self._args['limit'] = limit
        return self._ret()
    
    def types(self, types: list | str) -> 'Api':
        """
        Типы мультимедиа. Можно передавать либо один вариант, либо несколько.
        :types: Типы мультимедиа. Строка или список строк.

        Вы можете воспользоваться вспомогательным классом Types (Search.Types или List.Types или Api.Types).
        Доступные фильтры:

        * foreign-movie - Иностранный фильм
        * soviet-cartoon - Советский мультфильм
        * foreign-cartoon - Иностранный мультфильм
        * russian-cartoon - Русский мультфильм
        * anime - Аниме фильм (либо одна серия)
        * russian-movie - Русский фильм
        * cartoon-serial - мульт-сериал
        * documentary-serial - документальный сериал
        * russian-serial - Русский сериал
        * foreign-serial - Иностранный сериал
        * anime-serial - Аниме сериал (все, что больше 1 серии)
        * multi-part-film - Фильм из нескольких частей
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)
        """
        if type(types) == list:
            if self.allow_warnings and any([x in self.Types.get_list() for x in types]):
                print('Предупреждение! Один из параметров types не содержится в списках доступных!')
            self._args['types'] = ','.join(types)
        elif type(types) == str:
            if self.allow_warnings and types not in self.Types.get_list():
                print(f'Предупреждение! Один из параметров types ("{types}") не содержится в списках доступных!')
            self._args['types'] = types
        else:
            raise ValueError(f"Ожидался тип данных 'list' или 'str'. Получено: '{type(types)}'")
        return self._ret()

    def year(self, year: int) -> 'Api':
        """
        Год выпуска мультимедиа.
        :year: Год выпуска мультимедиа. Целое число.
        """
        self._args['year'] = year
        return self._ret()
    
    def camrip(self, camrip: bool = True) -> 'Api':
        """
        Снято ли с камеры.
        :camrip: Снято ли с камеры. По умолчанию True
        """
        self._args['camrip'] = camrip
        return self._ret()
    
    def lgbt(self, lgbt: bool = True) -> 'Api':
        """
        Имеется ли lgbt контент.
        :camrip: Имеется ли lgbt контент. По умолчанию True
        """
        self._args['lgbt'] = lgbt
        return self._ret()
    
    def translation_id(self, translation_id: int) -> 'Api':
        """
        Id перевода. Посмотреть все доступные переводы можно используя эндпоинт translations
        :translation_id: Id перевода.
        """
        self._args['translation_id'] = translation_id
        return self._ret()
    
    def translation_type(self, translation_type: str) -> 'Api':
        """
        Тип перевода. Озвучка или субтитры. subtitles/voice
        :translation_type: Тип перевода. subtitles/voice
        """
        if translation_type not in ['subtitles', 'voice']:
            raise ValueError(f'Параметр translation_type должен быть "subtitles" или "voice", получено: "{translation_type}"')
        self._args['translation_type'] = translation_type
        return self._ret()
    
    def anime_kind(self, anime_kind: str) -> 'Api':
        """
        Тип аниме (указывая этот параметр, в результате будет только аниме).
        :anime_kind: Тип аниме.

        Вы можете воспользоваться вспомогательным классом AnimeKind (KodikSearch.AnimeKind или KodikList.AnimeKind или Api.AnimeKind).
        Доступные фильтры:\n
        * tv - ТВ Сериал
        * tv13 - Длительность серии ~13 минут
        * tv24 - Длительность серии ~24 минут
        * tv48 - Длительность серии ~48 минут
        * movie - Фильм
        * special - Спец. выпуск
        * ova
        * ona
        * music - Музыкальный клип / Проморолик
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)\n
        """
        if self.allow_warnings and anime_kind not in self.AnimeKind.get_list():
            print(f'Предупреждение! Параметр anime_kind "{anime_kind}" не содержится в списках доступных.')
        self._args['anime_kind'] = anime_kind
        return self._ret()
    
    def anime_status(self, anime_status: str) -> 'Api':
        """
        Статус выхода аниме. Вышло/Онгоинг/Анонс - released/ongoing/anons
        :anime_status: Статус выхода аниме.
        """
        if anime_status not in ['released', 'ongoing', 'anons']:
            raise ValueError(f'Параметр anime_status должен быть одним из "released", "ongoing", "anons". Получено: {anime_status}')
        self._args['anime_status'] = anime_status
        return self._ret()
    
    def mydramalist_tags(self, mydramalist_tags: list|str) -> 'Api':
        """
        Теги на MyDramaList.
        :mydramalist_tags: Теги на MyDramaList.
        """
        if type(mydramalist_tags) == list:
            self._args['mydramalist_tags'] = ','.join(mydramalist_tags)
        else:
            self._args['mydramalist_tags'] = mydramalist_tags
        return self._ret()
    
    def rating_mpaa(self, rating_mpaa: str) -> 'Api':
        """
        Возрастной рейтинг по mpaa.
        :rating_mpaa: Возрастной рейтинг по mpaa.

        Вы можете воспользоваться вспомогательным классом MPAArating (KodikSearch.MPAArating или KodikList.MPAArating или Api.MPAArating).
        Доступные фильтры:\n
        * g - Нет возрастных ограничений.
        * pg - Рекомендуется присутствие родителей.
        * pg-13 - Детям до 13 лет просмотр нежелателен.
        * r - Лицам до 17 лет обязательно присутствие взрослого.
        * rx - Хeнтай / Пoрнография    
        \nЧисто технически, существует рейтинг r+, но почему-то у меня не получилось отфильтровать по нему поиск (выдавался рейтинг r).
        \n(Для передачи параметра напрямую, строкой, укажите его на английском, как указано выше)
        """
        if self.allow_warnings and rating_mpaa not in self.MPAArating.get_list():
            print(f'Предупреждение! Параметр rating_mpaa "{rating_mpaa}" не содержится в доступных.')
        self._args['rating_mpaa'] = rating_mpaa
        return self._ret()
    
    def minimal_age(self, minimal_age: int) -> 'Api':
        """
        Минимальный возраст зрителя. Через фильтр проходят все элементы, у которых указанный возраст совпадает с переданным параметром или больше его.
        :minimal_age: Минимальный возраст зрителя.
        """
        self._args['minimal_age'] = minimal_age
        return self._ret()
    
    def kinopoisk_rating(self, kinopoisk_rating: float) -> 'Api':
        """
        Рейтинг на кинопоиске. Ищет только элементы, у которых оценка точно совпадает с указанным.
        :kinopoisk_rating: Рейтинг на кинопоиске.
        """
        self._args['kinopoisk_rating'] = kinopoisk_rating
        return self._ret()
    
    def imdb_rating(self, imdb_rating: float) -> 'Api':
        """
        Рейтинг на imdb. Ищет только элементы, у которых оценка точно совпадает с указанным.
        :imdb_rating: Рейтинг на imdb.
        """
        self._args['imdb_rating'] = imdb_rating
        return self._ret()
    
    def shikimori_rating(self, shikimori_rating: float) -> 'Api':
        """
        Рейтинг на шикимори. Ищет только элементы, у которых оценка точно совпадает с указанным.
        :shikimori_rating: Рейтинг на шикимори.
        """
        self._args['shikimori_rating'] = shikimori_rating
        return self._ret()
    
    def anime_studios(self, anime_studios: list|str) -> 'Api':
        """
        Студия/студии анимации занимающиеся производством. Зависит от регистра.
        :anime_studios: Студия/студии анимации занимающиеся производством.
        """
        if type(anime_studios) == list:
            self._args['anime_studios'] = ','.join(anime_studios)
        else:
            self._args['anime_studios'] = anime_studios
        return self._ret()
    
    def genres(self, genres: str | list) -> 'Api':
        """
        Жанры мультимедиа. Принимает строку или список строк.
        :genres: Жанры мультимедиа.

        Вы можете воспользоваться вспомогательным классом Genres (KodikSearch.Genres или KodikList.Genres или Api.Genres).
        Доступные фильтры:\n    
        * anime - аниме
        * drama - драма
        * comedy - комедия
        * cartoon - мультфильм
        * fantasy - фэнтези
        * action - боевик
        * adventures - приключения
        * fantastika - фантастика
        \n(Для передачи параметра напрямую, строкой, укажите его на русском, как указано выше)
        """
        if type(genres) == list:
            if self.allow_warnings and any([x not in self.Genres.get_list() for x in genres]):
                print('Предупреждение! Один из указанных жанров отсутствует в списках доступных.')
            self._args['genres'] = ','.join(genres)
        else:
            if self.allow_warnings and genres not in self.Genres.get_list():
                print(f'Предупреждение! Указанный жанр "{genres}" отсутствует в списках доступных.')
            self._args['genres'] = genres
        return self._ret()
    
    def anime_genres(self, anime_genres: str | list) -> 'Api':
        """
        Аниме жанры. Принимает строку или список строк.
        :anime_genres: Аниме жанры.

        Вы можете воспользоваться вспомогательным классом AnimeGenres (KodikSearch.AnimeGenres или KodikList.AnimeGenres или Api.AnimeGenres).
        Доступные фильтры:\n
        * military - Военное
        * drama - Драма
        * history - Исторический
        * action - Экшен
        * adventures - Приключения
        * senen - Сёнен
        * fantasy - Фэнтези
        * comedy - Комедия
        * martial_arts - Боевые искусства
        * romance - Романтика
        * psychological - Психологическое
        * thriller - Триллер
        * everyday_life - Повседневность
        * supernatural - Сверхъестественное
        * sport - Спорт
        * school - Школа
        * music - Музыка
        * fantastika - Фантастика
        * samurai - Самураи
        \n(Для передачи параметра напрямую, строкой, укажите его на русском, как указано выше)
        """
        if type(anime_genres) == list:
            if self.allow_warnings and any([x not in self.AnimeGenres.get_list() for x in anime_genres]):
                print('Предупреждение! Один из указанных аниме жанров отсутствует в списках доступных.')
            self._args['anime_genres'] = ','.join(anime_genres)
        else:
            if self.allow_warnings and anime_genres not in self.AnimeGenres.get_list():
                print(f'Предупреждение! Указанный аниме жанр "{anime_genres}" отсутствует в списках доступных.')
            self._args['anime_genres'] = anime_genres
        return self._ret()
    
    def duration(self, duration: int) -> 'Api':
        """
        Продолжительность одной серии или фильма в минутах. Возвращаются только элементы с полностью совпадающим значением.
        :duration: Продолжительность в минутах.
        """
        self._args['duration'] = duration
        return self._ret()
    
    def player_link(self, player_link: str) -> 'Api':
        """
        Ссылка на embed страницу кодика. Пример: kodik.info/serial/48654/3520f3c13f024b8fe04bc6143ccdcb7d/720p
        :player_link: Ссылка на embed кодика.
        """
        self._args['player_link'] = player_link
        return self._ret()
    
    def has_field(self, has_field: str) -> 'Api':
        """
        Элемент содержит указанный параметр.
        """
        self._args['has_field'] = has_field
        return self._ret()
    
    def has_fields(self, has_fields: list) -> 'Api':
        """
        Элемент содержит указанные параметры.
        :has_fields: Список строк
        """
        self._args['has_fields'] = ','.join(has_fields)
        return self._ret()
    
    def has_field_and(self, has_field_and: list) -> 'Api':
        """
        Элемент содержит указанные параметры.
        :has_field_and: Список строк
        """
        self._args['has_field_and'] = ','.join(has_field_and)
        return self._ret()
    
    def prioritize_translations(self, prioritize_translations: str | list) -> 'Api':
        """
        Повысить приоритет указанных id переводов в результатах выдачи. Принимает строку или список строк.
        :prioritize_translations: Строка или список строк с id переводов.

        Посмотреть список переводов можно по эндпоинту translations. 
        По умолчанию приоритет выдается профессиональным и многоголосым озвучкам.
        Для отключения стандартного приоритета укажите 0.
        """
        if type(prioritize_translations) == list:
            self._args['prioritize_translations'] = ','.join(prioritize_translations)
        else:
            self._args['prioritize_translations'] = prioritize_translations
        return self._ret()
    
    def unprioritize_translations(self, unprioritize_translations: str | list) -> 'Api':
        """
        Понизить приоритет указанных id переводов в результатах выдачи. Принимает строку или список строк.
        :unprioritize_translations: Строка или список строк с id переводов.

        Посмотреть список переводов можно по эндпоинту translations. 
        По умолчанию установлен низкий приоритет озвучкам на Английском и Украинском языках, а также субтитров.
        Для отключения стандартного приоритета укажите 0.
        """
        if type(unprioritize_translations) == list:
            self._args['unprioritize_translations'] = ','.join(unprioritize_translations)
        else:
            self._args['unprioritize_translations'] = unprioritize_translations
        return self._ret()
    
    def block_translations(self, block_translations: str | list) -> 'Api':
        """
        Убрать переводы из результатов. Принимает строку или список строк.
        :block_translations: Строка или список строк с id переводов. 
        """
        if type(block_translations) == list:
            self._args['block_translations'] = ','.join(block_translations)
        else:
            self._args['block_translations'] = block_translations
        return self._ret()
    
    def prioritize_translation_type(self, prioritize_translation_type: str) -> 'Api':
        """
        Увеличить приоритет типа перевода subtitles/voice.
        :prioritize_translation_type: subtitles/voice
        """
        if prioritize_translation_type not in ['subtitles', 'voice']:
            raise ValueError(f'Параметр prioritize_translation_type должен быть "subtitles" или "voice". Получено: "{prioritize_translation_type}"')
        self._args['prioritize_translation_type'] = prioritize_translation_type
        return self._ret()
    
    def season(self, season: int) -> 'Api':
        """
        Сезон выхода аниме.
        :season: Сезон выхода аниме.
        """
        self._args['season'] = season
        return self._ret()
    
    def episode(self, episode: int) -> 'Api':
        """
        В результате будут только элементы у которых есть указанный эпизод.
        :episode: Эпизод для поиска.
        """
        self._args['episode'] = episode
        return self._ret()
    
    def not_blocked_in(self, not_blocked_in: str | list) -> 'Api':
        """
        В результате будут элементы не заблокированные в указанной стране/странах.
        :not_blocked_in: Строка или список строк с названиям стран на русском языке (зависит от регистра).
        """
        if type(not_blocked_in) == list:
            self._args['not_blocked_in'] = ','.join(not_blocked_in)
        else:
            self._args['not_blocked_in'] = not_blocked_in
        return self._ret()
    
    def not_blocked_for_me(self, not_blocked_for_me: bool = True) -> 'Api':
        """
        В результате будут элементы не заблокированные в стране, откуда отправлен запрос (предположительно проверка по ip)
        :not_blocked_for_me: Не заблокировано в стране запроса. По умолчанию True.
        """
        self._args['not_blocked_for_me'] = not_blocked_for_me
        return self._ret()
    
    def countries(self, countries: str | list) -> 'Api':
        """
        Страны в которых снят фильм/сериал.
        :countries: Строка или список строк с названиям стран на русском языке (зависит от регистра).
        """
        if type(countries) == list:
            self._args['countries'] = ','.join(countries)
        else:
            self._args['countries'] = countries
        return self._ret()
    
    def actors(self, actors: str | list) -> 'Api':
        """
        Вернет элементы где в актерах указан(ы) переданные имена.
        :actors: Строка или список строк с именами (зависит от регистра).
        """
        if type(actors) == list:
            self._args['actors'] = ','.join(actors)
        else:
            self._args['actors'] = actors
        return self._ret()
    
    def directors(self, directors: str | list) -> 'Api':
        """
        Вернет элементы где в режиссерах указан(ы) переданные имена.
        :directors: Строка или список строк с именами (зависит от регистра).
        """
        if type(directors) == list:
            self._args['directors'] = ','.join(directors)
        else:
            self._args['directors'] = directors
        return self._ret()
    
    def producers(self, producers: str | list) -> 'Api':
        """
        Вернет элементы где в продюсерах указан(ы) переданные имена.
        :producers: Строка или список строк с именами (зависит от регистра).
        """
        if type(producers) == list:
            self._args['producers'] = ','.join(producers)
        else:
            self._args['producers'] = producers
        return self._ret()
    
    def writers(self, writers: str | list) -> 'Api':
        """
        Вернет элементы где в писателях/сценаристах указан(ы) переданные имена.
        :writers: Строка или список строк с именами (зависит от регистра).
        """
        if type(writers) == list:
            self._args['writers'] = ','.join(writers)
        else:
            self._args['writers'] = writers
        return self._ret()
    
    def composers(self, composers: str | list) -> 'Api':
        """
        Вернет элементы где в композиторах указан(ы) переданные имена.
        :composers: Строка или список строк с именами (зависит от регистра).
        """
        if type(composers) == list:
            self._args['composers'] = ','.join(composers)
        else:
            self._args['composers'] = composers
        return self._ret()

    def editors(self, editors: str | list) -> 'Api':
        """
        Вернет элементы где в монтажерах указан(ы) переданные имена.
        :editors: Строка или список строк с именами (зависит от регистра).
        """
        if type(editors) == list:
            self._args['editors'] = ','.join(editors)
        else:
            self._args['editors'] = editors
        return self._ret()
    
    def designers(self, designers: str | list) -> 'Api':
        """
        Вернет элементы где в дизайнерах/художниках указан(ы) переданные имена.
        :designers: Строка или список строк с именами (зависит от регистра).
        """
        if type(designers) == list:
            self._args['designers'] = ','.join(designers)
        else:
            self._args['designers'] = designers
        return self._ret()
    
    def operators(self, operators: str | list) -> 'Api':
        """
        Вернет элементы где в операторах указан(ы) переданные имена.
        :operators: Строка или список строк с именами (зависит от регистра).
        """
        if type(operators) == list:
            self._args['operators'] = ','.join(operators)
        else:
            self._args['operators'] = operators
        return self._ret()
    
    def licensed_by(self, licensed_by: str | list) -> 'Api':
        """
        Вернет элементы где владельцем лицензии (на перевод/озвучку ?) является указанная компания.
        :licensed_by: Строка или список строк с названиями компаний - владельцев лицензии. (Зависит от регистра). 
        """
        if type(licensed_by) == list:
            self._args['licensed_by'] = ','.join(licensed_by)
        else:
            self._args['licensed_by'] = licensed_by
        return self._ret()
    
    def with_material_data(self, with_material_data: bool = True) -> 'Api':
        """
        Добавляет в результат дополнительные данные о мультимедиа.
        :with_material_data: Добавить доп. данные. По умолчанию True.
        """
        self._args['with_material_data'] = with_material_data
        return self._ret()
    
    def with_seasons(self, with_seasons: bool = True) -> 'Api':
        """
        Добавляет в результат ссылки на сезоны. (ссылки на embed на kodik.info)
        :with_seasons: Добавить список сезонов. По умолчанию True.
        """
        self._args['with_seasons'] = with_seasons
        return self._ret()
    
    def with_episodes(self, with_episodes: bool = True) -> 'Api':
        """
        Добавляет в результат ссылки на конкретные эпизоды, автоматически включается параметр with_seasons. (ссылки на embed на kodik.info)
        :with_episodes: Добавить список эпизодов. По умолчанию True.
        """
        self._args['with_episodes'] = with_episodes
        return self._ret()
    
    def with_episodes_data(self, with_episodes_data: bool = True) -> 'Api':
        """
        Добавляет в результат данные для конкретных эпизодов (если есть) в виде названия, описания, автоматически включается параметр with_episodes.
        :with_episodes_data: Добавить данные для эпизодов, если есть. По умолчанию True.
        """
        self._args['with_episodes_data'] = with_episodes_data
        return self._ret()
    
    def with_page_links(self, with_page_links: bool = True) -> 'Api':
        """
        Заменяет в результате ссылку на embed (kodik.info) на сайт с плеером (kodik.online)
        :with_page_links: Заменить ссылку на сайт с плеером.
        """
        self._args['with_page_links'] = with_page_links
        return self._ret()
    
    # ================================================================
    def api_request(self, parameters: dict | None = None, link: str | None = None) -> dict:
        """
        Запрос к api. Требуется передать только один из параметров parameters или link

        :parameters: Параметры и фильтры для запроса.
        :link: Полная ссылка (для следующей и предыдущей страниц)
        """
        if link is None and self._endpoint not in ['search', 'list', 'translations']:
            raise errors.PostArgumentsError(f'Неизвестный эндпоинт. Ожидался один из "search", "list", "translations". Получен: "{self._endpoint}"')
        if self.token is None:
            raise errors.TokenError('Токен kodik не указан')
        if parameters is None and link is None:
            raise ValueError('Хотя-бы один из параметров "parameters" или "link" должен быть указан для использования api_request')
        
        if parameters:
            payload = {"token": self.token}
            for item, val in parameters.items():
                payload[item] = val

            url = f"https://kodikapi.com/{self._endpoint}"
            data = requests.post(url, data=payload)
        else:
            url = link
            data = requests.post(url)

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
        if 'next_page' in data.keys():
            self._next_link = data['next_page']
        else:
            self._next_link = None
        if 'prev_page' in data.keys():
            self._prev_link = data['prev_page']
        else:
            self._prev_link = None
        return data
    
    async def api_request_async(self, parameters: dict | None = None, link: str | None = None) -> dict:
        """
        Асинхронный запрос к api. Требуется передать только один из параметров parameters или link

        :parameters: Параметры и фильтры для запроса.
        :link: Полная ссылка (для следующей и предыдущей страниц)
        """
        if not async_available:
            raise RuntimeError('При попытке импорта внутренних инструментов библиотеки anime-parsers-ru произошла ошибка и AsyncSession не доступен.')

        if link is None and self._endpoint not in ['search', 'list', 'translations']:
            raise errors.PostArgumentsError(f'Неизвестный эндпоинт. Ожидался один из "search", "list", "translations". Получен: "{self._endpoint}"')
        if self.token is None:
            raise errors.TokenError('Токен kodik не указан')
        if parameters is None and link is None:
            raise ValueError('Хотя-бы один из параметров "parameters" или "link" должен быть указан для использования api_request')
        
        if parameters:
            payload = {"token": self.token}
            for item, val in parameters.items():
                payload[item] = val
            url = f"https://kodikapi.com/{self._endpoint}"
            data = await AsyncSession().post(url, data=payload)
        else:
            url = link
            data = await AsyncSession().post(url)
        
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
        if 'next_page' in data.keys():
            self._next_link = data['next_page']
        else:
            self._next_link = None
        if 'prev_page' in data.keys():
            self._prev_link = data['prev_page']
        else:
            self._prev_link = None
        return data

    def execute(self, return_json: bool = False) -> Response:
        """
        Выполнить запрос.
        :return_json: Возвращать чистый ответ сервера, вместо Response. По умолчанию False.
        """
        if self._endpoint is None:
            raise TypeError('Don\'t use _ApiRequest directly! Use Search and List classes instead.')
        data = self.api_request(parameters=self._args)
        if return_json:
            return data
        else:
            return Response(data)

    async def execute_async(self, return_json: bool = False) -> Response:
        """
        Выполнить запрос асинхронно.
        :return_json: Возвращать чистый ответ сервера, вместо Response. По умолчанию False.
        """
        if self._endpoint is None:
            raise TypeError('Don\'t use _ApiRequest directly! Use Search and List classes instead.')
        data = await self.api_request_async(parameters=self._args)
        if return_json:
            return data
        else:
            return Response(data)
    
    def next_page(self, link: str | None = None) -> Response:
        """
        Выполнить запрос для получения следующей страницы списка. (Не работает для поиска)

        Для использования требуется выполнение обычного запроса типа List который в своем ответе вернет ссылку на следующую страницу.
        Или передать параметр link.

        :link: Полная ссылка на следующую страницу. Если None - использует внутреннюю переменную на следующую страницу. По умолчанию None.
        """
        if link:
            data = self.api_request(link=link)
            return Response(data)
        if self._next_link:
            data = self.api_request(link=self._next_link)
            return Response(data)
        raise ValueError('Для использования этой функции параметр next_page должен быть в результатах предыдущего запроса.')
    
    def prev_page(self, link: str | None = None) -> Response:
        """
        Выполнить запрос для получения предыдущей страницы списка. (Не работает для поиска)

        Для использования требуется выполнение обычного запроса типа List который в своем ответе вернет ссылку на предыдущую страницу.
        Или передать параметр link.

        :link: Полная ссылка на предыдущую страницу. Если None - использует внутреннюю переменную на предыдущую страницу. По умолчанию None.
        """
        if link:
            data = self.api_request(link=link)
            return Response(data)
        if self._prev_link:
            data = self.api_request(link=self._prev_link)
            return Response(data)
        raise ValueError('Для использования этой функции параметр prev_page должен быть в результатах предыдущего запроса.')
    
    async def next_page_async(self, link: str | None = None) -> Response:
        """
        Выполнить асинхронный запрос для получения следующей страницы списка. (Не работает для поиска)

        Для использования требуется выполнение обычного запроса типа List который в своем ответе вернет ссылку на следующую страницу.
        Или передать параметр link.

        :link: Полная ссылка на следующую страницу. Если None - использует внутреннюю переменную на следующую страницу. По умолчанию None.
        """
        if link:
            data = await self.api_request_async(link=link)
            return Response(data)
        if self._next_link:
            data = await self.api_request_async(link=self._next_link)
            return Response(data)
        raise ValueError('Для использования этой функции параметр next_page должен быть в результатах предыдущего запроса.')
    
    async def prev_page_async(self, link: str | None = None) -> Response:
        """
        Выполнить асинхронный запрос для получения предыдущей страницы списка. (Не работает для поиска)

        Для использования требуется выполнение обычного запроса типа List который в своем ответе вернет ссылку на предыдущую страницу.
        Или передать параметр link.

        :link: Полная ссылка на предыдущую страницу. Если None - использует внутреннюю переменную на предыдущую страницу. По умолчанию None.
        """
        if link:
            data = await self.api_request_async(link=link)
            return Response(data)
        if self._prev_link:
            data = await self.api_request_async(link=self._prev_link)
            return Response(data)
        raise ValueError('Для использования этой функции параметр prev_page должен быть в результатах предыдущего запроса.')
    
    def get_translations(self) -> dict:
        """
        Выполняет запрос к апи по эндпоинту translations.
        Возвращает словарь.
        """
        self._endpoint = 'translations' # Да, костыль. Но плодить еще один класс чтобы сделать 1 запрос, тоже странно.
        data = self.api_request(parameters={})
        self._endpoint = None
        return data
    
    def order(self, value: str):
        """
        Устанавливает параметр направления сортировки для запроса list.

        Параметры:
            value (str): Параметр направления сортировки из списка KodikList.Order
            * asc - По возрастанию
            * desc - По убыванию

        Raises:
            errors.PostArgumentsError: Если указан недопустимый параметр направления сортировки.
        """
        if value not in self.Order.get_list():
            raise errors.PostArgumentsError(
                f'Недопустимый параметр направления сортировки: {value}. Допустимые параметры: {", ".join(self.Order.get_list())}')

        self._args['order'] = value
        return self._ret()

    def sort(self, value: str):
        """
        Устанавливает параметр сортировки для запроса list.

        Параметры:
            value (str): Параметр сортировки из списка KodikList.Sort
            * year - По году
            * created_at - По дате добавления
            * updated_at - По дате обновления
            * kinopoisk_rating - По рейтингу Кинопоиска
            * imdb_rating - По рейтингу IMDb
            * shikimori_rating - По рейтингу Shikimori

        Raises:
            errors.PostArgumentsError: Если указан недопустимый параметр сортировки.
        """
        if value not in self.Sort.get_list():
            raise errors.PostArgumentsError(
                f'Недопустимый параметр сортировки: {value}. Допустимые параметры: {", ".join(self.Sort.get_list())}')

        self._args['sort'] = value
        return self._ret()


class KodikSearch(Api):
    """
    Абстракция для запроса к апи плеера кодик.

    Документацию по доступным параметрам вы можете найти в репозитории: https://github.com/YaNesyTortiK/AnimeParsers/blob/main/KODIK_API.md
    
    Пример использования:

    query = Search().title("Кулинарные скитания").limit(5).anime_status('released')
    data = query.execute()

    """
    def __init__(self, token: str | None = None, allow_warnings: bool = True, _args: dict = {}):
        super().__init__(token, allow_warnings, _args, _endpoint='search')

    def order(self, *args):
        """
        Данный параметр недоступен для запроса search.
        """
        raise errors.PostArgumentsError('Для запроса list параметр order не доступен.') 
    
    def sort(self, *args):
        """
        Данный параметр недоступен для запроса search.
        """
        raise errors.PostArgumentsError('Для запроса list параметр sort не доступен.') 

class KodikList(Api):
    def __init__(self, token: str | None = None, allow_warnings: bool = True, _args: dict = {}):
        super().__init__(token, allow_warnings, _args, _endpoint='list')


    def title(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр title не доступен.')
    
    def title_orig(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр title_orig не доступен.')
    
    def strict(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр strict не доступен.')

    def full_match(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр full_match не доступен.') 

    def shikimori_id(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр shikimori_id не доступен.') 

    def kinopoisk_id(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр kinopoisk_id не доступен.') 

    def imdb_id(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр imdb_id не доступен.') 

    def id(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр id не доступен.') 

    def mdl_id(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр mdl_id не доступен.') 

    def worldart_cinema_id(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр worldart_cinema_id не доступен.') 

    def worldart_link(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр worldart_link не доступен.') 
    
    def player_link(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр player_link не доступен.') 
    
    def prioritize_translations(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр prioritize_translations не доступен.') 
    
    def unprioritize_translations(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр unprioritize_translations не доступен.') 
    
    def season(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр season не доступен.') 
    
    def episode(self, *args):
        """
        Данный параметр недоступен для запроса list.
        """
        raise errors.PostArgumentsError('Для запроса list параметр episode не доступен.') 
    
