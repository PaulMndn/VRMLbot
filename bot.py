import discord
from discord import Embed
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import re
import json
from typing import Optional, Literal

import lib
import vrml

config = lib.get_config()

logging.getLogger("discord").level=logging.INFO
handler = RotatingFileHandler(filename="./log/VRMLbot.log",
                              backupCount=4,
                              maxBytes=1 * 1024 * 1024,
                              encoding="utf-8")
logging.basicConfig(level=logging.DEBUG if config.dev else logging.INFO,
                    handlers=[handler],
                    format="{asctime} - {levelname:<8} - {name}: {message}",
                    style="{")
log = logging.getLogger("main")


debug_guilds = config.debug_guilds if config.dev else None
game_names = list(vrml.short_game_names.keys())

# Set up intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content in admin commands

class VRMLBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        # Sync the command tree for slash commands
        if config.dev and config.debug_guilds:
            # Sync to debug guilds only in dev mode
            for guild_id in config.debug_guilds:
                guild = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
        else:
            # Sync globally in production
            await self.tree.sync()
        print("Command tree synced!")

bot = VRMLBot()
admin_actions = lib.AdminActions(bot)

def init():
    lib.init_guilds(bot)
    lib.start_tasks()


@bot.event
async def on_ready():
    init()
    log.info("Bot initialized and logged in.")


@bot.event
async def on_guild_join(guild):
    log.info(f"Bot was added to new guild: {guild}, ID: {guild.id}")
    e = Embed(title="Hello :wave:")
    e.description = (
        "Thanks for adding me to your server!\n"
        "With me you can access [VRML](https://vrmasterleague.com) "
        "data like player or team info directly from inside Discord.")
    e.add_field(
        name="Commands",
        value=("You can use slash commands to interact with me. Just "
               "type `/` in a chat on your server and the available "
               "commands will show up.\n"
               "It is recommended to **set a default game for your server**. "
               "You can do so using the `/set game` command."),
        inline=False
    )
    e.add_field(
        name="Coming soon",
        value=("Soon I will also be able to automatically manage team "
               "roles and add and remove them as players join and "
               "leave VRML teams. So you can directly ping a specific team "
               "or see what team a player is playing on."),
        inline=False
    )
    e.set_footer(text=f"Sent from {guild.name}")
    owner = await bot.fetch_user(guild.owner_id)
    try:
        await owner.send(embed=e)
    except discord.errors.Forbidden:
        log.warning(
            f"Can't send welcome message to guild owner {owner} in {guild.name}"
        )
        pass

    if guild.system_channel is not None:
        await guild.system_channel.send(
            "Hello there :wave:\n"
            "I have just been added to this server. With me you can access "
            "VRML data like player or team info directly from inside Discord.\n"
            "Give it a try! Just type `/` to see my available commands."
        )
    log.debug(f"{guild.id}: Welcome messages sent")


@bot.event
async def on_guild_remove(guild):
    log.info(f"Bot left guild {guild}, ID: {guild.id}")
    lib.drop_guild(guild.id)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        command_name = interaction.command.name if interaction.command else "unknown"
        log.info(f"{interaction.guild_id}: {interaction.user} used command '{command_name}'")

@bot.event
async def on_application_command(ctx):
    cmd_name = ctx.command.qualified_name
    params = {}
    for o in ctx.interaction.data.get('options', []):
        params[o['name']] = o['value']
    log.info(f"{ctx.guild_id}: {ctx.author} sent command '{cmd_name}' "
             f"with {params}.")

@bot.event
async def on_error(event_method: str, *args, **kwargs) -> None:
    log.error(f"Error occured in {event_method}", exc_info=True)

@bot.event
async def on_application_command_completion(ctx):
    log.debug(f"{ctx.guild_id}: Finished command '{ctx.command.qualified_name}'.")

# Error handler for app_commands (slash commands)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandInvokeError):
        original = error.original
        log.error(f"{interaction.guild_id}: An exception was raised during execution "
                  f"of command '{interaction.command.name}'.")
        log.exception(f"{original.__class__.__name__}: {original}", 
                      exc_info=original)
        
        if isinstance(original, vrml.http.HTTPServiceUnavailable):
            message = ("VRML is not responding. This can happen during match "
                      "generation. Please try again later. \nIf the issue persists, "
                      "please contact the developer or report a bug. \n"
                      "Information on where to report bugs can be found in `/about`.")
        else:
            message = ("An unknown error occured during execution of the command. "
                      "Please try again later. \nIf the issue persists, please contact "
                      "the developer or report a bug. Infos for how and where to do that "
                      "can be found in `/about`.")
        
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    else:
        log.error(f"App command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "An unexpected error occurred. Please try again later.",
                ephemeral=True
            )

