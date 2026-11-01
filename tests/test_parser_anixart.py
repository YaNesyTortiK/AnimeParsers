import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest


PACKAGE_PATH = Path(__file__).parents[1] / "src" / "anime_parsers_ru"
package = types.ModuleType("anime_parsers_ru")
package.__path__ = [str(PACKAGE_PATH)]
sys.modules.setdefault("anime_parsers_ru", package)
spec = importlib.util.spec_from_file_location(
    "anime_parsers_ru.parser_anixart", PACKAGE_PATH / "parser_anixart.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
AnixartParser = module.AnixartParser
from anime_parsers_ru import errors


EXPECTED_ANIXART_STUDIOS = [
    "A-1 Pictures",
    "A.C.G.T",
    "ACTAS, Inc",
    "ACiD FiLM",
    "AIC A.S.T.A",
    "AIC PLUS",
    "AIC Spirits",
    "AIC",
    "Animac",
    "ANIMATE",
    "Aniplex",
    "ARMS",
    "Artland",
    "ARTMIC Studios",
    "Asahi Production",
    "Asia-Do",
    "ASHI",
    "Asread",
    "Asmik Ace",
    "Aubeck",
    "BM Entertainment",
    "Bandai Visua",
    "Barnum Studio",
    "Bee Train",
    "BeSTACK",
    "Blender Foundation",
    "Bones",
    "Brains Base",
    "Bridge",
    "Cinema Citrus",
    "Chaos Project",
    "Cherry Lips",
    "David Production",
    "Daume",
    "Doumu",
    "Dax International",
    "DLE INC",
    "Digital Frontier",
    "Digital Works",
    "Diomedea",
    "DIRECTIONS Inc",
    "Dogakobo",
    "Dofus",
    "Encourage Films",
    "Feel",
    "Fifth Avenue",
    "Five Ways",
    "Fuji TV",
    "Foursome",
    "GRAM Studio",
    "G&G Entertainment",
    "Gainax",
    "GANSIS",
    "Gathering",
    "Gonzino",
    "Gonzo",
    "GoHands",
    "Green Bunny",
    "Group TAC",
    "Hal Film Maker",
    "Hasbro Studios",
    "h.m.p",
    "Himajin",
    "Hoods Entertainment",
    "Idea Factory",
    "J.C.Staff",
    "KANSAI",
    "Kaname Production",
    "Kitty Films",
    "Knack",
    "Kokusai Eigasha",
    "KSS (студия)",
    "Kyoto Animation",
    "Lemon Heart",
    "LMD",
    "Madhouse Studios",
    "Magic Bus",
    "Manglobe Inc.",
    "Manpuku Jinja",
    "MAPPA",
    "Milky",
    "Minamimachi Bugyosho",
    "Media Blasters",
    "Mook Animation",
    "Moonrock",
    "MOVIC",
    "Mushi Productions",
    "Natural High",
    "Nippon Animation",
    "Nomad",
    "Lerche",
    "OB Planning",
    "Office AO",
    "Ordet",
    "Oriental Light and Magic",
    "OLM Inc.",
    "P.A. Works",
    "Palm Studio",
    "Pastel",
    "Phoenix Entertainment",
    "Picture Magic",
    "Pink",
    "Pink Pineapple",
    "Planet",
    "Plum",
    "PPM",
    "Primastea",
    "Production I.G",
    "Project No.9",
    "Radix",
    "Rikuentai",
    "Robot",
    "Satelight",
    "Seven",
    "Seven Arcs",
    "Shaft",
    "Silver Link",
    "Shinei Animation",
    "Shogakukan Music & Digital Entertainment",
    "Soft on Demand",
    "Starchild Records",
    "Studio 9 Maiami",
    "Studio Tulip",
    "Studio 4°C",
    "Studio e.go!",
    "Studio A.P.P.P",
    "Studio Barcelona",
    "Studio Blanc",
    "Studio Comet",
    "Studio Deen",
    "Studio Fantasia",
    "Studio Flag",
    "Studio Gallop",
    "Studio Ghibli",
    "Studio Guts",
    "Studio Gokumi",
    "Studio Rikka",
    "Studio Hibari",
    "Studio Junio",
    "Studio Khara",
    "Studio Live",
    "Studio Matrix",
    "Studio Pierrot",
    "Studio Egg",
    "Sunrise",
    "Synergy SP",
    "Synergy Japan",
    "Tatsunoko Production",
    "Tele-Cartoon Japan",
    "Telecom Animation Film",
    "Tezuka Productions",
    "The Answer Studio",
    "TMS",
    "TNK",
    "Toei Animation",
    "Tokyo Kids",
    "TYO Animations",
    "Transarts",
    "Triangle Staff",
    "Trinet Entertainment",
    "Ufotable",
    "Vega Entertainment",
    "Victor Entertainment",
    "Viewworks",
    "White Fox",
    "Wonder Farm",
    "XEBEC-M2",
    "Xebec",
    "Yumeta Company",
    "Zexcs",
    "Zuiyo Eizo",
    "8bit",
]
EXPECTED_ANIXART_GENRES = [
    "авангард",
    "гурман",
    "драма",
    "комедия",
    "повседневность",
    "приключения",
    "романтика",
    "сверхъестественное",
    "спорт",
    "тайна",
    "триллер",
    "ужасы",
    "фантастика",
    "фэнтези",
    "экшен",
    "эротика",
    "этти",
    "детское",
    "дзёсей",
    "сэйнэн",
    "сёдзё",
    "сёдзё-ай",
    "сёнен",
    "сёнен-ай",
    "CGDCT",
    "антропоморфизм",
    "боевые искусства",
    "вампиры",
    "взрослые персонажи",
    "видеоигры",
    "военное",
    "выживание",
    "гарем",
    "гонки",
    "городское фэнтези",
    "гэг-юмор",
    "детектив",
    "жестокость",
    "забота о детях",
    "злодейка",
    "игра с высокими ставками",
    "идолы (жен.)",
    "идолы (муж.)",
    "изобразительное искусство",
    "исполнительское искусство",
    "исторический",
    "исэкай",
    "иясикэй",
    "командный спорт",
    "космос",
    "кроссдрессинг",
    "культура отаку",
    "любовный многоугольник",
    "магическая смена пола",
    "махо-сёдзё",
    "медицина",
    "меха",
    "мифология",
    "музыка",
    "образовательное",
    "организованная преступность",
    "пародия",
    "питомцы",
    "психологическое",
    "путешествие во времени",
    "работа",
    "реверс-гарем",
    "реинкарнация",
    "романтический подтекст",
    "самураи",
    "спортивные единоборства",
    "стратегические игры",
    "супер сила",
    "удостоено наград",
    "хулиганы",
    "школа",
    "шоу-бизнес",
]


def response(payload, status_code=200):
    result = Mock()
    result.status_code = status_code
    result.json.return_value = payload
    result.raise_for_status.return_value = None
    return result


def test_filter_sort_constants_match_android_values():
    assert AnixartParser.SORT_DATE_UPDATE == 0
    assert AnixartParser.SORT_GRADE == 1
    assert AnixartParser.SORT_YEAR == 2
    assert AnixartParser.SORT_POPULAR == 3


def test_get_studios_returns_complete_ordered_anixart_8_5_2_values():
    studios = AnixartParser.get_studios()

    assert studios == EXPECTED_ANIXART_STUDIOS
    assert len(studios) == 172
    assert "Неважно" not in studios
    assert not any(studio.startswith("@") for studio in studios)

    studios.append("caller mutation")

    next_studios = AnixartParser.get_studios()
    assert next_studios == EXPECTED_ANIXART_STUDIOS
    assert next_studios is not studios


def test_get_genres_returns_complete_ordered_anixart_8_5_2_values():
    genres = AnixartParser.get_genres()

    assert genres == EXPECTED_ANIXART_GENRES
    assert len(genres) == 77
    assert "Неважно" not in genres
    assert not any(genre.startswith("@") for genre in genres)

    genres.append("caller mutation")

    next_genres = AnixartParser.get_genres()
    assert next_genres == EXPECTED_ANIXART_GENRES
    assert next_genres is not genres


def test_filter_sends_complete_request_and_returns_pagination_envelope():
    session = Mock()
    content = [
        {"id": 2, "title": "Второй"},
        {"id": 1, "title_original": "First"},
    ]
    session.post.return_value = response(
        {
            "code": 0,
            "content": content,
            "current_page": 3,
            "total_count": 12,
            "total_page_count": 4,
        }
    )
    parser = AnixartParser(base_url="https://example.test/api", session=session)

    result = parser.filter(
        page=3,
        extended=False,
        category_id=2,
        country="Япония",
        end_year=2024,
        episode_duration_from=20,
        episode_duration_to=30,
        episodes_from=1,
        episodes_to=24,
        is_genres_exclude_mode_enabled=True,
        season=2,
        source="Манга",
        start_year=2000,
        status_id=1,
        studio="Bones",
        sort=AnixartParser.SORT_POPULAR,
        genres=["Экшен", "Драма"],
        profile_list_exclusions=[10, 11],
        types=[1, 2],
        age_ratings=[3, 4],
    )

    assert result == {
        "content": content,
        "current_page": 3,
        "total_count": 12,
        "total_page_count": 4,
    }
    assert result["content"] is content
    session.post.assert_called_once_with(
        "https://example.test/api/filter/3?extended_mode=false",
        json={
            "category_id": 2,
            "country": "Япония",
            "end_year": 2024,
            "episode_duration_from": 20,
            "episode_duration_to": 30,
            "episodes_from": 1,
            "episodes_to": 24,
            "is_genres_exclude_mode_enabled": True,
            "season": 2,
            "source": "Манга",
            "start_year": 2000,
            "status_id": 1,
            "studio": "Bones",
            "sort": 3,
            "genres": ["Экшен", "Драма"],
            "profile_list_exclusions": [10, 11],
            "types": [1, 2],
            "age_ratings": [3, 4],
        },
        headers=parser._HEADERS,
        proxies=None,
        timeout=10,
    )


def test_filter_defaults_use_fresh_empty_lists_and_allow_empty_content():
    session = Mock()
    session.post.return_value = response(
        {
            "code": 0,
            "content": [],
            "current_page": 0,
            "total_count": 0,
            "total_page_count": 0,
        }
    )
    parser = AnixartParser(session=session)

    expected = {
        "content": [],
        "current_page": 0,
        "total_count": 0,
        "total_page_count": 0,
    }
    assert parser.filter() == expected
    assert parser.filter() == expected

    first_body = session.post.call_args_list[0].kwargs["json"]
    second_body = session.post.call_args_list[1].kwargs["json"]
    assert first_body == {
        "category_id": None,
        "country": None,
        "end_year": None,
        "episode_duration_from": None,
        "episode_duration_to": None,
        "episodes_from": None,
        "episodes_to": None,
        "is_genres_exclude_mode_enabled": False,
        "season": None,
        "source": None,
        "start_year": None,
        "status_id": None,
        "studio": None,
        "sort": 0,
        "genres": [],
        "profile_list_exclusions": [],
        "types": [],
        "age_ratings": [],
    }
    for key in ("genres", "profile_list_exclusions", "types", "age_ratings"):
        assert first_body[key] is not second_body[key]


def test_filter_sends_zero_profile_list_exclusion_unchanged():
    session = Mock()
    session.post.return_value = response(
        {
            "code": 0,
            "content": [],
            "current_page": 0,
            "total_count": 0,
            "total_page_count": 0,
        }
    )
    parser = AnixartParser(session=session)

    parser.filter(profile_list_exclusions=[0])

    assert session.post.call_args.kwargs["json"]["profile_list_exclusions"] == [0]


@pytest.mark.parametrize(
    "field",
    [
        "page",
        "category_id",
        "end_year",
        "episode_duration_from",
        "episode_duration_to",
        "episodes_from",
        "episodes_to",
        "season",
        "start_year",
        "status_id",
        "sort",
    ],
)
def test_filter_rejects_booleans_for_integer_fields(field):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(TypeError, match=field):
        parser.filter(**{field: True})
    session.post.assert_not_called()


@pytest.mark.parametrize(
    "field",
    [
        "page",
        "episode_duration_from",
        "episode_duration_to",
        "episodes_from",
        "episodes_to",
    ],
)
def test_filter_rejects_negative_page_count_and_duration_fields(field):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(ValueError, match=field):
        parser.filter(**{field: -1})
    session.post.assert_not_called()


@pytest.mark.parametrize("field", ["category_id", "status_id"])
def test_filter_requires_positive_scalar_ids(field):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(ValueError, match=field):
        parser.filter(**{field: 0})
    session.post.assert_not_called()


@pytest.mark.parametrize("value", [-1, 4])
def test_filter_rejects_unknown_sort_values(value):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(ValueError, match="sort"):
        parser.filter(sort=value)
    session.post.assert_not_called()


@pytest.mark.parametrize("field", ["extended", "is_genres_exclude_mode_enabled"])
def test_filter_requires_boolean_flags(field):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(TypeError, match=field):
        parser.filter(**{field: 1})
    session.post.assert_not_called()


@pytest.mark.parametrize("field", ["country", "source", "studio"])
@pytest.mark.parametrize("value", [1, "  "])
def test_filter_rejects_invalid_optional_strings(field, value):
    session = Mock()
    parser = AnixartParser(session=session)

    error_type = TypeError if value == 1 else ValueError
    with pytest.raises(error_type, match=field):
        parser.filter(**{field: value})
    session.post.assert_not_called()


@pytest.mark.parametrize(
    ("lower_name", "upper_name", "kwargs"),
    [
        ("start_year", "end_year", {"start_year": 2025, "end_year": 2024}),
        ("episodes_from", "episodes_to", {"episodes_from": 13, "episodes_to": 12}),
        (
            "episode_duration_from",
            "episode_duration_to",
            {"episode_duration_from": 31, "episode_duration_to": 30},
        ),
    ],
)
def test_filter_rejects_reversed_ranges(lower_name, upper_name, kwargs):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(ValueError, match=f"{lower_name}.*{upper_name}"):
        parser.filter(**kwargs)
    session.post.assert_not_called()


@pytest.mark.parametrize(
    "field", ["genres", "profile_list_exclusions", "types", "age_ratings"]
)
def test_filter_list_arguments_must_be_lists(field):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(TypeError, match=field):
        parser.filter(**{field: ()})
    session.post.assert_not_called()


@pytest.mark.parametrize(
    "field", ["profile_list_exclusions", "types", "age_ratings"]
)
@pytest.mark.parametrize("value", [True, 1.5, -1])
def test_filter_integer_lists_require_non_negative_non_boolean_ids(field, value):
    session = Mock()
    parser = AnixartParser(session=session)

    error_type = TypeError if value is True or value == 1.5 else ValueError
    with pytest.raises(error_type, match=field):
        parser.filter(**{field: [value]})
    session.post.assert_not_called()


@pytest.mark.parametrize("field", ["types", "age_ratings"])
def test_filter_type_and_age_rating_ids_must_be_positive(field):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(ValueError, match=field):
        parser.filter(**{field: [0]})
    session.post.assert_not_called()


@pytest.mark.parametrize(
    ("value", "error_type"),
    [([1], TypeError), ([""], ValueError), (["  "], ValueError)],
)
def test_filter_genres_require_nonempty_strings(value, error_type):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(error_type, match="genres"):
        parser.filter(genres=value)
    session.post.assert_not_called()


def test_filter_copies_caller_owned_lists_before_request():
    caller_lists = {
        "genres": ["Экшен"],
        "profile_list_exclusions": [10],
        "types": [1],
        "age_ratings": [2],
    }
    originals = {key: list(value) for key, value in caller_lists.items()}
    session = Mock()

    def mutate_request(*args, **kwargs):
        for value in kwargs["json"].values():
            if isinstance(value, list):
                value.append("server mutation")
        return response(
            {
                "code": 0,
                "content": [],
                "current_page": 0,
                "total_count": 0,
                "total_page_count": 0,
            }
        )

    session.post.side_effect = mutate_request
    parser = AnixartParser(session=session)

    parser.filter(**caller_lists)

    assert caller_lists == originals
    request = session.post.call_args.kwargs["json"]
    for key, caller_value in caller_lists.items():
        assert request[key] is not caller_value


@pytest.mark.parametrize(
    "field", ["current_page", "total_count", "total_page_count"]
)
@pytest.mark.parametrize("value", [True, "1", -1, None])
def test_filter_rejects_invalid_pagination_values(field, value):
    payload = {
        "code": 0,
        "content": [],
        "current_page": 0,
        "total_count": 0,
        "total_page_count": 0,
    }
    payload[field] = value
    session = Mock()
    session.post.return_value = response(payload)
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match=field):
        parser.filter()


