from src.anime_parsers_ru import AnimegoParserAsync, AnimegoParser, errors
from time import sleep

def sync_test(proxy: str | None = None, mirror: str | None = None, use_lxml: bool = False, delay: float | int = 2.0):

    try_errors = 0
    try_succes = 0

    parser = AnimegoParser(mirror, proxy, use_lxml=use_lxml)

    try:
        data = parser.search("Наруто")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]['id']) != str:
            raise AssertionError(f'id is not str. id: {data[0]['id']}')
        if type(data[0]['image']) != str:
            raise AssertionError(f'image is not str. image: {data[0]['image']}')
        if type(data[0]['link']) != str:
            raise AssertionError(f'link is not str. link: {data[0]['link']}')
        if type(data[0]['title']) != str:
            raise AssertionError(f'title is not str. link: {data[0]['title']}')
    except Exception as ex:
        print(f'[FAIL] search Наруто. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] search Наруто")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.search("Кулинарные скитания")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]['id']) != str:
            raise AssertionError(f'id is not str. id: {data[0]['id']}')
        if type(data[0]['image']) != str:
            raise AssertionError(f'image is not str. image: {data[0]['image']}')
        if type(data[0]['link']) != str:
            raise AssertionError(f'link is not str. link: {data[0]['link']}')
        if type(data[0]['title']) != str:
            raise AssertionError(f'title is not str. link: {data[0]['title']}')
    except Exception as ex:
        print(f'[FAIL] search Кулинарные скитания. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] search Кулинарные скитания")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_voices('3132')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['total_episodes']) != int:
            raise AssertionError(f'total_episodes is not int. total_episodes: {data['total_episodes']}')
        if type(data['voices']) != list:
            raise AssertionError(f'voices is not list. voices: {data['voices']}')
    except Exception as ex:
        print(f'[FAIL] get_voices 3132. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_voices 3132")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_voices('3122')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['total_episodes'] != None:
            raise AssertionError(f'total_episodes is not None. total_episodes: {data['total_episodes']}')
        if type(data['voices']) != list:
            raise AssertionError(f'voices is not list. voices: {data['voices']}')
    except Exception as ex:
        print(f'[FAIL] get_voices 3122. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_voices 3122")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.aniboom_get_stream_for_voice('95', 1, '3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['url']) != str:
            raise AssertionError(f'No url')
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream_for_voice: 95. Ep: 1. Id: 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] aniboom_get_stream_for_voice: 95. Ep: 1. Id: 3286.")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.aniboom_get_stream_for_voice('95', 3, '3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['url']) != str:
            raise AssertionError(f'No url')
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream_for_voice: 95. Ep: 3. Id: 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] aniboom_get_stream_for_voice: 95. Ep: 3. Id: 3286.")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.aniboom_get_stream_for_voice('14', 1, '3286')
    except errors.UnexpectedBehavior:
        print("[OK] no data for aniboom_get_stream_for_voice: 14. Ep: 1. Id: 3286.")
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream_for_voice: 14. Ep: 1. Id: 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[FAIL] Unexpected data for aniboom_get_stream_for_voice: 14. Ep: 1. Id: 3286. Expected exception but got data.")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.aniboom_get_stream('https://aniboom.one/embed/Z61MpLQMrx4?episode=3&translation=41&parent=https%3A%2F%2Fanimego.me%2Fanime%2Fdobro-pozhalovat-v-klass-prevoskhodstva-4-vtoroi-god-pervyi-semestr-3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['url']) != str:
            raise AssertionError(f'No url')
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:        
        print("[OK] aniboom_get_stream.")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.cvh_get_playlist('59708')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        season = list(data.keys())[0]
        if type(season) != int:
            raise AssertionError(f'season number is not int. Actual season number: {season}')
        episode = list(data[season].keys())[0]
        if type(episode) != int:
            raise AssertionError(f'episode number is not int. Actual episode number: {episode}')
        if type(data[season][episode][0]['vkId']) != str:
            raise AssertionError(f'vkId is not str. Actual vkId: {data[season][episode]["vkId"]}')
        if type(data[season][episode][0]['voiceStudio']) != str:
            raise AssertionError(f'voiceStudio is not str. Actual voiceStudio: {data[season][episode]["voiceStudio"]}')
    except Exception as ex:
        print(f'[FAIL] cvh_get_playlist. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] cvh_get_playlist.")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.cvh_get_stream('59708', 2, 4, 'AnimeVost')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['HLS'] == None and data['DASH'] == None and len(data['MP4s']) == 0:
            raise AssertionError(f'Got no data but exception NoResults was not triggered')
    except Exception as ex:
        print(f'[FAIL] cvh_get_stream. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:        
        print("[OK] cvh_get_stream.")
        try_succes += 1
    sleep(delay)

    try:
        data = parser.cvh_get_stream_by_id('13026642254576')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['HLS'] is None and data['MPD'] is None and len(data['MP4s']) == 0:
            raise AssertionError(f'Got no data but exception NoResults was not triggered')
    except Exception as ex:
        print(f'[FAIL] cvh_get_stream_by_id. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:        
        print("[OK] cvh_get_stream_by_id.")
        try_succes += 1
    sleep(delay)
    
    try:
        data = parser.anime_info('https://animego.me/anime/kulinarnyye-skitaniya-v-parallel-nom-mire-2-3261')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 3261. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 3261')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.anime_info('https://animego.me/anime/boruto-film-naruto-385')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 385. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 385')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.anime_info('https://animego.me/anime/dobro-pozhalovat-v-klass-prevoskhodstva-4-vtoroi-god-pervyi-semestr-3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 3286')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.anime_info('https://animego.me/anime/osvobodite-yetu-ved-mu-3366')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 3366. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 3366')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_episodes_info('3261')
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] episodes_info 3261. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] episodes_info 3261')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_episodes_info('385')
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] episodes_info 385. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] episodes_info 385')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_episodes_info('3286')
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] episodes_info 385. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] episodes_info 385')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_anime_updates()
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_updates. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_updates')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_schedule()
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['schedule']) != dict:
            raise AssertionError(f'data[schedule] is not dict. Actual type: {type(data)}')
        if type(data['schedule_dates']) != dict:
            raise AssertionError(f'data[schedule_dates] is not dict. Actual type: {type(data)}')
        if type(data['schedule']['Понедельник']) != list:
            raise AssertionError(f'data[schedule][Понедельник] is not list. Actual type: {type(data)}')
        if type(data['schedule']['Понедельник'][0]) != dict:
            raise AssertionError(f'data[schedule][Понедельник][0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] get_schedule. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] get_schedule')
        try_succes += 1
    sleep(delay)

    try:
        data = parser.get_anime_from_current_season()
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] get_anime_from_current_season. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] get_anime_from_current_season')
        try_succes += 1
    sleep(delay)

    return (try_errors, try_succes)

