from .utils import *
from . import http
from .season import Season
from .user import User
from .game import PartialGame, Game
from .set import Set
from .match import Match
from .player import PartialPlayer, Player
from .team import PartialTeam, Team



async def player_search(name):
    data = await http.player_search(name)
    return [PartialPlayer(d) for d in data]

async def get_game(name) -> Game:
    name = short_game_names[name]
    data =  await http.get_game(name)
    return Game(data)

