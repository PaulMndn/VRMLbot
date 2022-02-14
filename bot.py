import discord
from discord import Embed, Option, OptionChoice
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import logging
from logging.handlers import RotatingFileHandler

import vrml


logging.getLogger("discord").level=logging.INFO
handler = RotatingFileHandler(filename="./log/VRMLbot.log",
                              backupCount=3,
                              maxBytes=100 * 1024,
                              encoding="utf-8")
logging.basicConfig(level=logging.DEBUG,
                    handlers=[handler],
                    format="{asctime} - {levelname:<8} - {name}: {message}",
                    style="{")
log = logging.getLogger("main")


with open("bot.token", "r") as f:
    token = f.read().strip()


debug_guilds = [927322319691591680]
game_names = ["Echo Arena", "Onward", "Pavlov",
              "Snapshot", "Contractors", "Final Assult"]


bot = Bot(debug_guilds=debug_guilds)

@bot.event
async def on_ready():
    log.info("Bot initialized and logged in.")


@bot.slash_command()
async def ping(ctx):
    await ctx.respond("Pong!")


@bot.slash_command()
async def game(ctx,
               game: Option(str, "game name", choices=game_names)):
    "Get general information of a game in VRML."
    game: vrml.Game = await vrml.get_game(game)
    await ctx.respond(f"{game.name} ({game.id}): can be found here: <{game.url}>")


@bot.slash_command()
async def player(ctx,
                 name: Option(str, "Name of the player"),
                 game: Option(str, "Name of the game", required=False, choices=game_names)):
    await ctx.defer()   # buying some time

    found_players = await vrml.player_search(name)
    if len(found_players) > 10:
        await ctx.respond("Many players found. This might take a bit.", ephemeral=True)
    fetch_tasks = [bot.loop.create_task(player.fetch()) for player in found_players]
    players = await asyncio.gather(*fetch_tasks)

    if game is not None:
        players = list(filter(lambda p:p.game.name == game, players))
    
    if not len(players):
        await ctx.respond("No player found.")
        return
    
    embeds = []
    for player in players:
        e = Embed(title=f"`{player.name}`", description=f"`{player.user.discord_tag}`")
        e.set_thumbnail(url=player.logo_url)
        embeds.append(e)
    await ctx.respond("", embeds=embeds)


@bot.slash_command()
async def team(ctx,
               team: Option(str, "Team name to search for."),
               game: Option(str, "The game the team plays.", choices=game_names)):
    await ctx.respond("foobar")


@bot.user_command(name="VRML Team")
async def vrml_team(ctx, member):
    await ctx.respond(f"Some info about {member}.")



bot.run(token)
