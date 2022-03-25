import json
from pathlib import Path
import asyncio
from lib.utils import schedule

__all__ = [
    "Guild",
    "get_guild",
    "init_guilds"
]

class Guild:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self._path = Path(f"data/{guild_id}.json")
        if not self._path.exists():
            self._data = {}
            return
        
        with open(str(self._path)) as f:
            self._data = json.load(f)
        

    @property
    def default_game(self):
        return self._data.get("default_game", None)
    
    @default_game.setter
    def default_game(self, game):
        self._data["default_game"] = game
        schedule(self._sync)
    
    def _sync(self):
        with open(str(self._path), "w") as f:
            json.dump(self._data, f)