@pytest.mark.parametrize(
    "field", ["current_page", "total_count", "total_page_count"]
)
def test_filter_requires_every_pagination_field(field):
    payload = {
        "code": 0,
        "content": [],
        "current_page": 0,
        "total_count": 0,
        "total_page_count": 0,
    }
    payload.pop(field)
    session = Mock()
    session.post.return_value = response(payload)
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match=field):
        parser.filter()


@pytest.mark.parametrize(
    "content",
    [
        None,
        {},
        [None],
        [[]],
        [{}],
        [{"id": True, "title": "Наруто"}],
        [{"id": "42", "title": "Наруто"}],
        [{"id": 42}],
        [{"id": 42, "title": "  "}],
        [{"id": 42, "title": None, "title_ru": ""}],
    ],
)
def test_filter_rejects_malformed_release_content(content):
    session = Mock()
    session.post.return_value = response(
        {
            "code": 0,
            "content": content,
            "current_page": 0,
            "total_count": 1,
            "total_page_count": 1,
        }
    )
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="content"):
        parser.filter()


def test_search_sends_expected_request_and_returns_releases():
    session = Mock()
    releases = [{"id": 42, "title": "Наруто"}]
    session.post.return_value = response({"code": 0, "releases": releases})
    parser = AnixartParser(
        base_url="https://example.test/api/",
        proxy="socks5://proxy.test:1080",
        timeout=7,
        session=session,
    )

    assert parser.search("Наруто", page=2, search_by=1) == releases
    session.post.assert_called_once_with(
        "https://example.test/api/search/releases/2",
        json={"query": "Наруто", "searchBy": 1},
        headers={
            "Accept": "application/json",
            "API-Version": "v2",
            "User-Agent": "anime-parsers-ru/AnixartParser",
        },
        proxies={
            "http": "socks5://proxy.test:1080",
            "https": "socks5://proxy.test:1080",
        },
        timeout=7,
    )


