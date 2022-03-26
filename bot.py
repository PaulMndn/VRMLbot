import discord
from discord import Embed, Option
from discord.ext.commands import Bot
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import re
import json

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
game_names = ["Echo Arena", "Onward", "Pavlov",
              "Snapshot", "Contractors", "Final Assault"]


bot = Bot(debug_guilds=debug_guilds)
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
async def on_application_command(ctx):
    cmd_name = ctx.command.qualified_name
    params = {}
    for o in ctx.interaction.data.get('options', []):
        params[o['name']] = o['value']
    log.info(f"{ctx.guild_id}: {ctx.author} sent command '{cmd_name}' "
             f"with {params}.")

@bot.event
async def on_application_command_completion(ctx):
    log.debug(f"{ctx.guild_id}: Finished command '{ctx.command.qualified_name}'.")

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
            "the deveoper or report a bug. Infos for how and where to do that "
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
    log.info(f"Admin sent {cmd} with {content}.")

    if cmd == "!help":
        s = await admin_actions.help()
        await msg.channel.send(s)

    if cmd == "!msg_guilds":
        count = await admin_actions.msg_guilds(content)
        await msg.channel.send(f"Sent message to {count}/{len(bot.guilds)} guild(s).")

    if cmd == "!msg_owners":
        count = await admin_actions.msg_owners(content)
        await msg.channel.send(f"Sent message to {count} guild owners")
    
    if cmd == "!msg_both":
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


@bot.slash_command()
async def about(ctx):
    'About this bot...'
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
         "    - searching players by their Discord tag\n"
         "    - role management to add team roles to server members\n")
    await ctx.respond(s)


@bot.slash_command(guild_ids=config.debug_guilds)
async def ping(ctx):
    await ctx.respond("Pong!")


set = bot.create_group(name="set")

@set.command(name="game")
async def set_game(ctx, 
                   game: Option(str, description="Game/league name. None removes the server's default game", choices=game_names+["None"])):
    """Set a default game/league for the commands."""
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.respond(
            "You need the `Manage Server` permission to use this command.\n"
            "(This is the same permission required to add bots to a server.)",
            ephemeral=True)
        return
    
    if game == "None":
        game = None
    
    guild = lib.get_guild(ctx.guild_id)
    old = guild.default_game
    guild.default_game = game
    if old:
        s = f"Changed default game for this server vom {old} to {game}."
    else:
        s = f"Set default game for this server to {game}."
    await ctx.respond(s, ephemeral=True)


@bot.slash_command()
async def game(ctx,
               game: Option(str, "game name", choices=game_names)=None):
    "Get general information about a league in VRML."
    game = game or lib.get_guild(ctx.guild_id).default_game
    if game is None:
        # no game given and no default set
        await ctx.respond(
            "Please specify a game as no default is set for this server.\n"
            "You can set one using `/set game`")
        return
    
    game: vrml.Game = await vrml.get_game(game)
    await ctx.respond(embed = game.get_embed())


