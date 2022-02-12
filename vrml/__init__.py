from .utils import *
from . import http
from .game import PartialGame, Game
from .season import Season
from .player import PartialPlayer, Player
from .user import User



async def player_search(name):
    data = await http.player_search(name)
    return [PartialPlayer(d) for d in data]

async def get_game(name) -> Game:
    data =  await http.get_game(name)
    return Game(data)