async def async_test(proxy: str | None = None, mirror: str | None = None, use_lxml: bool = False, delay: float | int = 2.0):
    try_errors = 0
    try_succes = 0

    parser = AnimegoParserAsync(mirror, proxy, use_lxml=use_lxml)

    try:
        data = await parser.search("Наруто")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]['id']) != str:
            raise AssertionError(f'id is not str. id: {data[0]['id']}')
        if type(data[0]['image']) != str:
            raise AssertionError(f'image is not str. image: {data[0]['image']}')
        if type(data[0]['link']) != str:
            raise AssertionError(f'link is not str. link: {data[0]['link']}')
        if type(data[0]['title']) != str:
            raise AssertionError(f'title is not str. link: {data[0]['title']}')
    except Exception as ex:
        print(f'[FAIL] search Наруто. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] search Наруто")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.search("Кулинарные скитания")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]['id']) != str:
            raise AssertionError(f'id is not str. id: {data[0]['id']}')
        if type(data[0]['image']) != str:
            raise AssertionError(f'image is not str. image: {data[0]['image']}')
        if type(data[0]['link']) != str:
            raise AssertionError(f'link is not str. link: {data[0]['link']}')
        if type(data[0]['title']) != str:
            raise AssertionError(f'title is not str. link: {data[0]['title']}')
    except Exception as ex:
        print(f'[FAIL] search Кулинарные скитания. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] search Кулинарные скитания")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_voices('3132')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['total_episodes']) != int:
            raise AssertionError(f'total_episodes is not int. total_episodes: {data['total_episodes']}')
        if type(data['voices']) != list:
            raise AssertionError(f'voices is not list. voices: {data['voices']}')
    except Exception as ex:
        print(f'[FAIL] get_voices 3132. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_voices 3132")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_voices('3122')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['total_episodes'] != None:
            raise AssertionError(f'total_episodes is not None. total_episodes: {data['total_episodes']}')
        if type(data['voices']) != list:
            raise AssertionError(f'voices is not list. voices: {data['voices']}')
    except Exception as ex:
        print(f'[FAIL] get_voices 3122. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_voices 3122")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.aniboom_get_stream_for_voice('95', 1, '3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['url']) != str:
            raise AssertionError(f'No url')
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream_for_voice: 95. Ep: 1. Id: 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] aniboom_get_stream_for_voice: 95. Ep: 1. Id: 3286.")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.aniboom_get_stream_for_voice('95', 3, '3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['url']) != str:
            raise AssertionError(f'No url')
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream_for_voice: 95. Ep: 3. Id: 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] aniboom_get_stream_for_voice: 95. Ep: 3. Id: 3286.")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.aniboom_get_stream_for_voice('14', 1, '3286')
    except errors.UnexpectedBehavior:
        print("[OK] no data for aniboom_get_stream_for_voice: 14. Ep: 1. Id: 3286.")
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream_for_voice: 14. Ep: 1. Id: 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[FAIL] Unexpected data for aniboom_get_stream_for_voice: 14. Ep: 1. Id: 3286. Expected exception but got data.")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.aniboom_get_stream('https://aniboom.one/embed/Z61MpLQMrx4?episode=3&translation=41&parent=https%3A%2F%2Fanimego.me%2Fanime%2Fdobro-pozhalovat-v-klass-prevoskhodstva-4-vtoroi-god-pervyi-semestr-3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['url']) != str:
            raise AssertionError(f'No url')
    except Exception as ex:
        print(f'[FAIL] aniboom_get_stream. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:        
        print("[OK] aniboom_get_stream.")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.cvh_get_playlist('59708')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        season = list(data.keys())[0]
        if type(season) != int:
            raise AssertionError(f'season number is not int. Actual season number: {season}')
        episode = list(data[season].keys())[0]
        if type(episode) != int:
            raise AssertionError(f'episode number is not int. Actual episode number: {episode}')
        if type(data[season][episode][0]['vkId']) != str:
            raise AssertionError(f'vkId is not str. Actual vkId: {data[season][episode]["vkId"]}')
        if type(data[season][episode][0]['voiceStudio']) != str:
            raise AssertionError(f'voiceStudio is not str. Actual voiceStudio: {data[season][episode]["voiceStudio"]}')
    except Exception as ex:
        print(f'[FAIL] cvh_get_playlist. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] cvh_get_playlist.")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.cvh_get_stream('59708', 2, 4, 'AnimeVost')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['HLS'] == None and data['DASH'] == None and len(data['MP4s']) == 0:
            raise AssertionError(f'Got no data but exception NoResults was not triggered')
    except Exception as ex:
        print(f'[FAIL] cvh_get_stream. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:        
        print("[OK] cvh_get_stream.")
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.cvh_get_stream_by_id('13026642254576')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['HLS'] is None and data['MPD'] is None and len(data['MP4s']) == 0:
            raise AssertionError(f'Got no data but exception NoResults was not triggered')
    except Exception as ex:
        print(f'[FAIL] cvh_get_stream_by_id. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:        
        print("[OK] cvh_get_stream_by_id.")
        try_succes += 1
    sleep(delay)
    
    try:
        data = await parser.anime_info('https://animego.me/anime/kulinarnyye-skitaniya-v-parallel-nom-mire-2-3261')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 3261. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 3261')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.anime_info('https://animego.me/anime/boruto-film-naruto-385')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 385. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 385')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.anime_info('https://animego.me/anime/dobro-pozhalovat-v-klass-prevoskhodstva-4-vtoroi-god-pervyi-semestr-3286')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 3286. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 3286')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.anime_info('https://animego.me/anime/osvobodite-yetu-ved-mu-3366')
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_info 3366. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_info 3366')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_episodes_info('3261')
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] episodes_info 3261. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] episodes_info 3261')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_episodes_info('385')
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] episodes_info 385. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] episodes_info 385')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_episodes_info('3286')
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] episodes_info 385. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] episodes_info 385')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_anime_updates()
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] anime_updates. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] anime_updates')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_schedule()
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['schedule']) != dict:
            raise AssertionError(f'data[schedule] is not dict. Actual type: {type(data)}')
        if type(data['schedule_dates']) != dict:
            raise AssertionError(f'data[schedule_dates] is not dict. Actual type: {type(data)}')
        if type(data['schedule']['Понедельник']) != list:
            raise AssertionError(f'data[schedule][Понедельник] is not list. Actual type: {type(data)}')
        if type(data['schedule']['Понедельник'][0]) != dict:
            raise AssertionError(f'data[schedule][Понедельник][0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] get_schedule. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] get_schedule')
        try_succes += 1
    sleep(delay)

    try:
        data = await parser.get_anime_from_current_season()
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if type(data[0]) != dict:
            raise AssertionError(f'data[0] is not dict. Actual type: {type(data)}')
    except Exception as ex:
        print(f'[FAIL] get_anime_from_current_season. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[OK] get_anime_from_current_season')
        try_succes += 1
    sleep(delay)

    await parser.close()
    return (try_errors, try_succes)
    