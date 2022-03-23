from discord import Embed
import asyncio
from . import BASE_URL, http
from .utils import *
from .season import Season
from .newspost import NewsPost

import logging
log = logging.getLogger(__name__)

__all__ = (
    "PartialGame",
    "Game"
)

class PartialGame:
    def __init__(self, data) -> None:
        self.id = data.get("gameID", None)
        self.name = data.get("gameName", None)
        self.team_mode = data.get("teamMode", None)
        self.match_mode = data.get("matchMode", None)
        self.url = data.get("url", None)
        self.has_substitutes = data.get("hasSubstitutes", None)
        self.has_ties = data.get("hasTies", None)
        self.has_casters = data.get("hasCasters", None)
        self.has_cameraman = data.get("hasCameraman", None)

        self._short_name = short_game_names[self.name]
        if self.url is not None:
            self.url = BASE_URL + self.url
    
    async def fetch(self):
        "Return a full `Game` object."
        return http.get_game(self._short_name)
    
    async def search_team(self, name):
        from .team import PartialTeam
        data = await http.search_team(self._short_name, name)
        return [PartialTeam(d) for d in data]


class Game:
    def __init__(self, data) -> None:
        game_data = data.pop("game", {})
        news_posts_data = data.pop("newsPosts", {})
        next_matches_data = data.pop("nextMatches", {})
        current_season_data = data.pop("season", {})

        self.url = game_data.get("urlComplete", None)
        self.game_by_url = game_data.get("gameByUrl", None)
        self.game_by_image_url = game_data.get("gameByImage", None)
        if self.game_by_image_url is not None:
            self.game_by_image_url = (
                f"{BASE_URL}/images/logos/gamesDev/"
                f"{self.game_by_image_url}.png"
            )
        self.header_image_url = game_data.get("headerImage", None)
        if self.header_image_url is not None:
            self.header_image_url = (
                f"{BASE_URL}/images/logos/home/{self.header_image_url}.png"
            )
        self.id = game_data.get("gameID", None)
        self.name = game_data.get("gameName", None)
        self.team_mode = game_data.get("teamMode", None)
        self.match_mode = game_data.get("matchMode", None)
        self.relative_url = game_data.get("url", None)
        
        self.has_substitutes = game_data.get("hasSubstitutes", None)
        self.has_ties = game_data.get("hasTies", None)
        self.has_casters = game_data.get("hasCasters", None)
        self.has_cameraman = game_data.get("hasCameraman", None)

        # social media URLs
        self.youtube = game_data.get("youtube", None)
        self.twitter = game_data.get("twitter", None)
        if self.twitter is not None:
            self.twitter = "https://twitter.com/" + self.twitter
        self.reddit = game_data.get("reddit", None)
        if self.reddit is not None:
            self.reddit = "https://www.reddit.com/r/" + self.reddit
        self.facebook = game_data.get("facebook", None)
        if self.facebook is not None:
            self.facebook = "https://www.facebook.com/" + self.facebook
        self.discord = game_data.get("discordInvite", None)
        if self.discord is not None:
            self.discord_invite_url = "https://discord.gg/" + self.discord

        self.current_season = Season(current_season_data)

        self.news_posts = [NewsPost(d) for d in news_posts_data]
        for n in self.news_posts:
            n.game = self

        self._short_name = short_game_names[self.name]
    
    def get_embed(self):
        e = Embed(title=self.name,
                  url=self.url)
        d = f"Current season: {self.current_season.name}"
        e.description = d

        s = (f"[Discord]({self.discord_invite_url})\n"
             f"[YouTube]({self.youtube})\n"
             f"[Twitter]({self.twitter})\n"
             f"[Reddit]({self.reddit})\n"
             f"[Facebook]({self.facebook})")
        e.add_field(name="Socials", value=s, inline=False)
        
        lines = (f'<t:{int(n.date_submitted.timestamp())}:d> [{n.title}]({n.url})'
                 for n in self.news_posts)
        block = ""
        for line in lines:
            new_block = "\n".join([block, line])
            if len(new_block) > 1024:
                break
            block = new_block
        e.add_field(
            name="Recent news posts",
            value=block or "No recent posts.",
            inline=False)
        e.set_image(url=self.header_image_url)
        return e
        


    async def search_team(self, name):
        from .team import PartialTeam
        data = await http.search_team(self._short_name, name)
        return [PartialTeam(d) for d in data]
    
    async def fetch_players(self):
        from . import PartialPlayer
        player_data = []
        
        first = await http.get_game_players(self._short_name)
        player_data += first['players']
        total = first['total']
        per_req = first['nbPerPage']
        
        min_positions = list(range(per_req+1, total, per_req))
        for i in range(0, len(min_positions), 5):
            tasks = []
            for pos in min_positions[i:i+5]:
                tasks.append(asyncio.create_task(
                    http.get_game_players(self._short_name, pos)
                ))
            data = await asyncio.gather(*tasks)
            for d in data:
                player_data += d['players']
        
        return [PartialPlayer(d) for d in player_data]
