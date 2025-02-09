import unittest
import asyncio

GLOBAL_USE_LXML = False
class TestKodik(unittest.TestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import KodikParser
        import src.anime_parsers_ru.errors as errors

    def test_auto_token(self):
        from src.anime_parsers_ru import KodikParser
        goten_token = KodikParser.get_token()
        self.assertIsInstance(goten_token, str)
    
    def test_init(self):
        from src.anime_parsers_ru import KodikParser
        parser = KodikParser(use_lxml=self.USE_LXML)
    
    def test_base_search(self):
        from src.anime_parsers_ru import KodikParser
        import src.anime_parsers_ru.errors as errors
        parser = KodikParser(use_lxml=self.USE_LXML)
        search = parser.base_search('Наруто', 10) # Гарантированно существующий результат
        self.assertIsInstance(search, dict)
        self.assertNotEqual(search['total'], 0)
        try:
            parser.base_search('grtk~Q@@!#JKBNVFLD', 10) # Гарантированно несуществующий резльтат
        except errors.NoResults:
            pass
        except Exception as ex:
            raise AssertionError(f'Base search with guaranteed bad search query returned error other then NoResults. Exception: {ex}')

    def test_base_search_by_id(self):
        from src.anime_parsers_ru import KodikParser
        import src.anime_parsers_ru.errors as errors
        parser = KodikParser(use_lxml=self.USE_LXML)
        search = parser.base_search_by_id('20', 'shikimori') # Гарантированно существующий результат
        self.assertIsInstance(search, dict)
        self.assertNotEqual(search['total'], 0)
        try:
            parser.base_search_by_id('0', 'shikimori') # Гарантированно несуществующий резльтат
        except errors.NoResults:
            pass
        except Exception as ex:
            raise AssertionError(f'Base search with guaranteed bad search query returned error other then NoResults. Exception: {ex}')

    def test_list(self):
        from src.anime_parsers_ru import KodikParser
        import src.anime_parsers_ru.errors as errors
        parser = KodikParser(use_lxml=self.USE_LXML)
        data = parser.get_list(include_material_data=False)
        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertTrue(len(data[0]) > 0)
        self.assertIsInstance(data[0][0], dict)

        data = parser.get_list(limit_per_page=10, pages_to_parse=3, only_anime=True)
        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertTrue(len(data[0]) > 0)
        self.assertIsInstance(data[0][0], dict)

        data = parser.get_list(anime_status='ongoing')
        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertTrue(len(data[0]) > 0)
        self.assertIsInstance(data[0][0], dict)

    def test_search(self):
        from src.anime_parsers_ru import KodikParser
        import src.anime_parsers_ru.errors as errors
        parser = KodikParser(use_lxml=self.USE_LXML)

        search = parser.search('Наруто')
        self.assertIsInstance(search, list)
        self.assertNotEqual(len(search), 0)

        search = parser.search('О моём перерождении в слизь', strict=True, only_anime=True)
        self.assertIsInstance(search, list)
        self.assertNotEqual(len(search), 0)
    
    def test_search_by_id(self):
        from src.anime_parsers_ru import KodikParser
        import src.anime_parsers_ru.errors as errors
        parser = KodikParser(use_lxml=self.USE_LXML)
        search = parser.search_by_id('20', 'shikimori')
        self.assertIsInstance(search, list)
        self.assertNotEqual(len(search), 0)

    def test_get_info_serial(self):
        from src.anime_parsers_ru import KodikParser
        parser = KodikParser(use_lxml=self.USE_LXML)
        cur_search = parser.get_info('z20', 'shikimori')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = parser.get_info('283290', 'kinopoisk')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = parser.get_info('tt0409591', 'imdb')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)

    def test_get_info_video(self):
        from src.anime_parsers_ru import KodikParser
        parser = KodikParser(use_lxml=self.USE_LXML)
        cur_search = parser.get_info('2472', 'shikimori')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = parser.get_info('283418', 'kinopoisk')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = parser.get_info('tt0988982', 'imdb')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)

    def test_get_link_serial(self):
        from src.anime_parsers_ru import KodikParser
        parser = KodikParser(use_lxml=self.USE_LXML)
        link = parser.get_link('z20', 'shikimori', 1, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)
    
    def test_get_link_video(self):
        from src.anime_parsers_ru import KodikParser
        parser = KodikParser(use_lxml=self.USE_LXML)
        link = parser.get_link('2472', 'shikimori', 0, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)

