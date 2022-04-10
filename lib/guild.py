import json
import logging
from pathlib import Path
import logging
import discord
from discord.ext.commands import Bot
import vrml
from .utils import schedule
from .player_cache import PlayerCache

__all__ = [
    "Guild",
    "get_guild",
    "drop_guild",
    "init_guilds"
]

log = logging.getLogger(__name__)


class SourceView(discord.ui.View):
    def __init__(self, source):
        super().__init__(
            discord.ui.Button(label=f"Sent from server: {source}", 
                              disabled=True))

class Guild:
    POINTER_ROLE_NAME = "-----team_roles-----"

    def __init__(self, bot, guild_id):
        self.bot: Bot = bot
        self.guild_id = guild_id
        self._guild = bot.get_guild(guild_id)
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
        self.sync()
    
    @property
    def manage_team_roles(self):
        return self._data.get("manage_team_roles", None)
    
    @manage_team_roles.setter
    def manage_team_roles(self, val):
        self._data["manage_team_roles"] = val
        self.sync()
    
    def get_team_roles(self):
        return self._data.get("team_roles", {}).copy()
    
    def add_team_role(self, role: discord.Role):
        if "team_role" in self._data:
            self._data['team_role'][role.name] = role.id
        else:
            self._data['team_role'] = {role.name: role.id}
        self.sync()
        
    def del_team_role(self, name):
        try:
            del self._data['team_role'][name]
        except KeyError:
            pass
        self.sync()
    
    def _sync(self):
        with open(str(self._path), "w") as f:
            json.dump(self._data, f)
    
    def sync(self):
        schedule(self._sync())
    
    async def message_guild(self, msg):
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
    
    async def message_owner(self, msg):
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

    async def _get_pointer_role(self):
        guild = self.bot.get_guild(self.guild_id)
        if not any(r.name == self.POINTER_ROLE_NAME for r in guild.roles):
            return
        roles = list(filter(lambda r: r.name == self.POINTER_ROLE_NAME, 
                            guild.roles))
        for role in reversed(roles):
            try:
                await role.edit(name=self.POINTER_ROLE_NAME)
            except discord.Forbidden:
                continue
            return role
    
    async def _standings_sort_key(self):
        game = await vrml.get_game(self.default_game)
        standings = await game.fetch_standings()
        return {t.name: t.rank for t in standings}
    
    async def _get_needed_roles(self):
        cache = PlayerCache()
        guild = self.bot.get_guild(self.guild_id)
        needed_roles = set()
        for member in guild.members:
            teams = cache.get_teams_from_discord_id(member.id, self.default_game)
            if not teams:
                continue
            needed_roles.add(teams[0].name)
        
        key = await self._standings_sort_key()
        needed_roles = list(needed_roles)
        needed_roles.sort(key=lambda x: key[x])
        return needed_roles
    
    async def _create_roles(self, roles):
        guild = self.bot.get_guild(self.guild_id)
        for role in roles:
            id_if_existing = self.get_managed_roles()[role]
            if (id_if_existing is not None 
                    and guild.get_role(id_if_existing) is not None):
                continue
            r = await guild.create_role(name=role, hoist=True, mentionable=True)
            self.add_managed_role(r)
    
    async def _sort_roles(self, roles):
        guild = await self.bot.fetch_guild(self.guild_id)
        managed_roles = self.get_managed_roles()
        pointer_role = await self._get_pointer_role()
        for role in roles:
            id = managed_roles.get(role, None)
            if id is None:
                continue
            r = guild.get_role(id)
            offset = 0 if r >= pointer_role else -1
            await r.edit(position=pointer_role.position + offset)
    
    async def _create_sort_team_roles(self, roles):
        await self._create_roles(roles)
        await self._sort_roles(roles)
    
    async def _assign_team_roles(self):
        cache = PlayerCache()
        guild = self.bot.get_guild(self.guild_id)
        roles = self.get_managed_roles()
        for member in guild.members:
            teams = cache.get_teams_from_discord_id(member.id, self.default_game)
            if not teams:
                continue
            role = guild.get_role(roles[teams[0].name])
            if role is None:
                continue
            await member.add_roles(role)
    
    async def _delete_empty_team_roles(self):
        guild = self.bot.get_guild(self.guild_id)
        role_ids = list(self.get_managed_roles().values())
        for id in role_ids:
            role = guild.get_role(id)
            if not any(r.id == role.id for m in guild.members for r in m.roles):
                await role.delete()
    
    async def _create_assign_team_roles(self, managed_roles):
        member_roles = set()
        cache = PlayerCache()
        for member in self.guild.members:
            player_profiles = cache.get_players_from_discord_id(
                id=member.id, 
                game=self.default_game)
            if player_profiles:
                # member is playing in VRML, update roles
                player = player_profiles[0]
                
            
            else:
                # member is not playing in VRML (any more)
                # removing roles
                pass
        return member_roles

    async def update_team_roles(self):
        if not self.manage_team_roles:
            log.info(f"{self.guild_id}: Guild does not manage team roles.")
            return
        if not self.default_game:
            log.info(f"{self.guild_id}: No default game found, update of team roles skipped.")
            return
        existing_roles = self.get_team_roles()
        member_roles = await self._create_assign_team_roles(existing_roles)
        await self._delete_empty_team_roles(roles)
        await self._update_team_role_ranking
        

_guilds = {}
_bot = None

def get_guild(guild_id):
    g = _guilds.get(guild_id, None)
    if g is None:
        g = Guild(_bot, guild_id)
        _guilds[guild_id] = g
    return g

def drop_guild(guild_id):
    _guilds.pop(guild_id, None)

def init_guilds(bot):
    global _bot
    _bot = bot
    for guild in bot.guilds:
        get_guild(guild.id)

