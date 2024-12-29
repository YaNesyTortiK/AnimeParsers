import requests
try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True
from bs4 import BeautifulSoup as Soup

try:
    from . import errors # Импорт если библиотека установлена
except ImportError:
    import errors # Импорт если библиотека не установлена и файл лежит локально

class JutsuParser:
    """
    Парсер jut.su
    """
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
            self._dmn = "jut.su"
    
    def get_mp4_link(self, link: str) -> dict:
        """
        Получает ссылку на mp4 файл по ссылке на страницу.

        :link: ссылка на страницу c плеером (прим: https://jut.su/tondemo-skill/episode-1.html)
        
        Возвращает словарь в виде:
        {
            'качество': 'ссылка'
        }
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
        }
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response, 'html.parser')
        if soup.find('video', {'id': 'my-player'}) is None:
            raise errors.UnexpectedBehavior(f'Ожидался тег "video" на странице по ссылке "{link}"')
        sources = soup.find('video', {'id': 'my-player'}).find_all('source')
        links = {}
        for src in sources:
            q = src.get_attribute_list('res')[0]
            link = src.get_attribute_list('src')[0]
            links[q] = link
        return links
    
    def get_anime_info(self, link: str) -> dict:
        """
        Получает данные аниме по ссылке.

        :link: ссылка на страницу аниме (прим: https://jut.su/tondemo-skill/)

        Возвращает словарь вида:
        {
            "title": "Название аниме",
            "origin_title": "Оригинальное название (транслит японского названия на английском)",
            "age_rating": "Возрастное ограничение",
            "description": "Описание",
            "years": ["Год выхода 1 сезона", "Год выхода 2 сезона"],
            "genres": ["Жанр 1", "Жанр 2"],
            "poster": "Ссылка на картинку (плохое качество)",
            "seasons": [
                [ # 1 сезон будет обязательно, даже если у аниме нет других сезонов
                    "ссылка на 1 серию 1 сезона (страница с плеером)",
                    "ссылка на 2 серию 1 сезона (страница с плеером)"
                ],
                [ # 2 сезон если есть
                    "ссылка на 1 серию 2 сезона (страница с плеером)",
                    "ссылка на 2 серию 2 сезона (страница с плеером)"
                ],
                ...
            ],
            "seasons_names": [ # Если у аниме только 1 сезон, этот список будет пустым
                "Название 1 сезона", 
                "Название 2 сезона"
            ],
            "films": [ # Если фильмов нет - список пустой
                "Ссылка на фильм 1 (страница с плеером)",
                "Ссылка на фильм 2 (страница с плеером)",
            ]
        }
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
        }
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response, 'html.parser')
        soup = soup.find('div', {'id': 'dle-content'})

        if soup.find('a', {'class': 'video'}) is None:
            raise errors.UnexpectedBehavior(f'Предполагалось, что на странице "{link}" будет находится информация об аниме и ссылки на серии, однако они были не найдены. Проверьте ссылку вручную.')

        c_data = {}
        c_data['title'] = soup.find('h1', {'class': 'header_video'}).text.replace('Смотреть ', '', 1).replace(' все серии и сезоны', '', 1).replace(' все серии', '', 1)
        
        poster = soup.find('div', {'class': 'all_anime_title'})
        if poster is None:
            c_data['poster'] = None
        else:
            poster = poster.get_attribute_list('style')[0]
            c_data['poster'] = poster[poster.find("'")+1:poster.rfind("'")]

        additional_data = soup.find('div', {'class': 'under_video_additional'})
        c_data['genres'] = []
        c_data['years'] = [] # Потому что может быть указано сразу несколько годов (для разных сезонов)
        for a in additional_data.find_all('a'):
            href = a.get_attribute_list('href')[0]
            content = a.get_text()
            content = content[content.find(' ')+1:]
            if href[href.rfind('/', 0, -2)+1:-1].isdigit() or \
                all(x.isdigit() for x in href[href.rfind('/', 0, -2)+1:-1].split('-')):
                c_data['years'].append(content)
            else:
                c_data['genres'].append(content)

        c_data['original_title'] = additional_data.find('b').text
        c_data['age_rating'] = additional_data.find('span', {'class': 'age_rating_all'}).text
        
        desc = soup.find('p')
        for i in desc.find_all('i'):
            i.decompose() # Чистим текст от всякого мусора
        c_data['description'] = desc.text.strip()

        c_data['seasons'] = []
        c_data['films'] = []
        # А тут начинается веселье с эпизодами и сезонами, потому что на jutsu оно в коде никак не выделяется отдельно. Поэтому следите за руками
        for episode in soup.find_all('a', {'class': 'video'}):
            href = episode.get_attribute_list('href')[0]
            if 'season' in href:
                season_num = int(href[href.find('season')+7:href.rfind('/')])
                if len(c_data['seasons']) < season_num:
                    c_data['seasons'].append([])
                c_data['seasons'][season_num-1].append(f'https://{self._dmn}/'+href)
            elif 'film' in href:
                c_data['films'].append(f'https://{self._dmn}/'+href)
            else:
                if len(c_data['seasons']) == 0:
                    c_data['seasons'].append([])
                c_data['seasons'][-1].append(f'https://{self._dmn}/'+href)

        # Если сезонов как минимум 2, то скорее всего у них есть название (либо ремейки, они тоже как отдельный сезон идут)
        c_data['seasons_names'] = []
        if len(c_data['seasons']) > 1:
            for season_name in soup.find_all('h2', {'class': 'the-anime-season'}):
                c_data['seasons_names'].append(season_name.text.strip())

        return c_data
    
    """
    Поиска нет, потому что jut.su использует яндекс поиск для поиска по своему сайту.
    И это поиск настолько непредсказуем, что проще не трогать.
    В качестве поиска вы можете использовать оригинальное название для ссылки.
    Типо так:
    
    Название аниме: Волчица и пряности
    Оригинальное название: Ookami to Koushinryou
    Ссылка на страницу: https://jut.su/ookami-to-koshinryou/

    Ну суть понятна.
    Правда есть и исключения по типу наруто, которое в принципе не подчиняется правилам других аниме.
    """