class TestKodikAsync(unittest.IsolatedAsyncioTestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import KodikParserAsync
        import src.anime_parsers_ru.errors as errors

    async def test_auto_token(self):
        from src.anime_parsers_ru import KodikParserAsync
        goten_token = await KodikParserAsync.get_token()
        self.assertIsInstance(goten_token, str)
    
    async def test_init(self):
        from src.anime_parsers_ru import KodikParserAsync
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
    
    async def test_base_search(self):
        from src.anime_parsers_ru import KodikParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        search = await parser.base_search('Наруто', 10) # Гарантированно существующий результат
        self.assertIsInstance(search, dict)
        self.assertNotEqual(search['total'], 0)
        try:
            await parser.base_search('grtk~Q@@!#JKBNVFLD', 10) # Гарантированно несуществующий резльтат
        except errors.NoResults:
            pass
        except Exception as ex:
            raise AssertionError(f'Base search with guaranteed bad search query returned error other then NoResults. Exception: {ex}')

    async def test_base_search_by_id(self):
        from src.anime_parsers_ru import KodikParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        search = await parser.base_search_by_id('20', 'shikimori') # Гарантированно существующий результат
        self.assertIsInstance(search, dict)
        self.assertNotEqual(search['total'], 0)
        try:
            await parser.base_search_by_id('0', 'shikimori') # Гарантированно несуществующий резльтат
        except errors.NoResults:
            pass
        except Exception as ex:
            raise AssertionError(f'Base search with guaranteed bad search query returned error other then NoResults. Exception: {ex}')

    async def test_list(self):
        from src.anime_parsers_ru import KodikParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        data = await parser.get_list(include_material_data=False)
        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertTrue(len(data[0]) > 0)
        self.assertIsInstance(data[0][0], dict)

        data = await parser.get_list(limit_per_page=10, pages_to_parse=3, only_anime=True)
        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertTrue(len(data[0]) > 0)
        self.assertIsInstance(data[0][0], dict)

        
        data = await parser.get_list(anime_status='ongoing')
        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertTrue(len(data[0]) > 0)
        self.assertIsInstance(data[0][0], dict)

    async def test_search(self):
        from src.anime_parsers_ru import KodikParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        search = await parser.search('Наруто')
        self.assertIsInstance(search, list)
        self.assertNotEqual(len(search), 0)

        search = await parser.search('О моём перерождении в слизь', strict=True, only_anime=True)
        self.assertIsInstance(search, list)
        self.assertNotEqual(len(search), 0)
    
    async def test_search_by_id(self):
        from src.anime_parsers_ru import KodikParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        search = await parser.search_by_id('20', 'shikimori')
        self.assertIsInstance(search, list)
        self.assertNotEqual(len(search), 0)

    async def test_get_info_serial(self):
        from src.anime_parsers_ru import KodikParserAsync
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        cur_search = await parser.get_info('z20', 'shikimori')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = await parser.get_info('283290', 'kinopoisk')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = await parser.get_info('tt0409591', 'imdb')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)

    async def test_get_info_video(self):
        from src.anime_parsers_ru import KodikParserAsync
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        cur_search = await parser.get_info('2472', 'shikimori')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = await parser.get_info('283418', 'kinopoisk')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)
        
        cur_search = await parser.get_info('tt0988982', 'imdb')
        self.assertIsInstance(cur_search, dict)
        self.assertIsInstance(cur_search['series_count'], int)
        self.assertIsInstance(cur_search['translations'], list)
        self.assertIsInstance(cur_search['translations'][0], dict)

    async def test_get_link_serial(self):
        from src.anime_parsers_ru import KodikParserAsync
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        link = await parser.get_link('z20', 'shikimori', 1, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)
    
    async def test_get_link_video(self):
        from src.anime_parsers_ru import KodikParserAsync
        parser = KodikParserAsync(use_lxml=self.USE_LXML)
        link = await parser.get_link('2472', 'shikimori', 0, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)