def test_search_extended_returns_releases_and_preserves_valid_related_fields():
    session = Mock()
    releases = [{"id": 42, "title": "Наруто"}]
    related = {
        "id": 7,
        "release_count": 2,
        "name_ru": "Наруто",
        "name": "Naruto",
        "image": "https://example.test/related.jpg",
        "description": "Связанные релизы",
        "images": ["https://example.test/1.jpg"],
        "unknown": {"preserved": True},
    }
    session.post.return_value = response(
        {"code": 0, "releases": releases, "related": related}
    )
    parser = AnixartParser(
        base_url="https://example.test/api",
        proxy="socks5://proxy.test:1080",
        timeout=7,
        session=session,
    )

    result = parser.search_extended("Наруто", page=2, search_by=1)

    assert result == {"releases": releases, "related": related}
    assert result["related"] is related
    session.post.assert_called_once_with(
        "https://example.test/api/search/releases/2",
        json={"query": "Наруто", "searchBy": 1},
        headers=parser._HEADERS,
        proxies={
            "http": "socks5://proxy.test:1080",
            "https": "socks5://proxy.test:1080",
        },
        timeout=7,
    )


@pytest.mark.parametrize(
    "related",
    [
        None,
        {
            "id": 1,
            "release_count": 0,
            "name": "Original name",
            "image": "image.jpg",
            "description": None,
            "images": None,
        },
        {
            "id": 1,
            "release_count": 0,
            "name_ru": "Русское название",
            "image": "image.jpg",
            "description": "",
            "images": ["", "image-2.jpg"],
        },
    ],
)
def test_search_extended_accepts_nullable_related_fields(related):
    session = Mock()
    session.post.return_value = response(
        {"code": 0, "releases": [{"id": 1, "title": "Аниме"}], "related": related}
    )
    parser = AnixartParser(session=session)

    assert parser.search_extended("Аниме")["related"] is related


