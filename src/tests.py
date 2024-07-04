import unittest

class TestKodik(unittest.TestCase):
    def test_import(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        import anime_parsers_ru.errors as errors

    def test_auto_token(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        goten_token = KodikParser.get_token()
        self.assertIsInstance(goten_token, str)
    
    def test_init(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
    
    def test_base_search(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        import anime_parsers_ru.errors as errors
        parser = KodikParser()
        search = parser.base_search('Наруто', 10) # Гарантированно существующий результат
        self.assertIsInstance(search, dict)
        self.assertNotEqual(search['total'], 0)
        try:
            parser.base_search('grtk~Q@@!#JKBNVFLD', 10) # Гарантированно несуществующий резльтат
        except errors.NoResults:
            pass
        except Exception as ex:
            raise AssertionError(f'Base search with guaranteed bad search query returned error other then NoResults. Exception: {ex}')

    def test_get_info_serial(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
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
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
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
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
        link = parser.get_link('z20', 'shikimori', 1, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)
    
    def test_get_link_video(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
        link = parser.get_link('2472', 'shikimori', 0, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)

class TestAniboom(unittest.TestCase):
    def test_import(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        import anime_parsers_ru.errors as errors

    def test_init(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
    
    def test_fast_search(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
        search = parser.fast_search('Наруто')
        self.assertGreater(len(search), 0) # Гарантированно имеются данные
        self.assertIsInstance(search, list)
        self.assertIsInstance(search[0], dict)
        # Нельзя проверить на то что нет результатов, потому что у animego всегда есть результаты на какой угодно запрос \_(-_-)_/
        
    def test_episodes_info(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
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
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
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
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
        data = parser.anime_info('https://animego.org/anime/volchica-i-pryanosti-torgovec-vstrechaet-mudruyu-volchicu-2546')
        self.assertIsInstance(data, dict)
        self.assertTrue('episodes_info' in data.keys())
        self.assertTrue('translations' in data.keys())

        # Проверка без трейлера и переводов
        data = parser.anime_info('https://animego.org/anime/naruto-bitva-na-hidden-fols-106')
        self.assertIsInstance(data, dict)
        self.assertTrue('episodes_info' in data.keys())
        self.assertTrue('translations' in data.keys())
    
    def test_get_embed_link(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
        data = parser._get_embed_link('2546')
        self.assertIsInstance(data, str)
    
    def test_get_embed(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
        link = parser._get_embed_link('2546') # Волчица и пряности 2024
        data = parser._get_embed(link, 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)

        # Проверка для фильма
        link = parser._get_embed_link('1327') # Психопаспорт (фильм)
        data = parser._get_embed(link, 0, '15') # Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
    
    def test_get_media_src(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
        link = parser._get_embed_link('2546') # Волчица и пряности 2024
        data = parser._get_media_src(link, 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)

        # Проверка для фильма
        link = parser._get_embed_link('1327') # Психопаспорт (фильм)
        data = parser._get_media_src(link, 0, '15') # Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
    
    def test_get_mpd_playlist(self):
        from anime_parsers_ru.parser_aniboom import AniboomParser
        parser = AniboomParser()
        data = parser.get_mpd_playlist('2546', 1, '2') # Озвучка от AniLibria
        self.assertIsInstance(data, str)
        first_row = data[:data.find('\n')]
        self.assertTrue(first_row == '<?xml version="1.0" encoding="utf-8"?>')

        # Проверка для фильма
        data = parser.get_mpd_playlist('1327', 0, '15') # Психопаспорт (фильм) Озвучка от СВ-Дубль
        self.assertIsInstance(data, str)
        first_row = data[:data.find('\n')]
        self.assertTrue(first_row == '<?xml version="1.0" encoding="utf-8"?>')

if __name__ == "__main__":
    unittest.main()