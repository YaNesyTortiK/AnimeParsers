from urllib.parse import urlsplit

import requests

from . import errors


class AnixartParser:
    """Синхронный клиент каталога Anixart."""

    SORT_DATE_UPDATE = 0
    SORT_GRADE = 1
    SORT_YEAR = 2
    SORT_POPULAR = 3

    _TITLE_FIELDS = ("title", "title_ru", "title_original", "title_alt")
    _STUDIOS = (
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
    )
    _GENRES = (
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
    )

    _HEADERS = {
        "Accept": "application/json",
        "API-Version": "v2",
        "User-Agent": "anime-parsers-ru/AnixartParser",
    }

    def __init__(
        self,
        base_url: str = "https://api-s.anixsekai.com/",
        proxy: str | None = None,
        timeout: float = 10,
        session: requests.Session | None = None,
    ) -> None:
        if not isinstance(base_url, str):
            raise TypeError("base_url должен быть строкой.")
        if not base_url.strip():
            raise ValueError("base_url не должен быть пустым.")
        if proxy is not None and not isinstance(proxy, str):
            raise TypeError("proxy должен быть строкой или None.")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout должен быть числом.")
        if timeout <= 0:
            raise ValueError("timeout должен быть больше нуля.")
        if session is not None and not all(
            callable(getattr(session, method, None)) for method in ("get", "post")
        ):
            raise TypeError("session должен поддерживать методы get и post.")

        self.base_url = base_url.strip().rstrip("/") + "/"
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = getattr(self.session, method)(
                f"{self.base_url}{path}",
                headers=self._HEADERS,
                proxies=self.proxies,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise errors.ServiceError(f"Ошибка HTTP-запроса к Anixart: {exc}") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise errors.UnexpectedBehavior(
                "Anixart вернул ответ, который не является корректным JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise errors.UnexpectedBehavior("Anixart вернул ответ неверного формата.")
        code = payload.get("code")
        if type(code) is not int:
            raise errors.UnexpectedBehavior("В ответе Anixart отсутствует корректный код.")
        if code in (402, 403):
            raise errors.ContentBlocked(f"Anixart вернул код блокировки {code}.")
        if code != 0:
            raise errors.ServiceError(f"Anixart вернул код ошибки {code}.")
        return payload

    @staticmethod
    def _extract(payload: dict, key: str, expected_type: type):
        value = payload.get(key)
        if not isinstance(value, expected_type):
            raise errors.UnexpectedBehavior(
                f'В ответе Anixart отсутствует корректное поле "{key}".'
            )
        return value

    @classmethod
    def _extract_items(
        cls,
        payload: dict,
        key: str,
        required_keys: tuple,
        integer_keys: tuple,
        string_keys: tuple = (),
    ) -> list:
        items = cls._extract(payload, key, list)
        for item in items:
            if not isinstance(item, dict) or not all(
                required_key in item for required_key in required_keys
            ):
                raise errors.UnexpectedBehavior(
                    f'В ответе Anixart поле "{key}" содержит некорректный элемент.'
                )
            if any(type(item[integer_key]) is not int for integer_key in integer_keys):
                raise errors.UnexpectedBehavior(
                    f'В ответе Anixart поле "{key}" содержит некорректный числовой ID.'
                )
            if any(not isinstance(item[string_key], str) for string_key in string_keys):
                raise errors.UnexpectedBehavior(
                    f'В ответе Anixart поле "{key}" содержит некорректную строку.'
                )
        return items

    @staticmethod
    def _validate_int(name: str, value: int, minimum: int | None = None) -> None:
        if type(value) is not int:
            raise TypeError(f"{name} должен быть целым числом.")
        if minimum is not None and value < minimum:
            raise ValueError(f"{name} должен быть не меньше {minimum}.")

    @staticmethod
    def get_studios() -> list[str]:
        return list(AnixartParser._STUDIOS)

    @staticmethod
    def get_genres() -> list[str]:
        return list(AnixartParser._GENRES)

    @classmethod
    def _extract_releases(cls, payload: dict, key: str) -> list:
        releases = cls._extract(payload, key, list)
        for release in releases:
            if (
                not isinstance(release, dict)
                or type(release.get("id")) is not int
                or not any(
                    isinstance(release.get(field), str)
                    and bool(release[field].strip())
                    for field in cls._TITLE_FIELDS
                )
            ):
                raise errors.UnexpectedBehavior(
                    f'В ответе Anixart поле "{key}" содержит некорректный элемент.'
                )
        return releases

    def filter(
        self,
        *,
        page: int = 0,
        extended: bool = True,
        category_id: int | None = None,
        country: str | None = None,
        end_year: int | None = None,
        episode_duration_from: int | None = None,
        episode_duration_to: int | None = None,
        episodes_from: int | None = None,
        episodes_to: int | None = None,
        is_genres_exclude_mode_enabled: bool = False,
        season: int | None = None,
        source: str | None = None,
        start_year: int | None = None,
        status_id: int | None = None,
        studio: str | None = None,
        sort: int = SORT_DATE_UPDATE,
        genres: list[str] | None = None,
        profile_list_exclusions: list[int] | None = None,
        types: list[int] | None = None,
        age_ratings: list[int] | None = None,
    ) -> dict:
        self._validate_int("page", page, 0)
        for name, value, minimum in (
            ("category_id", category_id, 1),
            ("end_year", end_year, None),
            ("episode_duration_from", episode_duration_from, 0),
            ("episode_duration_to", episode_duration_to, 0),
            ("episodes_from", episodes_from, 0),
            ("episodes_to", episodes_to, 0),
            ("season", season, None),
            ("start_year", start_year, None),
            ("status_id", status_id, 1),
        ):
            if value is not None:
                self._validate_int(name, value, minimum)
        self._validate_int("sort", sort)
        if sort not in (
            self.SORT_DATE_UPDATE,
            self.SORT_GRADE,
            self.SORT_YEAR,
            self.SORT_POPULAR,
        ):
            raise ValueError("sort должен быть одним из значений 0, 1, 2 или 3.")
        for name, value in (
            ("extended", extended),
            ("is_genres_exclude_mode_enabled", is_genres_exclude_mode_enabled),
        ):
            if type(value) is not bool:
                raise TypeError(f"{name} должен быть логическим значением.")
        for name, value in (
            ("country", country),
            ("source", source),
            ("studio", studio),
        ):
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} должен быть строкой или None.")
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"{name} не должен быть пустым.")
        for lower_name, lower, upper_name, upper in (
            ("start_year", start_year, "end_year", end_year),
            ("episodes_from", episodes_from, "episodes_to", episodes_to),
            (
                "episode_duration_from",
                episode_duration_from,
                "episode_duration_to",
                episode_duration_to,
            ),
        ):
            if lower is not None and upper is not None and lower > upper:
                raise ValueError(f"{lower_name} не должен превышать {upper_name}.")
        for name, value in (
            ("genres", genres),
            ("profile_list_exclusions", profile_list_exclusions),
            ("types", types),
            ("age_ratings", age_ratings),
        ):
            if value is not None and not isinstance(value, list):
                raise TypeError(f"{name} должен быть списком.")
        if genres is not None:
            if any(not isinstance(genre, str) for genre in genres):
                raise TypeError("genres должен содержать только строки.")
            if any(not genre.strip() for genre in genres):
                raise ValueError("genres не должен содержать пустые строки.")
        for name, values in (
            ("profile_list_exclusions", profile_list_exclusions),
            ("types", types),
            ("age_ratings", age_ratings),
        ):
            if values is None:
                continue
            if any(type(value) is not int for value in values):
                raise TypeError(f"{name} должен содержать только целые числа.")
            minimum = 0 if name == "profile_list_exclusions" else 1
            if any(value < minimum for value in values):
                raise ValueError(f"{name} должен содержать значения не меньше {minimum}.")

        request = {
            "category_id": category_id,
            "country": country,
            "end_year": end_year,
            "episode_duration_from": episode_duration_from,
            "episode_duration_to": episode_duration_to,
            "episodes_from": episodes_from,
            "episodes_to": episodes_to,
            "is_genres_exclude_mode_enabled": is_genres_exclude_mode_enabled,
            "season": season,
            "source": source,
            "start_year": start_year,
            "status_id": status_id,
            "studio": studio,
            "sort": sort,
            "genres": [] if genres is None else list(genres),
            "profile_list_exclusions": (
                []
                if profile_list_exclusions is None
                else list(profile_list_exclusions)
            ),
            "types": [] if types is None else list(types),
            "age_ratings": [] if age_ratings is None else list(age_ratings),
        }
        payload = self._request(
            "post",
            f"filter/{page}?extended_mode={str(extended).lower()}",
            json=request,
        )
        result = {"content": self._extract_releases(payload, "content")}
        for field in ("current_page", "total_count", "total_page_count"):
            value = payload.get(field)
            if type(value) is not int or value < 0:
                raise errors.UnexpectedBehavior(
                    f'В ответе Anixart отсутствует корректное поле "{field}".'
                )
            result[field] = value
        return result

    def _search_request(self, query: str, page: int, search_by: int) -> dict:
        if not isinstance(query, str):
            raise TypeError("query должен быть строкой.")
        if not query.strip():
            raise ValueError("query не должен быть пустым.")
        self._validate_int("page", page, 0)
        self._validate_int("search_by", search_by, 0)
        return self._request(
            "post",
            f"search/releases/{page}",
            json={"query": query, "searchBy": search_by},
        )

    def search(self, query: str, page: int = 0, search_by: int = 0) -> list:
        payload = self._search_request(query, page, search_by)
        releases = self._extract_releases(payload, "releases")
        if not releases:
            raise errors.NoResults(f'По запросу "{query}" ничего не найдено.')
        return releases

    def search_extended(
        self, query: str, page: int = 0, search_by: int = 0
    ) -> dict:
        payload = self._search_request(query, page, search_by)
        releases = self._extract_releases(payload, "releases")
        if not releases:
            raise errors.NoResults(f'По запросу "{query}" ничего не найдено.')

        if "related" not in payload:
            raise errors.UnexpectedBehavior(
                'В ответе Anixart отсутствует корректное поле "related".'
            )
        related = payload["related"]
        if related is not None:
            images = related.get("images") if isinstance(related, dict) else None
            if (
                not isinstance(related, dict)
                or type(related.get("id")) is not int
                or related["id"] < 1
                or type(related.get("release_count")) is not int
                or related["release_count"] < 0
                or not any(
                    isinstance(related.get(field), str) and related[field].strip()
                    for field in ("name_ru", "name")
                )
                or not isinstance(related.get("image"), str)
                or not related["image"].strip()
                or "description" not in related
                or (
                    related["description"] is not None
                    and not isinstance(related["description"], str)
                )
                or "images" not in related
                or (
                    images is not None
                    and (
                        not isinstance(images, list)
                        or any(not isinstance(image, str) for image in images)
                    )
                )
            ):
                raise errors.UnexpectedBehavior(
                    'В ответе Anixart отсутствует корректное поле "related".'
                )
        return {"releases": releases, "related": related}

    def get_schedule(self) -> dict:
        payload = self._request("get", "schedule")
        return {
            day: self._extract_releases(payload, day)
            for day in (
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            )
        }

    def get_related_releases(self, related_id: int, page: int = 0) -> dict:
        self._validate_int("related_id", related_id, 1)
        self._validate_int("page", page, 0)
        payload = self._request("get", f"related/{related_id}/{page}")
        result = {"content": self._extract_releases(payload, "content")}
        for field in ("current_page", "total_count", "total_page_count"):
            value = payload.get(field)
            if type(value) is not int or value < 0:
                raise errors.UnexpectedBehavior(
                    f'В ответе Anixart отсутствует корректное поле "{field}".'
                )
            result[field] = value
        return result

    def get_random_release(self, extended: bool = True) -> dict:
        if type(extended) is not bool:
            raise TypeError("extended должен быть логическим значением.")
        payload = self._request(
            "get", f"release/random?extended_mode={str(extended).lower()}"
        )
        release = self._extract(payload, "release", dict)
        if (
            not release
            or type(release.get("id")) is not int
            or release["id"] < 1
            or not any(
                isinstance(release.get(field), str) and release[field].strip()
                for field in self._TITLE_FIELDS
            )
        ):
            raise errors.UnexpectedBehavior(
                'В ответе Anixart отсутствует корректное поле "release".'
            )
        return release

    def anime_info(self, release_id: int, extended: bool = True) -> dict:
        self._validate_int("release_id", release_id, 1)
        if type(extended) is not bool:
            raise TypeError("extended должен быть логическим значением.")
        payload = self._request(
            "get",
            f"release/{release_id}?extended_mode={str(extended).lower()}",
        )
        release = self._extract(payload, "release", dict)
        if (
            not release
            or type(release.get("id")) is not int
            or release["id"] != release_id
        ):
            raise errors.UnexpectedBehavior(
                'В ответе Anixart отсутствует корректное поле "release".'
            )
        return release

    def get_types(self, release_id: int) -> list:
        self._validate_int("release_id", release_id, 1)
        payload = self._request("get", f"episode/{release_id}")
        return self._extract_items(
            payload, "types", ("id", "name"), ("id",), ("name",)
        )

    def get_sources(self, release_id: int, type_id: int) -> list:
        self._validate_int("release_id", release_id, 1)
        self._validate_int("type_id", type_id, 1)
        payload = self._request("get", f"episode/{release_id}/{type_id}")
        return self._extract_items(
            payload, "sources", ("id", "name"), ("id",), ("name",)
        )

    def get_episodes(
        self,
        release_id: int,
        type_id: int,
        source_id: int,
        sort: int | None = None,
    ) -> list:
        self._validate_int("release_id", release_id, 1)
        self._validate_int("type_id", type_id, 1)
        self._validate_int("source_id", source_id, 1)
        if sort is not None:
            self._validate_int("sort", sort)
        kwargs = {}
        if sort is not None:
            kwargs["params"] = {"sort": sort}
        payload = self._request(
            "get",
            f"episode/{release_id}/{type_id}/{source_id}",
            **kwargs,
        )
        episodes = self._extract_items(
            payload,
            "episodes",
            (
                "position",
                "name",
                "iframe",
                "quality",
                "url",
                "sourceId",
                "releaseId",
            ),
            ("position", "sourceId", "releaseId"),
            ("name",),
        )
        for episode in episodes:
            quality = episode["quality"]
            url = episode["url"]
            try:
                parsed_url = urlsplit(url) if isinstance(url, str) else None
            except ValueError:
                parsed_url = None
            if (
                episode["releaseId"] != release_id
                or episode["sourceId"] != source_id
                or type(episode["iframe"]) is not bool
                or (quality is not None and type(quality) is not int)
                or parsed_url is None
                or parsed_url.scheme.lower() not in ("http", "https")
                or not parsed_url.netloc
            ):
                raise errors.UnexpectedBehavior(
                    'В ответе Anixart поле "episodes" содержит некорректный элемент.'
                )
        return episodes

    def get_player_urls(self, release_id: int) -> list:
        """Возвращает плоский список внешних плееров в порядке ответа сервера.

        Каждый элемент содержит ровно ключи ``type_id``, ``type_name``,
        ``source_id``, ``source_name``, ``episode_position``, ``episode_name``,
        ``iframe``, ``quality`` и ``url``.
        """
        self._validate_int("release_id", release_id, 1)
        result = []
        for type_item in self.get_types(release_id):
            type_id = type_item["id"]
            type_name = type_item["name"]
            for source in self.get_sources(release_id, type_id):
                source_id = source["id"]
                source_name = source["name"]
                for episode in self.get_episodes(release_id, type_id, source_id):
                    result.append(
                        {
                            "type_id": type_id,
                            "type_name": type_name,
                            "source_id": source_id,
                            "source_name": source_name,
                            "episode_position": episode["position"],
                            "episode_name": episode["name"],
                            "iframe": episode["iframe"],
                            "quality": episode["quality"],
                            "url": episode["url"],
                        }
                    )
        return result
