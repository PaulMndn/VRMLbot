from discord import Embed
from . import BASE_URL, http
from .utils import *
from .season import Season

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
        new_posts_data = data.pop("newPosts", {})
        next_matches_data = data.pop("nextMatches", {})
        current_season_data = data.pop("season", {})

        self.url = game_data.get("urlComplete", None)
        self.by_url = game_data.get("gameByUrl", None)
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

        self._short_name = short_game_names[self.name]
    
    def get_embed(self):
        e = Embed()

    async def search_team(self, name):
        from .team import PartialTeam
        data = await http.search_team(self._short_name, name)
        return [PartialTeam(d) for d in data]
