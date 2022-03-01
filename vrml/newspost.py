from .user import User
from datetime import datetime, timezone

class NewsPost:
    def __init__(self, data):
        self.id = data.get("newsID", None)
        self.user = User(data)
        self.date_submitted = data.get("dateSubmittedUTC", None)
        self.date_edited = data.get("dateEditedUTC", None)
        self.title = data.get("title", None)
        self._html = data.get("html", None)
        self._game = None

        if self.date_submitted:
            aware = self.date_submitted + "+00:00"
            self.date_submitted = datetime.fromisoformat(aware)
        if self.date_edited:
            aware = self.date_edited + "+00:00"
            self.date_edited = datetime.fromisoformat(aware)

    @property
    def game(self):
        return self._game
    
    @game.setter
    def game(self, val):
        from .game import Game
        if not isinstance(val, Game):
            raise TypeError(
                f"Expected type Game, but got type {val.__class__.__name__}."
            )
        self._game = val
    
    @property
    def url(self):
        if self.game is None:
            return None
        return f"{self.game.url}/News/{self.id}"
