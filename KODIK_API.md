# Документация по api плеера Kodik

> [!IMPORTANT]
> !!! ВАЖНО !!!
> Это НЕ официальная документация для апи. Все что приведено ниже было установлено методом проб и ошибок, а также подсмотрено с https://docs.rs/kodik-api/latest/kodik_api/index.html, поэтому может содержать неточности и неполноценное описание.

Если у вас есть более полная информация или вы хотите дополнить/исправить имеющуюся, просьба написать мне на почту [ya.nesy.tortik.email@gmail.com](mailto:ya.nesy.tortik.email@gmail.com?subject=[GitHub]%20Kodik%20api%20docs)

## Содержание
* [Как достучаться до апи](#как-достучаться-до-апи)
    - [Эндпоинты](#эндпоинты)
    - [Методы](#методы)
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