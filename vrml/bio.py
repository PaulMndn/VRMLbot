from datetime import datetime
from .utils import *
from .season import Season

class Bio:      # only using data from player/bioHistory[]
    def __init__(self, data) -> None:
        self.season = Season(data)
        self.division_logo_url = data.get("divisionLogo", None)
        if self.division_logo_url is not None:
            self.division_logo_url = BASE_URL + self.division_logo_url
        self.division = data.get("divisionName", None)
        self.mmr = data.get("mmr", None)
        self.player_id = data.get("playerID", None)
        self.user_id = data.get("userID", None)
        self.player_name = data.get("playerName", None)
        self.logo_url = data.get("userLogo", None)
        if self.logo_url is not None:
            self.logo_url = BASE_URL + self.logo_url
        self.country = data.get("country", None)
        self.nationality = data.get("nationality", None)
        self.role_id = data.get("roleID", None)
        self.role = data.get("role", None)
        self.is_team_owner = data.get("isTeamOwner", None)
        self.is_team_starter = data.get("isTeamStarter", None)
        self.team_id = data.get("teamID", None)
        self.team_name = data.get("teamName", None)
        self.team_logo_url = data.get("teamLogo", None)
        if self.team_logo_url is not None:
            self.team_logo_url = BASE_URL + self.team_logo_url
        self.honours_mention = data.get("honoursMention", None)
        self.honours_mention_logo_url = data.get("honoursMentionLogo", None)
        self.cooldown_id = data.get("cooldownID", None)
        self.cooldown_note = data.get("cooldownNote", None)
        self.cooldown_date_expires = data.get("cooldownDateExpiresUTC", None)
        if self.cooldown_date_expires is not None:
            aware = self.cooldown_date_expires + "+00:00"
            self.cooldown_date_expires = datetime.fromisoformat(aware)
    
    async def fetch_player(self):
        raise NotImplementedError
        
    async def fetch_team(self):
        raise NotImplementedError