@pytest.mark.parametrize(
    ("args", "error_type"),
    [
        ((1,), TypeError),
        (("  ",), ValueError),
        (("x", True), TypeError),
        (("x", "0"), TypeError),
        (("x", -1), ValueError),
        (("x", 0, False), TypeError),
        (("x", 0, "0"), TypeError),
        (("x", 0, -1), ValueError),
    ],
)
def test_search_extended_validates_arguments_before_request(args, error_type):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(error_type):
        parser.search_extended(*args)
    session.post.assert_not_called()


def test_empty_successful_search_extended_raises_no_results():
    session = Mock()
    session.post.return_value = response({"code": 0, "releases": [], "related": None})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.NoResults, match="ничего не найдено"):
        parser.search_extended("Несуществующее аниме")


def test_search_extended_requires_related_field():
    session = Mock()
    session.post.return_value = response(
        {"code": 0, "releases": [{"id": 1, "title": "Аниме"}]}
    )
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="related"):
        parser.search_extended("Аниме")


@pytest.mark.parametrize("releases", [None, {}, [None], [{"id": 1, "title": " "}]])
def test_search_extended_rejects_malformed_releases(releases):
    session = Mock()
    session.post.return_value = response(
        {"code": 0, "releases": releases, "related": None}
    )
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="releases"):
        parser.search_extended("Аниме")


