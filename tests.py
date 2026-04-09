from src.anime_parsers_ru import *
import parser_tests.animego_test as animego
import asyncio

if __name__ == "__main__":
    proxy = None
    GLOBAL_USE_LXML = False
    delay = 0

    animego_mirror = "animego.me"
    print('=== ANIMEGO === ASYNC TEST ===')
    asyncio.run(animego.async_test(proxy, animego_mirror, GLOBAL_USE_LXML, delay))