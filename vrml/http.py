import logging
from urllib.parse import quote
import aiohttp
import json
import asyncio

from vrml.season import Season

log = logging.getLogger(__name__)


class HTTPException(Exception):
    pass


class Route:
    BASE = 'https://api.vrmasterleague.com'

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        
        url = (self.BASE + self.path)
        if parameters:
            self.url = url.format(**{k: quote(v) if isinstance(v, str) else v for k,v in parameters.items()})
        else:
            self.url = url


async def request(route, **kwargs):
    method = route.method
    url = route.url

    async with aiohttp.ClientSession() as session:
        for tries in range(5):
            async with session.request(method, url, **kwargs) as r:
                data = json.loads(await r.text(encoding="utf-8"))

                # request successfull, return json data
                if r.status == 200:
                    log.debug("%s %s has returned %s", method, url, r.status)
                    return data
                
                # rate limited, wait and try again if tries left
                if r.status == 429:
                    wait_time = float(r.headers['X-RateLimit-Reset-After'])
                    log.warning(f"We're being rate limited. Retry in {wait_time:.3f} seconds.")
                    
                    if r.headers['X-RateLimit-Global'] == 'True':
                        log.warning("Rate limit is global. %s", r.headers['X-RateLimit-Global'])
                    
                    await asyncio.sleep(wait_time)
                    log.debug("Done waiting for rate limit. Retrying...")
                    
                    continue

        # ran out of retries
        raise HTTPException(f"{route.method} {route.url} with querry params {kwargs} ran out of retries.")



async def player_search(name):
    """Get data from endpoint `/Players/Search`.
    Searches all leagues.
    
    Query
        name: Player name to search for
    """
    params = {"name": name}
    return await request(Route("GET", "/Players/Search"), params=params)


async def get_game(game):
    """Get data from `/{game}`.
    
    URL params
        game: Name of game (with omitted whitespaces)
    """
    return await request(Route("GET", "/{game}", game=game))


async def get_player_detailed(player_id):
    """Get data from `/Players/{player_id}/Detailed`
    
    URL params
        player_id: ID of player to fetch data for.
    """
    r = Route("GET", "/Players/{player_id}/Detailed", player_id=player_id)
    return await request(r)


async def get_team(team_id):
    """Get data from `/Teams/{team_id}`
    
    URL params
        team_id: ID of team to fetch data for.
    """
    r = Route("GET", "/Teams/{team_id}", team_id=team_id)
    return await request(r)


async def search_team(game, name, season=None, region=None):
    """Get data from `/{game}/Teams/Search`
    
    URL params
        game: game name the team plays (omit whitespaces)
    
    Query params
        name: Team name to search for.
        season: `str` of season id or `Season` object.
        region: Region the team plays in (`NA`, `EU`, `OCE`, or `none`).
    """
    r = Route("GET", "/{game}/Teams/Search", game=game)
    query = {"name": name}
    if season:
        if isinstance(season, Season):
            query["season"] = season.id
        else:
            query["season"] = season
    if region:
        query["region"] = region
    return await request(r, params=query)


async def get_match_sets(match_id):
    r = Route("GET", "/Matches/{match_id}/Sets", match_id=match_id)
    return await request(r)



# async def main():
#     # loop = asyncio.get_event_loop()
#     # loop.run_until_complete()
#     r = Route("GET", "/{game}/Standings", game="EchoArena")
#     params = {
#         "region": "EU"
#     }
#     data = await request(r, params=params)
#     for dict in data:
#         for k, v in dict.items():
#             print(k, "    ", v)

# if __name__ == '__main__':
#     for i in range(20):
#         asyncio.run(main())
#         print("============================================================0")


