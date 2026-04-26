from src.anime_parsers_ru import ShikimoriParser, ShikimoriParserAsync, errors
from time import sleep
import asyncio

def sync_test(delay: float, GLOBAL_USE_LXML: bool = False, mirror: str | None = None, proxy: str | None = None):
    from src.anime_parsers_ru import ShikimoriParser

    try_errors = 0

    parser = ShikimoriParser(GLOBAL_USE_LXML, mirror=mirror, proxy=proxy)

    try:
        data = parser.search("Кулинарные скитания")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Кулинарные скитания". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Кулинарные скитания"')
    sleep(delay)

    try:
        data = parser.search("Наруто")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Наруто". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Наруто"')
    sleep(delay)

    try:
        data = parser.search("Класс превосходства")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Класс превосходства". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Класс превосходства"')
    sleep(delay)

    try:
        data = parser.search("Клинок рассекающий демонов")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Клинок рассекающий демонов". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Клинок рассекающий демонов"')
    sleep(delay)

    try:
        data = parser.anime_info('https://shikimori.one/animes/z20-naruto')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "z20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "z20"')
    sleep(delay)

    try:
        data = parser.anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "53446". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "53446"')
    sleep(delay)

    try:
        data = parser.anime_info('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "58426". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "58426"')
    sleep(delay)
    
    try:
        data = parser.anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "z40456"')
    sleep(delay)

    try:
        data = parser.anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "z40456"')
    sleep(delay)

    # Проверка на ограничение по возрасту (все поудаляли, не актуально)
    """
    try:
        data = parser.anime_info('https://shikimori.one/animes/53725-class-de-otoko-wa-boku-ichinin')
    except errors.AgeRestricted:
        print('[OK] Info "53725". AgeRestricted block works')
    except Exception as ex:
        print(f'[FAIL] Info "53725". Непредвиденная ошибка "{ex}". Ожидалось: "AgeRestricted"')
        try_errors += 1
    else:
        print('[FAIL] Info "53725". Обработка ограниченного по возрасту аниме не вернуло ошибку. Ожидалось: "AgeRestricted"')
    sleep(delay)
    """    
    
    try:
        data = parser.additional_anime_info('https://shikimori.one/animes/z20-naruto')
        if type(data) != dict:
            raise AssertionError
        if len(data['related']) == 0:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Additional info "z20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Additional info "z20"')
    sleep(delay)

    try:
        data = parser.additional_anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Additional info "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Additional info "z40456"')
    sleep(delay)

    try:
        data = parser.additional_anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        if type(data) != dict:
            raise AssertionError
        if len(data['main_characters']) == 0:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Additional info "53446". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Additional info "53446"')
    sleep(delay)

    try:
        data = parser.link_by_id('20') # Наруто (реальный id - z20)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "20"')
    sleep(delay)
    
    try:
        data = parser.link_by_id('40456') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "40456"')
    sleep(delay)
    
    try:
        data = parser.link_by_id('58426') # Моя подруга-олениха Нокотан (реальный id - 58426)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "58426". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "58426"')
    sleep(delay)

    try:
        data = parser.link_by_id('53446') # Кулинарные скитания в параллельном мире (реальный id - 53446)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "53446". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "53446"')
    sleep(delay)

    try:
        data = parser.id_by_link('https://shikimori.one/animes/z20-naruto') # Наруто (реальный id - z20 ожидаем - 20)
        if type(data) != str:
            raise AssertionError
        if data != "20":
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Id by link "z20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Id by link "z20"')
    sleep(delay)

    try:
        data = parser.id_by_link('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456 ожидаем - 40456)
        if type(data) != str:
            raise AssertionError
        if data != "40456":
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Id by link "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Id by link "z40456"')
    sleep(delay)

    try:
        data = parser.id_by_link('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan') # Моя подруга-олениха Нокотан (реальный id - 58426 ожидаем - 58426)
        if type(data) != str:
            raise AssertionError
        if data != "58426":
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Id by link "58426". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Id by link "58426"')
    sleep(delay)

    try:
        data = parser.get_anime_list()
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list')
    sleep(delay)

    try:
        data = parser.get_anime_list(status=['ongoing'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list ongoing. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list ongoing')
    sleep(delay)

    try:
        data = parser.get_anime_list(status=['released'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list released. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list released')
    sleep(delay)

    try:
        data = parser.get_anime_list(status=['released', 'ongoing'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list released & ongoing. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list released & ongoing')
    sleep(delay)

    try:
        data = parser.get_anime_list(anime_type=['tv'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type tv. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type tv')
    sleep(delay)

    try:
        data = parser.get_anime_list(anime_type=['movie'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'Фильм':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type movie. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type movie')
    sleep(delay)

    try:
        data = parser.get_anime_list(anime_type=['movie', 'tv'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'Фильм' and data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type movie | tv. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type movie | tv')
    sleep(delay)

    try:
        data = parser.get_anime_list(status=['ongoing'], anime_type=['tv'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type ongoing tv. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type ongoing tv')
    sleep(delay)

    try:
        data = parser.get_anime_list(status=['ongoing'], anime_type=['tv'], start_page=3, page_limit=2, sort_by='popularity')
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type ongoing tv with pages and sort. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type ongoing tv with pages and sort')
    sleep(delay)

    try:
        data = parser.get_anime_list(status=['ongoing'], anime_type=['tv'], rating='pg_13', genres=['2-Adventure'], start_page=1, page_limit=2, sort_by='popularity')
        if len(data) == 0:
            raise AssertionError("Len data == 0")
        if type(data) != list:
            raise AssertionError(f"typeof data != list. Type: {type(data)}")
        if type(data[0]) != dict:
            raise AssertionError(f"typeof data[0] != dict. Type: {type(data[0])}")
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError(f"data[0]['type'] != TV Сериал. ->: {data[0]['type']}")
    except Exception as ex:
        print(f'[FAIL] Anime list type ongoing tv with pages, sort, pg rating, genres. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type ongoing tv with pages, sort, pg rating, genres')
    sleep(delay)

    try:
        data = parser.deep_search('Кулинарные скитания', {}, ['id', 'name', 'url', 'genres { name russian }'])
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Deep search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Deep search')
    sleep(delay)

    try:
        data = parser.deep_anime_info('53446', ['id', 'name', 'url', 'genres { name russian }'])
        if type(data) != dict:
            raise AssertionError
        if type(data['name']) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Deep info. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Deep info')
    sleep(delay)

    try: # Проверка на несуществующем id
        data = parser.deep_anime_info('fff', ['id', 'name', 'url', 'genres { name russian }'])
        if type(data) != dict:
            raise AssertionError
        if type(data['name']) != str:
            raise AssertionError
    except errors.NoResults:
        print('[OK] Deep info with unknown id')
    except Exception as ex:
        print(f'[FAIL] Deep info with unknown id. Exception: {ex}')
        try_errors += 1
    else:
        print(f'[FAIL] Deep info with unknown id. Expected NoResults exception but no exception was triggered')
    sleep(delay)

    return try_errors

async def async_test(delay: float, GLOBAL_USE_LXML: bool = False, mirror: str | None = None, proxy: str | None = None):
    from src.anime_parsers_ru import ShikimoriParserAsync

    try_errors = 0

    parser = ShikimoriParserAsync(GLOBAL_USE_LXML, mirror=mirror, proxy=proxy)

    try:
        data = await parser.search("Кулинарные скитания")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Кулинарные скитания". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Кулинарные скитания"')
    sleep(delay)

    try:
        data = await parser.search("Наруто")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Наруто". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Наруто"')
    sleep(delay)

    try:
        data = await parser.search("Класс превосходства")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Класс превосходства". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Класс превосходства"')
    sleep(delay)

    try:
        data = await parser.search("Клинок рассекающий демонов")
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search "Клинок рассекающий демонов". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search "Клинок рассекающий демонов"')
    sleep(delay)

    try:
        data = await parser.anime_info('https://shikimori.one/animes/z20-naruto')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "z20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "z20"')
    sleep(delay)

    try:
        data = await parser.anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "53446". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "53446"')
    sleep(delay)

    try:
        data = await parser.anime_info('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "58426". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "58426"')
    sleep(delay)
    
    try:
        data = await parser.anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "z40456"')
    sleep(delay)

    try:
        data = await parser.anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Info "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Info "z40456"')
    sleep(delay)

    # Проверка на ограничение по возрасту (все поудаляли, не актуально)
    """
    try:
        data = await parser.anime_info('https://shikimori.one/animes/53725-class-de-otoko-wa-boku-ichinin')
    except errors.AgeRestricted:
        print('[OK] Info "53725". AgeRestricted block works')
    except Exception as ex:
        print(f'[FAIL] Info "53725". Непредвиденная ошибка "{ex}". Ожидалось: "AgeRestricted"')
        try_errors += 1
    else:
        print('[FAIL] Info "53725". Обработка ограниченного по возрасту аниме не вернуло ошибку. Ожидалось: "AgeRestricted"')
    sleep(delay)
    """
    try:
        data = await parser.additional_anime_info('https://shikimori.one/animes/z20-naruto')
        if type(data) != dict:
            raise AssertionError
        if len(data['related']) == 0:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Additional info "z20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Additional info "z20"')
    sleep(delay)

    try:
        data = await parser.additional_anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        if type(data) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Additional info "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Additional info "z40456"')
    sleep(delay)

    try:
        data = await parser.additional_anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        if type(data) != dict:
            raise AssertionError
        if len(data['main_characters']) == 0:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Additional info "53446". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Additional info "53446"')
    sleep(delay)

    try:
        data = await parser.link_by_id('20') # Наруто (реальный id - z20)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "20"')
    sleep(delay)
    
    try:
        data = await parser.link_by_id('40456') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "40456"')
    sleep(delay)
    
    try:
        data = await parser.link_by_id('58426') # Моя подруга-олениха Нокотан (реальный id - 58426)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "58426". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "58426"')
    sleep(delay)

    try:
        data = await parser.link_by_id('53446') # Кулинарные скитания в параллельном мире (реальный id - 53446)
        if type(data) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Link by id "53446". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Link by id "53446"')
    sleep(delay)

    try:
        data = parser.id_by_link('https://shikimori.one/animes/z20-naruto') # Наруто (реальный id - z20 ожидаем - 20)
        if type(data) != str:
            raise AssertionError
        if data != "20":
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Id by link "z20". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Id by link "z20"')
    sleep(delay)

    try:
        data = parser.id_by_link('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456 ожидаем - 40456)
        if type(data) != str:
            raise AssertionError
        if data != "40456":
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Id by link "z40456". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Id by link "z40456"')
    sleep(delay)

    try:
        data = parser.id_by_link('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan') # Моя подруга-олениха Нокотан (реальный id - 58426 ожидаем - 58426)
        if type(data) != str:
            raise AssertionError
        if data != "58426":
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Id by link "58426". Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Id by link "58426"')
    sleep(delay)

    try:
        data = await parser.get_anime_list()
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list')
    sleep(delay)

    try:
        data = await parser.get_anime_list(status=['ongoing'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list ongoing. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list ongoing')
    sleep(delay)

    try:
        data = await parser.get_anime_list(status=['released'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list released. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list released')
    sleep(delay)

    try:
        data = await parser.get_anime_list(status=['released', 'ongoing'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list released & ongoing. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list released & ongoing')
    sleep(delay)

    try:
        data = await parser.get_anime_list(anime_type=['tv'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type tv. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type tv')
    sleep(delay)

    try:
        data = await parser.get_anime_list(anime_type=['movie'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'Фильм':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type movie. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type movie')
    sleep(delay)

    try:
        data = await parser.get_anime_list(anime_type=['movie', 'tv'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'Фильм' and data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type movie | tv. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type movie | tv')
    sleep(delay)

    try:
        data = await parser.get_anime_list(status=['ongoing'], anime_type=['tv'])
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type ongoing tv. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type ongoing tv')
    sleep(delay)

    try:
        data = await parser.get_anime_list(status=['ongoing'], anime_type=['tv'], start_page=3, page_limit=2, sort_by='popularity')
        if len(data) == 0:
            raise AssertionError
        if type(data) != list:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Anime list type ongoing tv with pages and sort. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type ongoing tv with pages and sort')
    sleep(delay)

    try:
        data = await parser.get_anime_list(status=['ongoing'], anime_type=['tv'], rating='pg_13', genres=['2-Adventure'], start_page=1, page_limit=2, sort_by='popularity')
        if len(data) == 0:
            raise AssertionError("Len data == 0")
        if type(data) != list:
            raise AssertionError(f"typeof data != list. Type: {type(data)}")
        if type(data[0]) != dict:
            raise AssertionError(f"typeof data[0] != dict. Type: {type(data[0])}")
        if data[0]['type'] != 'TV Сериал':
            raise AssertionError(f"data[0]['type'] != TV Сериал. ->: {data[0]['type']}")
    except Exception as ex:
        print(f'[FAIL] Anime list type ongoing tv with pages, sort, pg rating, genres. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Anime list type ongoing tv with pages, sort, pg rating, genres')
    sleep(delay)

    try:
        data = await parser.deep_search('Кулинарные скитания', {}, ['id', 'name', 'url', 'genres { name russian }'])
        if type(data) != list:
            raise AssertionError
        if len(data) == 0:
            raise AssertionError
        if type(data[0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Deep search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Deep search')
    sleep(delay)

    try:
        data = await parser.deep_anime_info('53446', ['id', 'name', 'url', 'genres { name russian }'])
        if type(data) != dict:
            raise AssertionError
        if type(data['name']) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Deep info. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Deep info')
    sleep(delay)

    try: # Проверка на несуществующем id
        data = await parser.deep_anime_info('fff', ['id', 'name', 'url', 'genres { name russian }'])
        if type(data) != dict:
            raise AssertionError
        if type(data['name']) != str:
            raise AssertionError
    except errors.NoResults:
        print('[OK] Deep info with unknown id')
    except Exception as ex:
        print(f'[FAIL] Deep info with unknown id. Exception: {ex}')
        try_errors += 1
    else:
        print(f'[FAIL] Deep info with unknown id. Expected NoResults exception but no exception was triggered')
    sleep(delay)

    parser.close_async_session()
    return try_errors