import json
import logging
from typing import Optional, Any
import vrml

__all__ = [
    "PlayerCache"
]

log = logging.getLogger(__name__)

class PlayerCache:
    def __init__(self) -> None:
        try:
            with open("data/discord_players.json") as f:
                self._data: dict[str, list[dict[str, Any]]] = json.load(f)
        except FileNotFoundError as e:
            log.error('"data/discord_players.json" file not found.')
            self._data = {}
    
    def _get_players(self, id: str | int) -> list[dict[str, Any]]:
        return self._data.get(str(id), [])
    
    def _filter_for_game(self, players: list[dict[str, Any]], game: str) -> list[dict[str, Any]]:
        return [p for p in players if p['gameName'] == game]
    
    def get_players_from_discord_id(self, id: str | int, game: Optional[str] = None) -> list[vrml.PartialPlayer]:
        players = self._get_players(id)
        if game is not None:
            players = self._filter_for_game(players, game)
        return [vrml.PartialPlayer(d) for d in players]
    
    def get_teams_from_discord_id(self, id: str | int, game: Optional[str] = None) -> list[vrml.PartialTeam]:
        players = self._get_players(id)
        if game is not None:
            players = self._filter_for_game(players, game)
        return [vrml.PartialTeam(d) for d in players]
