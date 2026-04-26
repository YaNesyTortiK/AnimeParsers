from src.anime_parsers_ru import JutsuParser
from time import sleep

def sync_test(delay: float, GLOBAL_USE_LXML: bool = False, proxy: str | None = None):
    from src.anime_parsers_ru import JutsuParser
    import src.anime_parsers_ru.errors as errors

    try_errors = 0

    parser = JutsuParser(GLOBAL_USE_LXML, proxy=proxy)

    try: # Проверка на аниме с одним сезоном
        data = parser.get_anime_info('https://jut.su/life-no-game/') # Нет игры - нет жизни (когда-нибудь он не будет подходить под определение одного сезона... :copium:)
        if type(data) != dict:
            raise AssertionError(f"Typeof data != dict. Actual: {type(data)}")
        if type(data['seasons']) != list:
            raise AssertionError(f"Typeof data['seasons'] != list. Actual: {type(data['seasons'])}")
        if data['title'] != 'Нет игры - нет жизни':
            raise AssertionError(f"data['title'] is not expected. Actual: {data['title']}")
        if len(data['seasons']) != 1:
            raise AssertionError(f"data['seasons'] != 1")
        if len(data['seasons_names']) != 0:
            raise AssertionError(f"data['seasons_names'] != 0")
        if type(data['seasons'][0][0]) != str:
            raise AssertionError(f"data['seasons'][0][0] != str")
    except Exception as ex:
        print(f'[FAIL] One season. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] One season')
    sleep(delay)

    try: # Проверка на аниме с несколькими сезонами
        data = parser.get_anime_info('https://jut.su/ookami-to-koshinryou/') # Волчица и пряности
        if type(data) != dict:
            raise AssertionError(f"Typeof data != dict. Actual: {type(data)}")
        if type(data['seasons']) != list:
            raise AssertionError(f"Typeof data['seasons'] != list. Actual: {type(data['seasons'])}")
        if data['title'] != 'Волчица и пряности':
            raise AssertionError(f"data['title'] is not expected. Actual: {data['title']}")
        if len(data['seasons']) == 1:
            raise AssertionError(f"data['seasons'] == 1")
        if len(data['seasons_names']) == 0:
            raise AssertionError(f"data['seasons_names'] == 0")
        if type(data['seasons'][0][0]) != str:
            raise AssertionError(f"data['seasons'][0][0] != str")
    except Exception as ex:
        print(f'[FAIL] Multi season. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Multi season')
    sleep(delay)

    try: # Проверка на аниме с фильмами
        data = parser.get_anime_info('https://jut.su/fullmeetal-alchemist/') # Стальной алхимик
        if type(data) != dict:
            raise AssertionError
        if type(data['seasons']) != list:
            raise AssertionError
        if data['title'] != 'Стальной алхимик':
            raise AssertionError
        if len(data['seasons']) == 1:
            raise AssertionError
        if len(data['seasons_names']) == 0:
            raise AssertionError
        if len(data['films']) == 0:
            raise AssertionError
        if type(data['seasons'][0][0]) != str:
            raise AssertionError
        if type(data['films'][0]) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] Multi season with films. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] Multi season with films')
    sleep(delay)

    try: # Проверка без сезонов
        data = parser.get_mp4_link('https://jut.su/tondemo-skill/episode-1.html') # Кулинарные скитания в параллельном мире 1 серия
        if type(data) != dict:
            raise AssertionError
        if len(data.keys()) == 0:
            raise AssertionError
        if type(data['720']) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get link no seasons. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get link no seasons')
    sleep(delay)

    try: # Проверка с сезонами
        data = parser.get_mp4_link('https://jut.su/ookami-to-koshinryou/season-1/episode-1.html') # Волчица и пряности 1 сезон 1 серия
        if type(data) != dict:
            raise AssertionError
        if len(data.keys()) == 0:
            raise AssertionError
        if type(data['720']) != str:
            raise AssertionError
    except Exception as ex:
        print(f'[FAIL] get link with seasons. Exception: {ex}')
        try_errors += 1
    else:
        print('[OK] get link with seasons')
    sleep(delay)
    return try_errors