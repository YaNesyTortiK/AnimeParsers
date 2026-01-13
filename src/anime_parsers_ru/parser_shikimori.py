import requests
try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True
import re
from bs4 import BeautifulSoup as Soup
import json

try:
    from . import errors # Импорт если библиотека установлена
except ImportError:
    import errors # Импорт если библиотека не установлена и файл лежит локально
    
class ShikimoriParser:
    """
    Парсер шикимори. Не использует встроенный в шикимори api.
    """

    genres_list = ['1-Action', '2-Adventure', '3-Racing', '4-Comedy', '5-Avant-Garde', '6-Mythology', '7-Mystery', '8-Drama', '9-Ecchi', '10-Fantasy', '11-Strategy-Game', '13-Historical', '14-Horror', '15-Kids', '17-Martial-Arts', '18-Mecha', '19-Music', '20-Parody', '21-Samurai', '22-Romance', '23-School', '24-Sci-Fi', '25-Shoujo', '27-Shounen', '29-Space', '30-Sports', '31-Super-Power', '32-Vampire', '35-Harem', '36-Slice-of-Life', '37-Supernatural', '38-Military', '39-Detective', '40-Psychological', '42-Seinen', '43-Josei', '102-Team-Sports', '103-Video-Game', '104-Adult-Cast', '105-Gore', '106-Reincarnation', '107-Love-Polygon', '108-Visual-Arts', '111-Time-Travel', '112-Gag-Humor', '114-Award-Winning', '117-Suspense', '118-Combat-Sports', '119-CGDCT', '124-Mahou-Shoujo', '125-Reverse-Harem', '130-Isekai', '131-Delinquents', '134-Childcare', '135-Magical-Sex-Shift', '136-Showbiz', '137-Otaku-Culture', '138-Organized-Crime', '139-Workplace', '140-Iyashikei', '141-Survival', '142-Performing-Arts', '143-Anthropomorphic', '144-Crossdressing', '145-Idols-(Female)', '146-High-Stakes-Game', '147-Medical', '148-Pets', '149-Educational', '150-Idols-(Male)', '151-Romantic-Subtext', '543-Gourmet']

    def __init__(self, use_lxml: bool = False, mirror: str|None = None) -> None:
        """
        :use_lxml: Использовать lxml парсер. В некоторых случаях может не работать, однако работает значительно быстрее стандартного.
        :mirror: В случае, если оригинальный домен заблокирован, можно использовать этот параметр, чтобы заменить адрес сайта на зеркало. Пример: "1234.net"
        """
        if not LXML_WORKS and use_lxml:
            raise ImportWarning('Параметр use_lxml установлен в true, однако при попытке импорта lxml произошла ошибка')
        self.USE_LXML = use_lxml
        if mirror: # Если есть зеркало, то меняем домен на него
            self._dmn = mirror
        else:
            self._dmn = "shikimori.one"

    def search(self, title: str) -> list:
        """
        Быстрый поиск аниме по названию (ограничено по количеству результатов).

        :title: название аниме

        Возвращает список словарей в виде:
        [
            {
                "genres": ["Жанр1", "Жанр2"],
                "link": "Ссылка на страницу аниме",
                "original_title": "Оригинальное название (транслит японского названия на английском)",
                "poster": "Ссылка на постер к аниме (плохое качество) (если есть, иначе None)",
                "shikimori_id": "id шикимори",
                "status": "статус (вышло, онгоинг, анонс) (если есть, иначе None)",
                "studio": "студия анимации (если есть, иначе None)",
                "title": "Название",
                "type": "тип аниме (TV сериал, OVA, ONA, ...) (если есть, иначе None)",
                "year": "год выхода (если есть, иначе None)"
            }
        ]
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
        }

        params = {
            'search': title,
        }
        # Используем autocomplete эндпоинт, потому что обычный поиск тупо блокируется если находит 18+ контент
        response = requests.get(f'https://{self._dmn}/animes/autocomplete/v2', params=params, headers=headers)
        if response.status_code == 429:
            raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code == 520:
            raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()['content']
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response, 'html.parser')
        res = []
        for anime in soup.find_all('div', {'class': 'b-db_entry-variant-list_item'}):
            if anime.get_attribute_list('data-type')[0] != 'anime': # нас интересует только аниме
                continue
            c_data = {}
            c_data['link'] = anime.get_attribute_list('data-url')[0]
            c_data['shikimori_id'] = anime.get_attribute_list('data-id')[0]
            if not anime.find('div', {'class': 'image'}) is None:
                c_data['poster'] = anime.find('div', {'class': 'image'}).find('picture').find('img').get_attribute_list('srcset')[0].replace(' 2x', '')
            else:
                c_data['poster'] = None
            info = anime.find('div', {'class': 'info'})
            c_data['original_title'] = info.find('div', {'class': 'name'}).find('a').get_attribute_list('title')[0]
            c_data['title'] = info.find('div', {'class': 'name'}).find('a').text.split('/')[0]
            if info.find('div', {'class': 'line'}).find('div', {'class': 'key'}).text == 'Тип:':
                c_data['type'] = info.find('div', {'class': 'line'}).find('div', {'class': 'value'}).find('div', {'class': 'b-tag'}).text
                c_data['status'] = info.find('div', {'class': 'line'}).find('div', {'class': 'value'}).find_all('div', {'class': 'b-anime_status_tag'})[-1].get_attribute_list('data-text')[0]
                if len(info.find('div', {'class': 'line'}).find('div', {'class': 'value'}).find_all('div', {'class': 'b-anime_status_tag'})) > 1:
                    c_data['studio'] = info.find('div', {'class': 'line'}).find('div', {'class': 'value'}).find_all('div', {'class': 'b-anime_status_tag'})[0].get_attribute_list('data-text')[0]
                else:
                    c_data['studio'] = None
                if len(info.find('div', {'class': 'line'}).find('div', {'class': 'value'}).find_all('div', {'class': 'b-tag'})) > 1:
                    c_data['year'] = info.find('div', {'class': 'line'}).find('div', {'class': 'value'}).find_all('div', {'class': 'b-tag'})[-1].text.replace(' год', '')
                else:
                    c_data['year'] = None
            else:
                c_data['type'] = None # В некоторых случаях возможна ситуация когда не известна ни дата выхода, ни тип аниме.
                c_data['status'] = None
                c_data['studio'] = None
                c_data['year'] = None
            c_data['genres'] = []
            for genre in info.find_all('span', {'class': 'genre-ru'}):
                c_data['genres'].append(genre.text)
            res.append(c_data)
        return res
    
    def anime_info(self, shikimori_link: str) -> dict:
        """
        Получение данных по аниме парсингом.

        :shikimori_link: ссылка на страницу шикимори с информацией (прим: https://shikimori.one/animes/z20-naruto)

        Возвращает словарь вида:
        {
            "dates": "Даты выхода",
            "description": "Описание",
            "episode_duration": "Средняя продолжительность серии",
            "episodes": "Количество эпизодов если статус 'вышло' или 'вышедших эпизодов / анонсировано эпизодов' или None (если фильм)",
            "genres": ["Жанр1", "Жанр2"],
            "licensed": "Кто лицензировал в РФ или None",
            "licensed_in_ru": "Название аниме как лицензировано в РФ или None",
            "next_episode": "Дата выхода следующего эпизода или None",
            "original_title": "Оригинальное название",
            "picture": "Ссылка на jpeg постер",
            "premiere_in_ru": "Дата премьеры в РФ или None",
            "rating": "возрастной рейтинг",
            "score": "оценка на шикимори",
            "status": "статус выхода",
            "studio": "студия анимации",
            "themes": ["Тема1", "Тема2"],
            "title": "Название на русском",
            "type": "тип аниме (TV Сериал, Фильм, т.п.)"
        }
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        }
        response = requests.get(shikimori_link, headers=headers)
        if response.status_code == 429:
            raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code == 520:
            raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response, 'html.parser')
        if not soup.find('p', {'class': 'age-restricted-warning'}) is None:
            raise errors.AgeRestricted(f'Аниме по ссылке "{shikimori_link}" невозможно обработать из-за блокировки по возрастному рейтингу.')
        res = {}
        title = soup.find('header', {'class': 'head'}).find('h1').text.split(' / ')
        res['title'] = title[0]
        res['original_title'] = title[1]
        picture = soup.find('picture')
        if not picture is None:
            res['picture'] = picture.find('img').get_attribute_list('srcset')[0].replace(' 2x', '')
        else:
            res['picture'] = None
        info = soup.find('div', {'class': 'c-info-left'}).find('div', {'class': 'block'})
        for line in info.find_all('div', {'class': 'line'}):
            key = line.find('div', {'class': 'key'}).text
            value = line.find('div', {'class': 'value'})
            if key == 'Тип:': res['type'] = value.text
            elif key == 'Эпизоды:': res['episodes'] = value.text
            elif key == 'Следующий эпизод:': res['next_episode'] = value.find('span').get_attribute_list('data-datetime')[0]
            elif key == 'Длительность эпизода:': res['episode_duration'] = value.text
            elif key == 'Статус:': 
                res['status'] = value.find('span').get_attribute_list('data-text')[0]
                if len(value.find_all('span')) > 1:
                    res['dates'] = value.find_all('span')[-1].text
                else:
                    res['dates'] = value.text.strip()
            elif key == 'Жанры:': res['genres'] = [genre.text for genre in value.find_all('span', 'genre-ru')]
            elif key == 'Темы:' or key == 'Тема:': res['themes'] = [genre.text for genre in value.find_all('span', 'genre-ru')]
            elif key == 'Рейтинг:': res['rating'] = value.text
            elif key == 'Лицензировано:': res['licensed'] = value.text
            elif key == 'Лицензировано в РФ под названием:': res['licensed_in_ru'] = value.text
            elif key == 'Премьера в РФ:': res['premiere_in_ru'] = value.text
        
        # Заполняем ключи если их нет в информации
        for k in ["type", "episodes", "next_episode", "episode_duration", "status", "genres", "themes", "rating", 
                  "dates", "licensed", "licensed_in_ru", "premiere_in_ru"]:
            if k not in res.keys():
                res[k] = None

        desc = soup.find('div', {'class': 'text'})
        if not desc is None:
            res['description'] = desc.text
        else:
            res['description'] = None
        score = soup.find('div', {'class': 'score-value'})
        if not score is None:
            res['score'] = score.text
        else:
            res['score'] = None
        
        studio = soup.find('a', {'title': re.compile(r'Аниме студии.*')})
        if not studio is None:
            res['studio'] = studio.get_attribute_list('title')[0].replace('Аниме студии ', '', 1)
        else:
            res['studio'] = None
        return res
    
    def additional_anime_info(self, shikimori_link: str) -> dict:
        """
        Получение дополнительных данных об аниме.
        Получаемые данные: связанные аниме (продолжение, предыстория, альтернативное и т.п.), Авторы (автор манги, режиссер), Главные герои, Скриншоты, Ролики, Похожее
        
        :shikimori_link: ссылка на страницу шикимори с информацией (прим: https://shikimori.one/animes/z20-naruto)

        Возвращает словарь вида:
        {
            "related": [
                {
                    "date": "Даты выхода/сезон",
                    "name": "Название",
                    "picture": "Ссылка на картинку",
                    "relation": "тип связи (продолжение, предыстория, адаптация и т.п.)",
                    "type": "Тип (TV сериал, OVA, ONA, манга, ранобэ и т.д.)",
                    "url": "Ссылка на страницу шикимори"
                }
            ],
            "staff": [
                {
                    "name": "Имя человека (на русском)",
                    "roles": ["Роль1", "Роль2"],
                    "link": "ссылка шикимори на человека"
                }
            ],
            "main_characters": [
                {
                    "name": "Имя персонажа",
                    "picture": "Картинка (jpeg)"
                }
            ],
            "screenshots": ["Ссылка на скриншот 1", "Ссылка на скриншот 2"],
            "videos": [
                {
                    "name": "Название видео",
                    "link": "Ссылка на видео (обычно ютуб)"
                }
            ],
            "similar": [
                {
                    "name": "Название аниме (похожего)",
                    "picture": "Картинка (постер)",
                    "link": "Ссылка на шикимори"
                }
            ]
        }
        """

        link = shikimori_link+'resources' if shikimori_link[-1] == '/' else shikimori_link+'/resources'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        }
        response = requests.get(link, headers=headers)
        if response.status_code == 429:
            raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code == 520:
            raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response, 'html.parser')
        if not soup.find('p', {'class': 'age-restricted-warning'}) is None:
            raise errors.AgeRestricted(f'Аниме по ссылке "{shikimori_link}" невозможно обработать из-за блокировки по возрастному рейтингу.')
        res = {
            'related': [], 'staff': [], 'main_characters': [], 'screenshots': [], 'videos': [], 'similar': []
        }
        r1 = soup.find('div', {'class': 'cc-related-authors'})
        for col in r1.find_all('div', {'class': 'c-column'}):
            col_type = col.find('div', {'class': 'subheadline'}).text
            if col_type == 'Связанное':
                for entry in col.find_all('div', {'class': 'b-db_entry-variant-list_item'}):
                    c_data = {}
                    c_data['url'] = entry.get_attribute_list('data-url')[0]
                    c_data['picture'] = None
                    if not entry.find('picture') is None:
                        c_data['picture'] = entry.find('picture').find('img').get_attribute_list('srcset')[0].replace(' 2x', '')
                    try:
                        c_data['name'] = entry.find('div', {'class': 'name'}).find('span', {'class': 'name-ru'}).text
                    except AttributeError:
                        try:
                            c_data['name'] = entry.find('div', {'class': 'name'}).find('span', {'class': 'name-en'}).text
                        except AttributeError:
                            c_data['name'] = None
                    for other in entry.find('div', {'class': 'line'}).find_all('div'):
                        cls = other.get_attribute_list('class')
                        if 'b-anime_status_tag' in cls:
                            c_data['relation'] = other.text
                        elif 'linkeable' in cls:
                            link = other.get_attribute_list('data-href')[0]
                            if '/kind/' in link:
                                c_data['type'] = other.text
                            elif '/season/' in link:
                                c_data['date'] = other.text
                    # Если в связанных клип (по другому отрисовано имя)
                    if c_data['type'] == 'Клип' and c_data['name'] == None:
                        try:
                            c_data['name'] = _tmp.text if (_tmp := entry.find('div', {'class': 'name'}).find('a')) else ''
                        except:
                            pass
                    # Заполняем пустое
                    for k in ['relation', 'type', 'date']:
                        if k not in c_data.keys():
                            c_data[k] = None
                    res['related'].append(c_data)
            
            elif col_type == 'Авторы':
                for entry in col.find_all('div', {'class': 'b-db_entry-variant-list_item'}):
                    c_data = {}
                    c_data['link'] = entry.get_attribute_list('data-url')[0]
                    c_data['name'] = entry.get_attribute_list('data-text')[0]
                    c_data['roles'] = []
                    for role in entry.find('div', {'class': 'line'}).find_all('div', {'class': 'b-tag'}):
                        c_data['roles'].append(role.text)
                    res['staff'].append(c_data)
        try:
            r1 = soup.find('div', {'class': 'c-characters'})
            for char in r1.find_all('article'):
                c_data = {}
                c_data['picture'] = None
                if not char.find('meta', {'itemprop': 'image'}) is None:
                    c_data['picture'] = char.find('meta', {'itemprop': 'image'}).get_attribute_list('content')[0]
                c_data['name'] = _tmp.text if (_tmp := char.find('span', {'class': 'name-ru'})) else ''
                res['main_characters'].append(c_data)
        except:
            pass
        try:
            r1 = soup.find('div', {'class': 'two-videos'})
            if not r1 is None:
                if not r1.find('div', {'class': 'c-screenshots'}) is None:
                    for img in r1.find_all('a', {'class': 'c-screenshot'}):
                        res['screenshots'].append(img.get_attribute_list('href')[0])
                if not r1.find('div', {'class': 'c-videos'}) is None:
                    for vid in r1.find_all('div', {'class': 'c-video'}):
                        c_data = {}
                        c_data['link'] = vid.find('a').get_attribute_list('href')[0]
                        c_data['name'] = _tmp.text if (_tmp := vid.find('span', {'class': 'name'})) else ''
                        res['videos'].append(c_data)
        except:
            pass
        try:
            r1 = soup.find('div', {'class': 'block'})
            if not r1 is None:
                for sim in r1.find_all('article'):
                    c_data = {}
                    c_data['picture'] = None
                    if not sim.find('meta', {'itemprop': 'image'}) is None:
                        c_data['picture'] = sim.find('meta', {'itemprop': 'image'}).get_attribute_list('content')[0]
                    c_data['name'] = sim.find('span', {'class': 'name-ru'}).text
                    c_data['link'] = sim.find('div').get_attribute_list('data-href')[0]
                    res['similar'].append(c_data)
        except:
            pass
        return res
    
    def get_anime_list(self, status: list[str] = [], anime_type: list[str] = [], rating: str | None = None, genres: list[str] = [], start_page: int = 1, page_limit: int = 3, sort_by: str = 'rating') -> list:
        """
        Получить список аниме по фильтрам

        :status: текущий статус аниме (список нужных) (Доступно: ongoing, anons, released, latest) (По умолчанию пусто - любой)
        :anime_type: Тип аниме (список нужных) (Доступно: tv (тв сериал), movie (фильм), ova, ona, special (спецвыпуски), tv_special (тв спецвыпуск), music (клип), pv (проморолик), cm (реклама)) (По умолчанию пусто - любой)
        :rating: Возрастной рейтинг (Один вариант) (Доступно: g (нет возрастного ограничения), pg (рекомендуется присутствие родителей), pg_13 (детям до 13 просмотр не желателен), r (Лицам до 17 лет обязательно присутствие взрослого), r_plus (Лицам до 17 лет просмотр запрещен)) (По умолчанию пусто - любой)
        :genres: Жанры (список нужных) (Доступно: 
            "1-Action": "Экшен",
            "2-Adventure": "Приключения",
            "3-Racing": "Гонки",
            "4-Comedy": "Комедия",
            "5-Avant-Garde": "Авангард",
            "6-Mythology": "Мифология",
            "7-Mystery": "Тайна",
            "8-Drama": "Драма",
            "9-Ecchi": "Этти",
            "10-Fantasy": "Фэнтези",
            "11-Strategy-Game": "Стратегические игры",
            "13-Historical": "Исторический",
            "14-Horror": "Ужасы",
            "15-Kids": "Детское",
            "17-Martial-Arts": "Боевые искусства",
            "18-Mecha": "Меха",
            "19-Music": "Музыка",
            "20-Parody": "Пародия",
            "21-Samurai": "Самураи",
            "22-Romance": "Романтика",
            "23-School": "Школа",
            "24-Sci-Fi": "Фантастика",
            "25-Shoujo": "Сёдзё",
            "27-Shounen": "Сёнен",
            "29-Space": "Космос",
            "30-Sports": "Спорт",
            "31-Super-Power": "Супер сила",
            "32-Vampire": "Вампиры",
            "35-Harem": "Гарем",
            "36-Slice-of-Life": "Повседневность",
            "37-Supernatural": "Сверхъестественное",
            "38-Military": "Военное",
            "39-Detective": "Детектив",
            "40-Psychological": "Психологическое",
            "42-Seinen": "Сэйнэн",
            "43-Josei": "Дзёсей",
            "102-Team-Sports": "Командный спорт",
            "103-Video-Game": "Видеоигры",
            "104-Adult-Cast": "Взрослые персонажи",
            "105-Gore": "Жестокость",
            "106-Reincarnation": "Реинкарнация",
            "107-Love-Polygon": "Любовный многоугольник",
            "108-Visual-Arts": "Изобразительное искусство",
            "111-Time-Travel": "Путешествие во времени",
            "112-Gag-Humor": "Гэг-юмор",
            "114-Award-Winning": "Удостоено наград",
            "117-Suspense": "Триллер",
            "118-Combat-Sports": "Спортивные единоборства",
            "119-CGDCT": "CGDCT",
            "124-Mahou-Shoujo": "Махо-сёдзё",
            "125-Reverse-Harem": "Реверс-гарем",
            "130-Isekai": "Исэкай",
            "131-Delinquents": "Хулиганы",
            "134-Childcare": "Забота о детях",
            "135-Magical-Sex-Shift": "Магическая смена пола",
            "136-Showbiz": "Шоу-бизнес",
            "137-Otaku-Culture": "Культура отаку",
            "138-Organized-Crime": "Организованная преступность",
            "139-Workplace": "Работа",
            "140-Iyashikei": "Иясикэй",
            "141-Survival": "Выживание",
            "142-Performing-Arts": "Исполнительское искусство",
            "143-Anthropomorphic": "Антропоморфизм",
            "144-Crossdressing": "Кроссдрессинг",
            "145-Idols-(Female)": "Идолы (Жен.)",
            "146-High-Stakes-Game": "Игра с высокими ставками",
            "147-Medical": "Медицина",
            "148-Pets": "Питомцы",
            "149-Educational": "Образовательное",
            "150-Idols-(Male)": "Идолы (Муж.)",
            "151-Romantic-Subtext": "Романтический подтекст",
            "543-Gourmet": "Гурман"
            )
            (По умолчанию пусто - любой)
        :start_page: Начальная страница для поиска (По умолчанию 1)
        :page_limit: ограничение по количеству страниц для парсинга (По умолчанию 3)
        :sort_by: как сортировать выдачу (Доступно: rating (рейтинг), popularity (популярность), name (по алфавиту), aired_on (по дате выхода), ranked_random (случайно), id_desc (по id)) (По умолчанию: rating)

        Возвращает список словарей вида:
        [
            {
                'original_title': 'Оригинальное название (на английском)',
                'poster': 'Ссылка на картинку-постер',
                'shikimori_id': 'id шикимори',
                'title': 'Название на русском',
                'type': 'Тип аниме (TV Сериал, ONA, ...)',
                'url': 'Ссылка на страницу аниме',
                'year': 'год выхода аниме'
            },
            ...
        ]
        """
        if page_limit <= 0:
            return []

        status = [st for st in status if st in ['ongoing', 'anons', 'released', 'latest']] # Убираем все неизвестные варианты чтобы ничего не сломалось
        anime_type = [st for st in anime_type if st in ['tv', 'movie', 'ova', 'ona', 'special', 'tv_special', 'music', 'pv', 'cm']] # Убираем все неизвестные варианты чтобы ничего не сломалось
        if sort_by not in ['rating', 'popularity', 'name', 'aired_on', 'ranked_random', 'id_desc']:
            sort_by = 'rating' # По умолчанию сортировка по рейтингу
        genres = [st for st in genres if st in self.genres_list]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'https://{self._dmn}/animes/status/ongoing',
            'X-Requested-With': 'XMLHttpRequest',
        }

        search_url = f'https://{self._dmn}/animes'
        if len(anime_type) > 0:
            search_url += f'/kind/{",".join(anime_type)}'
        if len(status) > 0:
            search_url += f'/status/{",".join(status)}'
        if len(genres) > 0:
            search_url += f'/genre/{",".join(genres)}'
        if rating != None and rating not in ['g', 'pg' 'pg_13', 'r', 'r_plus']:
            rating = None # Проверяем что введены только доступные (для рейтинга rx требуется аккаунт или пользуйтесь функцией deep_search)

        res = []
        i = start_page
        total_pages = start_page+1 # (После первого запроса обновится)
        while i < start_page+page_limit and i <= total_pages:
            response = requests.get(f'{search_url}/page/{i}.json?order={sort_by}{f"&rating={rating}" if rating != None else ""}', headers=headers)
            if response.status_code == 429:
                raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
            elif response.status_code == 520:
                raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
            elif response.status_code != 200:
                raise errors.ServiceError('Произошла непредвиденная ошибка при получении данных об онгоингах. Ожидался статус ответа 200. Получен: ', response.status_code)
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise errors.UnexpectedBehavior('Ошибка парсинга json при получении данных об онгоингах')
            else:
                total_pages = data['pages_count']
                soup = Soup(data['content'], 'lxml') if self.USE_LXML else Soup(data['content'], 'html.parser')
                articles = soup.find_all('article')
                if len(articles) == 0 and i > 1:
                    return res # В случае если страница есть но данных на ней нет
                elif len(articles) == 0 and i == 1: # Если на первой странице нет данных
                    raise errors.NoResults('Данные по онгоингам не найдены')
                for art in articles:
                    res.append(self._get_anime_info_from_article(art))
            i += 1
        return res
    
    def _get_anime_info_from_article(self, article: Soup) -> dict:
        """
        Используется для получения данных из article
        """
        c_data = {}
        c_data['shikimori_id'] = article.get_attribute_list('id')[0]
        link = article.find('a')
        c_data['url'] = link.get_attribute_list('href')[0]
        try:
            pict = article.find('picture').find('img')
            c_data['poster'] = pict.get_attribute_list('srcset')[0][:-3]
        except:
            c_data['poster'] = None
        try:
            c_data['original_title'] = article.find('span', {'class': 'name-en'}).text
            c_data['title'] = article.find('span', {'class': 'name-ru'}).text
        except: # Если не найдено по отдельности, то скорее всего есть только один вариант
            try:
                c_data['original_title'] = article.find('span', {'class': 'title'}).text
                c_data['title'] = c_data['original_title']
            except:
                c_data['original_title'] = None
                c_data['title'] = None
        c_data['type'] = None
        c_data['year'] = None
        try:
            misc = article.find('span', {'class': 'misc'}).find_all('span')
            for m in misc:
                if m.text.isdigit():
                    c_data['year'] = m.text
                else:
                    c_data['type'] = m.text
        except:
            pass
        return c_data

    def link_by_id(self, shikimori_id: str) -> str:
        """
        Получить ссылку на страницу аниме по shikimori_id.

        :shikimori_id: id шикимори
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        }
        response = requests.get(f'https://{self._dmn}/animes/{shikimori_id}', headers=headers)
        if response.status_code == 404:
            soup = Soup(response.text, 'lxml') if self.USE_LXML else Soup(response.text, 'html.parser')
            actual_code = soup.find('p', {'class': 'error-404'}).text
            if actual_code == '404':
                raise errors.NoResults(f'Страница аниме с shikimori_id "{shikimori_id}" не найдена.')
            elif actual_code == '429':
                raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
            elif actual_code == '302':
                return soup.find('a').get_attribute_list('href')[0]
            else:
                raise errors.UnexpectedBehavior(f'Непредвиденная ошибка при попытке нахождения страницы по id ({shikimori_id}). Ожидались коды: "404", "429", "302", "200". Обнаружен: "{actual_code}"')
        elif response.status_code == 429:
            raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code == 520:
            raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
        elif response.status_code == 200 or response.status_code == 302:
            return response.url
        else:
            raise errors.UnexpectedBehavior(f'Непредвиденная ошибка при попытке нахождения страницы по id ({shikimori_id}). Ожидались коды: "404", "302", "200". Обнаружен: "{response.status_code}"')

    def id_by_link(self, shikimori_link: str) -> str:
        """
        Возвращает shikimori_id из ссылки на страницу аниме.

        :shikimori_link: Ссылка на страницу шикимори. (прим: https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi)
        """
        sid = shikimori_link[shikimori_link.rfind('/')+1:shikimori_link.find('-')]
        # Убираем все буквы в id, потому что это шикимори зачем-то их туда начал добавлять
        nsid = ''
        for x in sid:
            if x.isdigit():
                nsid += x
        return nsid
    
    def deep_search(self, title: str, search_parameters: dict = {}, return_parameters: list = ['id', 'name', 'russian', 'genres { id name russian kind}', 'status', 'url']) -> list:
        """
        Использует playground для graphql. Эмуляция api без необходимости использовать ключ и без ограничений на количество запросов (предположительно).
        ## ! Возможна блокировка ip, используйте на свой страх и риск !
        
        Вы можете прочитать пример запроса в файле: SHIKI_API.md

        :title: Название аниме
        :search_parameters: Параметры поиска. Конкретнее читайте в документации. 
            Пример параметров: {'limit': 10, 'kind': 'tv', 'status': 'released'}
        :return_parameters: Какие данные возвращать. Примеры параметров можно посмотреть тут: https://shikimori.one/api/doc/graphql.
            Пример параметров: ['id', 'name', 'russian', 'genres { id name russian kind }', 'status', 'url']
            Вы можете прочитать пример запроса в файле: SHIKI_API.md
        
        Возвращает список словарей.
        """
        query = "{\n"
        search_query = f'animes(search: \"{title}\"'
        for parameter, value in search_parameters.items():
            if type(value) == str:
                val = f'"{value}"'
            elif type(value) == bool:
                val = 'true' if value else 'false'
            else:
                val = value
            search_query += f', {parameter}: {val}'
        search_query += ")"
        query += search_query
        return_query = '{\n'
        for param in return_parameters:
            return_query += param + '\n'
        return_query += '}'
        query += return_query + '\n}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': '*/*',
            'Referer': f'https://{self._dmn}/api/doc/graphql',
            'content-type': 'application/json',
            'Origin': f'https://{self._dmn}',
        }

        json_data = {
            'operationName': None,
            'variables': {},
            'query': query
        }
        
        response = requests.post(f'https://{self._dmn}/api/graphql', headers=headers, json=json_data)
        if response.status_code == 429:
            raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code == 520:
            raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()
        if 'errors' in response.keys():
            raise errors.PostArgumentsError(f"Ошибка запроса. Ошибка: {response['errors'][0]['message']}")
        response = response['data']
        if 'animes' in response.keys():
            return response['animes']
        else:
            return []
        
    def deep_anime_info(self, shikimori_id: str, return_parameters: list = ['id', 'name', 'russian', 'genres { id name russian kind}', 'status', 'url']) -> dict:
        """
        Использует playground для graphql. Эмуляция api без необходимости использовать ключ и без ограничений на количество запросов (предположительно).
        ## ! Возможна блокировка ip, используйте на свой страх и риск !

        Вы можете прочитать пример запроса в файле: SHIKI_API.md

        :shikimori_id: id шикимори
        :return_parameters: Какие данные возвращать. Примеры параметров можно посмотреть тут: https://shikimori.one/api/doc/graphql.
            Пример параметров: ['id', 'name', 'russian', 'genres { id name russian kind }', 'status', 'url']
            Вы можете прочитать пример запроса в файле: SHIKI_API.md
        
        Возвращает словарь.
        """
        query = "{\n"
        search_query = f'animes(ids: \"{shikimori_id}\")'
        query += search_query
        return_query = '{\n'
        for param in return_parameters:
            return_query += param + '\n'
        return_query += '}'
        query += return_query + '\n}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': '*/*',
            'Referer': f'https://{self._dmn}/api/doc/graphql',
            'content-type': 'application/json',
            'Origin': f'https://{self._dmn}',
        }

        json_data = {
            'operationName': None,
            'variables': {},
            'query': query
        }
        
        response = requests.post(f'https://{self._dmn}/api/graphql', headers=headers, json=json_data)
        if response.status_code == 429:
            raise errors.TooManyRequests(f'Сервер вернул код 429 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code == 520:
            raise errors.ServiceIsOverloaded("Сервер вернул статус ответа 520, что означает что он перегружен и не может ответить сразу.")
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()
        if 'errors' in response.keys():
            raise errors.PostArgumentsError(f"Ошибка запроса. Ошибка: {response['errors'][0]['message']}")
        response = response['data']
        if 'animes' in response.keys():
            if len(response['animes']) > 0:
                return response['animes'][0]
            else:
                raise errors.NoResults(f'Нет данных по shikimori_id "{shikimori_id}"')
        else:
            return {}

"""
Пример запроса для deep_search:

