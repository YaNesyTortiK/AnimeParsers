import unittest

class TestKodik(unittest.TestCase):
    def test_import(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        import anime_parsers_ru.errors as errors
        print('[OK] Test import')

    def test_auto_token(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        goten_token = KodikParser.get_token()
        self.assertIsInstance(goten_token, str)
        print('[OK] Test auto token')
    
    def test_init(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
        print('[OK] Test init')
    
    def test_base_search(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        import anime_parsers_ru.errors as errors
        parser = KodikParser()
        search = parser.base_search('Наруто', 10) # Гарантированно существующий результат
        self.assertIsInstance(search, dict)
        print('[OK] Test guaranteed good base_search query')
        self.assertNotEqual(search['total'], 0)
        try:
            parser.base_search('grtk~Q@@!#JKBNVFLD', 10) # Гарантированно несуществующий резльтат
        except errors.NoResults:
            print('[OK] Test guaranteed bad base_search query')
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
        print('[OK] Test getting info from serial')

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
        print('[OK] Test getting info from video')

    def test_get_link_serial(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
        link = parser.get_link('z20', 'shikimori', 1, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)
        print('[OK] Test getting link to serial')
    
    def test_get_link_video(self):
        from anime_parsers_ru.parser_kodik import KodikParser
        parser = KodikParser()
        link = parser.get_link('2472', 'shikimori', 0, '609')
        self.assertIsInstance(link, tuple)
        self.assertIsInstance(link[0], str)
        self.assertIsInstance(link[1], int)
        print('[OK] Test getting link to video')

if __name__ == "__main__":
    unittest.main()