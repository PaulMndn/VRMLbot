from .utils import BASE_URL, dc_escape
from .user import User
from .game import PartialGame
from .bio import Bio
from . import http
from datetime import datetime, timedelta
from discord import Embed

__all__ = (
    "PartialPlayer",
    "TeamPlayer",
    "Player"
)


class PartialPlayer:    # like from `/Players/Search`
    def __init__(self, data) -> None:
        self.id = data.get("playerID", None)
        self.name = data.get("playerName", None)
        self.logo_url = data.get("playerLogo", None)
        
        if self.id == None:
            self.id = data.get("id", None)
        if self.name == None:
            self.name = data.get("name", None)
        if self.logo_url == None:
            self.logo_url = data.get("image", None)
        
        if self.logo_url is not None:
            self.logo_url = BASE_URL + self.logo_url
    
    async def fetch(self):
        data = await http.get_player_detailed(self.id)
        return Player(data)


class Player:       # like from `/Players/player_id/Detailed`
    def __init__(self, data) -> None:
        user_data = data.pop("user", {})
        player_data = data.pop("thisGame", {})
        # connoisseur_data = data     # remaining data is connoisseur related. This is not used yet

        self.user = User(user_data)
        self.id = player_data.get("playerID", None)
        self.name = player_data.get("playerName", None)
        self.logo_url = player_data.get("userLogo", None)
        if self.logo_url is not None:
            self.logo_url = BASE_URL + self.logo_url
        self.game = PartialGame(player_data.get("game", {}))

        self.url = f"{self.game.url}/Players/{self.id}"

        self.bio_current = Bio(player_data.get("bioCurrent", {}))
        bio_history = player_data.get("bioHistory", [])
        try:
            self.bio_history = [Bio(d) for d in bio_history[1:]]
        except IndexError:
            self.bio_history = []
        
        self.team = None
        if self.bio_current.team_id is not None:
            from .team import PartialTeam
            self.team = PartialTeam(player_data.get("bioCurrent",{}))
        
    def get_embed(self):
        e = Embed(title=dc_escape(self.name),
                  url=self.url)
        d = (f"Team: {self.team.name if self.team else '*not on a team*'}\n"
             f"Discord handle: `{self.user.discord_tag or 'Unlinked'}`\n"
             f"Plays from: {self.user.country or 'Not specified'}\n"
             f"Nationality: {self.user.nationality or 'Not specified'}\n")
        if self.user.stream_url:
            d += f"[Stream]({self.user.stream_url})\n" 
        if self.bio_current.honours_mention:
            d += f"**{self.bio_current.honours_mention}**"
        e.description = d
        e.set_thumbnail(url=self.logo_url)
        e.set_footer(text=f"Plays {self.game.name}\nJoined VRML on")
        e.timestamp = self.user.date_joined

        s = "\n".join(
            f"{b.season.name} | {b.team_name} | {b.division} | MMR: {b.mmr}"
            for b in self.bio_history
        )
        e.add_field(name="Teams history",
                    value=s or "No prior teams")
        
        return e


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
        self.user_id = data.get("userID", None)
        self.logo_url = data.get("userLogo", None)
        if self.logo_url is not None:
            self.logo_url = BASE_URL+self.logo_url
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
        from .team import Team
        if not isinstance(value, Team):
            raise TypeError(f"Argument must be type <vrml.Team>. Not <{value.__class__.__name__}>")
        self._team = value
    
    @property
    def discord_team_role(self):
        match self._discord_team_role_id:
            case 1:
                return "Captain"
            case 2:
                return "Co-captain"
            case _:
                return None
    
    async def fetch(self):
        data = await http.get_player_detailed(self.id)
        return Player(data)

        