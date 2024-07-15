# Changelog

## To 1.0.0
- Added Kodik parser
    * Auto grabbing api key

## To 1.0.5
- Fixed dependencies
- Upload to pypi

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
- Added Shikimori parser (with peudo-api wrapper)
- Written tests for shikimori parser
- Added new tags for project ('shikimori', 'шикимори')