{
  # look for more query params in the documentation
  animes(
    
    // параметры запроса
    // параметр: тип значения - описание параметра
    search: str, - Название аниме
    limit: int, - Максимальное количество выдач (макс: 50)
    rating: str, - Возрастной рейтинг
        // "g" – G - Все возрасты
        // "pg" – PG - Дети
        // "pg_13" – PG-13 - Подростки от 13 лет
        // "r" – R - рекомендовано 17+ (насилие и ненормативная лексика)
        // "r_plus" – R+ - Умеренная нагота (также может содержать насилие и ненормативную лексику)
        // "rx" – Rx - Hentai (экстремальный сексуальный контент или нагота)
    page: int - номер страницы (значение между 1 и 100000)
    order: str - сортировать
        // "id" – по id
        // "ranked" – по рейтингу
        // "kind" – по типу (TV serial, OVA, ...)
        // "popularity" – по популярности
        // "name" – по алфавиту (названия)
        // "aired_on" – по дате выхода
        // "episodes" – по количеству эпизодов
        // "status" – по статусу выхода (вышел, анонс, онгоинг)
        // "random" – перемешать
    kind: str - тип аниме (Одно из: tv, movie, ova, ona, special, tv_special, music, pv, cm, tv_13, tv_24, tv_48)
    status: str - статус выхода (Одно из: anons, ongoing, released)
    season: str - сезон аниме (Примеры: summer_2017, 2016, 2014_2016, 199x)
    score: int - минимальный рейтинг
    duration: str - продолжительность ("S" - меньше 5 минут, "D" - меньше 30 минут, "F" - больше 30 минут)
    genre: str - жанры (указываются id жанров через запятую)
    genre_v2: str - жанры v2 (указываются id v2 жанров через запятую)
    studio: str - студии (указываются id студий через запятую)
    franchize: str - франшизы (указываются id франшиз через запятую)
    censored: boolean - скрывать 18+ (false - чтобы разрешить поиск hentai, yaoi, yuri)
    ids: str - id аниме (указываются через запятую)
    exclude_ids: str - id аниме которые не будут включены в поиск (указываются через запятую)
    ) {
    
    // Возвращаемые параметры
    // параметр - описание возвращенных данных (тип данных)
    //
    id - id шикимори (str)
    malId - id myanimelist (str)
    name - японское название транслитом на английском (str)
    russian - русское название (str)
    licenseNameRu - название русской лицензии (str)
    english - английское название (str)
    japanese - японское название (str) 
    synonyms - список других названий (list[str])
    kind - тип аниме ('tv', 'ova' и т.д.) (str)
    rating - возрастной рейтинг (str)
    score - оценка на шикимори (float)
    status - статус ('released', 'ongoing', 'anons') (str)
    episodes - количество эпизодов (int)
    episodesAired - количество анонсированных эпизодов (int)
    duration - продолжительность серии в минутах (int)
    airedOn { year month day date } - дата анонса (dict) {"year": год (int), "month": месяц (int), "day": день (int), "date": дата в формате "YYYY-MM-DD" (str)}
    releasedOn { year month day date } - дата релиза (dict) {"year": год (int), "month": месяц (int), "day": день (int), "date": дата в формате "YYYY-MM-DD" (str)}
    url - ссылка на страницу на шикимори (str)
    season - сезон аниме (str) (пример: "winter_2023")

    poster { id originalUrl mainUrl } - постер (dict) {"id": id постера (str), "originalUrl": ссылка на jpg картинку (str), 'mainUrl': ссылка на webp картинку (str)}

    fansubbers - субтитры (list[str])
    fandubbers - озвучка (list[str])
    licensors - лицензиаторы? (list)
    createdAt, - дата создания (str)
    updatedAt, - дата обновления (str)
    nextEpisodeAt, - дата выхода следующего эпизода (str или null)
    isCensored - зацензурено ли (boolean)

    genres { id name russian kind } - жанры (list[dict]) {"id": id жанра (str), "name": английское название жанра (str), "russian": русское название жанра (str), "kind": жанр или тема ("genre" или "theme")}
    studios { id name imageUrl } - студии анимации (list[dict]) {"id": id студии (str), "name": название студии (str), "imageUrl": ссылка на картинку студии (str)}

    externalLinks { - внешние ссылки (list[dict])
      id - id ссылки (str)
      kind - тип ссылки (str) Примеры: ("official_site", "wikipedia", "anime_news_network", "myanimelist", "anime_db", "world_art", "kinopoisk", "twitter")
      url - ссылка (str)
      createdAt - дата создания (str)
      updatedAt - дата обновления (str)
    }

    personRoles { - роли-люди (продюсеры, аниматоры, звуковики и т.п.) (list[dict])
      id - id чего-то (str)
      rolesRu - список ролей на русском (list[str])
      rolesEn - список ролей на английском (list[str])
      person { - информация о человеке (dict)
        id - id человека (str)
        name - имя человека (str)
        poster { - данные о фотографии (dict или null)
            id - id фотографии (str)
            mainUrl - ссылка на фотографию webp (str)
            mainAltUrl - ссылка на фотографию jpeg (str)
        } 
      }
    }
    characterRoles { - персонаж-роль (list[dict])
      id - id персонажа (str)
      rolesRu - роли на русском (list[str])
      rolesEn - роли на английском (list[str])
      character { - данные о персонаже (dict)
        id - id персонажа (str)
        name - имя персонажа на английском (str)
        russian - имя персонажа на русском (str)
        poster { - картинка (dict)
            id  - id картинки (str)
            mainUrl - ссылка на webp (str)
            mainAltUrl - ссылка на jpeg (str)
        } 
      }
    }

    related { - связанные (list[dict])
      id - id чего-то (str)
      anime { - связь с аниме (если есть, иначе None) (dict)
        id - id аниме (str)
        name - транслит японского названия на английском (str)
        russian - название на русском (str)
        english - название на английском (str)
        url - ссылка на страницу (str)
      }
      manga { - связь с мангой (если есть, иначе None) (dict)
        id - id манги (str)
        name - транслит японского названия на английском (str)
        russian - название на русском (str)
        english - название на английском (str)
        url - ссылка на страницу (str)
      } // Скорее всего есть и ранобэ
      relationKind - тип связи (str) ("adaptation" - адаптация, "sequel" - продолжение и так далее)
      relationText - тип связи на русском (str)
    }

    videos { - связанные видео (предпросмотры серий) (list[dict])
        id - id чего-то (str)
        url - ссылка на видео (чаще всего ютуб) (str)
        name - имя видео? (str)
        kind - тип видео (episode_preview - трейлер эпизода и т.п.) (str)
        playerUrl - ссылка на плеер (embed ютуба) (str)
        imageUrl - ссылка на обложку видео (тоже ютуб) (str)
    }
    screenshots { - скриншоты (list[dict]) 
        id - id скриншота (str)
        originalUrl - ссылка на оригинальную картинку (str)
        x166Url - ссылка на очень маленькую картинку (str)
        x332Url - ссылка на маленькую картинку (str)
    }

    scoresStats { - статистика оценок (list[dict])
        score - оценка (int)
        count - количество людей поставивших эту оценку (int)
    }
    statusesStats { - статистика статусов просмотра (заброшено, просмотрено, запланировано и т.п.) (list[dict])
        status - статус на английском (str)
        count - количество людей с данным статусом аниме (int)
    }

    description - описание аниме (просто текст) (str)
    descriptionHtml - описание аниме с гиперссылками и html версткой (ыек)
    descriptionSource - откуда взяли описание (если есть, иначе None)
  }
}
"""