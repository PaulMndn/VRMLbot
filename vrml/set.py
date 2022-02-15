class Set:
    def __init__(self, data) -> None:
        self.map = data.get("map", None)
        self.map_id = data.get("mapID", None)
        self.home_score = data.get("scoreHome", None)
        self.away_score = data.get("scoreAway", None)