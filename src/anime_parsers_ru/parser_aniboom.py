import requests
try:
    import lxml
except ImportError:
    LXML_WORKS = False
else:
    LXML_WORKS = True
from bs4 import BeautifulSoup as Soup
import re
import json

try:
    from . import errors # Импорт если библиотека установлена
except ImportError:
    import errors # Импорт если библиотека не установлена и файл лежит локально

class AniboomParser:
    """
    Парсер для плеера AniBoom
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
            self._dmn = "animego.me"

    def fast_search(self, title: str) -> list[dict]:
        """
        Быстрый поиск через animego.me
        
        :title: Название аниме

        Возвращает список словарей в виде:
        [
            {
                'title': Название аниме
                'year': Год выпуска
                'other_title': Другое название (оригинальное название)
                'type': Тип аниме (ТВ сериал, фильм, ...)
                'link': Ссылка на страницу с информацией
                'animego_id': id на анимего (по сути в ссылке на страницу с информацией последняя цифра и есть id)
            },
            ...
        ]
        """
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://{self._dmn}/'
        }
        params = {
            'type': 'small',
            'q': title,
        }
        response = requests.get(f'https://{self._dmn}/search/all', params=params, headers=headers).json()
        if response['status'] != 'success':
            raise errors.ServiceError(f'На запрос "{title}" сервер не вернул ожидаемый ответ "status: success". Status: "{response["status"]}"')

        soup = Soup(response['content'], 'lxml') if self.USE_LXML else Soup(response['content'], 'html.parser')
        res = []
        for elem in soup.find('div', {'class': 'result-search-anime'}).find_all('div', {'class': 'result-search-item'}):
            c_data = {}
            c_data['title'] = elem.find('h5').text.strip()
            c_data['year'] = elem.find('span', {'class': 'anime-year'}).text.strip()
            o_t_c = elem.find('div', {'class': 'text-truncate'})
            c_data['other_title'] = o_t_c.text.strip() if not o_t_c is None else ''
            c_data['type'] = elem.find('a', {'href': re.compile(r'.*anime/type.*')}).text.strip()
            c_data['link'] = f'https://{self._dmn}'+elem.find('h5').find('a').get_attribute_list('href')[0]
            c_data['animego_id'] = c_data['link'][c_data['link'].rfind('-')+1:]
            res.append(c_data)
        return res
    
    def search(self, title: str) -> list[dict]:
        """
        Расширенный поиск через animego.me. Собирает дополнительные данные об аниме.

        :title: Название

        Возвращает список из словарей:
        [
            {
                'title': Название
                'other_titles': [Альтернативное название 1, ...]
                'status': Статус аниме (онгоинг, анонс, вышел, ...)
                'type': Тип аниме (ТВ сериал, фильм, ...)
                'genres': [Список жанров]
                'description': описание
                'episodes': если аниме вышло, то количество серий, если еще идет, то "вышло / всего"
                'episodes_info': [
                    {
                        'num': Номер эпизода
                        'title': Название эпизода
                        'date': Даты выхода (предполагаемые если анонс)
                        'status': 'вышло' или 'анонс' (Имеется в виду вышло в оригинале, не переведено)
                    },
                    ...
                ],
                'translations': [
                    {
                        'name': Название студии,
                        'translation_id': id перевода в плеере aniboom
                    },
                    ...
                ],
                'poster_url': Ссылка на постер аниме
                'trailer': Ссылка на ютуб embed трейлер
                'screenshots': [Список ссылок на скриншоты]
                'other_info': {
                    Данная информация может меняться в зависимости от типа или состояния тайтла
                    'Возрастные ограничения': (прим: 16+)
                    'Выпуск': (прим: с 2 апреля 2024)
                    'Главные герои': [Список главных героев]
                    'Длительность': (прим: 23 мин. ~ серия)
                    'Первоисточник': (прим: Легкая новела)
                    'Рейтинг MPAA': (прим: PG-13),
                    'Сезон': (прим. Весна 2024),
                    'Снят по ранобэ': название ранобэ (Или так же может быть 'Снят по манге')
                    'Студия': название студии
                }
                'link': Ссылка на страницу с информацией
                'animego_id': id на анимего (по сути в ссылке на страницу с информацией последняя цифра и есть id)
            },
            ...
        ]
        """
        elements = self.fast_search(title)
        res = []
        for anime in elements:
            c_data = self.anime_info(anime['link'])
            res.append(c_data)
        return res
    
    def episodes_info(self, link: str):
        """
        Возвращает данные по эпизодам.

        :link: ссылка на страницу с данными (прим: https://animego.me/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546)

        Возвращает отсортированный по номеру серии список словарей в виде:
        [
            {
                'num': Номер эпизода
                'title': Название эпизода
                'date': Даты выхода (предполагаемые если анонс)
                'status': 'вышло' или 'анонс' (Имеется в виду вышло в оригинале, не переведено)
            },
            ...
        ]
        """
        headers = {
            'Referer': f'https://{self._dmn}/search/all?q=anime',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = {
            'type': 'episodeSchedule',
            'episodeNumber': '99999'
        }
        response = requests.get(link, headers=headers, params=params).json()
        if response['status'] != 'success':
            raise errors.NoResults(f'По запросу данных эпизодов id "{id}" ничего не найдено')
        soup = Soup(response['content'], 'lxml') if self.USE_LXML else Soup(response['content'], 'html.parser')
        episodes_list = []
        for ep in soup.find_all('div', {'class': ['row', 'm-0']}):
            items = ep.find_all('div')
            num = items[0].find('meta').get_attribute_list('content')[0]
            ep_title = items[1].text.strip() if items[1].text else ''
            ep_date = items[2].find('span').get_attribute_list('data-label')[0] if items[2].find('span') else ''
            ep_status = 'анонс' if items[3].find('span') is None else 'вышел'
            episodes_list.append({'num': num, 'title': ep_title, 'date': ep_date, 'status': ep_status})
        
        return sorted(episodes_list, key=lambda x: int(x['num']) if x['num'].isdigit() else x['num'])

    def anime_info(self, link: str) -> dict:
        """
        Получение данных об аниме с его страницы на animego.me.

        :link: Ссылка на страницу (прим: https://animego.me/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546)

        Возвращает словарь следующего вида:
        {
            'title': Название
            'other_titles': [Альтернативное название 1, ...]
            'status': Статус аниме (онгоинг, анонс, вышел, ...)
            'type': Тип аниме (ТВ сериал, фильм, ...)
            'genres': [Список жанров]
            'description': описание
            'episodes': если аниме вышло, то количество серий, если ще идет, то "вышло / всего"
            'episodes_info': [
                {
                    'num': Номер эпизода
                    'title': Название эпизода
                    'date': Даты выхода (предполагаемые если анонс)
                    'status': 'вышло' или 'анонс' (Имеется в виду вышло в оригинале, не переведено)
                },
                ...
            ],
            'translations': [
                {
                    'name': Название студии,
                    'translation_id': id перевода в плеере aniboom
                }  
            ],
            'poster_url': Ссылка на постер аниме
            'trailer': Ссылка на ютуб embed трейлер
            'screenshots': [Список ссылок на скриншоты]
            'other_info': {
                Данная информация может меняться в зависимости от типа или состояния тайтла
                'Возрастные ограничения': (прим: 16+)
                'Выпуск': (прим: с 2 апреля 2024)
                'Главные герои': [Список главных героев]
                'Длительность': (прим: 23 мин. ~ серия)
                'Первоисточник': (прим: Легкая новела)
                'Рейтинг MPAA': (прим: PG-13),
                'Сезон': (прим. Весна 2024),
                'Снят по ранобэ': название ранобэ (Или так же может быть 'Снят по манге')
                'Студия': название студии
            },
            'link': Ссылка на страницу с информацией
            'animego_id': id на анимего (по сути в ссылке на страницу с информацией последняя цифра и есть id)
        }
        """
        c_data = {}
        response = requests.get(link, headers={'Referer': f'https://{self._dmn}/search/all?q=anime'})
        if response.status_code == 429:
            raise errors.TooManyRequests('Сервер вернул код ошибки 429. Слишком частые запросы')
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.text
        soup = Soup(response, 'lxml') if self.USE_LXML else Soup(response, 'html.parser')
        c_data['link'] = link
        c_data['animego_id'] = link[link.rfind('-')+1:]
        c_data['title'] = soup.find('div', {'class': 'anime-title'}).find('h1').text.strip()
        c_data['other_titles'] = []
        for syn in soup.find('div', {'class': 'anime-synonyms'}).find_all('li'):
            c_data['other_titles'].append(syn.text.strip())
        c_data['poster_url'] = soup.find('img').get_attribute_list('src')[0]
        c_data['poster_url'] = f'https://{self._dmn}'+c_data['poster_url'][c_data['poster_url'].find('/upload'):]
        anime_info = soup.find('div', {'class': 'anime-info'}).find('dl')
        keys = anime_info.find_all('dt')
        values = anime_info.find_all('dd')
        c_data['other_info'] = {}
        for i in range(len(keys)):
            if values[i].get_attribute_list('class') == ['mt-2','col-12'] or not values[i].find('hr') is None:
                # Просто пустая строка которая может сбить порядок
                del values[i]
            if keys[i].text.strip() == 'Озвучка':
                continue
            elif keys[i].text.strip() == 'Жанр':
                c_data['genres'] = []
                for tt in values[i].find_all('a'):
                    c_data['genres'].append(tt.text)
            elif keys[i].text.strip() == 'Главные герои':
                c_data['other_info']['Главные герои'] = []
                for tt in values[i].find_all('a'):
                    c_data['other_info']['Главные герои'].append(tt.text)
            elif keys[i].text.strip() == 'Эпизоды':
                c_data['episodes'] = values[i].text
            elif keys[i].text.strip() == 'Статус':
                c_data['status'] = values[i].text
            elif keys[i].text.strip() == 'Тип':
                c_data['type'] = values[i].text
            else:
                c_data['other_info'][keys[i].text.strip()] = values[i].text.strip()

        c_data['description'] = soup.find('div', {'class': 'description'}).text.strip()
        c_data['screenshots'] = []
        for screenshot in soup.find_all('a', {'class': 'screenshots-item'}):
            c_data['screenshots'].append(f'https://{self._dmn}'+screenshot.get_attribute_list('href')[0])
        trailer_cont = soup.find('div', {'class': 'video-block'})
        if not trailer_cont is None:
            c_data['trailer'] = trailer_cont.find('a', {'class': 'video-item'}).get_attribute_list('href')[0]
        else:
            c_data['trailer'] = None
        c_data['episodes_info'] = self.episodes_info(link)
        try:
            c_data['translations'] = self.get_translations_info(c_data['animego_id'])
        except errors.ContentBlocked:
            c_data['translations'] = []
        return c_data
    
    def get_translations_info(self, animego_id: str) -> list:
        """
        Получает информацию о переводах и их id для плеера aniboom

        :animego_id: id аниме на animego.me

        Возвращает список словарей:
        [
            {
                'name': Название студии озвучки,
                'translation_id': id перевода в плеере aniboom
            }
        ]
        """
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://{self._dmn}/search/all?q=anime',
        }
        params = {
            '_allow': 'true',
        }
        response = requests.get(f'https://{self._dmn}/anime/{animego_id}/player', params=params, headers=headers)
        if response.status_code == 429:
            raise errors.TooManyRequests('Сервер вернул код ошибки 429. Слишком частые запросы')
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()
        soup = Soup(response['content'], 'lxml') if self.USE_LXML else Soup(response['content'], 'html.parser')
        if soup.find('div', {'class': 'player-blocked'}):
            reason_elem = soup.find('div', {'class': 'h5'})
            reason = reason_elem.text if reason_elem else None
            raise errors.ContentBlocked(f'Контент по id {animego_id} заблокирован. Причина блокировки: "{reason}"')
        translations_container = soup.find('div', {'id': 'video-dubbing'}).find_all('span', {'class': 'video-player-toggle-item'})
        players_container = soup.find('div', {'id': 'video-players'}).find_all('span', {'class': 'video-player-toggle-item'})
        translations = {
            # data-dubbing: {'name': str, 'translation_id': str}
        }
        for translation in translations_container:
            dubbing = translation.get_attribute_list('data-dubbing')[0]
            name = translation.text.strip()
            translations[dubbing] = {'name': name}
        
        for player in players_container:
            if player.get_attribute_list('data-provider')[0] == '24': # Нам нужен только aniboom
                dubbing = player.get_attribute_list('data-provide-dubbing')[0]
                translation_id = player.get_attribute_list('data-player')[0]
                translation_id = translation_id[translation_id.rfind('=')+1:]
                translations[dubbing]['translation_id'] = translation_id
        
        res = []
        for translation in translations.values():
            if len(translation.keys()) == 2: # Проверяем чтобы для озвучки был плеер
                res.append(translation)
        return res

    
    def _get_embed_link(self, animego_id: str) -> str:
        """
        Возвращает ссылку на embed от aniboom. Сама по себе ссылка не может быть использована, однако требуется для дальнейшего парсинга.

        :animego_id: id аниме на animego.me

        Возвращает ссылку в виде: https://aniboom.one/embed/yxVdenrqNar
        Если ссылка не найдена, выкидывает NoResults exception
        """
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = {
            '_allow': 'true',
        }
        response = requests.get(f'https://{self._dmn}/anime/{animego_id}/player', params=params, headers=headers)
        if response.status_code == 429:
            raise errors.TooManyRequests('Сервер вернул код ошибки 429. Слишком частые запросы')
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        response = response.json()
        if response['status'] != 'success':
            raise errors.UnexpectedBehavior(f'Сервер не вернул ожидаемый статус "success". Статус: "{response["status"]}"')
        soup = Soup(response['content'], 'lxml') if self.USE_LXML else Soup(response['content'], 'html.parser')
        if soup.find('div', {'class': 'player-blocked'}):
            reason_elem = soup.find('div', {'class': 'h5'})
            reason = reason_elem.text if reason_elem else None
            raise errors.ContentBlocked(f'Контент по id {animego_id} заблокирован. Причина блокировки: "{reason}"')
        link = soup.find('div', {'id': 'video-players'})
        try:
            link = link.find('span', {'class': 'video-player-toggle-item', 'data-provider': '24'}).get_attribute_list('data-player')[0]
        except AttributeError:
            raise errors.NoResults(f'Для указанного id "{animego_id}" не удалось найти aniboom embed_link')
        return 'https:'+link[:link.rfind('?')]

    def _get_embed(self, embed_link: str, episode: int, translation: str) -> str:
        """
        Возвращает html от embed(iframe) плеера aniboom

        :embed_link: ссылка на embed (можно получить из _get_embed_link)
        :episode: Номер эпизода (вышедшего) (Если фильм - 0)
        :translation: id перевода (который именно для aniboom плеера) (можно получить из get_translations_info)
        """
        headers = {
            'Referer': f'https://{self._dmn}/',
        }
        if episode != 0:
            params = {
                'episode': episode,
                'translation': translation,
            }
        else:
            params = {
                'translation': translation,
            }
        response = requests.get(embed_link, headers=headers, params=params)
        if response.status_code == 429:
            raise errors.TooManyRequests('Сервер вернул код ошибки 429. Слишком частые запросы')
        if response.status_code != 200:
            raise errors.ServiceError(f'Сервер не вернул ожидаемый код 200. Код: "{response.status_code}"')
        return response.text
    
    def _get_media_src(self, embed_link: str, episode: int, translation: str) -> str:
        """
        Возвращает ссылку на mpd файл. Скачивать файл нужно обязательно с header'ами что отправлен запрос от animego.me или aniboom.one (иначе 403 ошибка)

        :embed_link: ссылка на embed (можно получить из _get_embed_link)
        :episode: Номер эпизода (вышедшего) (Если фильм - 0)
        :translation: id перевода (который именно для aniboom плеера) (можно получить из get_translations_info)

        Пример возвращаемого: https://sophia.yagami-light.com/7p/7P9qkv26dQ8/v26utto64xx66.mpd
        """
        embed = self._get_embed(embed_link, episode, translation)
        soup = Soup(embed, 'lxml') if self.USE_LXML else Soup(embed, 'html.parser')
        data = json.loads(soup.find('div', {'id': 'video'}).get_attribute_list('data-parameters')[0])
        media_src = json.loads(data['dash'])['src']
        return media_src
    
    def _get_media_server(self, embed_link: str, episode: int, translation: str) -> str:
        """
        Возвращает путь до mpd файла (без самого файла)

        :embed_link: ссылка на embed (можно получить из _get_embed_link)
        :episode: Номер эпизода (вышедшего) (Если фильм - 0)
        :translation: id перевода (который именно для aniboom плеера) (можно получить из get_translations_info)

        Пример возвращаемого: https://sophia.yagami-light.com/7p/7P9qkv26dQ8/
        """
        src = self._get_media_src(embed_link, episode, translation)
        return src[:src.rfind('/')+1]
    
    def _get_media_server_from_src(self, media_src: str) -> str:
        """
        Просто отрезает от ссылки на mpd файл сам файл.

        :media_src: ссылка на mpd файл (прим: https://sophia.yagami-light.com/7p/7P9qkv26dQ8/v26utto64xx66.mpd)

        Пример возвращаемого: https://sophia.yagami-light.com/7p/7P9qkv26dQ8/
        """
        return media_src[:media_src.rfind('/')+1]
    
    def _get_mpd_playlist(self, embed_link: str, episode: int, translation: str) -> str:
        """
        Получение файла mpd через embed_link

        :embed_link: ссылка на embed (можно получить из _get_embed_link)
        :episode: Номер эпизода (вышедшего) (Если фильм - 0)
        :translation: id перевода (который именно для aniboom плеера) (можно получить из get_translations_info)

        Возвращает mpd файл в виде текста. (Можно сохранить результат как res.mpd и при запуске через поддерживающий mpd файлы плеер должна начаться серия)
        Обратите внимание, что файл содержит именно ссылки на части изначального файла, поэтому не сможет запуститься без интернета.
        Также в файле содержится сразу несколько "качеств" видео (от 480 до 1080 в большинстве случаев).
        Если вам нужен mp4 файл воспользуйтесь ffmpeg или другими конвертерами
        """
        embed = self._get_embed(embed_link, episode, translation)
        soup = Soup(embed, 'lxml') if self.USE_LXML else Soup(embed, 'html.parser')
        data = json.loads(soup.find('div', {'id': 'video'}).get_attribute_list('data-parameters')[0])
        media_src = json.loads(data['dash'])['src']
        headers = {
            'Origin': f'https://aniboom.one',
            'Referer': f'https://aniboom.one/',
        }
        playlist = requests.get(media_src, headers=headers).text
        # Вставляем полный путь до сервера
        if '<MPD' in playlist:
            filename = media_src[media_src.rfind('/')+1:media_src.rfind('.')]
            server_path = media_src[:media_src.rfind('.')]
            playlist = playlist.replace(filename, server_path)
        else:
            server_path = media_src[:media_src.rfind('master_device.m3u8')]
            playlist = playlist.replace('media_', server_path+'media_')
        return playlist
    
    def get_mpd_playlist(self, animego_id: str, episode: int, translation_id: str) -> str:
        """
        Возвращает mpd файл строкой (содержимое файла)
        
        :animego_id: id аниме на animego.me (может быть найдена из fast_search по ключу 'animego_id' для нужного аниме или из search по ключу 'animego_id' для нужного аниме) (из ссылки на страницу аниме https://animego.me/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546 > 2546)
        :episode: Номер эпизода (вышедшего) (Если фильм - 0)
        :translation_id: id перевода (который именно для aniboom плеера) (можно получить из get_translations_info)

        Возвращает mpd файл в виде текста. (Можно сохранить результат как res.mpd и при запуске через поддерживающий mpd файлы плеер должна начаться серия)
        Обратите внимание, что файл содержит именно ссылки на части изначального файла, поэтому не сможет запуститься без интернета.
        Также в файле содержится сразу несколько "качеств" видео (от 480 до 1080 в большинстве случаев).
        Если вам нужен mp4 файл воспользуйтесь ffmpeg или другими конвертерами
        """
        embed_link = self._get_embed_link(animego_id)
        return self._get_mpd_playlist(embed_link, episode, translation_id)
    
    def get_as_file(self, animego_id: str, episode: int, translation_id: str, filename: str) -> None:
        """
        Сохраняет mpd файл как указанный filename
        
        :animego_id: id аниме на animego.me (может быть найдена из fast_search по ключу 'animego_id' для нужного аниме или из search по ключу 'animego_id' для нужного аниме) (из ссылки на страницу аниме https://animego.me/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546 > 2546)
        :episode: Номер эпизода (вышедшего) (Если фильм - 0)
        :translation_id: id перевода (который именно для aniboom плеера) (можно получить из get_translations_info)
        :filename: Имя/путь для сохраняемого файла обязательно чтобы было .mpd расширение (прим: result.mpd или content/result.mpd)

        Обратите внимание, что файл содержит именно ссылки на части изначального файла, поэтому не сможет запуститься без интернета.
        Также в файле содержится сразу несколько "качеств" видео (от 480 до 1080 в большинстве случаев).
        Если вам нужен mp4 файл воспользуйтесь ffmpeg или другими конвертерами
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_mpd_playlist(animego_id, episode, translation_id))

""" 
На будущее, если m3u8 будет

    def get_quality_info(self, animego_id: str, episode: int, translation: str):
        \"""
        
        Returns list of available qualities. Example:

        \"""
        _emb_link = self._get_embed_link(animego_id)
        master_playlist = self._get_playlist(_emb_link, episode, translation) # Поработать с плейлистом еще

        if master_playlist[:master_playlist.find('\n')] != "#EXTM3U":
            raise errors.UnexpectedBehavior(f'Expected m3u8 master playlist, where first line should be "#EXTM3U", but got "{master_playlist[:master_playlist.find('\n')]}" instead')
        res = []
        while "RESOLUTION" in master_playlist:
            ind = master_playlist.find('RESOLUTION=')+11
            res.append(master_playlist[ind:master_playlist.find(',', ind)])
            master_playlist = master_playlist[ind:]
        return res

    def _fix_playlist(self, playlist: str, server_path: str) -> str:
        uri = playlist[playlist.find('#EXT-X-MAP:URI="')+16:]
        uri = uri[:uri.find('_')+1]
        print(uri)
        return playlist.replace(uri, server_path+uri)
    
    def get_files(self, animego_id: str, episode: int, translation: str, folder_path: str = ''):
        _emb_link = self._get_embed_link(animego_id)
        master_playlist = self._get_playlist(_emb_link, episode, translation)
        print(master_playlist)

        if master_playlist[:master_playlist.find('\n')] != "#EXTM3U":
            raise errors.UnexpectedBehavior(f'Expected m3u8 master playlist, where first line should be "#EXTM3U", but got "{master_playlist[:master_playlist.find('\n')]}" instead')

        master_copy = master_playlist
        
        audio_link = master_playlist[master_playlist.find('URI="')+5:master_playlist.find('"', master_playlist.find('URI="')+6)]
        
        available_qualities = []
        while "RESOLUTION" in master_playlist:
            ind = master_playlist.find('RESOLUTION=')+11
            master_playlist = master_playlist[ind:]
            uri = master_playlist[master_playlist.find('\n')+1:master_playlist.find('\n', master_playlist.find('\n')+1)]
            available_qualities.append(uri)

        server_path = audio_link[:audio_link.rfind('/')+1]
        master_playlist = master_playlist.replace(server_path, '')
        
        headers = {
            'Origin': f'https://aniboom.one',
            'Referer': f'https://aniboom.one/',
        }
        with open(folder_path+audio_link[audio_link.rfind('/')+1:], 'w', encoding='utf-8') as f:
            f.write(self._fix_playlist(requests.get(audio_link, headers=headers).text, server_path))
        
        for v in available_qualities:
            with open(folder_path+v[v.rfind('/')+1:], 'w', encoding='utf-8') as f:
                 f.write(self._fix_playlist(requests.get(v, headers=headers).text, server_path))

        with open(folder_path+'master.m3u8', 'w', encoding='utf-8') as f:
            f.write(master_copy.replace(server_path, ''))

"""