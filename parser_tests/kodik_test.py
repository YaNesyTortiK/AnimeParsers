import unittest
import asyncio
from time import sleep

def api_test(delay: float, TOKEN: str, proxy: str | None = None):
    from src.anime_parsers_ru import KodikList
    from src.anime_parsers_ru import KodikSearch
    from src.anime_parsers_ru.api_kodik import Response, Api

    try_errors = 0
    try_succes = 0

    try:
        s = KodikSearch(token=TOKEN, proxy=proxy).title('Кулинарные скитания').limit(2).with_material_data().with_episodes_data()
        if type(s) != Api:
            raise AssertionError
        data = s.execute()
        if type(data) != Response:
            raise AssertionError
        if len(data.results) == 0:
            raise AssertionError
        if type(data.results[0]) != Response.Element:
            raise AssertionError
        if type(data.results[0].raw_data) != dict:
            raise AssertionError
        if type(data.results[0].translation) != Response.Translation:
            raise AssertionError
        if type(data.results[0].material_data) != Response.MaterialData:
            raise AssertionError
        if type(data.results[0].seasons) != dict:
            raise AssertionError
        r = list(data.results[0].seasons.keys())
        if type(data.results[0].seasons[r[0]]) != Response.Season:
            raise AssertionError
        t = list(data.results[0].seasons[r[0]].episodes.keys())
        if type(data.results[0].seasons[r[0]].episodes[t[0]]) != Response.Season.Episode:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] List. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] List')
        try_succes += 1

    sleep(delay)

    try:
        s = KodikList(token=TOKEN, proxy=proxy).anime_status('ongoing').limit(2).with_material_data().with_episodes_data()
        if type(s) != Api:
            raise AssertionError
        data = s.execute()
        if type(data) != Response:
            raise AssertionError
        if len(data.results) == 0:
            raise AssertionError
        if type(data.results[0]) != Response.Element:
            raise AssertionError
        if type(data.results[0].raw_data) != dict:
            raise AssertionError
        if type(data.results[0].translation) != Response.Translation:
            raise AssertionError
        if type(data.results[0].material_data) != Response.MaterialData:
            raise AssertionError
        if type(data.results[0].seasons) != dict:
            raise AssertionError
        r = list(data.results[0].seasons.keys())
        if type(data.results[0].seasons[r[0]]) != Response.Season:
            raise AssertionError
        t = list(data.results[0].seasons[r[0]].episodes.keys())
        if type(data.results[0].seasons[r[0]].episodes[t[0]]) != Response.Season.Episode:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Search')
        try_succes += 1
    sleep(delay)

    return (try_errors, try_succes)
        

def main_test(delay: float, TOKEN: str, GLOBAL_USE_LXML: bool = False, GLOBAL_TOKEN_VALIDATION: bool = False, proxy: str | None = None):
    from src.anime_parsers_ru import KodikParser
    import src.anime_parsers_ru.errors as errors

    try_errors = 0
    try_succes = 0

    parser = KodikParser(token=TOKEN, use_lxml=GLOBAL_USE_LXML, validate_token=GLOBAL_TOKEN_VALIDATION, proxy=proxy, use_cache=True)

    try:
        goten_token = KodikParser.get_token(proxy)
        if not type(goten_token) == str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Token. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Token')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.base_search('Наруто', limit=2, include_material_data=False)
        if not type(data) == dict:
            raise AssertionError
        if data['total'] == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] base_search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] base_search')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.base_search_by_id('z20', 'shikimori', limit=2, include_material_data=False)
        if not type(data) == dict:
            raise AssertionError
        if data['total'] == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] base_search_by_id. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] base_search_by_id')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_list(limit_per_page=10, pages_to_parse=1, include_material_data=False)
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != list:
            raise AssertionError
        if len(data[0]) <= 0:
            raise AssertionError
        if type(data[0][0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_list. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_list')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.search('Наруто', limit=2, include_material_data=False)
        if not type(data) == list:
            raise AssertionError
        if len(data) == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] search')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.search_by_id('z20', 'shikimori', limit=2)
        if not type(data) == list:
            raise AssertionError
        if len(data) == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] search_by_id. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] search_by_id')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_info('z20', 'shikimori')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info shiki. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info shiki')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_info('283290', 'kinopoisk')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info kinopoisk. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info kinopoisk')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_info('tt0409591', 'imdb')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info imdb. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info imdb')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_info('2472', 'shikimori')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info shiki video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info shiki video')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_info('283418', 'kinopoisk')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info kinopoisk video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info kinopoisk video')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_info('tt0988982', 'imdb')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info imdb video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info imdb video')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_link('z20', 'shikimori', 1, '609')
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != str:
            raise AssertionError
        if type(data[1]) != int:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_link serial. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_link serial')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_link('2472', 'shikimori', 0, '609')
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != str:
            raise AssertionError
        if type(data[1]) != int:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_link video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_link video')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_link('51179', 'shikimori', 0, '609')
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != str:
            raise AssertionError
        if type(data[1]) != int:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_link seria 0. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_link seria 0')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_m3u8_playlist_link('z20', 'shikimori', 1, '609', 480)
        if not type(data) == str:
            raise AssertionError
        if "cloud.solodcdn.com" not in data:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_m3u8_playlist_link. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_m3u8_playlist_link')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_m3u8_playlist('z20', 'shikimori', 1, '609', 480)
        if not type(data) == str:
            raise AssertionError
        if '#EXTM3U' not in data:
            raise AssertionError
        if '.mp4:hls:seg-1-v1-a1.ts' not in data:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_m3u8_playlist. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_m3u8_playlist')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_calendar()
        if not type(data) == list:
            raise AssertionError(f'data is not list. Type: {type(data)}')
        if not type(data[0]) == dict:
            raise AssertionError(f'data[0] is not dict. Type: {type(data[0])}')
    except Exception as ex:
        print(f'[FAIL] get_calendar as class method. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_calendar as class method')
        try_succes += 1
    sleep(delay)

    try:
        data = KodikParser.get_calendar()
        if not type(data) == list:
            raise AssertionError(f'data is not list. Type: {type(data)}')
        if not type(data[0]) == dict:
            raise AssertionError(f'data[0] is not dict. Type: {type(data[0])}')
    except Exception as ex:
        print(f'[FAIL] get_calendar as static method. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_calendar as static method')
        try_succes += 1
    sleep(delay)

    return (try_errors, try_succes)