# Keep the old error handler for any remaining command framework usage        
@bot.event
async def on_application_command_error(ctx, exc):
    original = exc.original
    log.error(f"{ctx.guild_id}: An exception was raised during execution "
              f"of command '{ctx.command.qualified_name}'.")
    log.exception(f"{original.__class__.__name__}: {original}", 
                  exc_info=original)
    
    if isinstance(original, vrml.http.HTTPServiceUnavailable):
        await ctx.respond(
            "VRML is not responding. This can happen during match "
            "generation. Please try again later. \nIf the issue persists, "
            "please contact the developer or report a bug. \n"
            "Information on where to report bugs can be found in `/about`.",
            ephemeral=True)
    else:
        await ctx.respond(
            "An unknown error occured during execution of the command. "
            "Please try again later. \nIf the issue persists, please contact "
            "the developer or report a bug. Infos for how and where to do that "
            "can be found in `/about`.",
            ephemeral=True)


@bot.event
async def on_message(msg: discord.Message):
    if msg.guild is not None or msg.author.id != config.admin_id:
        return
    
    cmd, sep, content = msg.content.partition(" ")
    if not sep or "\n" in cmd:
        cmd, sep, content = msg.content.partition("\n")
    content = content.strip()
    log.info(f"Admin sent {cmd} with {content !r}.")

    if cmd == "!help":
        s = await admin_actions.help()
        await msg.channel.send(s)

    if cmd == "!msg_guilds":
        if not content:
            await msg.channel.send(f"Please include a message.")
            return
        count = await admin_actions.msg_guilds(content)
        await msg.channel.send(f"Sent message to {count}/{len(bot.guilds)} guild(s).")

    if cmd == "!msg_owners":
        if not content:
            await msg.channel.send(f"Please include a message.")
            return
        count = await admin_actions.msg_owners(content)
        await msg.channel.send(f"Sent message to {count} guild owners")
    
    if cmd == "!msg_both":
        if not content:
            await msg.channel.send(f"Please include a message.")
            return
        count_guilds, count_owners = await admin_actions.msg_both(content)
        s = f"Sent message to {count_guilds}/{len(bot.guilds)} guild(s)."
        await msg.channel.send(s)
        s = f"Sent message to {count_owners} guild owners"
        await msg.channel.send(s)

    if cmd == "!stats":
        stats = await admin_actions.stats()
        s = ""
        for k, v in stats.items():
            if isinstance(v, list):
                v = ", ".join(v)
            s += f"{k}: {v}\n"
        await msg.channel.send(s[:2000])

    if cmd == "!log":
        try:
            file = await admin_actions.log(content)
            await msg.channel.send(file=file)
        except FileNotFoundError:
            await msg.channel.send(f"Invalid option `{content}`. File not found.")
    
    if cmd == "!update_cache":
        await msg.channel.send("Start updating discord_players.json.")
        await admin_actions.update_discord_players()
        await msg.channel.send("Finished updating discord_players")


@bot.tree.command(name="about", description="About this bot...")
async def about(interaction: discord.Interaction):
    s = ("This is an unofficial Discord integration for VRML. "
         "Developed and maintained by PartyPaul#7757.\n"
         "\n"
         "Since the [VRML API](https://api.vrmasterleague.com) is still in "
         "alpha, this bot is also an alpha version and will be expanded "
         "with functionality continuously.\n"
         "If you found a bug or have a request please DM me or submit them "
         "at <https://github.com/PaulMndn/VRMLbot/issues>.\n"
         "\n"
         "Features that are currently in development include:\n"
         "    - `standings` command for (regional) standings of a league\n"
         "    - role management to add team roles to server members\n")
    await interaction.response.send_message(s)


# Debug command - only available in dev mode
if config.dev:
    @bot.tree.command(name="ping", description="Test command")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")


