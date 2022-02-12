from datetime import datetime
from . import BASE_URL

class User:
    def __init__(self, data) -> None:
        self.id = data.get("userID", None)
        self.name = data.get("userName", None)
        self.logo_url = data.get("userLogo", None)
        if self.logo_url is not None:
            self.logo_url = BASE_URL + self.logo_url

        self.country = data.get("country", None)
        self.nationality = data.get("nationality", None)
        self.date_joined = data.get("dateJoinedUTC", None)
        if self.date_joined is not None:
            aware_date = self.date_joined + "+00:00"
            self.date_joined = datetime.fromisoformat(aware_date)
        
        self.stream_url = data.get("streamUrl", None)
        self.discord_id = data.get("discordID", None)
        self.discord_tag = data.get("discordTag", None)
        self.is_terminated = data.get("isTerminated", None)