async def async_test(delay: float, TOKEN: str, GLOBAL_USE_LXML: bool = False, GLOBAL_TOKEN_VALIDATION: bool = False, proxy: str | None = None):
    from src.anime_parsers_ru import KodikParserAsync
    import src.anime_parsers_ru.errors as errors

    try_errors = 0
    try_succes = 0

    parser = KodikParserAsync(token=TOKEN, use_lxml=GLOBAL_USE_LXML, validate_token=GLOBAL_TOKEN_VALIDATION, proxy=proxy, use_cache=True)
    
    try:
        goten_token = parser.get_token_sync(proxy)
        if not type(goten_token) == str:
            raise AssertionError
        goten_token = await parser.get_token(proxy=proxy)
        if not type(goten_token) == str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Token. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Token')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.base_search('Наруто', limit=2, include_material_data=False)
        if not type(data) == dict:
            raise AssertionError
        if data['total'] == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] base_search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] base_search')
        try_succes += 1
    sleep(delay)
    
    try:
        data = await parser.base_search_by_id('z20', 'shikimori', limit=2, include_material_data=False)
        if not type(data) == dict:
            raise AssertionError
        if data['total'] == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] base_search_by_id. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] base_search_by_id')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_list(limit_per_page=10, pages_to_parse=1, include_material_data=False)
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != list:
            raise AssertionError
        if len(data[0]) <= 0:
            raise AssertionError
        if type(data[0][0]) != dict:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_list. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_list')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.search('Наруто', limit=2, include_material_data=False)
        if not type(data) == list:
            raise AssertionError
        if len(data) == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] search. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] search')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.search_by_id('z20', 'shikimori', limit=2)
        if not type(data) == list:
            raise AssertionError
        if len(data) == 0:
            raise errors.NoResults
    except Exception as ex:
        print(f'[FAIL] search_by_id. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] search_by_id')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_info('z20', 'shikimori')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info shiki. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info shiki')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_info('283290', 'kinopoisk')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info kinopoisk. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info kinopoisk')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_info('tt0409591', 'imdb')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info imdb. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info imdb')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_info('2472', 'shikimori')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info shiki video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info shiki video')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_info('283418', 'kinopoisk')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info kinopoisk video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info kinopoisk video')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_info('tt0988982', 'imdb')
        if not type(data) == dict:
            raise AssertionError
        if type(data['series_count']) != int:
            raise AssertionError
        if type(data['translations']) != list:
            raise AssertionError
        if type(data['translations'][0]) != dict:
            raise AssertionError
        if type(data['translations'][0]['series_range']) != tuple:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_info imdb video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_info imdb video')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_link('z20', 'shikimori', 1, '609')
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != str:
            raise AssertionError
        if type(data[1]) != int:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_link serial. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_link serial')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_link('2472', 'shikimori', 0, '609')
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != str:
            raise AssertionError
        if type(data[1]) != int:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_link video. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_link video')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_link('51179', 'shikimori', 0, '609')
        if not type(data) == tuple:
            raise AssertionError
        if type(data[0]) != str:
            raise AssertionError
        if type(data[1]) != int:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_link seria 0. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_link seria 0')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_m3u8_playlist_link('z20', 'shikimori', 1, '609', 480)
        if not type(data) == str:
            raise AssertionError
        if "cloud.solodcdn.com" not in data:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_m3u8_playlist_link. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_m3u8_playlist_link')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_m3u8_playlist('z20', 'shikimori', 1, '609', 480)
        if not type(data) == str:
            raise AssertionError
        if '#EXTM3U' not in data:
            raise AssertionError
        if '.mp4:hls:seg-1-v1-a1.ts' not in data:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get_m3u8_playlist. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_m3u8_playlist')
        try_succes += 1
    sleep(delay)
    
    try:
        data = await parser.get_calendar()
        if not type(data) == list:
            raise AssertionError(f'data is not list. Type: {type(data)}')
        if not type(data[0]) == dict:
            raise AssertionError(f'data[0] is not dict. Type: {type(data[0])}')
    except Exception as ex:
        print(f'[FAIL] get_calendar as class method. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get_calendar as class method')
        try_succes += 1
    sleep(delay)
    
    await parser.close_async_session()
    return (try_errors, try_succes)
