from . import BASE_URL, http
from .user import User
from .game import PartialGame


class PartialPlayer:
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


class Player:
    def __init__(self, data) -> None:
        user_data = data.pop("user", {})
        player_data = data.pop("thisGame", {})
        connoisseur_data = data     # remaining data is connoisseur related

        self.user = User(user_data)
        self.id = player_data.get("playerID", None)
        self.name = player_data.get("playerName", None)
        self._relative_logo_url = player_data.get("userLogo", None)
        self.logo_url = None
        if self._relative_logo_url is not None:
            self.logo_url = BASE_URL + self._relative_logo_url
        self.game = PartialGame(player_data.get("game", {}))


