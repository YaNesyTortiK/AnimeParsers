import requests
try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True
import re
from bs4 import BeautifulSoup as Soup

import anime_parsers_ru.errors as errors

class ShikimoriParser:
    """
    Парсер шикимори. Не использует встроенный в шикимори api.
    """
    def __init__(self, use_lxml: bool = True) -> None:
        """
        :use_lxml: использовать lxml парсер (в некоторых случаях lxml может не работать)
        """
        if not LXML_WORKS and use_lxml:
            raise ImportWarning('Параметр use_lxml установлен в true, однако при попытке импорта lxml произошла ошибка')
        self.USE_LXML = use_lxml

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
                "poster": "Ссылка на постер к аниме (плохое качество) если есть, иначе None",
                "shikimori_id": "id шикимори",
                "status": "статус (вышло, онгоинг, анонс)",
                "studio": "студия анимации (если есть, иначе None)",
                "title": "Название",
                "type": "тип аниме (TV сериал, OVA, ONA, ...)",
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
        response = requests.get('https://shikimori.one/animes/autocomplete/v2', params=params, headers=headers)
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()['content']
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response)
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
            "episodes": "Количество эпиходов если статус 'вышло' или 'вышедших эпизодов / анонсировано эпизодов' или None (если фильм)",
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
        if response.status_code == 520:
            raise errors.TooManyRequests(f'Сервер вернул код 520 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response)
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
                if res['status'] == 'онгоинг' or res['type'] == 'Фильм':
                    res['dates'] = value.text.strip()
                elif len(value.find_all('span')) > 1:
                    res['dates'] = value.find_all('span')[-1].text
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
        if response.status_code == 520:
            raise errors.TooManyRequests(f'Сервер вернул код 520 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response)
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
                    c_data['name'] = entry.find('div', {'class': 'name'}).find('span', {'class': 'name-ru'}).text
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

        r1 = soup.find('div', {'class': 'c-characters'})
        for char in r1.find_all('article'):
            c_data = {}
            c_data['picture'] = None
            if not char.find('meta', {'itemprop': 'image'}) is None:
                c_data['picture'] = char.find('meta', {'itemprop': 'image'}).get_attribute_list('content')[0]
            c_data['name'] = char.find('span', {'class': 'name-ru'}).text
            res['main_characters'].append(c_data)
        
        r1 = soup.find('div', {'class': 'two-videos'})
        if not r1 is None:
            if not r1.find('div', {'class': 'c-screenshots'}) is None:
                for img in r1.find_all('a', {'class': 'c-screenshot'}):
                    res['screenshots'].append(img.get_attribute_list('href')[0])
            if not r1.find('div', {'class': 'c-videos'}) is None:
                for vid in r1.find_all('div', {'class': 'c-video'}):
                    c_data = {}
                    c_data['link'] = vid.find('a').get_attribute_list('href')[0]
                    c_data['name'] = vid.find('span', {'class': 'name'}).text
                    res['videos'].append(c_data)

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
        return res

    def link_by_id(self, shikimori_id: str) -> str:
        """
        Получить ссылку на страницу аниме по shikimori_id.

        :shikimori_id: id шикимори
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        }
        response = requests.get(f'https://shikimori.one/animes/{shikimori_id}', headers=headers)
        if response.status_code == 404:
            soup = Soup(response.text, 'lxml') if self.USE_LXML else Soup(response.text)
            actual_code = soup.find('p', {'class': 'error-404'}).text
            if actual_code == '404':
                raise errors.NoResults(f'Страница аниме с shikimori_id "{shikimori_id}" не найдена.')
            elif actual_code == '302':
                return soup.find('a').get_attribute_list('href')[0]
            else:
                raise errors.UnexpectedBehaviour(f'Непредвиденная ошибка при попытке нахождения страницы по id ({shikimori_id}). Ожидались коды: "404", "302", "200". Обнаружен: "{actual_code}"')
        elif response.status_code == 200 or response.status_code == 302:
            return response.url
        elif response.status_code == 520:
            raise errors.TooManyRequests(f'Сервер вернул код 520 для обозначения что запросы выполняются слишком часто.')
        else:
            raise errors.UnexpectedBehaviour(f'Непредвиденная ошибка при попытке нахождения страницы по id ({shikimori_id}). Ожидались коды: "404", "302", "200". Обнаружен: "{response.status_code}"')

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
        :return_parameters: Какие данные возвращать. Примеры параметров можно постореть тут: https://shikimori.one/api/doc/graphql.
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
            'Referer': 'https://shikimori.one/api/doc/graphql',
            'content-type': 'application/json',
            'Origin': 'https://shikimori.one',
        }

        json_data = {
            'operationName': None,
            'variables': {},
            'query': query
        }
        
        response = requests.post('https://shikimori.one/api/graphql', headers=headers, json=json_data)
        if response.status_code == 520:
            raise errors.TooManyRequests(f'Сервер вернул код 520 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()
        if 'errors' in response.keys():
            raise errors.PostArgumentsError(f'Ошибка запроса. Ошибка: {response['errors'][0]['message']}')
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
        :return_parameters: Какие данные возвращать. Примеры параметров можно постореть тут: https://shikimori.one/api/doc/graphql.
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
            'Referer': 'https://shikimori.one/api/doc/graphql',
            'content-type': 'application/json',
            'Origin': 'https://shikimori.one',
        }

        json_data = {
            'operationName': None,
            'variables': {},
            'query': query
        }
        
        response = requests.post('https://shikimori.one/api/graphql', headers=headers, json=json_data)
        if response.status_code == 520:
            raise errors.TooManyRequests(f'Сервер вернул код 520 для обозначения что запросы выполняются слишком часто.')
        elif response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()
        if 'errors' in response.keys():
            raise errors.PostArgumentsError(f'Ошибка запроса. Ошибка: {response['errors'][0]['message']}')
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

    personRoles { - роли-люди (продюссеры, аниматоры, звуковики и т.п.) (list[dict])
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