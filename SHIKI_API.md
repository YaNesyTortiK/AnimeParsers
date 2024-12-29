# Шпаргалка ShikimoriParser
Данный файл содержит примеры запросов и параметров для использования https://shikimori.one/api/doc/graphql в качестве замены api у shikimori.

> [!IMPORTANT]
> !!! ВАЖНО !!!
> Данный способ не гарантирует что ваш ip адрес не будет забанен за некорректное использование документации шикимори

> [!NOTE]
> Данный способ также подвержен ограничениям по количеству запросов, однако лимит незначительно больше. Также данные функции работают значительно быстрее и надежнее стандартных парсеров.

Приведенные ниже инструкции относятся к функциям `deep_search` и `deep_anime_info` модуля `ShikimoriParser` в библиотеке `anime_parsers_ru`

## Содержание
- [Информация](#где-поиграться-с-параметрами-и-найти-нужные-для-своего-парсера)
- [Полный запрос](#полный-запрос)
- [Простой пример](#пример-простого-запроса)

## Где поиграться с параметрами и найти нужные для своего парсера:
Вы можете воспользоваться: 
- [Самим graphql](https://shikimori.one/api/doc/graphql)
- [Документацие шикимори по 1 версии api](https://shikimori.one/api/doc/1.0/animes/index)

(Используется документация для 1 версия api, потому что для 2 версии нет адекватной документации)

## Полный запрос
Для graphql
```
{
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
      }
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
```

### Пример простого запроса
1. Для graphql:
    ```
    {
        animes(search: "Кулинарные скитания", limit: 2) {
            id
            name
            russian
            rating
            status
            score
            poster { originalUrl }
            genres { russian }
            description
            studios { name imageUrl }
        }
    }
    ```
    Результат:
    ```json
    {
        "data": {
            "animes": [
            {
                "id": "53446",
                "name": "Tondemo Skill de Isekai Hourou Meshi",
                "russian": "Кулинарные скитания в параллельном мире",
                "rating": "pg_13",
                "status": "released",
                "score": 7.66,
                "poster": {
                "originalUrl": "https://desu.shikimori.one/uploads/poster/animes/53446/558a04d14c503e52cb0a05f8cb117363.jpeg"
                },
                "genres": [
                {
                    "russian": "Приключения"
                },
                {
                    "russian": "Комедия"
                },
                {
                    "russian": "Фэнтези"
                },
                {
                    "russian": "Гурман"
                },
                {
                    "russian": "Исэкай"
                }
                ],
                "description": "Очередное королевство оказалось не в состоянии самостоятельно справиться с постигшими его проблемами и решило положиться на силу призванных иномирцев. Одного показалось маловато, поэтому с помощью ритуала перенесли сразу четырёх героев. Среди них затесался и 27-летний Цуёси Мукода. Вот только вскоре выяснилось, что его переместили в этот мир по ошибке. Никаких чудесных способностей у него, как не было, так и нет. Вернее, есть один навык, но совсем не героический и совершенно бесполезный в бою. Называется он «Сетевой супермаркет» и даёт Цуёси доступ к товарам, которые продаются в обычном японском продуктовом магазине.\r\n\r\nКогда Цуёси с его макаронами и колбасой турнули из королевства, он отправился в одиночку исследовать новый мир. Кто мог предположить,что кулинарные таланты Цуёси и продукты из гастронома окажутся так хороши, что привлекут внимание даже легендарного волка Фэру. Покорённый вкусной едой, Фэру заключил с Цуёси контракт и стал его фамильяром. Отныне дуэту из неудавшегося героя, вооружённого сковородкой, и могущественного волка-гурмана открыты все просторы мира.",
                "studios": [
                {
                    "name": "MAPPA",
                    "imageUrl": "https://desu.shikimori.one/system/studios/original/569.png?1351013196"
                }
                ]
            },
            {
                "id": "57025",
                "name": "Tondemo Skill de Isekai Hourou Meshi 2nd Season",
                "russian": "Кулинарные скитания в параллельном мире 2",
                "rating": "pg_13",
                "status": "anons",
                "score": 0,
                "poster": {
                "originalUrl": "https://desu.shikimori.one/uploads/poster/animes/57025/3d0e8aa4d2c6f2374c40711d2bcb1f15.jpeg"
                },
                "genres": [
                {
                    "russian": "Приключения"
                },
                {
                    "russian": "Комедия"
                },
                {
                    "russian": "Фэнтези"
                },
                {
                    "russian": "Гурман"
                },
                {
                    "russian": "Исэкай"
                }
                ],
                "description": null,
                "studios": []
            }
            ]
        }
    }
    ```
2. При использовании функции `deep_search` модуля `ShikimoriParser`
    ```python
    parser = ShikimoriParser()
    parser.deep_search(
        title='Кулинарные скитания',
        search_parameters={
            'limit': 2
        },
        return_parameters={
            'id',
            'name',
            'russian',
            'rating',
            'status',
            'score',
            'poster { originalUrl }',
            'genres { russian }',
            'description',
            'studios { name imageUrl }'
        }
    )
    ```
    Результат:
    ```json
    [
        {
            "score": 7.66,
            "description": "Очередное королевство оказалось не в состоянии самостоятельно справиться с постигшими его проблемами и решило положиться на силу призванных иномирцев. Одного показалось маловато, поэтому с помощью ритуала перенесли сразу четырёх героев. Среди них затесался и 27-летний Цуёси Мукода. Вот только вскоре выяснилось, что его переместили в этот мир по ошибке. Никаких чудесных способностей у него, как не было, так и нет. Вернее, есть один навык, но совсем не героический и совершенно бесполезный в бою. Называется он «Сетевой супермаркет» и даёт Цуёси доступ к товарам, которые продаются в обычном японском продуктовом магазине.\r\n\r\nКогда Цуёси с его макаронами и колбасой турнули из королевства, он отправился в одиночку исследовать новый мир. Кто мог предположить,что кулинарные таланты Цуёси и продукты из гастронома окажутся так хороши, что привлекут внимание даже легендарного волка Фэру. Покорённый вкусной едой, Фэру заключил с Цуёси контракт и стал его фамильяром. Отныне дуэту из неудавшегося героя, вооружённого сковородкой, и могущественного волка-гурмана открыты все просторы мира.",
            "name": "Tondemo Skill de Isekai Hourou Meshi",
            "id": "53446",
            "genres": [
                {
                    "russian": "Приключения"
                },
                {
                    "russian": "Комедия"
                },
                {
                    "russian": "Фэнтези"
                },
                {
                    "russian": "Гурман"
                },
                {
                    "russian": "Исэкай"
                }
            ],
            "poster": {
                "originalUrl": "https://desu.shikimori.one/uploads/poster/animes/53446/558a04d14c503e52cb0a05f8cb117363.jpeg"
            },
            "studios": [
                {
                    "name": "MAPPA",
                    "imageUrl": "https://desu.shikimori.one/system/studios/original/569.png?1351013196"
                }
            ],
            "status": "released",
            "russian": "Кулинарные скитания в параллельном мире",
            "rating": "pg_13"
        },
        {
            "score": 0,
            "description": null,
            "name": "Tondemo Skill de Isekai Hourou Meshi 2nd Season",
            "id": "57025",
            "genres": [
                {
                    "russian": "Приключения"
                },
                {
                    "russian": "Комедия"
                },
                {
                    "russian": "Фэнтези"
                },
                {
                    "russian": "Гурман"
                },
                {
                    "russian": "Исэкай"
                }
            ],
            "poster": {
                "originalUrl": "https://desu.shikimori.one/uploads/poster/animes/57025/3d0e8aa4d2c6f2374c40711d2bcb1f15.jpeg"
            },
            "studios": [],
            "status": "anons",
            "russian": "Кулинарные скитания в параллельном мире 2",
            "rating": "pg_13"
        }
    ]
    ```