def valid_related(**changes):
    related = {
        "id": 1,
        "release_count": 0,
        "name_ru": "Название",
        "image": "image.jpg",
        "description": None,
        "images": None,
    }
    related.update(changes)
    return related


def related_without(field):
    related = valid_related()
    related.pop(field)
    return related


@pytest.mark.parametrize(
    "related",
    [
        [],
        "related",
        related_without("id"),
        valid_related(id=None),
        valid_related(id=True),
        valid_related(id=0),
        valid_related(id=-1),
        valid_related(id="1"),
        valid_related(release_count=None),
        valid_related(release_count=True),
        valid_related(release_count=-1),
        valid_related(release_count="0"),
        related_without("name_ru"),
        valid_related(name_ru=" "),
        valid_related(name_ru=None),
        valid_related(name_ru="", name=" "),
        related_without("image"),
        valid_related(image=None),
        valid_related(image=" "),
        related_without("description"),
        valid_related(description=1),
        related_without("images"),
        valid_related(images="image.jpg"),
        valid_related(images=["image.jpg", None]),
    ],
)
def test_search_extended_rejects_malformed_related(related):
    session = Mock()
    session.post.return_value = response(
        {
            "code": 0,
            "releases": [{"id": 1, "title": "Аниме"}],
            "related": related,
        }
    )
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="related"):
        parser.search_extended("Аниме")


def test_get_schedule_returns_seven_ordered_days_and_sends_no_params():
    session = Mock()
    payload = {
        "code": 0,
        "monday": [{"id": 1, "title": "Понедельник"}],
        "tuesday": [],
        "wednesday": [{"id": 3, "title_ru": "Среда"}],
        "thursday": [],
        "friday": [],
        "saturday": [{"id": 6, "title_original": "Saturday"}],
        "sunday": [],
        "ignored": "value",
    }
    session.get.return_value = response(payload)
    parser = AnixartParser(base_url="https://example.test/api", session=session)

    result = parser.get_schedule()

    assert result == {key: payload[key] for key in payload if key not in ("code", "ignored")}
    assert list(result) == [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    session.get.assert_called_once_with(
        "https://example.test/api/schedule",
        headers=parser._HEADERS,
        proxies=None,
        timeout=10,
    )


@pytest.mark.parametrize("value", [None, {}, "monday"])
def test_get_schedule_requires_each_day_to_be_a_list(value):
    payload = {
        "code": 0,
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": [],
    }
    payload["monday"] = value
    session = Mock()
    session.get.return_value = response(payload)
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="monday"):
        parser.get_schedule()


@pytest.mark.parametrize(
    "release",
    [None, {}, {"id": True, "title": "Аниме"}, {"id": 1, "title": "  "}],
)
def test_get_schedule_validates_releases_in_every_day(release):
    payload = {
        "code": 0,
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": [release],
    }
    session = Mock()
    session.get.return_value = response(payload)
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="sunday"):
        parser.get_schedule()


def test_get_related_releases_returns_pagination_without_arithmetic_checks():
    session = Mock()
    content = [{"id": 42, "title": "Связанный релиз"}]
    session.get.return_value = response(
        {
            "code": 0,
            "content": content,
            "current_page": 0,
            "total_count": 27,
            "total_page_count": 0,
        }
    )
    parser = AnixartParser(base_url="https://example.test/api", session=session)

    assert parser.get_related_releases(7) == {
        "content": content,
        "current_page": 0,
        "total_count": 27,
        "total_page_count": 0,
    }
    session.get.assert_called_once_with(
        "https://example.test/api/related/7/0",
        headers=parser._HEADERS,
        proxies=None,
        timeout=10,
    )


