from discord.ext.tasks import loop
from datetime import time, datetime, timezone
import asyncio
import json
import logging
import vrml
import logging

__all__ = [
    "start"
]

log = logging.getLogger(__name__)

@loop(time=time(hour=0, minute=0))
async def fetch_vrml_discord_player(force=False):
    """Separate for each game in VRML, the discord handle with corresponding 
    player_id and team_id and team rank are fetched. 
    
    Only fetched on Monday 00:00 UTC"""
    if not force and datetime.now(tz=timezone.utc).weekday != 0:
        # its not Monday morning
        log.debug(f"Skipped updating discord_players, not Monday.")
        return
    
    log.info(f"Start updating cached discord id to player profiles.")
    for game in vrml.utils.short_game_names:
        log.info(f"Updating cache for {game}...")
        game = await vrml.get_game(game)
        p_players = await game.fetch_players()
        players: list[vrml.Player]= []
        for i in range(0, len(p_players), 10):
            tasks = [
                asyncio.create_task(p.fetch()) for p in p_players[i: i+10]
            ]
            players += await asyncio.gather(*tasks)
        data = {}
        for player in players:
            if player.user.discord_id is None:
                continue
            data[player.user.discord_id] = {
                "game_name": game.name,
                "player_id": player.id,
                "player_name": player.name,
                "team_id": player.team.id,
                "team_name": player.team.name
            }
        with open(f"data/{game.name} - discord_players.json", "w") as f:
            json.dump(data, f)
    log.info(f"Finished updating cached discord id to player profiles.")

def start():
    try:
        fetch_vrml_discord_player.start()
    except RuntimeError as e:
        log.warning(f"{e.__class__.__name__}: {e}")