@bot.slash_command()
async def player(ctx,
                 name: Option(str, "Name of the player or @ a member"),
                 game: Option(str, "Name of the game/league to search, all leagues are searched if omitted.", choices=["Any"]+game_names)=None):
    """Search for an active player."""
    await ctx.defer()   # buying some time

    game = game or guilds[ctx.guild_id].default_game
    if game == "Any":
        game = None
    
    if match := re.match("^<@.?(\d+)>$", name):
        id = match.group(1)
        players = []
        with open("data/discord_players.json") as f:
            discord_players = json.load(f)
        exact_players = [vrml.PartialPlayer(d) 
                         for d in discord_players.get(str(id), [])]
    else:
        players = await vrml.player_search(name)
        exact_players = list(filter(lambda x: x.name.lower() == name.lower(),
                                    players))
    
    if exact_players:
        tasks = [bot.loop.create_task(p.fetch()) for p in exact_players]
        exact_players = await asyncio.gather(*tasks)
        if game is not None:
            exact_players = list(filter(lambda p: p.game.name == game, 
                                        exact_players))
        if exact_players:
            await ctx.respond(embeds=[p.get_embed() for p in exact_players])
            return
    
    if len(players) > 30:
        s = (f"{len(players)} players found. Please be more specific:\n"
             + ", ".join(p.name for p in players))
        if len(s) > 2000:   # string too long, shorten it
            s = s[:1996] + " ..."
        
        await ctx.respond(s, ephemeral=True)
        return
    
    if len(players) > 10:
        await ctx.respond("This might take a bit.", 
                          ephemeral=True)
    fetch_tasks = [bot.loop.create_task(player.fetch()) 
                   for player in players]
    players = await asyncio.gather(*fetch_tasks)

    if game is not None:
        players = list(filter(lambda p:p.game.name == game, players))
    
    if not players:
        await ctx.respond("No players found.")
        return
    
    if len(players) > 10:
        await ctx.respond(
            "More then 10 players found. Please be more specific.\n"
            f"Found players: {', '.join(p.name for p in players)}")
        return
    await ctx.respond(embeds=[p.get_embed() for p in players])
    

@bot.slash_command()
async def team(ctx,
               name: Option(str, "Team name to search for."),
               match_links: Option(bool, name="match-links", description="Include match links (Default: false)")=False,
               vod_links: Option(bool, name="vod-links", description="Include VOD links if exists (Default: true)")=True,
               game: Option(str, "The game the team plays.", choices=game_names)=None):
    "Get details on a specific team."
    game = game or guilds[ctx.guild_id].default_game
    if game is None:
        await ctx.respond(
            "Please spefify a game to search in. \n"
            "You can set a default game for this server with `/set game`",
            ephemeral=True)
        return

    await ctx.defer()
    
    game = await vrml.get_game(game)
    teams = await game.search_team(name)
    
    if len(teams) == 0:
        await ctx.respond("No teams found.")
        return
    
    exact_team = next(filter(lambda t: t.name.lower() == name.lower(), teams), None)
    if exact_team is not None:
        team = await exact_team.fetch()
        await ctx.respond(embed=team.get_embed(match_links, vod_links))
    else:
        if len(teams) > 10:
            s = "More than 10 teams found. Please be more specific.\n" \
                f"Found: {', '.join(t.name for t in teams)}"
            if len(s) > 2000:
                # cut off everything above the 2000 char limit
                s = s[:1996] + " ..."
            await ctx.respond(s)
            return
        
        tasks = [bot.loop.create_task(t.fetch()) for t in teams]
        teams = await asyncio.gather(*tasks)
        await ctx.respond(embeds=[t.get_embed(match_links, vod_links)
                                  for t in teams])


@bot.user_command(name="VRML Player")
async def vrml_player(ctx, member):
    game = lib.get_guild(ctx.guild_id).default_game
    cache = lib.PlayerCache()
    players = cache.get_players_from_discord_id(member.id, game)
    players = await asyncio.gather(*[p.fetch() for p in players])
    embeds = [p.get_embed() for p in players]
    if embeds:
        await ctx.respond("", embeds=embeds, ephemeral=True)
    else:
        await ctx.respond("No VRML player profiles found.", ephemeral=True)


@bot.user_command(name="VRML Team")
async def vrml_team(ctx, member):
    game = lib.get_guild(ctx.guild_id).default_game
    cache = lib.PlayerCache()
    teams = cache.get_teams_from_discord_id(member.id, game)
    teams = await asyncio.gather(*[t.fetch() for t in teams])
    embeds = [t.get_embed() for t in teams]
    if embeds:
        await ctx.respond("", embeds=embeds, ephemeral=True)
    else:
        await ctx.respond("No VRML teams found.", ephemeral=True)



bot.run(config.token)
