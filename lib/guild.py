import json
from pathlib import Path
import logging
import discord
from typing import Optional
from .utils import schedule

__all__ = [
    "Guild",
    "get_guild",
    "drop_guild",
    "init_guilds"
]

log = logging.getLogger(__name__)


class SourceView(discord.ui.View):
    def __init__(self, source: str) -> None:
        super().__init__(
            discord.ui.Button(label=f"Sent from server: {source}", 
                              disabled=True))

class Guild:
    def __init__(self, bot: discord.Client, guild_id: int) -> None:
        self.bot = bot
        self.guild_id = guild_id
        self._path = Path(f"data/{guild_id}.json")
        if not self._path.exists():
            self._data = {}
            return
        
        with open(str(self._path)) as f:
            self._data = json.load(f)
    
    @property
    def default_game(self) -> Optional[str]:
        return self._data.get("default_game", None)
    
    @default_game.setter
    def default_game(self, game: Optional[str]) -> None:
        self._data["default_game"] = game
        schedule(self._sync)
    
    def _sync(self) -> None:
        with open(str(self._path), "w") as f:
            json.dump(self._data, f)
    
    async def message_guild(self, msg: str) -> bool:
        guild = self.bot.get_guild(self.guild_id)
        channel = guild.system_channel
        if not channel:
            return False
        try:
            await channel.send(msg)
            return True
        except discord.Forbidden:
            log.warning(f"{guild.id}: Can't message system channel. "
                        f"Missing Permissions.")
        return False
    
    async def message_owner(self, msg: str) -> bool:
        guild = self.bot.get_guild(self.guild_id)
        owner = await self.bot.fetch_user(guild.owner_id)
        if owner is None:
            log.error(f"{guild.id}: No owner found to DM.")
            return False
        try:
            await owner.send(msg, view=SourceView(guild.name))
            return True
        except discord.Forbidden as e:
            log.error(f"{guild.id}: Can't DM owner {owner}. Missing Permissions")
        return False


_guilds: dict[int, Guild] = {}
_bot: Optional[discord.Client] = None

def get_guild(guild_id: int) -> Guild:
    g = _guilds.get(guild_id, None)
    if g is None:
        g = Guild(_bot, guild_id)
        _guilds[guild_id] = g
    return g

def drop_guild(guild_id: int) -> None:
    _guilds.pop(guild_id, None)

def init_guilds(bot: discord.Client) -> None:
    global _bot
    _bot = bot
    for guild in bot.guilds:
        get_guild(guild.id)

