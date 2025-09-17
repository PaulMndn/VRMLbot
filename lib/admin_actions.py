import asyncio
import discord
from typing import Any
from .tasks import fetch_vrml_discord_player
from .guild import get_guild

__all__ = [
    "AdminActions",
]

class AdminActions:
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
    
    async def help(self) -> str:
        s = ("Available admin commands:\n"
             "```\n"
             "!help          Show this help\n"
             "!msg_guilds    Message system channel in all servers\n"
             "!msg_owners    Message all server owners\n"
             "!msg_both      Message server owners and system channels in all servers\n"
             "!stats         Send bot stats\n"
             "!log           Send log file, 1-4 may be specified for log history\n"
             "!update_cache  Update cached data from VRML\n"
             "```")
        return s
    
    async def msg_guilds(self, msg: str) -> int:
        """Message system channels of all guilds the bot is a member of.

        Args:
            msg (str): Message

        Returns:
            int: Number of messaged guilds.
        """
        coros = []
        for g in self.bot.guilds:
            guild = get_guild(g.id)
            coros.append(guild.message_guild(msg))
        res = await asyncio.gather(*coros)
        return sum(res)
    
    async def msg_owners(self, msg: str) -> int:
        """Message owners of all guilds the bot is a member of.

        Args:
            msg (str): Message

        Returns:
            int: Number of messaged owners.
        """
        coros = []
        for g in self.bot.guilds:
            guild = get_guild(g.id)
            coros.append(guild.message_owner(msg))
        res = await asyncio.gather(*coros)
        return sum(res)

    async def msg_both(self, msg: str) -> tuple[int, int]:
        """Messages system channels (if exist) and owners of all guilds.

        Args:
            msg (str): Message to send

        Returns:
            tuple: Number of system channels and number of owners messaged.
        """
        t = [self.msg_guilds(msg),
             self.msg_owners(msg)]
        counts = await asyncio.gather(*t)
        return tuple(counts)

    async def stats(self) -> dict[str, Any]:
        return {
            "No. Servers": len(self.bot.guilds),
            "Server names": [g.name for g in self.bot.guilds]
        }

    async def log(self, i: str = "") -> discord.File:
        """Retriev log file in discord file format.

        Args:
            i (str, optional): i-th log file, `str` from "" to "4". Defaults to "".
        """
        path = "log/VRMLbot.log"
        if i:
            path += f".{i}"
        return discord.File(path, description=path)
    
    async def update_discord_players(self) -> None:
        await fetch_vrml_discord_player.coro(force=True)

