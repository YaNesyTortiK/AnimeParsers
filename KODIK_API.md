# Документация по api плеера Kodik

> [!IMPORTANT]
> !!! ВАЖНО !!!
> Это НЕ официальная документация для апи. Все что приведено ниже было установлено методом проб и ошибок, а также подсмотрено с https://docs.rs/kodik-api/latest/kodik_api/index.html, поэтому может содержать неточности и неполноценное описание.

Если у вас есть более полная информация или вы хотите дополнить/исправить имеющуюся, просьба написать мне на почту [ya.nesy.tortik.email@gmail.com](mailto:ya.nesy.tortik.email@gmail.com?subject=[GitHub]%20Kodik%20api%20docs)

## Содержание
* [Как достучаться до апи](#как-достучаться-до-апи)
    - [Эндпоинты](#эндпоинты)
    - [Методы](#методы)
* [Использование библиотеки](#как-пользоваться)
    - [Пример поиска](#пример-поиска)
    - [Пример списка](#пример-списка)
    - [Описание класса Api](#описание-класса-api)
        - [Доступные подклассы](#доступные-подклассы-контейнеры-с-предустановленными-параметрами)
        - [Доступные функции](#доступные-функции-накладываемые-на-запрос-параметры-и-фильтры)
        - [Функции выполнения запросов](#функции-выполнения-запросов)
    - [Примеры](#примеры)
        - [Пример выполнения нескольких запросов](#пример-выполнения-нескольких-запросов-по-одному-фильтру)
        - [Пример указания нескольких параметров](#пример-указания-нескольких-параметров-одного-типа)
        - [Следующая страница](#пример-выполнения-запроса-на-следующую-страницу)
    - [Описание класса Response](#описание-класса-response)
* [Подробнее про поиск](#подробнее-про-поиск)
    - [Поиск по названию](#поиск-по-названию)
    - [Поиск по id](#поиск-по-id)
* [Подробнее про список](#подробнее-про-список)
* [Фильтры и параметры запроса](#доступные-фильтры-и-параметры-запроса)
    - [Параметры фильтрации](#параметры-фильтрации)
    - [Дополнительные параметры](#дополнительные-параметры)
    - [Пример запроса с фильтрами](#пример-запроса-с-фильтрами)
* [Другое](#другое)
    - [Как получить ключ](#как-получить-api-ключ)
    - [MPAA рейтинги](#mpaa-рейтинги)
    - [Типы аниме](#типы-аниме)
    - [Доступные жанры](#доступные-жанры)
    - [Доступные аниме жанры](#доступные-аниме-жанры)


## Как достучаться до апи
Для того чтобы использовать апи кодика, вам понадобится ключ. Вы можете воспользоваться своим ключом (если он у вас есть), либо, если у вас нет ключа, воспользоваться общедоступным. [как получить ключ](#как-получить-api-ключ)

### Эндпоинты
* Основная ссылка api endpoint: `https://kodikapi.com`
* Ссылка для поисковых запросов: `https://kodikapi.com/search`
* Ссылка для получения списка: `https://kodikapi.com/list`
* Ссылка для получения json файла с переводами: `https://kodikapi.com/translations`

### Методы
Для каждого запроса нужно указывать параметр token
* Для поискового запроса используется POST запрос. [подробно](#подробнее-про-поиск)
    <details>
    <summary>Пример curl</summary>
    `curl --location --request POST 'https://kodikapi.com/search?token=your_token?title=%D0%9A%D1%83%D0%BB%D0%B8%D0%BD%D0%B0%D1%80%D0%BD%D1%8B%D0%B5%20%D1%81%D0%BA%D0%B8%D1%82%D0%B0%D0%BD%D0%B8%D1%8F'`
    Данный запрос выполняет поиск аниме с названием "Кулинарные скитания" и вернет список вариантов.
    </details>
* Для получения списка используется POST запрос. [подробно](#подробнее-про-список)
    <details>
    <summary>Пример curl</summary>
    `curl --location --request POST 'https://kodikapi.com/list?token=your_token'`
    В результате данного запроса вернется список вариантов (предположительно самые последние обновления)
    </details>
* Для получения json файла с переводами используется POST запрос.
    <details>
    <summary>Пример curl</summary>
    `curl --location --request POST 'https://kodikapi.com/translations?token=your_token'`
    В результате данного запроса вернется json со списком элементов вида `{"id": id перевода (int), "title": название студии / перевода (string), "type": тип перевода ("voice" / "subtitles")}`
    </details>

## Как пользоваться
Для обращения к апи вы можете воспользоваться функциями данной библиотеки.
Пример импорта:
```python
from anime_parsers_ru import KodikSearch, KodikList
# KodikSearch - реализует параметры для поиска (наследуется от внутреннего класса Api)
# KodikList - накладывает ограничения на те параметры, которые не могут быть использованы (наследуется от внутреннего класса Api)
```

### Пример поиска
```python
query = KodikSearch().title('Кулинарные скитания') # Инициализация параметров запроса
data = query.execute() # Выполнение запроса
print(type(data)) # -> Response
print(data.total) # Вернет количество найденных элементов. (Если найдено 0, то вернется NoResults exception)
print(data.results) # Вернет список элементов типа Element
print(data.results[0].title) # Вернет название первого элемента
```

### Пример списка
```python
query = KodikList().anime_kind(KodikList.AnimeKind.tv).limit(10)
data = query.execute() # Выполнение запроса
print(type(data)) # -> Response
print(data.total) # Вернет количество найденных элементов. (Если найдено 0, то вернется NoResults exception)
print(data.results) # Вернет список элементов типа Element
print(data.results[0].title) # Вернет название первого элемента
```

При инициализации классов, можно передать следующие параметры:
* `token` - Токен для апи кодика. По умолчанию None. Если токен не передан, то при инициализации класса, будет автоматически найден токен с помощью функций из `KodikParser` данной библиотеки.
* `allow_warnings` - Разрешить вывод в консоль предупреждений о некоторых параметрах. По умолчанию True.
* `_args` - Словарь параметров, если нужно добавить параметр которого нет в реализованных. По умолчанию пусто.

При выполнении запроса возвращается элемент типа Response. Если при использовании `execute()` в параметрах функции указать `return_json=True` то вместо Response функция вернет словарь.


> [!IMPORTANT]
> Если вы используете встроенную функцию поиска токена, а не указываете свой, то рекомендуется создать изначальный экземпляр класса в начале, а потом наследовать все следующие поиски от него, чтобы не тратить время на получение токена при каждом новом создании.

Пример:
```python
search = KodikSearch() # Создаем пустой класс, чтобы там был только автоматически найденный токен

# Создаем запросы как обычно, используя `search` вместо `KodikSearch`
query1 = search.title('Мастера меча онлайн')
query2 = search.title('Кулинарные скитания')
```


### Описание класса Api
И его наследников KodikSearch и KodikList

#### Доступные подклассы (контейнеры с предустановленными параметрами):
* AnimeKind - Тип аниме по виду. [Параметры](#типы-аниме)
* Types - Тип мультимедиа. [Параметры](#доступные-типы-мультимедиа)
* MPAArating - Возрастной рейтинг mpaa. [Параметры](#mpaa-рейтинги)
* Genres - Основные жанры. [Параметры](#доступные-жанры)
* AnimeGenres - Аниме жанры. [Параметры](#доступные-аниме-жанры)

> Все параметры, описанные на русском, вызываются через английский перевод (Прим: `военное` -> `AnimeGenres.military`)
> Дополнительно эти параметры указаны в документации к классам.

#### Доступные функции (накладываемые на запрос параметры и фильтры): 
[Фильтры и параметры запроса](#доступные-фильтры-и-параметры-запроса)

Все параметры указываются друг за другом в виде:

```python
query = KodikSearch().title('Кулинарные скитания').limit(3).anime_kind(KodikSearch.AnimeKind.tv).with_episodes()
```

#### Функции выполнения запросов
* `execute()` - выполнить запрос (Принимает параметр return_json, по умолчанию False; Если True, то вместо Response функция вернет изначальный json)
* `execute_async()` - асинхронное выполнение запроса
* `api_request()` - выполнить запрос по указанным параметрам или по прямой ссылке, для использования необходимо передать либо словарь параметров, либо ссылку
* `api_request_async()` - асинхронный запрос по параметрам
* `next_page()` - Можно использовать как `data = query.next_page()`, если до этого был выполнен хотя-бы один запрос для этого элемента и в ответе сервер вернул параметр `next_page` (только при запросе через KodikList)
* `next_page_async()` - Можно использовать как `data = await query.next_page_async()`, если до этого был выполнен хотя-бы один запрос для этого элемента и в ответе сервер вернул параметр `next_page` (только при запросе через KodikList)
* `prev_page()` - Можно использовать как `data = query.prev_page()`, если до этого был выполнен хотя-бы один запрос для этого элемента и в ответе сервер вернул параметр `prev_page` (только при запросе через KodikList)
* `prev_page_async()` - Можно использовать как `data = await query.prev_page_async()`, если до этого был выполнен хотя-бы один запрос для этого элемента и в ответе сервер вернул параметр `prev_page` (только при запросе через KodikList)
* `get_translations()` - Возвращает словарь всех доступных переводов (эндпоинт translations). Можно использовать как `KodikSearch().get_translations()`

### Примеры
#### Пример выполнения нескольких запросов по одному фильтру
```python
query = KodikSearch().limit(5).title('Мастера меча онлайн') # Создаем основной запрос
query_tv = query.anime_kind(KodikSearch.AnimeKind.tv) # Создаем запрос с фильтром на "ТВ-Сериал"
query_movie = query.anime_kind(KodikSearch.AnimeKind.movie) # Создаем запрос с фильтром на аниме фильмы
data_tv = query_tv.execute() # Получаем данные по запросу тв сериала
data_movie = query_movie.execute() # Получаем данные по запросу фильма
```
Аналогично:
```python
query = KodikSearch().limit(5).title('Мастера меча онлайн') # Создаем основной запрос
# В данном случае не создаем отдельных переменных
data_tv = query.anime_kind(KodikSearch.AnimeKind.tv).execute() # Получаем данные по запросу тв сериала
data_movie = query.anime_kind(KodikSearch.AnimeKind.movie).execute() # Получаем данные по запросу фильма
```

#### Пример указания нескольких параметров одного типа
Не все параметры допускают указывать несколько фильтров, читайте в документации к функции.
```python
query = KodikList().anime_genres([KodikSearch.AnimeGenres.military, KodikSearch.AnimeGenres.fantasy]).limit(5)
```
Аналогично:
```python
query = KodikList().anime_genres(['Военное', 'Фэнтези']).limit(5)
```

#### Пример выполнения запроса на следующую страницу:
Обратите внимание, что перед запросом на следующую страницу, класс запроса (в данном случае `query`) должен выполнить запрос по фильтрам хотя-бы один раз. В противном случае ссылка на следующую страницу является неизвестной.
```python
query = KodikList().anime_kind(KodikList.AnimeKind.tv).anime_status('ongoing').limit(5) # Инициализируем новый запрос и параметры
data1 = query.execute() # Выполняем первый запрос
print(data1.results[-1].id) # Результат: serial-62436
data2 = query.next_page() # Выполняем запрос на следующую страницу
print(data2.results[-1].id) # Результат: serial-64685
```

Для запроса на предыдущую страницу просто используется функция `prev_page` вместо `next_page` как в примере выше.

#### Пример получения списка переводов и количества серий
Для получения информации о переводах и количестве серий в каждом переводе, требуется выполнить запрос для получения какого-либо элемента, а затем функция вызывается от требуемого элемента.
```python
# Выполняем первичный поиск (Наруто)
initial = KodikSearch().shikimori_id('20').execute()
# Получаем список переводов и серий
data = initial.results[0].get_episodes_and_translations()
# Вывод:
"""
[{'episodes_count': 220,
  'title': 'AniDUB',
  'translation_id': 609,
  'type': 'voice'},
 {'episodes_count': 220,
  'title': '2x2',
  'translation_id': 735,
  'type': 'voice'},
 {'episodes_count': 135,
  'title': 'AniRise',
  'translation_id': 958,
  'type': 'voice'},
 {'episodes_count': 8,
  'title': 'ANI.OMNIA',
  'translation_id': 2550,
  'type': 'voice'},
 {'episodes_count': 220,
  'title': 'Субтитры',
  'translation_id': 869,
  'type': 'subtitles'}]
"""
```

### Описание класса Response

Подклассы:
* Element - элемент результата (из переменных этого типа формируется массив results)
* MaterialData - описывает дополнительный параметр результата при передаче параметра `with_material_data` (Используется подклассом Element в параметре Element.material_data)
* Season - описывает дополнительный параметр season (если имеется в ответе)
    * Episode - подкласс класса Season - описывает эпизоды (если имеются в ответе)
* Translation - описывает элемент перевода (Element.translation)

Структура класса Response (со всеми возможными полями)
> Не все поля будут присутствовать при разных запросах, поэтому некоторые значения будут обращаться в None

> Обратите внимание, что вы всегда можете обратиться к параметру `raw_data` чтобы получить исходный словарь

* Response:
    * raw_data - исходный json словарь (в виде питоновского словаря)
    * total - количество результатов
    * time - время выполнения запроса (считается на сервере кодика)
    * results - список элементов (типа Response.Element)
        * raw_data
        * _keys - ключи словаря
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
            * raw_data
            * _keys
            * id - id перевода/озвучки
            * title - Название перевода / Студии озвучки
            * type - Тип перевода ("voice" или "subtitles")
            * is_voice - Является ли озвучкой (проверка по типу на "voice")
        * seasons - Словарь сезонов (вид: '{'1': Response.Season}') (если есть, иначе None)
            * raw_data
            * link - embed ссылка на сезон (kodik.info/...) с возможностью выбора серии
            * episodes - Словарь эпизодов (вид: '{'1': Response.Season.Episode}') (если есть, иначе None)
                * link - embed ссылка на эпизод (kodik.info/...) без возможности сменить серию
                * title - Название эпизода (если есть, иначе None)
                * screenshots - Список ссылок на скриншоты (если есть, иначе None)
        * material_data - Дополнительные параметры (тип Response.MaterialData) (если есть, иначе None)
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
        * get_episodes_and_translations - Функция, возвращающая список словарей состоящих из озвучки и количества озвученных эпизодов этой озвучкой
        * get_episodes_and_translations_async - Асинхронная функция, возвращающая список словарей состоящих из озвучки и количества озвученных эпизодов этой озвучкой
        

## Подробнее про поиск
Для поиска требуется знать один из ключевых элементов контента: название или id.
Также в ответе сервера будут возможны повторения одного и того-же контента из-за того, что кодик разделяет разные озвучки как разные объекты не группируя их в один. Также вы можете фильтровать и устанавливать дополнительные флаги при запросе. [подробнее](#доступные-фильтры-и-параметры-запроса)

### Поиск по названию
Для поиска по названию ссылка будет выглядеть так: `https://kodikapi.com/search?token=your_token&title=Naruto`
> [!NOTE]
> Поиск по названию может возвращать несвязанные с запрошенным названием элементы (особенно если название введено с ошибкой или мультимедиа с таким названием не найдено).

Запрос: `https://kodikapi.com/search?token=your_token&title=Naruto` <br>
Ответ:
```json
{
    "time": "9ms",
    "total": 50,
    "results": [
        {
            "id": "movie-95847",
            "type": "anime",
            "link": "//kodik.info/video/95847/92165e64eeca2372c0fd0e6f4bd9a911/720p",
            "title": "Боруто: День, когда Наруто стал хокагэ",
            "title_orig": "Naruto ga Hokage ni natta hi",
            "other_title": "Боруто (Спешл) / Boruto: Naruto the Movie - Naruto ga Hokage ni Natta Hi / The Day Naruto Became Hokage",
            "translation": {
                "id": 1990,
                "title": "NekoVoice",
                "type": "voice"
            },
            "year": 2016,
            "kinopoisk_id": "991025",
            "imdb_id": "tt5866090",
            "shikimori_id": "32365",
            "quality": "BDRip 720p",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "created_at": "2023-06-21T20:05:46Z",
            "updated_at": "2023-06-21T20:05:46Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/video/95847/1.jpg",
                "https://i.kodik.biz/screenshots/video/95847/2.jpg",
                "https://i.kodik.biz/screenshots/video/95847/3.jpg",
                "https://i.kodik.biz/screenshots/video/95847/4.jpg",
                "https://i.kodik.biz/screenshots/video/95847/5.jpg"
            ]
        },
        ...
        {
            "id": "movie-95291",
            "type": "anime",
            "link": "//kodik.info/video/95291/8bf83bfe4479954ff87dbb2638ebc2dc/720p",
            "title": "Наруто 9: Путь ниндзя",
            "title_orig": "Road to Ninja: Naruto the Movie",
            "other_title": "Наруто (фильм девятый) - Становление ниндзя",
            "translation": {
                "id": 1002,
                "title": "Flarrow Films",
                "type": "voice"
            },
            "year": 2012,
            "kinopoisk_id": "678323",
            "imdb_id": "tt2290828",
            "worldart_link": "http://www.world-art.ru/animation/animation.php?id=837",
            "shikimori_id": "13667",
            "quality": "WEB-DLRip 720p",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "created_at": "2023-06-03T09:16:09Z",
            "updated_at": "2023-06-03T09:16:09Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/video/95291/1.jpg",
                "https://i.kodik.biz/screenshots/video/95291/2.jpg",
                "https://i.kodik.biz/screenshots/video/95291/3.jpg",
                "https://i.kodik.biz/screenshots/video/95291/4.jpg",
                "https://i.kodik.biz/screenshots/video/95291/5.jpg"
            ]
        }
    ]
}
```

### Поиск по id
Для поиска по id также потребуется уточнить, какой тип id. <br>
Проверенные: shikimori_id, kinopoisk_id, imdb_id, id (внутренний id kodik). <br>
Пример запроса: `https://kodikapi.com/search?token=your_token&shikimori_id=20`
> [!TIP]
> При поиске по id в ответе сервера возможны повторяющиеся элементы из-за разных озвучек. Поэтому таким образом можно получать список (возможно неполный) доступных озвучек.

Запрос: `https://kodikapi.com/search?token=your_token&shikimori_id=20` <br>
Ответ:
```json
{
    "time": "5ms",
    "total": 5,
    "results": [
        {
            "id": "serial-6647",
            "type": "anime-serial",
            "link": "//kodik.info/serial/6647/cd5cb18078eb1d1a96abe338b2ffeb16/720p",
            "title": "Наруто [ТВ-1]",
            "title_orig": "Naruto",
            "other_title": "ナルト",
            "translation": {
                "id": 609,
                "title": "AniDUB",
                "type": "voice"
            },
            "year": 2002,
            "last_season": 1,
            "last_episode": 220,
            "episodes_count": 220,
            "kinopoisk_id": "283290",
            "imdb_id": "tt0409591",
            "worldart_link": "http://www.world-art.ru/animation/animation.php?id=262",
            "shikimori_id": "20",
            "quality": "DVDRip",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "blocked_seasons": {},
            "created_at": "2017-11-26T17:20:57Z",
            "updated_at": "2019-12-06T07:17:42Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/seria/176463/1.jpg",
                "https://i.kodik.biz/screenshots/seria/176463/2.jpg",
                "https://i.kodik.biz/screenshots/seria/176463/3.jpg",
                "https://i.kodik.biz/screenshots/seria/176463/4.jpg",
                "https://i.kodik.biz/screenshots/seria/176463/5.jpg"
            ]
        },
        ...
        {
            "id": "serial-42758",
            "type": "anime-serial",
            "link": "//kodik.info/serial/42758/bb173bb49a1d7bd2d8a7ca43c70a4082/720p",
            "title": "Наруто [ТВ-1]",
            "title_orig": "Naruto",
            "other_title": "ナルト",
            "translation": {
                "id": 869,
                "title": "Субтитры",
                "type": "subtitles"
            },
            "year": 2002,
            "last_season": 1,
            "last_episode": 220,
            "episodes_count": 220,
            "kinopoisk_id": "283290",
            "imdb_id": "tt0409591",
            "worldart_link": "http://www.world-art.ru/animation/animation.php?id=262",
            "shikimori_id": "20",
            "quality": "DVDRip",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "blocked_seasons": {},
            "created_at": "2022-05-06T07:40:55Z",
            "updated_at": "2022-05-06T17:16:53Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/seria/996948/1.jpg",
                "https://i.kodik.biz/screenshots/seria/996948/2.jpg",
                "https://i.kodik.biz/screenshots/seria/996948/3.jpg",
                "https://i.kodik.biz/screenshots/seria/996948/4.jpg",
                "https://i.kodik.biz/screenshots/seria/996948/5.jpg"
            ]
        }
    ]
}
```

## Подробнее про список
В данном случае не требуется указывать никакие параметры (кроме токена) при запросе.

обратите внимание, что в дополнение к данным, в ответе добавлены параметры `next_page` и `prev_page` с помощью которых можно "листать" список и элементы не будут повторяться.

Пример запроса: `https://kodikapi.com/list?token=your_token`<br>
Пример ответа:
```json
{
    "time": "15ms",
    "total": 63887,
    "prev_page": null,
    "next_page": "https://kodikapi.com/list?token=447d179e875efe44217f20d1ee2146be&next=WzE3MzU2MTkwNjcwMDAsInNlcmlhbC02MzY5NSJd",
    "results": [
        {
            "id": "movie-108152",
            "type": "anime",
            "link": "//kodik.info/video/108152/869f513fbac154c33b73dcce24187bd2/720p",
            "title": "Поднятие уровня в одиночку. Второе пробуждение",
            "title_orig": "Ore dake Level Up na Ken: ReAwakening",
            "other_title": "Solo Leveling: ReAwakening",
            "translation": {
                "id": 1062,
                "title": "LE-Production",
                "type": "voice"
            },
            "year": 2024,
            "kinopoisk_id": "6634211",
            "imdb_id": "tt33428606",
            "shikimori_id": "59841",
            "quality": "TS 720p",
            "camrip": true,
            "lgbt": false,
            "blocked_countries": [],
            "created_at": "2024-12-31T11:32:15Z",
            "updated_at": "2024-12-31T11:32:15Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/video/108152/1.jpg",
                "https://i.kodik.biz/screenshots/video/108152/2.jpg",
                "https://i.kodik.biz/screenshots/video/108152/3.jpg",
                "https://i.kodik.biz/screenshots/video/108152/4.jpg",
                "https://i.kodik.biz/screenshots/video/108152/5.jpg"
            ]
        },
        ...
        {
            "id": "serial-63695",
            "type": "foreign-serial",
            "link": "//kodik.info/serial/63695/46c4452fad96e4281e931ccef12fc9dc/720p",
            "title": "Рыцарь розы",
            "title_orig": "Mei Gu Qi Shi",
            "other_title": "Knight of the Rose / Rose Knight / Rose and Knight",
            "translation": {
                "id": 1355,
                "title": "DubLik.Tv",
                "type": "voice"
            },
            "year": 2022,
            "last_season": 1,
            "last_episode": 11,
            "episodes_count": 11,
            "kinopoisk_id": "5453812",
            "imdb_id": "tt25503906",
            "mdl_id": "56743-mei-gui-qi-shi",
            "quality": "WEB-DLRip 720p",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "blocked_seasons": {},
            "created_at": "2024-12-08T19:58:55Z",
            "updated_at": "2024-12-31T04:24:27Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/seria/1391773/1.jpg",
                "https://i.kodik.biz/screenshots/seria/1391773/2.jpg",
                "https://i.kodik.biz/screenshots/seria/1391773/3.jpg",
                "https://i.kodik.biz/screenshots/seria/1391773/4.jpg",
                "https://i.kodik.biz/screenshots/seria/1391773/5.jpg"
            ]
        }
    ]
}
```



## Доступные фильтры и параметры запроса
В большинстве запросов вы можете добавить параметры фильтрации или дополнительные параметры которые сервер должен вернуть в ответе.

Ниже представлены известные параметры: (N/A - не проверено / нет возможности проверить)

### Параметры фильтрации
| Параметр | Тип данных | Описание | Ограничения | Поиск | Список |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | 
| `limit` | int | максимальное количество элементов в одном ответе | не более 100 | :heavy_check_mark: | :heavy_check_mark: |
| `title` | string | название мультимедиа | - | :heavy_check_mark: | :x: |
| `title_orig` | string | оригинальное название мультимедиа (на английском) | - | :heavy_check_mark: | :x: |
| `strict` | bool | Производить поиск по конкретному названию в названии элемента будет точно содержаться строка из запроса | - | :heavy_check_mark: | :x: |
| `full_match` | bool | Точное совпадение запроса и элемента | - | :heavy_check_mark: | :x: |
| `shikimori_id` | string/int | Поиск по id шикимори | - | :heavy_check_mark: | :x: |
| `kinopoisk_id` | string | Поиск по id кинопоиска | - | :heavy_check_mark: | :x: |
| `imdb_id` | string | Поиск по id imdb | - | :heavy_check_mark: | :x: |
| `id` | string | Поиск по внутреннему id кодика | - | :heavy_check_mark: | :x: |
| `mdl_id` | string | Поиск по id MyDramaList | - | :heavy_check_mark: | :x: |
| `worldart_animation_id` | string | Поиск по id WorldArt Animation | - | :heavy_check_mark: | :x: |
| `worldart_cinema_id` | string | Поиск по id WorldArt Cinema | - | N/A | :x: |
| `worldart_link` | string | Поиск по ссылке на WorldArt | <details><summary>Пример</summary>`http://www.world-art.ru/animation/animation.php?id=11464`</details> | :heavy_check_mark: | :x: |
| `types` | string | Типы мультимедиа (разделяется через запятую) | [Доступные типы](#доступные-типы-мультимедиа) | :heavy_check_mark: | :heavy_check_mark: |
| `year` | int | Год выхода | - | :heavy_check_mark: | :heavy_check_mark: |
| `camrip` | bool | Снято ли с камеры | - | :heavy_check_mark: | :heavy_check_mark: |
| `lgbt` | bool |  Имеются в фильме lgbt сцены | - | :heavy_check_mark: | :heavy_check_mark: |
| `translation_id` | int | Id перевода (студии) | [как узнать id](#эндпоинты) | :heavy_check_mark: | :heavy_check_mark: |
| `translation_type` | string | Тип перевода | voice (озвучка) / subtitles (субтитры) | :heavy_check_mark: | :heavy_check_mark: |
| `anime_kind` | string | Тип аниме | [Доступные типы](#типы-аниме) | :heavy_check_mark: | :heavy_check_mark: |
| `anime_status` | string | Статус выхода | released (вышло) / ongoing (выходит) / anons (анонсировано) | :heavy_check_mark: | :heavy_check_mark: |
| `mydramalist_tags` | string | Тэги MyDramaList (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `rating_mpaa` | string | Возрастное ограничение по MPAA | [Доступные рейтинги](#mpaa-рейтинги) | :heavy_check_mark: | :heavy_check_mark: |
| `minimal_age` | int | Минимальный допустимый возраст зрителя | - | :heavy_check_mark: | :heavy_check_mark: |
| `kinopoisk_rating` | float | Оценка на кинопоиске | 0-10 | :heavy_check_mark: | :heavy_check_mark: |
| `imdb_rating` | float | Оценка на imdb | 0-10 | :heavy_check_mark: | :heavy_check_mark: |
| `shikimori_rating` | float | Оценка на шикимори | 0-10 | :heavy_check_mark: | :heavy_check_mark: |
| `anime_studios` | string | Студия анимации | Зависит от регистра | :heavy_check_mark: | :heavy_check_mark: |
| `genres` | string | Жанр | [Доступные жанры](#доступные-жанры) | :heavy_check_mark: | :heavy_check_mark: |
| `anime_genres` | string | Аниме жанры | [Доступные жанры](#доступные-аниме-жанры) | :heavy_check_mark: | :heavy_check_mark: |
| `duration` | int | Продолжительность в минутах | - | :heavy_check_mark: | :heavy_check_mark: |
| `player_link` | string | Ссылка на embed плеер | <details><summary>Пример</summary>`kodik.info/serial/48654/3520f3c13f024b8fe04bc6143ccdcb7d/720p`</details> | :heavy_check_mark: | :x: |
| `has_field` | string | Ищет элементы у которых имеется указанный параметр | - | N/A | :heavy_check_mark: |
| `has_fields` | string | Ищет элементы у которых имеются указанные параметры (перечисляются через запятую) | - | N/A | N/A |
| `has_field_and` | string | Ищет элементы у которых имеются указанные параметры (перечисляются через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `prioritize_translations` | string | Указанные id переводов будут выше в списке элементов (разделяется через запятую) | [как узнать id](#эндпоинты) <details><summary>Дополнительно</summary>Также можно указать тип перевода ("voice"/"subtitles")<br>По умолчанию приоритет выдается профессиональным и многоголосым озвучкам<br>Для отключения стандартного приоритета укажите `0`</details> | :heavy_check_mark: | :x: |
| `unprioritize_translations` | string | Указанные id переводов будут выше в списке элементов (разделяется через запятую) | [как узнать id](#эндпоинты)<details><summary>Дополнительно</summary>Также можно указать тип перевода ("voice"/"subtitles")<br>По умолчанию установлен низкий приоритет озвучкам на Английском и Украинском языках, а также субтитров<br>Для отключения стандартного приоритета укажите `0`</details> | :heavy_check_mark: | :x: |
| `block_translations` | string | Удаляет из результата id переводов (разделяется через запятую) | [как узнать id](#эндпоинты) | :heavy_check_mark: | :heavy_check_mark: |
| `prioritize_translation_type` | string | Указать приоритет типа перевода | "voice"/"subtitles" | N/A | N/A |
| `season` | int | Будут выведены только элементы где имеется этот сезон | - | :heavy_check_mark: | :x: |
| `episode` | int | Будут выведены только элементы где имеется указанная серия  | - | N/A | :x: |
| `not_blocked_in` | string | Указать страны в которых элементы не должны быть заблокированы (разделяется через запятую) | - | N/A | N/A |
| `not_blocked_for_me` | string | Сервер автоматически уберет из результатов элементы заблокированные на территории страны откуда пришел запрос | - | N/A | N/A |
| `countries` | string | Возвращает элементы у которых указаны страны (разделяется через запятую) | Зависит от регистра (Страна с большой буквы), работает на русском | :heavy_check_mark: | :heavy_check_mark: |
| `actors` | string | Возвращает элементы у которых указаны актеры (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `directors` | string | Возвращает элементы у которых указаны режиссеры (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `producers` | string | Возвращает элементы у которых указаны продюсеры (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `writers` | string | Возвращает элементы у которых указаны авторы/писатели (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `composers` | string | Возвращает элементы у которых указаны композиторы (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `editors` | string | Возвращает элементы у которых указаны монтажеры (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `designers` | string | Возвращает элементы у которых указаны дизайнеры (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `operators` | string | Возвращает элементы у которых указаны операторы (разделяется через запятую) | - | :heavy_check_mark: | :heavy_check_mark: |
| `licensed_by` | string | Указать владельца лицензии (разделяется через запятую) | - | N/A | N/A |
| `sort` | string | Отсортировать элементы по определенному признаку. <details><summary>Доступные</summary>year; created_at; updated_at; kinopoisk_rating; imdb_rating; shikimori_rating</details> | - | :x: | :heavy_check_mark: |
| `order` | string | Указать порядок сортировки. asc - по возрастанию. desc - по убыванию. | - | :x: | :heavy_check_mark: |


### Дополнительные параметры
| Параметр | Тип данных | Описание | Дополнительно | Поиск | Список |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | 
| `with_material_data` | bool | Добавляет много дополнительной информации к элементу | - | :heavy_check_mark: | :heavy_check_mark: |
| `with_seasons` | bool | Добавляет элементу отдельный параметр `seasons` где содержаться ссылки на плеер на конкретный сезон | - | :heavy_check_mark: | :heavy_check_mark: |
| `with_episodes` | bool | Автоматически включает `with_seasons` и к каждому сезону также добавляет ссылки на серии | - | :heavy_check_mark: | :heavy_check_mark: |
| `with_episodes_data` | bool | Автоматически включает `with_episodes` и к каждому эпизоду добавляет название эпизода (если есть) и скриншоты (если есть) | - | :heavy_check_mark: | :heavy_check_mark: |
| `with_page_links` | bool | Заменяет ссылку на embed плеер на ссылку на страницу плеера | <details><summary>Пример</summary>`http://kodik.online/episode/1401678/3aoXdn0dc9e43d`</details> | :heavy_check_mark: | :heavy_check_mark: |

### Пример запроса с фильтрами
Поиск по названию.
Указанные фильтры:
* `title` = "Overlord" Поиск по названию
* `limit` = 3 Ограничение на количество результатов до 3
* `translation_id` = "609,610" Какие id переводов/озвучек возвращать (609 - AniDUB, 610 - AniLibria.TV)
* `types` = "anime,anime-serial" Какие типы мультимедиа возвращать (аниме и аниме сериал)
Указанные параметры:
* `with_seasons` - Указываем что нужно отправить информацию о сезонах

Ответ:
```json
{
    "time": "4ms",
    "total": 3,
    "results": [
        {
            "id": "movie-20623",
            "type": "anime",
            "link": "//kodik.info/video/20623/63d71bc65e630b2ebdf0f28a2f8c754c/720p",
            "title": "Повелитель: Пле-пле-плеяды",
            "title_orig": "Overlord: Pure Pure Pleiades",
            "other_title": "Повелитель OVA / Владыка: Пле-пле-плеяды",
            "translation": {
                "id": 609,
                "title": "AniDUB",
                "type": "voice"
            },
            "year": 2016,
            "worldart_link": "http://www.world-art.ru/animation/animation.php?id=8813",
            "shikimori_id": "33372",
            "quality": "HDTVRip 720p",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "created_at": "2018-01-21T14:06:44Z",
            "updated_at": "2019-11-14T17:03:33Z",
            "screenshots": [
                "https://i.kodik.biz/screenshots/video/20623/1.jpg",
                "https://i.kodik.biz/screenshots/video/20623/2.jpg",
                "https://i.kodik.biz/screenshots/video/20623/3.jpg",
                "https://i.kodik.biz/screenshots/video/20623/4.jpg",
                "https://i.kodik.biz/screenshots/video/20623/5.jpg"
            ]
        },
        {
            "id": "serial-7497",
            "type": "anime-serial",
            "link": "//kodik.info/serial/7497/9ce7aabe3ac908460b5ec6eccf01038e/720p",
            "title": "Повелитель [ТВ-1]",
            "title_orig": "Overlord",
            "other_title": "Повелитель I / Владыка ТВ-1",
            "translation": {
                "id": 610,
                "title": "AniLibria.TV",
                "type": "voice"
            },
            "year": 2015,
            "last_season": 1,
            "last_episode": 13,
            "episodes_count": 13,
            "kinopoisk_id": "923115",
            "imdb_id": "tt4869896",
            "worldart_link": "http://www.world-art.ru/animation/animation.php?id=8207",
            "shikimori_id": "29803",
            "quality": "BDRip 720p",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "blocked_seasons": {},
            "created_at": "2017-12-25T22:50:39Z",
            "updated_at": "2018-10-08T19:51:56Z",
            "seasons": {
                "1": {
                    "link": "//kodik.info/season/32715/89d68b6afc07d76f36fd4db6ee51e8b8/720p"
                }
            },
            "screenshots": [
                "https://i.kodik.biz/screenshots/seria/198525/1.jpg",
                "https://i.kodik.biz/screenshots/seria/198525/2.jpg",
                "https://i.kodik.biz/screenshots/seria/198525/3.jpg",
                "https://i.kodik.biz/screenshots/seria/198525/4.jpg",
                "https://i.kodik.biz/screenshots/seria/198525/5.jpg"
            ]
        },
        {
            "id": "serial-44042",
            "type": "anime-serial",
            "link": "//kodik.info/serial/44042/5a0185608facda4125ddad5fd03a66d6/720p",
            "title": "Повелитель [ТВ-4]",
            "title_orig": "Overlord IV",
            "other_title": "Повелитель IV / Повелитель 4 / Владыка ТВ-4 / Владыка 4",
            "translation": {
                "id": 610,
                "title": "AniLibria.TV",
                "type": "voice"
            },
            "year": 2022,
            "last_season": 4,
            "last_episode": 13,
            "episodes_count": 13,
            "kinopoisk_id": "923115",
            "imdb_id": "tt4869896",
            "worldart_link": "http://www.world-art.ru/animation/animation.php?id=10918",
            "shikimori_id": "48895",
            "quality": "WEB-DLRip 720p",
            "camrip": false,
            "lgbt": false,
            "blocked_countries": [],
            "blocked_seasons": {},
            "created_at": "2022-07-06T10:44:28Z",
            "updated_at": "2022-09-27T23:22:22Z",
            "seasons": {
                "4": {
                    "link": "//kodik.info/season/82795/3b6c5f94981565f62f6764545a5d7efb/720p"
                }
            },
            "screenshots": [
                "https://i.kodik.biz/screenshots/seria/1025453/1.jpg",
                "https://i.kodik.biz/screenshots/seria/1025453/2.jpg",
                "https://i.kodik.biz/screenshots/seria/1025453/3.jpg",
                "https://i.kodik.biz/screenshots/seria/1025453/4.jpg",
                "https://i.kodik.biz/screenshots/seria/1025453/5.jpg"
            ]
        }
    ]
}
```


## Другое
### Как получить api ключ
Вы можете воспользоваться встроенной функцией данной библиотеки `KodikParser.get_token()`. 
Обратите внимание, что данная функция основано на том, что во внутренних файлах кодика содержится актуальный рабочий ключ. Поэтому, в случае если такого нет, функция не сможет вернуть результат.

### Доступные типы мультимедиа
* `foreign-movie`
* `soviet-cartoon`
* `foreign-cartoon`
* `russian-cartoon`
* `anime` - Аниме фильм (либо одна серия)
* `russian-movie`
* `cartoon-serial`
* `documentary-serial`
* `russian-serial`
* `foreign-serial`
* `anime-serial`
* `multi-part-film`

### MPAA рейтинги
(Существует рейтинг `R+` но как по нему искать в кодике не понятно - как фильтр он работает идентично `R`)
* `g` - Нет возрастных ограничений.
* `pg` - Рекомендуется присутствие родителей.
* `pg-13` - Детям до 13 лет просмотр нежелателен.
* `r` - Лицам до 17 лет обязательно присутствие взрослого.
* `rx` - Хeнтай / Пoрнография

### Типы аниме
* `tv` - ТВ Сериал
    - `tv13` - ТВ Сериал с длительностью эпизода около 13 минут
    - `tv24` - ТВ Сериал с длительностью эпизода около 24 минут
    - `tv48` - ТВ Сериал с длительностью эпизода около 48 минут
* `movie` - Фильм
* `special` - Спецвыпуск
* `ova` - OVA
* `ona` - ONA
* `music` - Музыкальный клип

### Доступные жанры
(Список требует дополнения)
* `аниме`
* `драма`
* `комедия`
* `мультфильм`
* `фэнтези`
* `боевик`
* `приключения`
* `фантастика`

### Доступные аниме жанры
(Список требует дополнения)
* `Военное`
* `Драма`
* `Исторический`
* `Экшен`
* `Приключения`
* `Сёнен`
* `Фэнтези`
* `Комедия`
* `Боевые искусства`
* `Романтика`
* `Психологическое`
* `Триллер`
* `Повседневность`
* `Сверхъестественное`
* `Спорт`
* `Школа`
* `Музыка`
* `Фантастика`
* `Самураи`