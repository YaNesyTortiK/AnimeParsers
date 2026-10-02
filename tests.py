from src.anime_parsers_ru import *
import parser_tests.animego_test as animego
import parser_tests.kodik_test as kodik
import parser_tests.jutsu_test as jutsu
import parser_tests.shiki_test as shiki
import parser_tests.aniliberty_test as aniliberty
import parser_tests.dreamcast_test as dreamcast

import asyncio
import testconfig
from time import time

def kdk_sync():
    global try_errors, try_success
    print('=== KODIK === SYNC TEST ===')
    stats = kodik.main_test(delay=delay, TOKEN=KODIK_TOKEN, GLOBAL_USE_LXML=GLOBAL_USE_LXML, GLOBAL_TOKEN_VALIDATION=GLOBAL_TOKEN_VALIDATION, proxy=proxy)
    try_errors += stats[0]
    try_success += stats[1]

def kdk_async():
    global try_errors, try_success
    print('\n=== KODIK === ASYNC TEST ===')
    stats = asyncio.run(kodik.async_test(delay=delay, TOKEN=KODIK_TOKEN, GLOBAL_USE_LXML=GLOBAL_USE_LXML, GLOBAL_TOKEN_VALIDATION=GLOBAL_TOKEN_VALIDATION, proxy=proxy))
    try_errors += stats[0]
    try_success += stats[1]

def kdk_api():
    global try_errors, try_success
    print('\n=== KODIK === API TEST ===')
    stats = kodik.api_test(delay=delay, TOKEN=KODIK_TOKEN, proxy=proxy)
    try_errors += stats[0]
    try_success += stats[1]

def shiki_sync():
    global try_errors, try_success
    print('\n=== SHIKI === SYNC TEST ===')
    stats = shiki.sync_test(delay=delay, GLOBAL_USE_LXML=GLOBAL_USE_LXML, mirror=shiki_mirror, proxy=shiki_proxy)
    try_errors += stats[0]
    try_success += stats[1]

def shiki_async():
    global try_errors, try_success
    print('\n=== SHIKI === ASYNC TEST ===')
    stats = asyncio.run(shiki.async_test(delay=delay, GLOBAL_USE_LXML=GLOBAL_USE_LXML, mirror=shiki_mirror, proxy=shiki_proxy))
    try_errors += stats[0]
    try_success += stats[1]

def animego_sync():
    global try_errors, try_success
    print('\n=== ANIMEGO === SYNC TEST ===')
    stats = animego.sync_test(proxy, animego_mirror, GLOBAL_USE_LXML, delay)
    try_errors += stats[0]
    try_success += stats[1]

def animego_async():
    global try_errors, try_success
    print('\n=== ANIMEGO === ASYNC TEST ===')
    stats = asyncio.run(animego.async_test(proxy, animego_mirror, GLOBAL_USE_LXML, delay))
    try_errors += stats[0]
    try_success += stats[1]

def jutsu_sync():
    global try_errors, try_success
    print('\n=== JUT-SU === SYNC TEST ===')
    stats = jutsu.sync_test(delay=delay, GLOBAL_USE_LXML=GLOBAL_USE_LXML, proxy=proxy)
    try_errors += stats[0]
    try_success += stats[1]

def aniliberty_api_sync():
    global try_errors, try_success
    print('\n=== AnilibertyAPI === SYNC TEST ===')
    stats = aniliberty.api_sync_test(delay=delay, login=aniliberty_login, password=aniliberty_password, proxy=proxy)
    try_errors += stats[0]
    try_success += stats[1]

def dreamcast_sync():
    global try_errors, try_success
    print('\n=== DREAMCAST === SYNC TEST ===')
    stats = dreamcast.sync_test(proxy, dreamcast_mirror, GLOBAL_USE_LXML, delay)
    try_errors += stats[0]
    try_success += stats[1]

def dreamcast_async():
    global try_errors, try_success
    print('\n=== DREAMCAST === ASYNC TEST ===')
    stats = asyncio.run(dreamcast.async_test(proxy, dreamcast_mirror, GLOBAL_USE_LXML, delay))
    try_errors += stats[0]
    try_success += stats[1]

if __name__ == "__main__":
    proxy = None
    GLOBAL_USE_LXML = False
    KODIK_TOKEN = testconfig.KODIK_TOKEN
    GLOBAL_TOKEN_VALIDATION = False
    delay = 2
    animego_mirror = "animego.me"
    dreamcast_mirror = None
    shiki_mirror = None
    shiki_proxy = testconfig.SHIKI_PROXY
    aniliberty_login = testconfig.ANILIBERTY_LOGIN
    aniliberty_password = testconfig.ANILIBERTY_PASSWORD

    try_errors = 0
    try_success = 0

    t1 = time()

    kdk_sync()
    kdk_async()
    kdk_api()

    delay = 15 # Запросов много, плюс шики сильно ограничивает
    shiki_sync()
    shiki_async()

    delay = 2
    animego_sync()
    animego_async()
    
    jutsu_sync()

    aniliberty_api_sync()

    dreamcast_sync()
    dreamcast_async()

    t2 = time()
    print(f'\nTEST DONE!\nTotal errors: {try_errors}\nTotal success: {try_success}\nTest duration: {str(int((t2-t1)//60)).zfill(2)}:{str(int((t2-t1)%60)).zfill(2)}')