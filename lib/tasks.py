from discord.ext.tasks import loop
from datetime import time, datetime, timezone
import asyncio
import json
import vrml

@loop(time=time(hour=0, minute=0))
async def fetch_vrml_discord_player():
    """Separate for each game in VRML, the discord handle with corresponding 
    player_id and team_id and team rank are fetched. 
    
    Only fetched on Monday 00:00 UTC"""
    if datetime.now(tz=timezone.utc).weekday != 0:
        # its not Monday morning
        return
    
    for game in vrml.utils.short_game_names:
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
                "game": game.name,
                "player_id": player.id,
                "player_name": player.name,
                "team_id": player.team.id,
                "team_name": player.team.name
            }
        with open(f"data/{game._short_name} - discord_players.json", "w") as f:
            json.dump(data, f)

def start():
    fetch_vrml_discord_player.start()