def test_get_related_releases_allows_empty_content_and_nonzero_page():
    session = Mock()
    session.get.return_value = response(
        {
            "code": 0,
            "content": [],
            "current_page": 3,
            "total_count": 0,
            "total_page_count": 0,
        }
    )
    parser = AnixartParser(session=session)

    assert parser.get_related_releases(7, page=3)["content"] == []
    assert session.get.call_args.args[0].endswith("related/7/3")


@pytest.mark.parametrize(
    ("args", "error_type"),
    [
        ((True,), TypeError),
        (("1",), TypeError),
        ((0,), ValueError),
        ((-1,), ValueError),
        ((1, False), TypeError),
        ((1, "0"), TypeError),
        ((1, -1), ValueError),
    ],
)
def test_get_related_releases_validates_arguments_before_request(args, error_type):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(error_type):
        parser.get_related_releases(*args)
    session.get.assert_not_called()


@pytest.mark.parametrize("field", ["current_page", "total_count", "total_page_count"])
@pytest.mark.parametrize("value", [None, True, "0", -1])
def test_get_related_releases_rejects_invalid_pagination(field, value):
    payload = {
        "code": 0,
        "content": [],
        "current_page": 0,
        "total_count": 0,
        "total_page_count": 0,
    }
    payload[field] = value
    session = Mock()
    session.get.return_value = response(payload)
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match=field):
        parser.get_related_releases(1)


@pytest.mark.parametrize("content", [None, {}, [None], [{"id": 1, "title": " "}]])
def test_get_related_releases_rejects_malformed_content(content):
    session = Mock()
    session.get.return_value = response(
        {
            "code": 0,
            "content": content,
            "current_page": 0,
            "total_count": 1,
            "total_page_count": 1,
        }
    )
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="content"):
        parser.get_related_releases(1)


@pytest.mark.parametrize(("extended", "query_value"), [(True, "true"), (False, "false")])
def test_get_random_release_sends_boolean_query_and_returns_release(
    extended, query_value
):
    session = Mock()
    release = {"id": 42, "title_alt": "Random title", "unknown": "preserved"}
    session.get.return_value = response({"code": 0, "release": release})
    parser = AnixartParser(base_url="https://example.test/api", session=session)

    assert parser.get_random_release(extended=extended) is release
    session.get.assert_called_once_with(
        f"https://example.test/api/release/random?extended_mode={query_value}",
        headers=parser._HEADERS,
        proxies=None,
        timeout=10,
    )


@pytest.mark.parametrize("extended", [1, 0, None, "true"])
def test_get_random_release_requires_exact_boolean(extended):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(TypeError, match="extended"):
        parser.get_random_release(extended)
    session.get.assert_not_called()


@pytest.mark.parametrize(
    "release",
    [
        None,
        [],
        {},
        {"id": True, "title": "Аниме"},
        {"id": 0, "title": "Аниме"},
        {"id": -1, "title": "Аниме"},
        {"id": "1", "title": "Аниме"},
        {"id": 1},
        {"id": 1, "title": "  ", "title_ru": None},
    ],
)
def test_get_random_release_rejects_malformed_release(release):
    session = Mock()
    session.get.return_value = response({"code": 0, "release": release})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="release"):
        parser.get_random_release()


def test_anime_info_uses_release_path_and_extended_mode():
    session = Mock()
    release = {"id": 42, "title": "Наруто"}
    session.get.return_value = response({"code": 0, "release": release})
    parser = AnixartParser(base_url="https://example.test/api", session=session)

    assert parser.anime_info(42, extended=False) == release
    session.get.assert_called_once_with(
        "https://example.test/api/release/42?extended_mode=false",
        headers=parser._HEADERS,
        proxies=None,
        timeout=10,
    )


def test_episode_catalog_methods_extract_payloads_and_optional_sort():
    session = Mock()
    types = [{"id": 1, "name": "Озвучка"}]
    sources = [{"id": 2, "name": "Студия"}]
    episodes = [
        {
            "position": 1,
            "name": "Серия 1",
            "iframe": True,
            "quality": 720,
            "url": "https://external.test/1",
            "sourceId": 2,
            "releaseId": 42,
        }
    ]
    session.get.side_effect = [
        response({"code": 0, "types": types}),
        response({"code": 0, "sources": sources}),
        response({"code": 0, "episodes": episodes}),
        response({"code": 0, "episodes": episodes}),
    ]
    parser = AnixartParser(base_url="https://example.test/", session=session)

    assert parser.get_types(42) == types
    assert parser.get_sources(42, 1) == sources
    assert parser.get_episodes(42, 1, 2) == episodes
    assert parser.get_episodes(42, 1, 2, sort=1) == episodes
    assert [call.args[0] for call in session.get.call_args_list] == [
        "https://example.test/episode/42",
        "https://example.test/episode/42/1",
        "https://example.test/episode/42/1/2",
        "https://example.test/episode/42/1/2",
    ]
    assert "params" not in session.get.call_args_list[2].kwargs
    assert session.get.call_args_list[3].kwargs["params"] == {"sort": 1}


