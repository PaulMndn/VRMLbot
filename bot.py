import discord
from discord import Option
from discord.ext import commands
from discord.ext.commands.bot import Bot

import logging
from logging.handlers import RotatingFileHandler

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


debug_guilds = [927322319691591680]

bot = Bot(debug_guilds=debug_guilds)

@bot.event
async def on_ready():
    log.info("Bot initialized and logged in.")


@bot.slash_command()
async def ping(ctx):
    await ctx.respond("Pong!")



bot.run("")