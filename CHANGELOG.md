# Changelog

## To 1.0.0
- Added Kodik parser
    * Auto grabbing api key

## To 1.0.5
- Fixed dependencies
- Upload to pypl

## To 1.1.0
- Written tests for kodik_parser
- Changed `get_token` function to `@static_method`

## To 1.2.0
- Added Aniboom parser
- Written tests for aniboom parser
- Added new tags for project ('aniboom', 'анибум', 'animego', 'анимего')

## To 1.2.1
- Fixed search (forgot to change debug value)

## To 1.2.2
- Fixed getting trailer embed (can be NoneType error)
- Fixed getting data for films (don't have an episode_num parameter, now required to pass `0` as episode_num)
- Written tests for new errors

## To 1.2.3
- Added flag for testing with or without using lxml parser
- Moved imports of individual modules to init (now import should be like: `from anime_parsers_ru import KodikParser` instead of `from anime_parsers_ru.parser_kodik import KodikParser`)

## To 1.3.0
- Added Jutsu parser (without search function)
- Written tests for jutsu parser
- Added new tags for project ('jutsu', 'джутсу')

## To 1.4.0
- Added Shikimori parser (with pseudo-api wrapper)
- Written tests for shikimori parser
- Added new tags for project ('shikimori', 'шикимори')

## To 1.4.1
- Added `additional_anime_info` to shikimori parser

## To 1.4.2
- Fixed bug with single quotes in ShikimoriParser
- Added preferred 'html.parser' when lxml is not being used

## To 1.4.3
- Added exception in AniboomParser for blocked players

## To 1.4.4
- Fixed AniboomParser - mpd playlist was without full link to server

## To 1.5.0
- Created internal_tools.py with classes for async parsers
- Added KodikParserAsync
- Done tests for KodikParserAsync
- Fix missplelling in docs for `search` function in KodikParser

## To 1.6.0
- Added ShikimoriParserAsync
- Done tests for ShikimoriParserAsync
- Added `url` and `status_code` parameters to internal_tools.Response

## To 1.6.1
- Set `use_lxml` as `False` by default.

## To 1.7.0
- Added AniboomParserAsync
- Done tests for AniboomParserAsync

## To 1.7.1
- Added `base_search_by_id` and `search_by_id` for KodikParser and KodikParserAsync
- Added tests for new functions and test for `search` function (for some reason i forgot to add it earlier)
- Added `link` parameter to result of `search` function

## To 1.7.2
- Fixed when shikimori parser couldn't get name of related media (if this media is clip, it has different html scheme for naming)

## To 1.8.0
- Added get_anime_list function to shikimori parser to get list of animes by filters

## To 1.8.1
- Updated get_anime_list function to shikimori parser to have ability to pass multiple arguments, also added genre and rating filters 

## To 1.8.2
- Fixed tests (TestShikimoriParser never actually worked, because async version had same class name)
- Added new Exception type (errors.ServiceIsOverloaded) to indicate http response code 429 (for shikimori parsers)
- Added docs about existing Exceptions

## To 1.8.3
- Fixed rare bug in shikimori parser `search` function. Some animes don't have any info about type, year, type. Now this values will be `None` if this anime appeared.

## To 1.9.0
Overall fixes and adjustments to KodikParser and KodikParserAsync

- Added `get_list` function to get ongoings*.
- Fixed `include_material_data` flag to actually work
- Added `only_anime` flag to filter only results where type is `anime` or `anime-serial`
- Moved json parser to separate function `_prettify_data` to avoid repeating code
- Polished and refactored some parts of README about KodikParser

## To 1.9.1
- Added release status filter in search functions to KodikParser (available: released, ongoing)
- Added `strict` flag to `search` function to KodikParser (kodik will search by title more strictly, less random unrelated results)

## To 1.9.2
- Fixed `search` function in KodikParser

## To 1.9.3
- Fixed timeout bug in AniboomParser (Added `referer` header to request in `fast_search` function)
- Added additional checks to `get_link`, `get_info`, `search_by_id` functions in KodikParser (now all passed integer parameters will be autoconverted into strings)
- Change imports of `errors` module to local (from: from anime_parser_ru.errors to from . import errors)
- Fixed mismatch with `TooManyRequests` and `ServiceIsOverloaded` exceptions and their http codes

Thx to @nichind for pointing these out

- Moved `tests.py` from src to project root directory 

## To 1.9.3 DEV
- Fixed AniBoom parser (Now _get_embed_link is actually getting aniboom links consistently)
- Added `mirror` parameter to parsers to allow for changing domains (excluding kodik)

## To 1.9.4
- Releasing 1.9.3 DEV

## To 1.9.5
- Changed returning None in _get_embed_link in Aniboom parser to raising NoResults exception

## To 1.10.0
- Global spelling fix (renamed errors.UnexpectedBehaviour -> errors.UnexpectedBehavior)
- Added KODIK_API.md file with docs for kodikapi.com
- Added `api_request` for KodikParser and KodikParserAsync to make straight api calls with minimum checks
- Changed functions in kodik parsers to work on `api_request` (base_search, base_search_by_id, get_list)

## To 1.11.0
- Added `api_kodik` file with abstraction for using kodik api. 
- Docs for KODIK_API now include docs for internal api_kodik documentation

## To 1.11.1
- Fixed issue with KodikParser (links are now not crypted), added toggle to enable decryption functions back. (Thx to @reihitotsu)

## To 1.11.2
- Added function to get translations and episodes info to Response class in kodik_api.py
- Fixed readme (ShikimoriParser.anime_info requires link, not id)

## To 1.11.3
- Added `sort` and `order` parameters to KodikList (thx @SHCDevelops)

## To 1.11.4
- Fixed `_convert_char` function in kodik_parser and kodik_parser_async (Kodik reimplemented crypting link now with different step) (thx @reihitotsu)
- Removed toggle to enable decryption functions back (v 1.11.1)
- Added new exception `DecryptionFailure` when decrypting kodik link failed (thx @reihitotsu)

## To 1.11.5
- Fixed KodikParser link parsing and decoding (thx @reihitotsu)

## To 1.11.6
- Fixed bug in shikimori parser: When status is 'вышло' but only one date is specified, then no date was grabbed

## To 1.12.0
- Replace standard link in aniboom parser to refer to mirror animego.me instead of animego.org.
- Fixed async aniboom parser to use mirror
- Fixed mpd playlist completion to include full uri

## To 1.12.1
- Fixed mpd playlist for aniboom to check if playlist is mpd or m3u8
- Added TooManyRequests error case for aniboom parser

## To 1.12.2
- Improved error handling in kodik parser and api_kodik
- Added function to validate token (token from function get_token is now invalid for some api requests)

## To 1.12.3
- Updated function `get_token` in KodikParser: getting full token from github repository (thx @deathnoragami)

## To 1.13.0
- Added functions to get m3u8 playlists (both link and file content) for KodikParser
- Fixed KODIK_API.md (render error due to misalignment)

## To 1.13.1
- Fixed edge case with video names in ShikimoriParser