def test_empty_successful_search_raises_no_results():
    session = Mock()
    session.post.return_value = response({"code": 0, "releases": []})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.NoResults, match="ничего не найдено"):
        parser.search("Несуществующее аниме")


@pytest.mark.parametrize(
    "release",
    [
        None,
        [],
        {},
        {"id": True, "title": "Наруто"},
        {"id": "42", "title": "Наруто"},
        {"id": 42},
        {"id": 42, "title": "  "},
        {"id": 42, "title": None, "title_ru": ""},
    ],
)
def test_search_rejects_malformed_release_items(release):
    session = Mock()
    session.post.return_value = response({"code": 0, "releases": [release]})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="releases"):
        parser.search("Наруто")


@pytest.mark.parametrize("release", [{}, {"id": True}, {"id": "42"}])
def test_anime_info_rejects_empty_or_invalid_release_metadata(release):
    session = Mock()
    session.get.return_value = response({"code": 0, "release": release})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="release"):
        parser.anime_info(42)


def test_anime_info_rejects_release_id_that_differs_from_request():
    session = Mock()
    session.get.return_value = response({"code": 0, "release": {"id": 43}})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="release"):
        parser.anime_info(42)


def test_http_errors_raise_service_error():
    failed_response = response({}, status_code=503)
    failed_response.raise_for_status.side_effect = module.requests.HTTPError(
        "503 Server Error"
    )
    session = Mock()
    session.get.return_value = failed_response
    parser = AnixartParser(session=session)

    with pytest.raises(errors.ServiceError, match="HTTP"):
        parser.get_types(42)


@pytest.mark.parametrize(
    ("code", "error_type"),
    [
        (1, errors.ServiceError),
        (402, errors.ContentBlocked),
        (403, errors.ContentBlocked),
    ],
)
def test_nonzero_application_codes_raise_project_errors(code, error_type):
    session = Mock()
    session.get.return_value = response({"code": code, "types": []})
    parser = AnixartParser(session=session)

    with pytest.raises(error_type, match=str(code)):
        parser.get_types(42)


@pytest.mark.parametrize(
    "payload",
    [
        ValueError("invalid json"),
        [],
        {},
        {"code": False, "types": []},
        {"code": 0},
        {"code": 0, "types": {}},
    ],
)
def test_malformed_responses_raise_unexpected_behavior(payload):
    malformed_response = response(payload)
    if isinstance(payload, Exception):
        malformed_response.json.side_effect = payload
    session = Mock()
    session.get.return_value = malformed_response
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="ответ"):
        parser.get_types(42)


@pytest.mark.parametrize(
    ("payload_key", "path", "call"),
    [
        ("types", "episode/42", lambda parser: parser.get_types(42)),
        (
            "sources",
            "episode/42/1",
            lambda parser: parser.get_sources(42, 1),
        ),
    ],
)
def test_type_and_source_names_must_be_strings(payload_key, path, call):
    session = Mock()
    session.get.return_value = response(
        {"code": 0, payload_key: [{"id": 1, "name": None}]}
    )
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match=payload_key):
        call(parser)
    assert session.get.call_args.args[0].endswith(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("position", True),
        ("sourceId", "10"),
        ("releaseId", 42.0),
        ("iframe", 1),
        ("iframe", "https://player.test/1"),
        ("quality", True),
        ("quality", "720p"),
        ("name", None),
        ("url", ""),
        ("url", "   "),
        ("url", "/player/1"),
        ("url", "ftp://external.test/1"),
        ("url", "http://[invalid"),
    ],
)
def test_episodes_reject_malformed_field_values(field, value):
    episode = {
        "position": 1,
        "name": "Серия 1",
        "iframe": True,
        "quality": 720,
        "url": "https://external.test/1",
        "sourceId": 10,
        "releaseId": 42,
    }
    episode[field] = value
    session = Mock()
    session.get.return_value = response({"code": 0, "episodes": [episode]})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="episodes"):
        parser.get_episodes(42, 1, 10)


@pytest.mark.parametrize(
    ("field", "value"),
    [("releaseId", 43), ("sourceId", 11)],
)
def test_episodes_reject_ids_that_differ_from_the_request(field, value):
    episode = {
        "position": 1,
        "name": "Серия 1",
        "iframe": True,
        "quality": 720,
        "url": "https://external.test/1",
        "sourceId": 10,
        "releaseId": 42,
    }
    episode[field] = value
    session = Mock()
    session.get.return_value = response({"code": 0, "episodes": [episode]})
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="episodes"):
        parser.get_episodes(42, 1, 10)


@pytest.mark.parametrize(
    ("kwargs", "error_type"),
    [
        ({"base_url": 1}, TypeError),
        ({"base_url": "  "}, ValueError),
        ({"proxy": 1}, TypeError),
        ({"timeout": True}, TypeError),
        ({"timeout": 0}, ValueError),
        ({"session": object()}, TypeError),
    ],
)
def test_constructor_rejects_invalid_arguments(kwargs, error_type):
    with pytest.raises(error_type):
        AnixartParser(**kwargs)


def test_constructor_keeps_the_exact_injected_session():
    session = Mock()
    session.__bool__ = Mock(return_value=False)

    parser = AnixartParser(session=session)

    assert parser.session is session