class TestAniboom(unittest.TestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import AniboomParser
        import src.anime_parsers_ru.errors as errors

    def test_init(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
    
    def test_fast_search(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        search = parser.fast_search('Наруто')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)
        # Нельзя проверить на то что нет результатов, потому что у animego всегда есть результаты на какой угодно запрос \_(-_-)_/
        
    def test_episodes_info(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        data = parser.episodes_info('https://animego.org/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546')
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0) # У данного аниме гарантированно есть эпизоды
        self.assertIsInstance(data[0], dict)
        if len(data) > 1:
            self.assertGreater(data[-1]['num'], data[0]['num']) # Проверка сортировки

        # Проверка для фильмов
        data = parser.episodes_info('https://animego.org/anime/psihopasport-film-1327')
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    def test_translations_info(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        data = parser.get_translations_info('2546') # Волчица и пряности 2024
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0) # У данного аниме гарантированно есть переводы в плеере aniboom
        self.assertIsInstance(data[0], dict)
        self.assertTrue(list(data[0].keys()) == ['name', 'translation_id'])
    
        # Проверка для отсутсвующих переводов
        data = parser.get_translations_info('106') # Наруто: Битва на Хидден-Фолс
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_anime_info(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        data = parser.anime_info('https://animego.org/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546')
        self.assertIsInstance(data, dict)
        self.assertTrue('episodes_info' in data.keys())
        self.assertTrue('translations' in data.keys())

        # Проверка без трейлера и переводов
        data = parser.anime_info('https://animego.org/anime/naruto-bitva-na-hidden-fols-106')
        self.assertIsInstance(data, dict)
        self.assertTrue('episodes_info' in data.keys())
        self.assertTrue('translations' in data.keys())

    def test_search(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)

        search = parser.search('Наруто')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)

        search = parser.search('Кулинарные скитания')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)
    
    def test_get_embed_link(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        data = parser._get_embed_link('2546')
        self.assertIsInstance(data, str)
    
    def test_get_embed(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        link = parser._get_embed_link('2546') # Волчица и пряности 2024
        data = parser._get_embed(link, 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)

        # Проверка для фильма
        link = parser._get_embed_link('1327') # Психопаспорт (фильм)
        data = parser._get_embed(link, 0, '15') # Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
    
    def test_get_media_src(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        link = parser._get_embed_link('2546') # Волчица и пряности 2024
        data = parser._get_media_src(link, 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)

        # Проверка для фильма
        link = parser._get_embed_link('1327') # Психопаспорт (фильм)
        data = parser._get_media_src(link, 0, '15') # Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
    
    def test_get_mpd_playlist(self):
        from src.anime_parsers_ru import AniboomParser
        parser = AniboomParser(use_lxml=self.USE_LXML)
        data = parser.get_mpd_playlist('2546', 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)
        first_row = data[:data.find('\n')]
        self.assertTrue(first_row == '<?xml version="1.0" encoding="utf-8"?>')

        # Проверка для фильма
        data = parser.get_mpd_playlist('1327', 0, '15') # Психопаспорт (фильм) Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
        first_row = data[:data.find('\n')]
        self.assertTrue(first_row == '<?xml version="1.0" encoding="utf-8"?>')

class TestAniboomAsync(unittest.IsolatedAsyncioTestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import AniboomParserAsync
        import src.anime_parsers_ru.errors as errors

    def test_init(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
    
    async def test_fast_search(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        search = await parser.fast_search('Наруто')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)
        # Нельзя проверить на то что нет результатов, потому что у animego всегда есть результаты на какой угодно запрос \_(-_-)_/
        
    async def test_episodes_info(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        data = await parser.episodes_info('https://animego.org/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546')
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0) # У данного аниме гарантированно есть эпизоды
        self.assertIsInstance(data[0], dict)
        if len(data) > 1:
            self.assertGreater(data[-1]['num'], data[0]['num']) # Проверка сортировки

        # Проверка для фильмов
        data = await parser.episodes_info('https://animego.org/anime/psihopasport-film-1327')
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    async def test_translations_info(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        data = await parser.get_translations_info('2546') # Волчица и пряности 2024
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0) # У данного аниме гарантированно есть переводы в плеере aniboom
        self.assertIsInstance(data[0], dict)
        self.assertTrue(list(data[0].keys()) == ['name', 'translation_id'])
    
        # Проверка для отсутсвующих переводов
        data = await parser.get_translations_info('106') # Наруто: Битва на Хидден-Фолс
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    async def test_anime_info(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        data = await parser.anime_info('https://animego.org/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546')
        self.assertIsInstance(data, dict)
        self.assertTrue('episodes_info' in data.keys())
        self.assertTrue('translations' in data.keys())

        # Проверка без трейлера и переводов
        data = await parser.anime_info('https://animego.org/anime/naruto-bitva-na-hidden-fols-106')
        self.assertIsInstance(data, dict)
        self.assertTrue('episodes_info' in data.keys())
        self.assertTrue('translations' in data.keys())

    async def test_search(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)

        search = await parser.search('Наруто')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)

        search = await parser.search('Кулинарные скитания')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)
    
    async def test_get_embed_link(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        data = await parser._get_embed_link('2546')
        self.assertIsInstance(data, str)
    
    async def test_get_embed(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        link = await parser._get_embed_link('2546') # Волчица и пряности 2024
        data = await parser._get_embed(link, 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)

        # Проверка для фильма
        link = await parser._get_embed_link('1327') # Психопаспорт (фильм)
        data = await parser._get_embed(link, 0, '15') # Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
    
    async def test_get_media_src(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        link = await parser._get_embed_link('2546') # Волчица и пряности 2024
        data = await parser._get_media_src(link, 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)

        # Проверка для фильма
        link = await parser._get_embed_link('1327') # Психопаспорт (фильм)
        data = await parser._get_media_src(link, 0, '15') # Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
    
    async def test_get_mpd_playlist(self):
        from src.anime_parsers_ru import AniboomParserAsync
        parser = AniboomParserAsync(use_lxml=self.USE_LXML)
        data = await parser.get_mpd_playlist('2546', 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)
        first_row = data[:data.find('\n')]
        self.assertTrue(first_row == '<?xml version="1.0" encoding="utf-8"?>')

        # Проверка для фильма
        data = await parser.get_mpd_playlist('1327', 0, '15') # Психопаспорт (фильм) Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
        first_row = data[:data.find('\n')]
        self.assertTrue(first_row == '<?xml version="1.0" encoding="utf-8"?>')

class TestJutsu(unittest.TestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import JutsuParser
        import src.anime_parsers_ru.errors as errors
    
    def test_get_anime_info(self):
        from src.anime_parsers_ru import JutsuParser
        import src.anime_parsers_ru.errors as errors
        parser = JutsuParser(self.USE_LXML)
        
        # Проверка на аниме с одним сезоном
        data = parser.get_anime_info('https://jut.su/tondemo-skill/') # Кулинарные скитания
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['seasons'], list)
        self.assertTrue(data['title'] == 'Кулинарные скитания в параллельном мире')
        self.assertTrue(len(data['seasons']) == 1)
        self.assertTrue(len(data['seasons_names']) == 0)
        self.assertIsInstance(data['seasons'][0][0], str)

        # Проверка на аниме с несколькими сезонами
        data = parser.get_anime_info('https://jut.su/ookami-to-koshinryou/') # Волчица и пряности
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['seasons'], list)
        self.assertTrue(data['title'] == 'Волчица и пряности')
        self.assertTrue(len(data['seasons']) > 1)
        self.assertTrue(len(data['seasons_names']) > 0)
        self.assertIsInstance(data['seasons'][0][0], str)

        # Проверка на аниме с фильмами
        data = parser.get_anime_info('https://jut.su/fullmeetal-alchemist/') # Стальной алхимик
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['seasons'], list)
        self.assertTrue(data['title'] == 'Стальной алхимик')
        self.assertTrue(len(data['seasons']) > 1)
        self.assertTrue(len(data['seasons_names']) > 0)
        self.assertTrue(len(data['films']) > 0)
        self.assertIsInstance(data['seasons'][0][0], str)
        self.assertIsInstance(data['films'][0], str)
    
    def test_get_mp4_link(self):
        from src.anime_parsers_ru import JutsuParser
        import src.anime_parsers_ru.errors as errors
        parser = JutsuParser(self.USE_LXML)

        # Проверка без сезонов
        data = parser.get_mp4_link('https://jut.su/tondemo-skill/episode-1.html') # Кулинарные скитания в параллельном мире 1 серия
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data.keys()) > 0)
        self.assertIsInstance(data['720'], str) # Надеемся на то что есть 720

        # Проверка с сезонами
        data = parser.get_mp4_link('https://jut.su/ookami-to-koshinryou/season-1/episode-1.html') # Волчица и пряности 1 сезон 1 серия
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data.keys()) > 0)
        self.assertIsInstance(data['720'], str) # Надеемся на то что есть 720

class TestShikimori(unittest.TestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import ShikimoriParser
        import src.anime_parsers_ru.errors as errors

    def test_search(self):
        from src.anime_parsers_ru import ShikimoriParser
        parser = ShikimoriParser(self.USE_LXML)

        data = parser.search('Кулинарные скитания')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)
        
        data = parser.search('Наруто')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)

        data = parser.search('Класс превосходства')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)

        data = parser.search('Клинок рассекающий демонов')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)
    
    def test_anime_info(self):
        from src.anime_parsers_ru import ShikimoriParser
        import src.anime_parsers_ru.errors as errors
        parser = ShikimoriParser(self.USE_LXML)

        data = parser.anime_info('https://shikimori.one/animes/z20-naruto')
        self.assertIsInstance(data, dict)

        data = parser.anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        self.assertIsInstance(data, dict)

        data = parser.anime_info('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan')
        self.assertIsInstance(data, dict)

        data = parser.anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        self.assertIsInstance(data, dict)

        # Проверка на ограничение по возрасту
        try:
            data = parser.anime_info('https://shikimori.one/animes/53725-class-de-otoko-wa-boku-ichinin')
        except errors.AgeRestricted:
            pass
        except Exception as ex:
            raise Warning(f'Непредвиденная ошибка "{ex}". Ожидалось: "AgeRestricted"')
        else:
            raise Warning('Обработка ограниченного по возрасту аниме не вернуло ошибку. Ожидалось: "AgeRestricted"')

    def test_additional_anime_info(self):
        from src.anime_parsers_ru import ShikimoriParser
        parser = ShikimoriParser(self.USE_LXML)

        data = parser.additional_anime_info('https://shikimori.one/animes/z20-naruto')
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data['related']) > 0) # У наруто точно есть

        data = parser.additional_anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data['main_characters']) > 0) # Точно есть

        data = parser.additional_anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        self.assertIsInstance(data, dict)

    def test_link_by_id(self):
        from src.anime_parsers_ru import ShikimoriParser
        parser = ShikimoriParser(self.USE_LXML)

        data = parser.link_by_id('20') # Наруто (реальный id - z20)
        self.assertIsInstance(data, str)

        data = parser.link_by_id('40456') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456)
        self.assertIsInstance(data, str)

        data = parser.link_by_id('58426') # Моя подруга-олениха Нокотан (реальный id - 58426)
        self.assertIsInstance(data, str)

        data = parser.link_by_id('53446') # Кулинарные скитания в параллельном мире (реальный id - 53446)
        self.assertIsInstance(data, str)

    def test_id_by_link(self):
        from src.anime_parsers_ru import ShikimoriParser
        parser = ShikimoriParser(self.USE_LXML)

        data = parser.id_by_link('https://shikimori.one/animes/z20-naruto') # Наруто (реальный id - z20 ожидаем - 20)
        self.assertIsInstance(data, str)
        self.assertTrue(data == '20')

        data = parser.id_by_link('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456 ожидаем - 40456)
        self.assertIsInstance(data, str)
        self.assertTrue(data == '40456')

        data = parser.id_by_link('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan') # Моя подруга-олениха Нокотан (реальный id - 58426 ожидаем - 58426)
        self.assertIsInstance(data, str)
        self.assertTrue(data == '58426')

    def test_get_anime_list(self):
        from src.anime_parsers_ru import ShikimoriParser
        parser = ShikimoriParser(self.USE_LXML)

        data = parser.get_anime_list()
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = parser.get_anime_list(status=['ongoing'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = parser.get_anime_list(status=['released'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = parser.get_anime_list(status=['released', 'ongoing'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = parser.get_anime_list(anime_type=['tv'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')

        data = parser.get_anime_list(anime_type=['movie'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'Фильм')

        data = parser.get_anime_list(anime_type=['movie', 'tv'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'Фильм' or data[0]['type'] == 'TV Сериал')

        data = parser.get_anime_list(status=['ongoing'], anime_type=['tv'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')

        data = parser.get_anime_list(status=['ongoing'], anime_type=['tv'], start_page=3, page_limit=2, sort_by='popularity')
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')

        data = parser.get_anime_list(status=['ongoing'], anime_type=['tv'], rating='pg_13', genres=['2-Adventure'], start_page=1, page_limit=2, sort_by='popularity')
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')
        
    
    def test_deep_search(self):
        from src.anime_parsers_ru import ShikimoriParser
        parser = ShikimoriParser(self.USE_LXML)

        # Просто проверим доступность ссылки
        data = parser.deep_search('Кулинарные скитания', {}, ['id', 'name', 'url', 'genres { name russian }'])
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно должны быть данные
        self.assertIsInstance(data[0], dict)

    def test_deep_anime_info(self):
        from src.anime_parsers_ru import ShikimoriParser
        import src.anime_parsers_ru.errors as errors
        parser = ShikimoriParser(self.USE_LXML)

        # Просто проверим доступность ссылки
        data = parser.deep_anime_info('53446', ['id', 'name', 'url', 'genres { name russian }'])
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['name'], str)

        try: # Проверка на несуществующем id
            data = parser.deep_anime_info('fff', ['id', 'name', 'url', 'genres { name russian }'])
        except errors.NoResults:
            pass
        except Exception as ex:
            raise Warning(f'Непредвиденная ошиибка "{ex}". Ожидалось: NoResults')
        else:
            raise Warning(f'Гарантированно неверный код не вернул ошибку. Ожидалось: NoResults')

class TestShikimoriAsync(unittest.IsolatedAsyncioTestCase):
    USE_LXML = GLOBAL_USE_LXML
    def test_import(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        import src.anime_parsers_ru.errors as errors

    async def test_search(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        parser = ShikimoriParserAsync(self.USE_LXML)

        data = await parser.search('Кулинарные скитания')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)
        
        data = await parser.search('Наруто')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)

        data = await parser.search('Класс превосходства')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)

        data = await parser.search('Клинок рассекающий демонов')
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно есть результат
        self.assertIsInstance(data[0], dict)
    
    async def test_anime_info(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = ShikimoriParserAsync(self.USE_LXML)

        data = await parser.anime_info('https://shikimori.one/animes/z20-naruto')
        self.assertIsInstance(data, dict)

        data = await parser.anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        self.assertIsInstance(data, dict)

        data = await parser.anime_info('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan')
        self.assertIsInstance(data, dict)

        data = await parser.anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        self.assertIsInstance(data, dict)

        # Проверка на ограничение по возрасту
        try:
            data = await parser.anime_info('https://shikimori.one/animes/53725-class-de-otoko-wa-boku-ichinin')
        except errors.AgeRestricted:
            pass
        except Exception as ex:
            raise Warning(f'Непредвиденная ошибка "{ex}". Ожидалось: "AgeRestricted"')
        else:
            raise Warning('Обработка ограниченного по возрасту аниме не вернуло ошибку. Ожидалось: "AgeRestricted"')

    async def test_additional_anime_info(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        parser = ShikimoriParserAsync(self.USE_LXML)

        data = await parser.additional_anime_info('https://shikimori.one/animes/z20-naruto')
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data['related']) > 0) # У наруто точно есть

        data = await parser.additional_anime_info('https://shikimori.one/animes/53446-tondemo-skill-de-isekai-hourou-meshi')
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data['main_characters']) > 0) # Точно есть

        data = await parser.additional_anime_info('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen')
        self.assertIsInstance(data, dict)

    async def test_link_by_id(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        parser = ShikimoriParserAsync(self.USE_LXML)

        data = await parser.link_by_id('20') # Наруто (реальный id - z20)
        self.assertIsInstance(data, str)

        data = await parser.link_by_id('40456') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456)
        self.assertIsInstance(data, str)

        data = await parser.link_by_id('58426') # Моя подруга-олениха Нокотан (реальный id - 58426)
        self.assertIsInstance(data, str)

        data = await parser.link_by_id('53446') # Кулинарные скитания в параллельном мире (реальный id - 53446)
        self.assertIsInstance(data, str)

    def test_id_by_link(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        parser = ShikimoriParserAsync(self.USE_LXML)

        data = parser.id_by_link('https://shikimori.one/animes/z20-naruto') # Наруто (реальный id - z20 ожидаем - 20)
        self.assertIsInstance(data, str)
        self.assertTrue(data == '20')

        data = parser.id_by_link('https://shikimori.one/animes/z40456-kimetsu-no-yaiba-movie-mugen-ressha-hen') # Клинок, рассекающий демонов: Бесконечный поезд. Фильм (реальный id - z40456 ожидаем - 40456)
        self.assertIsInstance(data, str)
        self.assertTrue(data == '40456')

        data = parser.id_by_link('https://shikimori.one/animes/58426-shikanoko-nokonoko-koshitantan') # Моя подруга-олениха Нокотан (реальный id - 58426 ожидаем - 58426)
        self.assertIsInstance(data, str)
        self.assertTrue(data == '58426')

    async def test_get_anime_list(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        parser = ShikimoriParserAsync(self.USE_LXML)

        data = await parser.get_anime_list()
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = await parser.get_anime_list(status=['ongoing'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = await parser.get_anime_list(status=['released'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = await parser.get_anime_list(status=['released', 'ongoing'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)

        data = await parser.get_anime_list(anime_type=['tv'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')

        data = await parser.get_anime_list(anime_type=['movie'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'Фильм')

        data = await parser.get_anime_list(anime_type=['movie', 'tv'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'Фильм' or data[0]['type'] == 'TV Сериал')

        data = await parser.get_anime_list(status=['ongoing'], anime_type=['tv'])
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')

        data = await parser.get_anime_list(status=['ongoing'], anime_type=['tv'], start_page=3, page_limit=2, sort_by='popularity')
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')

        data = await parser.get_anime_list(status=['ongoing'], anime_type=['tv'], rating='pg_13', genres=['2-Adventure'], start_page=1, page_limit=2, sort_by='popularity')
        self.assertTrue(len(data) > 0)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertTrue(data[0]['type'] == 'TV Сериал')
    
    async def test_deep_search(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        parser = ShikimoriParserAsync(self.USE_LXML)

        # Просто проверим доступность ссылки
        data = await parser.deep_search('Кулинарные скитания', {}, ['id', 'name', 'url', 'genres { name russian }'])
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0) # Точно должны быть данные
        self.assertIsInstance(data[0], dict)

    async def test_deep_anime_info(self):
        from src.anime_parsers_ru import ShikimoriParserAsync
        import src.anime_parsers_ru.errors as errors
        parser = ShikimoriParserAsync(self.USE_LXML)

        # Просто проверим доступность ссылки
        data = await parser.deep_anime_info('53446', ['id', 'name', 'url', 'genres { name russian }'])
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['name'], str)

        try: # Проверка на несуществующем id
            data = await parser.deep_anime_info('fff', ['id', 'name', 'url', 'genres { name russian }'])
        except errors.NoResults:
            pass
        except Exception as ex:
            raise Warning(f'Непредвиденная ошибка "{ex}". Ожидалось: NoResults')
        else:
            raise Warning(f'Гарантированно неверный код не вернул ошибку. Ожидалось: NoResults')

class TestKodikApi(unittest.TestCase):
    def test_init(self):
        from src.anime_parsers_ru import KodikList
        from src.anime_parsers_ru import KodikSearch
        from src.anime_parsers_ru.api_kodik import Response
        s = KodikSearch()
        l = KodikList()
    
    def test_search(self):
        from src.anime_parsers_ru import KodikSearch
        from src.anime_parsers_ru.api_kodik import Response, Api
        s = KodikSearch().title('Кулинарные скитания').limit(2).with_material_data().with_episodes_data()
        self.assertIsInstance(s, Api)
        data = s.execute()
        self.assertIsInstance(data, Response)
        self.assertTrue(len(data.results) > 0)
        self.assertIsInstance(data.results[0], Response.Element)
        self.assertIsInstance(data.results[0].raw_data, dict)
        self.assertIsInstance(data.results[0].translation, Response.Translation)
        self.assertIsInstance(data.results[0].material_data, Response.MaterialData)
        self.assertIsInstance(data.results[0].seasons, dict)
        r = list(data.results[0].seasons.keys())
        self.assertIsInstance(data.results[0].seasons[r[0]], Response.Season)
        t = list(data.results[0].seasons[r[0]].episodes.keys())
        self.assertIsInstance(data.results[0].seasons[r[0]].episodes[t[0]], Response.Season.Episode)
        
    def test_list(self):
        from src.anime_parsers_ru import KodikList
        from src.anime_parsers_ru.api_kodik import Response, Api
        s = KodikList().anime_status('ongoing').limit(2).with_material_data().with_episodes_data()
        self.assertIsInstance(s, Api)
        data = s.execute()
        self.assertIsInstance(data, Response)
        self.assertTrue(len(data.results) > 0)
        self.assertIsInstance(data.results[0], Response.Element)
        self.assertIsInstance(data.results[0].raw_data, dict)
        self.assertIsInstance(data.results[0].translation, Response.Translation)
        self.assertIsInstance(data.results[0].material_data, Response.MaterialData)
        self.assertIsInstance(data.results[0].seasons, dict)
        r = list(data.results[0].seasons.keys())
        self.assertIsInstance(data.results[0].seasons[r[0]], Response.Season)
        t = list(data.results[0].seasons[r[0]].episodes.keys())
        self.assertIsInstance(data.results[0].seasons[r[0]].episodes[t[0]], Response.Season.Episode)
        

if __name__ == "__main__":
    GLOBAL_USE_LXML = True
    unittest.main()