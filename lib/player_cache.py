import json
import logging
import vrml

__all__ = [
    "PlayerCache"
]

log = logging.getLogger(__name__)

class PlayerCache:
    def __init__(self):
        try:
            with open("data/discord_players.json") as f:
                self._data = json.load(f)
        except FileNotFoundError as e:
            log.error('"data/discord_players.json" file not found.')
            self._data = {}
    
    def _get_players(self, id):
        return self._data.get(str(id), [])
    
    def _filter_for_game(self, players, game):
        return [p for p in players if p['gameName'] == game]
    
    def get_players_from_discord_id(self, id, game=None):
        players = self._get_players(id)
        if game is not None:
            players = self._filter_for_game(players, game)
        return [vrml.PartialPlayer(d) for d in players]
    
    def get_teams_from_discord_id(self, id, game=None):
        players = self._get_players(id)
        if game is not None:
            players = self._filter_for_game(players, game)
        return [vrml.PartialTeam(d) for d in players]
