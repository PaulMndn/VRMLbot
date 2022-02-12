import logging
from urllib.parse import quote
import aiohttp
import json
import asyncio

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
    params = {"name": name}
    return await request(Route("GET", "/Players/Search"), params=params)

async def get_game(name):
    return await request(Route("GET", "/{game}", game=name))

async def get_player_detailed(player_id):
    r = Route("GET", "/Players/{player_id}/Detailed", player_id=player_id)
    return await request(r)





async def main():
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete()
    r = Route("GET", "/{game}/Standings", game="EchoArena")
    params = {
        "region": "EU"
    }
    data = await request(r, params=params)
    for dict in data:
        for k, v in dict.items():
            print(k, "    ", v)

if __name__ == '__main__':
    for i in range(20):
        asyncio.run(main())
        print("============================================================0")


