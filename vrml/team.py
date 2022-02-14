from . import BASE_URL
from . import http
from .season import Season
from .player import TeamPlayer

__all__ = (
    "PartialTeam",
    "Team"
)


class MapStats:
    def __init__(self, data) -> None:
        self.map = data.get("mapName", None)
        self.times_played = data.get("played", None)
        self.times_won = data.get("win", None)
        self.win_percentage = data.get("winPercentage", None)
        self.rounds_played = data.get("roundsPlayed", None)
        self.rounds_win = data.get("mapName", None)
        self.rounds_win_percentage = data.get("roundsWinPercentage", None)


class PartialTeam:      # like from /{game}/Teams/Search
    def __init__(self, data) -> None:
        self.id = data.get("teamID", None)
        self.name = data.get("teamName", None)
        self.logo_url = data.get("teamLogo", None)

        # handle data coming from /game/Teams/Search   (this will hopefully be updated soon)
        if self.id is None:
            self.id = data.get("id", None)
        if self.name is None:
            self.name = data.get("name", None)
        if self.logo_url is None:
            self.logo_url = data.get("image", None)
        
        if self.logo_url is not None:
            self.logo_url = BASE_URL + self.logo_url

    async def fetch(self):
        data = await http.get_team(self.id)
        return Team(data)


class Team:
    def __init__(self, data) -> None:
        # data["context"] is ignored for now
        team_data = data.pop("team", {})
        self.season = Season(data.pop("season", {}))
        season_map_stats_data = data.pop("seasonStatsMaps", [])
        season_matchs_data =  data.pop("seasonMatches", [])
        ex_members_data = data.pop("exMembers", [])

        self.id = team_data.get("teamID", None)
        self.name = team_data.get("teamName", None)
        self.recruit_possible = team_data.get("recruitPossible", None)
        self.missing_gp_for_mmr = team_data.get("missingGPForMMR", None)
        self._relative_logo_url = team_data.get("teamLogo", None)
        self.logo_url = None
        if self._relative_logo_url is not None:
            self.logo_url = BASE_URL + self._relative_logo_url
        self.region_id = team_data.get("regionID", None)
        self.region = team_data.get("region", None)
        
        self._relative_fanart_url = team_data.get("fanart", None)
        self.fanart_url = None
        if self._relative_fanart_url is not None:
            self.fanart_url = BASE_URL + self._relative_fanart_url
        self.game_name = team_data.get("gameName", None)
        self.division = team_data.get("divisionName", None)
        self._relative_division_logo_url = team_data.get("divisionLogo", None)
        self.division_logo_url = None
        if self._relative_division_logo_url is not None:
            self.division_logo_url = BASE_URL + self._relative_division_logo_url
        self.games_played = team_data.get("gp", None)
        self.wins = team_data.get("w", None)
        self.ties = team_data.get("t", None)
        self.loses = team_data.get("l", None)
        self.points = team_data.get("pts", None)
        self.plus_minus = team_data.get("plusMinus", None)
        self.mmr = team_data.get("mmr", None)

        # some master cycle stuff
        self.cycle_games_played = team_data.get("cycleGP", None)
        self.cycle_wins = team_data.get("cycleW", None)
        self.cycle_ties = team_data.get("cycleT", None)
        self.cycle_loses = team_data.get("cycleL", None)
        self.cycle_tie_breaker = team_data.get("cycleTieBreaker", None)
        self.cycle_plus_minus = team_data.get("cyclePlusMinus", None)
        self.cycle_score_total = team_data.get("cycleScoreTotal", None)

        # some bools
        self.is_active = team_data.get("isActive", None)
        self.is_retired = team_data.get("isRetired", None)
        self.is_deleted = team_data.get("isDeleted", None)
        self.is_recruiting = team_data.get("isRecruiting", None)
        self.is_blocking_recruiting = team_data.get("isBlockingRecruiting", None)
        self.is_master = team_data.get("isMaster", None)
        self.is_league_team = team_data.get("isLeagueTeam", None)

        self.max_challenges_this_week = team_data.get("maxChallengesThisWeek", None)
        self.rank_regional = team_data.get("rank", None)
        self.rank_worldwide = team_data.get("rankWorldwide", None)
        
        self.seasons_played = [Season(d) for d in team_data.get("seasonsPlayed", []) ]
        self.players = [TeamPlayer(d) for d in team_data.get("players", []) ]
        for p in self.players:
            p.team = self
        
        bio = team_data.get("bio", {})
        self.bio = bio.get("bioInfo", None)
        self.discord_server_id = bio.get("discordServerID", None)
        self.discord_invite_url = bio.get("discordInvite", None)

        from .match import Match
        self.upcoming_matches = [Match(d) for d in team_data.get("upcomingMatches", [])]   # to implement from team_data["upcomingMatches"]

        self.map_stats = [MapStats(d) for d in season_map_stats_data]

        self.matches = [Match(d) for d in season_matchs_data]     # TODO: to implement from season_matches_data
        self.ex_memers = [TeamPlayer(d) for d in ex_members_data]


