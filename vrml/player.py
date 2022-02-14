from . import *
from .user import User
from .game import PartialGame
from datetime import datetime, timedelta

__all__ = (
    "PartialPlayer",
    "TeamPlayer",
    "Player"
)


class PartialPlayer:    # like from `/Players/Search`
    def __init__(self, data) -> None:
        self.id = data.get("id", None)
        self.name = data.get("name", None)
        self._relative_logo_url = data.get("image", None)
        self.logo_url = None
        if self._relative_logo_url is not None:
            self.logo_url = BASE_URL + self._relative_logo_url
    
    async def fetch(self):
        data = await http.get_player_detailed(self.id)
        return Player(data)


class Player:       # like from `/Players/player_id/Detailed`
    def __init__(self, data) -> None:
        user_data = data.pop("user", {})
        player_data = data.pop("thisGame", {})
        connoisseur_data = data     # remaining data is connoisseur related. This is not used yet

        self.user = User(user_data)
        self.id = player_data.get("playerID", None)
        self.name = player_data.get("playerName", None)
        self._relative_logo_url = player_data.get("userLogo", None)
        self.logo_url = None
        if self._relative_logo_url is not None:
            self.logo_url = BASE_URL + self._relative_logo_url
        self.game = PartialGame(player_data.get("game", {}))


class TeamPlayer:       # like from `/Team/team_id`
    def __init__(self, data) -> None:
        self.is_cooldown = data.get("isCooldown", None)
        self.cooldown_note = data.get("cooldownNote", None)
        self.cooldown_date_expires = data.get("cooldownDateExpiresUTC", None)
        self.honours_mention_note = data.get("honoursMentionNote", None)
        self.honours_mention_logo = data.get("honoursMentionLogo", None)
        self._discord_team_role_id = data.pop("discordTeamRole", None)

        self.id = data.get("playerID", None)
        self.name = data.get("playerName", None)
        self._user_id = data.get("userID", None)
        self._relative_logo_url = data.get("userLogo", None)
        self.logo_url = None
        if self._relative_logo_url is not None:
            self.logo_url = BASE_URL+self._relative_logo_url
        self.country = data.get("country", None)
        self.nationality = data.get("nationality", None)
        self.stream_url = data.get("streamURL", None)
        self.team_id = data.get("teamID", None)
        self.team_name = data.get("teamName", None)
        self._role_id = data.get("roleID", None)
        self.role = data.get("role", None)
        self.is_team_owner = data.get("isTeamOwner", None)
        self.is_team_starter = data.get("isTeamStarter", None)

        if self.cooldown_date_expires is not None:
            aware_date = self.cooldown_date_expires+"+00:00"
            self.cooldown_date_expires = datetime.fromisoformat(aware_date)

        self._team = None
    
    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, value):
        if not isinstance(value, vrml.Team):
            raise TypeError(f"Argument must be type <vrml.Team>. Not <{value.__class__.__name__}>")
        self._team = value
    
    @property
    def discord_team_role(self):
        match self._discord_team_role_id:
            case "1":
                return "Captain"
            case "2":
                return "Co-Captain"
            case _:
                return None
    
    async def fetch_player(self):
        data = await http.get_player_detailed(self.id)
        return Player(data)

        