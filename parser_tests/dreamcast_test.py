from src.anime_parsers_ru import DreamcastParserAsync, DreamcastParser, errors
from time import sleep
import asyncio
import base64
import json


def _playerjs_page(config: dict) -> str:
    """Страница с плеером как у DreamCast: base64 настроек с мусорными вставками, одна вложена в другую."""
    data = base64.b64encode(json.dumps(config).encode()).decode()
    junks = ["//" + base64.b64encode((ch * 64).encode()).decode() for ch in "ABC"]
    data = data[:10] + junks[0] + data[10:40] + junks[1] + data[40:]
    data = data[:20] + junks[2] + data[20:] # Вставка внутри первой вставки
    return f'<script>var pjs = new Playerjs("#2{data}");</script>'


def sync_test(proxy: str | None = None, mirror: str | None = None, use_lxml: bool = False, delay: float | int = 2.0):

    try_errors = 0
    try_success = 0

    parser = DreamcastParser(mirror, proxy, use_lxml=use_lxml)

    try:
        config = {"file": [{"title": "Серия 1", "file": "https://a/b.mpd or https://a/b.m3u8"}]}
        data = DreamcastParser.decode_player(_playerjs_page(config))
        if data != config:
            raise AssertionError(f'decoded config is not expected. Actual: {data}')
    except Exception as ex:
        print(f'[FAIL] decode_player (offline). Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] decode_player (offline)")
        try_success += 1

    try:
        data = parser.search("Sousou no Frieren")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if not any(x['slug'] == '209-sousou-no-frieren' for x in data):
            raise AssertionError(f'209-sousou-no-frieren not in results. Actual: {[x["slug"] for x in data]}')
        if type(data[0]['id']) != str:
            raise AssertionError(f'id is not str. id: {data[0]["id"]}')
        if type(data[0]['link']) != str:
            raise AssertionError(f'link is not str. link: {data[0]["link"]}')
        if type(data[0]['title']) != str:
            raise AssertionError(f'title is not str. title: {data[0]["title"]}')
        if type(data[0]['genres']) != list:
            raise AssertionError(f'genres is not list. genres: {data[0]["genres"]}')
    except Exception as ex:
        print(f'[FAIL] search Sousou no Frieren. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] search Sousou no Frieren")
        try_success += 1
    sleep(delay)

    try:
        parser.search("zzqqxxzzqqxx")
    except errors.NoResults:
        print("[OK] search no results")
        try_success += 1
    except Exception as ex:
        print(f'[FAIL] search no results. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[FAIL] search no results. Expected errors.NoResults')
        try_errors += 1
    sleep(delay)

    try:
        data = parser.anime_info("https://dreamerscast.com/home/release/209-sousou-no-frieren")
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if data['title'] != 'Провожающая в последний путь Фрирен':
            raise AssertionError(f'title is not expected. Actual: {data["title"]}')
        if data['original_title'] != 'Sousou no Frieren':
            raise AssertionError(f'original_title is not expected. Actual: {data["original_title"]}')
        if data['year'] != 2023:
            raise AssertionError(f'year is not expected. Actual: {data["year"]}')
        if data['episodes'] != 28:
            raise AssertionError(f'episodes is not expected. Actual: {data["episodes"]}')
        if type(data['voice_actors']) != list or len(data['voice_actors']) == 0:
            raise AssertionError(f'voice_actors is empty. Actual: {data["voice_actors"]}')
        if type(data['description']) != str or len(data['description']) == 0:
            raise AssertionError(f'description is empty')
    except Exception as ex:
        print(f'[FAIL] anime_info 209-sousou-no-frieren. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] anime_info 209-sousou-no-frieren")
        try_success += 1
    sleep(delay)

    try:
        data = parser.get_episodes("209-sousou-no-frieren")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if len(data) != 28:
            raise AssertionError(f'len(data) != 28. Actual: {len(data)}')
        if [x['episode'] for x in data] != list(range(1, 29)):
            raise AssertionError(f'episodes are not 1..28. Actual: {[x["episode"] for x in data]}')
        if not data[0]['hls'].endswith('.m3u8'):
            raise AssertionError(f'hls is not m3u8. hls: {data[0]["hls"]}')
    except Exception as ex:
        print(f'[FAIL] get_episodes 209-sousou-no-frieren. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_episodes 209-sousou-no-frieren")
        try_success += 1
    sleep(delay)

    try:
        data = parser.get_stream("120-o-moiom-pererozhdenii-v-mech-tensei-shitara-ken-deshita", 12)
        if type(data) != dict:
            raise AssertionError(f'data is not dict. Actual type: {type(data)}')
        if type(data['HLS']) != str:
            raise AssertionError(f'HLS is not str. HLS: {data["HLS"]}')
        qualities = parser.get_qualities(data['HLS'])
        if type(qualities) != dict or '1080' not in qualities:
            raise AssertionError(f'1080 not in qualities. Actual: {qualities}')
    except Exception as ex:
        print(f'[FAIL] get_stream + get_qualities. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_stream + get_qualities")
        try_success += 1
    sleep(delay)

    try:
        parser.get_stream("209-sousou-no-frieren", 999)
    except errors.NoResults:
        print("[OK] get_stream no episode")
        try_success += 1
    except Exception as ex:
        print(f'[FAIL] get_stream no episode. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[FAIL] get_stream no episode. Expected errors.NoResults')
        try_errors += 1

    try:
        parser.get_episodes("https://example.com/home/release/209-sousou-no-frieren")
    except errors.PostArgumentsError:
        print("[OK] get_episodes foreign link")
        try_success += 1
    except Exception as ex:
        print(f'[FAIL] get_episodes foreign link. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[FAIL] get_episodes foreign link. Expected errors.PostArgumentsError')
        try_errors += 1
    sleep(delay)

    return (try_errors, try_success)


async def async_test(proxy: str | None = None, mirror: str | None = None, use_lxml: bool = False, delay: float | int = 2.0):

    try_errors = 0
    try_success = 0

    parser = DreamcastParserAsync(mirror, proxy, use_lxml=use_lxml)

    try:
        data = await parser.search("Sousou no Frieren")
        if type(data) != list:
            raise AssertionError(f'data is not list. Actual type: {type(data)}')
        if not any(x['slug'] == '209-sousou-no-frieren' for x in data):
            raise AssertionError(f'209-sousou-no-frieren not in results. Actual: {[x["slug"] for x in data]}')
    except Exception as ex:
        print(f'[FAIL] search Sousou no Frieren. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] search Sousou no Frieren")
        try_success += 1
    await asyncio.sleep(delay)

    try:
        data = await parser.anime_info("209-sousou-no-frieren")
        if data['title'] != 'Провожающая в последний путь Фрирен':
            raise AssertionError(f'title is not expected. Actual: {data["title"]}')
        if data['episodes'] != 28:
            raise AssertionError(f'episodes is not expected. Actual: {data["episodes"]}')
    except Exception as ex:
        print(f'[FAIL] anime_info 209-sousou-no-frieren. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] anime_info 209-sousou-no-frieren")
        try_success += 1
    await asyncio.sleep(delay)

    try:
        data = await parser.get_episodes("209-sousou-no-frieren")
        if len(data) != 28:
            raise AssertionError(f'len(data) != 28. Actual: {len(data)}')
        stream = await parser.get_stream("209-sousou-no-frieren", 1)
        if stream['HLS'] != data[0]['hls']:
            raise AssertionError(f'get_stream HLS != get_episodes hls')
        qualities = await parser.get_qualities(stream['HLS'])
        if '1080' not in qualities:
            raise AssertionError(f'1080 not in qualities. Actual: {qualities}')
    except Exception as ex:
        print(f'[FAIL] get_episodes + get_stream + get_qualities. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print("[OK] get_episodes + get_stream + get_qualities")
        try_success += 1
    await asyncio.sleep(delay)

    try:
        await parser.get_stream("209-sousou-no-frieren", 999)
    except errors.NoResults:
        print("[OK] get_stream no episode")
        try_success += 1
    except Exception as ex:
        print(f'[FAIL] get_stream no episode. Exception: {ex}. Exception type: {type(ex)}')
        try_errors += 1
    else:
        print('[FAIL] get_stream no episode. Expected errors.NoResults')
        try_errors += 1

    await parser.close()
    return (try_errors, try_success)