@pytest.mark.parametrize(
    ("call", "error_type"),
    [
        (lambda parser: parser.search(1), TypeError),
        (lambda parser: parser.search("  "), ValueError),
        (lambda parser: parser.search("x", page=True), TypeError),
        (lambda parser: parser.search("x", page=-1), ValueError),
        (lambda parser: parser.search("x", search_by=False), TypeError),
        (lambda parser: parser.anime_info(0), ValueError),
        (lambda parser: parser.anime_info(1, extended=1), TypeError),
        (lambda parser: parser.get_types(True), TypeError),
        (lambda parser: parser.get_sources(1, "2"), TypeError),
        (lambda parser: parser.get_episodes(1, 2, False), TypeError),
        (lambda parser: parser.get_episodes(1, 2, 3, sort=True), TypeError),
    ],
)
def test_public_methods_validate_arguments_before_request(call, error_type):
    session = Mock()
    parser = AnixartParser(session=session)

    with pytest.raises(error_type):
        call(parser)
    session.get.assert_not_called()
    session.post.assert_not_called()


def test_player_urls_preserve_server_order_context_and_fail_fast():
    session = Mock()
    session.get.side_effect = [
        response(
            {
                "code": 0,
                "types": [
                    {"id": 2, "name": "Субтитры"},
                    {"id": 1, "name": "Озвучка"},
                ],
            }
        ),
        response({"code": 0, "sources": [{"id": 20, "name": "Source A"}]}),
        response(
            {
                "code": 0,
                "episodes": [
                    {
                        "position": 2,
                        "name": "Серия 2",
                        "iframe": True,
                        "quality": 1080,
                        "url": "https://external.test/2",
                        "sourceId": 20,
                        "releaseId": 42,
                    },
                    {
                        "position": 1,
                        "name": "Серия 1",
                        "iframe": False,
                        "quality": 720,
                        "url": "https://external.test/1",
                        "sourceId": 20,
                        "releaseId": 42,
                    },
                ],
            }
        ),
        response({"code": 0, "sources": [{"id": 10, "name": "Source B"}]}),
        response(
            {
                "code": 0,
                "episodes": [
                    {
                        "position": 1,
                        "name": "Эпизод",
                        "iframe": True,
                        "quality": None,
                        "url": "https://external.test/voice",
                        "sourceId": 10,
                        "releaseId": 42,
                    }
                ],
            }
        ),
    ]
    parser = AnixartParser(base_url="https://example.test/", session=session)

    assert parser.get_player_urls(42) == [
        {
            "type_id": 2,
            "type_name": "Субтитры",
            "source_id": 20,
            "source_name": "Source A",
            "episode_position": 2,
            "episode_name": "Серия 2",
            "iframe": True,
            "quality": 1080,
            "url": "https://external.test/2",
        },
        {
            "type_id": 2,
            "type_name": "Субтитры",
            "source_id": 20,
            "source_name": "Source A",
            "episode_position": 1,
            "episode_name": "Серия 1",
            "iframe": False,
            "quality": 720,
            "url": "https://external.test/1",
        },
        {
            "type_id": 1,
            "type_name": "Озвучка",
            "source_id": 10,
            "source_name": "Source B",
            "episode_position": 1,
            "episode_name": "Эпизод",
            "iframe": True,
            "quality": None,
            "url": "https://external.test/voice",
        },
    ]
    assert [call.args[0] for call in session.get.call_args_list] == [
        "https://example.test/episode/42",
        "https://example.test/episode/42/2",
        "https://example.test/episode/42/2/20",
        "https://example.test/episode/42/1",
        "https://example.test/episode/42/1/10",
    ]

    failing_session = Mock()
    failing_session.get.side_effect = [
        response({"code": 0, "types": [{"id": 1, "name": "Озвучка"}]}),
        response({"code": 0, "sources": [{"id": 10, "name": "Source"}]}),
        response({"code": 1, "episodes": []}),
        response({"code": 0, "episodes": []}),
    ]
    failing_parser = AnixartParser(session=failing_session)

    with pytest.raises(errors.ServiceError):
        failing_parser.get_player_urls(42)
    assert failing_session.get.call_count == 3


def test_malformed_catalog_items_raise_without_partial_aggregation():
    session = Mock()
    session.get.side_effect = [
        response({"code": 0, "types": [{"id": 1, "name": "Озвучка"}]}),
        response({"code": 0, "sources": [{"id": 10, "name": "Source"}]}),
        response(
            {
                "code": 0,
                "episodes": [
                    {
                        "position": 1,
                        "name": "Серия 1",
                        "iframe": True,
                        "quality": 720,
                        "url": "https://external.test/1",
                        "sourceId": 10,
                        "releaseId": 42,
                    },
                    {
                        "position": 2,
                        "name": "Серия 2",
                        "iframe": False,
                        "quality": 720,
                        "sourceId": 10,
                        "releaseId": 42,
                    },
                ],
            }
        ),
        response({"code": 0, "sources": []}),
    ]
    parser = AnixartParser(session=session)

    with pytest.raises(errors.UnexpectedBehavior, match="episodes"):
        parser.get_player_urls(42)
    assert session.get.call_count == 3