# Custom transformers for better parameter handling
class GameTransformer(app_commands.Transformer):
    """Transform game input to validate against available games"""
    
    async def transform(self, interaction: discord.Interaction, value: str) -> str:
        # Validate the game exists
        if value and value not in game_names:
            # Try to find a close match (case insensitive)
            for game in game_names:
                if game.lower() == value.lower():
                    return game
            # If no exact match, return as-is and let the command handle it
        return value
    
    async def autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Provide autocomplete for game names"""
        return [
            app_commands.Choice(name=game, value=game)
            for game in game_names if current.lower() in game.lower()
        ][:25]  # Discord limits to 25 choices

# Interactive views for better UX
class TeamSelectionView(discord.ui.View):
    """Interactive view for selecting teams when multiple are found"""
    
    def __init__(self, teams, match_links: bool = False, vod_links: bool = True):
        super().__init__(timeout=300)  # 5 minute timeout
        self.teams = teams
        self.match_links = match_links
        self.vod_links = vod_links
        
        # Add team selection dropdown if we have multiple teams
        if len(teams) > 1:
            self.add_item(TeamSelectDropdown(teams, match_links, vod_links))
    
    async def on_timeout(self):
        # Disable all items when timeout occurs
        for item in self.children:
            item.disabled = True

class TeamSelectDropdown(discord.ui.Select):
    """Dropdown for selecting a team from multiple results"""
    
    def __init__(self, teams, match_links: bool, vod_links: bool):
        self.teams = teams
        self.match_links = match_links
        self.vod_links = vod_links
        
        options = [
            discord.SelectOption(
                label=team.name[:100],  # Discord limits label length
                description=f"Game: {team.game.name}" if hasattr(team, 'game') else "Team details",
                value=str(i)
            )
            for i, team in enumerate(teams[:25])  # Discord limits to 25 options
        ]
        
        super().__init__(
            placeholder="Select a team to view details...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Get the selected team
        team_index = int(self.values[0])
        selected_team = self.teams[team_index]
        
        # Fetch and show team details
        team = await selected_team.fetch()
        await interaction.response.send_message(
            embed=team.get_embed(self.match_links, self.vod_links),
            ephemeral=True
        )

class SetGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="set", description="Server settings commands")

set_group = SetGroup()

@set_group.command(name="game", description="Set a default game/league for the commands")
@app_commands.describe(game="Game/league name. None removes the server's default game")
@app_commands.choices(game=[app_commands.Choice(name=name, value=name) for name in game_names + ["None"]])
async def set_game(interaction: discord.Interaction, game: str):
    # We'll need to handle choices differently - for now, accept any string
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "You need the `Manage Server` permission to use this command.\n"
            "(This is the same permission required to add bots to a server.)",
            ephemeral=True)
        return
    
    if game.lower() == "none":
        game = None
    
    guild = lib.get_guild(interaction.guild_id)
    old = guild.default_game
    guild.default_game = game
    if old:
        s = f"Changed default game for this server from {old} to {game}."
    else:
        s = f"Set default game for this server to {game}."
    await interaction.response.send_message(s, ephemeral=True)

bot.tree.add_command(set_group)


@bot.tree.command(name="game", description="Get general information about a league in VRML")
@app_commands.describe(game="Game name")
@app_commands.choices(game=[app_commands.Choice(name=name, value=name) for name in game_names])
async def game_cmd(interaction: discord.Interaction, game: Optional[str] = None):
    game = game or lib.get_guild(interaction.guild_id).default_game
    if game is None:
        # no game given and no default set
        await interaction.response.send_message(
            "Please specify a game as no default is set for this server.\n"
            "You can set one using `/set game`")
        return
    
    game: vrml.Game = await vrml.get_game(game)
    await interaction.response.send_message(embed=game.get_embed())


@bot.tree.command(name="player", description="Search for an active player")
@app_commands.describe(
    name="Name of the player or @ a member",
    game="Name of the game/league to search, all leagues are searched if omitted"
)
@app_commands.choices(game=[app_commands.Choice(name="Any", value="Any")] + [app_commands.Choice(name=name, value=name) for name in game_names])
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))  # 1 use per 5 seconds per user per guild
async def player_cmd(interaction: discord.Interaction, name: str, game: Optional[str] = None):
    await interaction.response.defer()   # buying some time

    game = game or lib.get_guild(interaction.guild_id).default_game
    if game == "Any":
        game = None
    
    if match := re.match(r"^<@!?(\d+)>$", name):
        id = match.group(1)
        players = []
        exact_players = lib.PlayerCache().get_players_from_discord_id(id)
    else:
        players = await vrml.player_search(name)
        exact_players = list(filter(lambda x: x.name.lower() == name.lower(),
                                    players))
    
    if exact_players:
        tasks = [asyncio.create_task(p.fetch()) for p in exact_players]
        exact_players = await asyncio.gather(*tasks)
        if game is not None:
            exact_players = list(filter(lambda p: p.game.name == game, 
                                        exact_players))
        if exact_players:
            await interaction.followup.send(embeds=[p.get_embed() for p in exact_players])
            return
    
    if len(players) > 30:
        s = (f"{len(players)} players found. Please be more specific:\n"
             + ", ".join(p.name for p in players))
        if len(s) > 2000:   # string too long, shorten it
            s = s[:1996] + " ..."
        
        await interaction.followup.send(s, ephemeral=True)
        return
    
    if len(players) > 10:
        await interaction.followup.send("This might take a bit.", 
                          ephemeral=True)
    fetch_tasks = [asyncio.create_task(player.fetch()) 
                   for player in players]
    players = await asyncio.gather(*fetch_tasks)

    if game is not None:
        players = list(filter(lambda p:p.game.name == game, players))
    
    if not players:
        await interaction.followup.send("No players found.")
        return
    
    if len(players) > 10:
        await interaction.followup.send(
            "More then 10 players found. Please be more specific.\n"
            f"Found players: {', '.join(p.name for p in players)}")
        return
    await interaction.followup.send(embeds=[p.get_embed() for p in players])
    

@bot.tree.command(name="team", description="Get details on a specific team")
@app_commands.describe(
    name="Name of the team or @ a member",
    match_links="Include match links (Default: false)",
    vod_links="Include VOD links if exist (Default: true)",
    game="The game the team plays"
)
@app_commands.choices(game=[app_commands.Choice(name=name, value=name) for name in game_names])
@app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))  # 1 use per 3 seconds per user per guild
async def team_cmd(interaction: discord.Interaction, name: str, match_links: bool = False, vod_links: bool = True, game: Optional[str] = None):
    if match := re.match(r"^<@!?(\d+)>$", name):
        # search team by discord member
        id = match.group(1)
        teams = lib.PlayerCache().get_teams_from_discord_id(id)
        exact_team = None
        await interaction.response.defer() # buying time
    else:
        # search team by name
        game = game or lib.get_guild(interaction.guild_id).default_game
        if game is None:
            await interaction.response.send_message(
                "Please specify a game to search in. \n"
                "You can set a default game for this server with `/set game`",
                ephemeral=True)
            return
        
        await interaction.response.defer()   # buying time
        game = await vrml.get_game(game)
        teams = await game.search_team(name)
        exact_team = next(filter(lambda t: t.name.lower() == name.lower(), teams), None)
    
    if len(teams) == 0:
        await interaction.followup.send("No teams found.")
        return
    
    if exact_team is not None:
        team = await exact_team.fetch()
        await interaction.followup.send(embed=team.get_embed(match_links, vod_links))
    else:
        if len(teams) > 10:
            # Too many teams, use interactive selection
            view = TeamSelectionView(teams[:25], match_links, vod_links)  # Discord limits
            s = f"Found {len(teams)} teams. Use the dropdown below to select one:\n" \
                f"Showing first 25: {', '.join(t.name for t in teams[:25])}"
            if len(s) > 2000:
                s = s[:1996] + " ..."
            await interaction.followup.send(s, view=view)
            return
        elif len(teams) > 3:
            # Medium number of teams, offer interactive selection
            view = TeamSelectionView(teams, match_links, vod_links)
            s = f"Found {len(teams)} teams. You can select one below or scroll through all results:\n" \
                f"{', '.join(t.name for t in teams)}"
            tasks = [asyncio.create_task(t.fetch()) for t in teams]
            teams = await asyncio.gather(*tasks)
            await interaction.followup.send(s, view=view, embeds=[t.get_embed(match_links, vod_links) for t in teams])
            return
        else:
            # Few teams, just show them all
            tasks = [asyncio.create_task(t.fetch()) for t in teams]
            teams = await asyncio.gather(*tasks)
            await interaction.followup.send(embeds=[t.get_embed(match_links, vod_links)
                                      for t in teams])


@bot.tree.context_menu(name="VRML Player")
async def vrml_player(interaction: discord.Interaction, member: discord.Member):
    game = lib.get_guild(interaction.guild_id).default_game
    cache = lib.PlayerCache()
    players = cache.get_players_from_discord_id(member.id, game)
    players = await asyncio.gather(*[p.fetch() for p in players])
    embeds = [p.get_embed() for p in players]
    if embeds:
        await interaction.response.send_message("", embeds=embeds, ephemeral=True)
    else:
        await interaction.response.send_message("No VRML player profiles found.", ephemeral=True)


@bot.tree.context_menu(name="VRML Team")
async def vrml_team(interaction: discord.Interaction, member: discord.Member):
    game = lib.get_guild(interaction.guild_id).default_game
    cache = lib.PlayerCache()
    teams = cache.get_teams_from_discord_id(member.id, game)
    teams = await asyncio.gather(*[t.fetch() for t in teams])
    embeds = [t.get_embed() for t in teams]
    if embeds:
        await interaction.response.send_message("", embeds=embeds, ephemeral=True)
    else:
        await interaction.response.send_message("No VRML teams found.", ephemeral=True)



bot.run(config.token)
