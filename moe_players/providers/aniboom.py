from re import compile
from typing import List
from json import loads
from ..classes import Anime, Parser


class AniboomAnime(Anime):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser: AniboomParser = kwargs["parser"] if "parser" in kwargs else None

    async def get_episodes(self):
        self.episodes = await self.parser.get_episodes(self.url)
        self.total_episodes = int(self.episodes[-1].get("num", 0))
        return self.episodes

    async def get_translations(self):
        self.translations = await self.parser.get_translations(self.anime_id)
        return self.translations

    async def get_info(self):
        self.data = await self.parser.get_info(self.url)
        self.episodes = self.data['episodes']
        self.translations = self.data['translations']
        return self.data
    
    async def get_file(self, episode: int | str, translation_id: int | str):
        return await self.parser.get_mpd_content(self.anime_id, episode, translation_id)


class AniboomParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://animego.org/"
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://animego.org/",
        }

    async def convert2anime(self, *args, **kwargs) -> Anime:
        anime = AniboomAnime(
            orig_title=kwargs["other_title"],
            title=kwargs["title"],
            anime_id=kwargs["id"],
            url=kwargs["link"],
            parser=self,
            id_type="aniboom",
        )
        return anime

    async def search(self, query: str) -> List[AniboomAnime]:
        content = (await self.get("search/all", params={"type": "small", "q": query}))[
            "content"
        ]

        page = await self.soup(content)
        results_list = page.find("div", {"class": "result-search-anime"}).find_all(
            "div", {"class": "result-search-item"}
        )

        results = []
        for result in results_list:
            data = {}
            data["title"] = result.find("h5").text.strip()
            data["year"] = result.find("span", {"class": "anime-year"}).text.strip()
            data["other_title"] = (
                result.find("div", {"class": "text-truncate"}).text.strip()
                if result.find("div", {"class": "text-truncate"})
                else ""
            )
            data["type"] = result.find(
                "a", {"href": compile(r".*anime/type.*")}
            ).text.strip()
            data["link"] = (
                "https://animego.org" + result.find("h5").find("a").attrs["href"]
            )
            data["id"] = data["link"][data["link"].rfind("-") + 1 :]
            results.append(await self.convert2anime(**data))

        return results

    async def get_episodes(self, link: str, *args, **kwargs) -> List[dict]:
        params = {"type": "episodeSchedule", "episodeNumber": "99999"}
        response = await self.get(link, params=params)
        soup = await self.soup(response["content"])
        episodes_list = []
        for ep in soup.find_all("div", {"class": ["row", "m-0"]}):
            items = ep.find_all("div")
            num = items[0].find("meta").get_attribute_list("content")[0]
            ep_title = items[1].text.strip() if items[1].text else ""
            ep_date = (
                items[2].find("span").get_attribute_list("data-label")[0]
                if items[2].find("span")
                else ""
            )
            ep_status = "анонс" if items[3].find("span") is None else "вышел"
            episodes_list.append(
                {"num": num, "title": ep_title, "date": ep_date, "status": ep_status}
            )

        return sorted(
            episodes_list,
            key=lambda x: int(x["num"]) if x["num"].isdigit() else x["num"],
        )

    async def get_info(self, link: str, *args, **kwargs):
        anime_data = {}
        response = await self.get(link)
        soup = await self.soup(response)

        anime_data['link'] = link
        anime_data['animego_id'] = link[link.rfind('-') + 1:]
        anime_data['title'] = soup.find('div', class_='anime-title').find('h1').text.strip()

        anime_data['other_titles'] = [
            syn.text.strip() for syn in soup.find('div', class_='anime-synonyms').find_all('li')
        ]

        poster_path = soup.find('img').get('src', '')
        anime_data['poster_url'] = f'https://animego.org{poster_path[poster_path.find("/upload"):]}' if poster_path else ''

        anime_info = soup.find('div', class_='anime-info').find('dl')
        keys = anime_info.find_all('dt')
        values = anime_info.find_all('dd')

        anime_data['other_info'] = {}
        for key, value in zip(keys, values):
            key_text = key.text.strip()
            if value.get('class') == ['mt-2', 'col-12'] or value.find('hr'):
                continue
            if key_text == 'Озвучка':
                continue
            if key_text == 'Жанр':
                anime_data['genres'] = [genre.text for genre in value.find_all('a')]
            elif key_text == 'Главные герои':
                anime_data['other_info']['Главные герои'] = [hero.text for hero in value.find_all('a')]
            elif key_text == 'Эпизоды':
                anime_data['episodes'] = value.text
            elif key_text == 'Статус':
                anime_data['status'] = value.text
            elif key_text == 'Тип':
                anime_data['type'] = value.text
            else:
                anime_data['other_info'][key_text] = value.text.strip()

        anime_data['description'] = soup.find('div', class_='description').text.strip()

        anime_data['screenshots'] = [
            f"https://animego.org{screenshot.get('href')}"
            for screenshot in soup.find_all('a', class_='screenshots-item')
        ]

        trailer_container = soup.find('div', class_='video-block')
        anime_data['trailer'] = trailer_container.find('a', class_='video-item').get('href') if trailer_container else None

        anime_data['episodes'] = await self.get_episodes(link)

        try:
            anime_data['translations'] = await self.get_translations(anime_data['animego_id'])
        except Exception:
            anime_data['translations'] = []

        return anime_data

    async def get_translations(self, animego_id: int | str, *args, **kwargs):
        params = {
            '_allow': 'true',
        }
        response = await self.get(f"anime/{animego_id}/player", params=params)
        soup = await self.soup(response["content"])

        if soup.find("div", {"class": "player-blocked"}):
            reason_elem = soup.find("div", {"class": "h5"})
            reason = reason_elem.text if reason_elem else None
            raise Exception(f"Player is blocked: {reason}")

        translations_elem = soup.find("div", {"id": "video-dubbing"}).find_all(
            "span", {"class": "video-player-toggle-item"}
        )
        translations = {}
        for translation in translations_elem:
            dubbing = translation.get_attribute_list("data-dubbing")[0]
            name = translation.text.strip()
            translations[dubbing] = {"name": name}

        players_elem = soup.find("div", {"id": "video-players"}).find_all(
            "span", {"class": "video-player-toggle-item"}
        )
        for player in players_elem:
            if player.get_attribute_list("data-provider")[0] == "24":
                dubbing = player.get_attribute_list("data-provide-dubbing")[0]
                translation_id = player.get_attribute_list("data-player")[0]
                translation_id = translation_id[translation_id.rfind("=") + 1 :]
                translations[dubbing]["translation_id"] = translation_id

        filtered_translations = []
        for translation in translations.values():
            if "translation_id" in translation:
                filtered_translations.append(translation)

        return filtered_translations

    async def get_embed_link(self, animego_id: int | str) -> str:
        params = {'_allow': 'true'}
        response = await self.get(f'anime/{animego_id}/player', params=params)
        if response['status'] != 'success':
            raise Exception(f'Unexpected status: {response["status"]}')
        soup = await self.soup(response['content'])
        if soup.find('div', {'class': 'player-blocked'}):
            reason = soup.find('div', {'class': 'h5'}).text
            raise Exception(f'Content is blocked: {reason}')
        player_container = soup.find('div', {'id': 'video-players'})
        player_link = player_container.find('span', {'class': 'video-player-toggle-item'}).get('data-player')
        return 'https:' + player_link[:player_link.rfind('?')]

    async def get_embed(self, embed_link: str, episode: int, translation: str) -> str:
        if episode != 0:
            params = {
                'episode': episode,
                'translation': translation,
            }
        else:
            params = {
                'translation': translation,
            }
        return await self.get(embed_link, params=params, text=True)

    async def get_mpd_playlist(self, embed_link: str, episode: int, translation: str) -> str:
        embed = await self.get_embed(embed_link, episode, translation)
        soup = await self.soup(embed)
        data = loads(soup.find("div", {"id": "video"}).get("data-parameters"))
        media_src = loads(data["dash"])["src"]

        headers = {
            "Origin": "https://aniboom.one",
            "Referer": "https://aniboom.one/",
        }

        playlist = await self.get(media_src, headers=headers, text=True)
        filename = media_src[media_src.rfind("/") + 1 : media_src.rfind(".")]
        server_path = media_src[: media_src.rfind(".")]
        playlist = playlist.replace(filename, server_path)

        return playlist

    async def get_mpd_content(self, animego_id: int | str, episode: int, translation_id: int, *args, **kwargs):
        embed_link = await self.get_embed_link(animego_id)
        return await self.get_mpd_playlist(embed_link, episode, translation_id, *args, **kwargs)