from discord.ext.tasks import loop
from datetime import time, datetime, timezone
import asyncio
import json
import logging
import vrml
import logging

__all__ = [
    "start_tasks"
]

log = logging.getLogger(__name__)

@loop(time=time(hour=0, minute=0))
async def fetch_vrml_discord_player(force=False):
    """Separate for each game in VRML, the discord handle with 
    corresponding player_id and team_id and team rank are fetched.
    
    Only fetched on Monday 00:00 UTC"""
    if not force and datetime.now(tz=timezone.utc).weekday != 0:
        # its not Monday morning
        log.debug(f"Skipped updating discord_players, not Monday.")
        return
    
    log.info(f"Start updating discord_players.json.")
    data = {}
    for game in vrml.utils.short_game_names:
        log.info(f"Updating cache for {game}...")
        game = await vrml.get_game(game)
        p_players = await game.fetch_players()
        players: list[vrml.Player]= []
        for i in range(0, len(p_players), 10):
            # fetching 10 players at once to speed up but not overload
            # the API
            async def fetch_player(p_player):
                for i in range(5):
                    try:
                        return await p_player.fetch()
                    except TypeError:
                        # Catch weird API response returning `None` instead
                        # of `dict` give it 5 tries or return `None`.
                        continue
                
            coros = [fetch_player(p) for p in p_players[i: i+10]]
            ret = await asyncio.gather(*coros)
            players += [p for p in ret if p is not None]
        for player in players:
            id = player.user.discord_id
            if id is None:
                continue
            player_data = {
                "gameName": game.name,
                "playerID": player.id,
                "playerName": player.name,
                "teamID": player.team.id,
                "teamName": player.team.name
            }
            if id in data:
                data[id].append(player_data)
            else:
                data[id] = [player_data]
    with open(f"data/discord_players.json", "w") as f:
        json.dump(data, f)
    log.info(f"Finished updating cached discord id to player profiles.")

def start_tasks():
    try:
        fetch_vrml_discord_player.start()
        log.info("Started tasks.")
    except RuntimeError as e:
        log.warning(f"{e.__class__.__name__}: {e}")

