from src.anime_parsers_ru import *
import parser_tests.animego_test as animego
import parser_tests.kodik_test as kodik
import parser_tests.jutsu_test as jutsu
import asyncio

import testconfig


if __name__ == "__main__":
    proxy = None
    GLOBAL_USE_LXML = False
    KODIK_TOKEN = testconfig.KODIK_TOKEN
    GLOBAL_TOKEN_VALIDATION = False
    delay = 2
    animego_mirror = "animego.me"

    try_errors = 0

    print('=== KODIK === SYNC TEST ===')
    try_errors += kodik.main_test(delay=delay, TOKEN=KODIK_TOKEN, GLOBAL_USE_LXML=GLOBAL_USE_LXML, GLOBAL_TOKEN_VALIDATION=GLOBAL_TOKEN_VALIDATION, proxy=proxy)
    print('\n=== KODIK === ASYNC TEST ===')
    try_errors += asyncio.run(kodik.async_test(delay=delay, TOKEN=KODIK_TOKEN, GLOBAL_USE_LXML=GLOBAL_USE_LXML, GLOBAL_TOKEN_VALIDATION=GLOBAL_TOKEN_VALIDATION, proxy=proxy))
    print('\n=== KODIK === API TEST ===')
    try_errors += kodik.api_test(delay=delay, TOKEN=KODIK_TOKEN, proxy=proxy)


    print('\n=== ANIMEGO === ASYNC TEST ===')
    asyncio.run(animego.async_test(proxy, animego_mirror, GLOBAL_USE_LXML, delay))

    print('\n=== JUT-SU === SYNC TEST ===')
    try_errors += jutsu.sync_test(delay=delay, GLOBAL_USE_LXML=GLOBAL_USE_LXML, proxy=proxy)

    print(f'\nTEST DONE!\nTotal errors: {try_errors}')