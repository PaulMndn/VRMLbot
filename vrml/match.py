from datetime import datetime
from . import BASE_URL
from .team import PartialTeam

__all__ = (
    "Match",
)


class CastingInfo:
    def __init__(self, data) -> None:
        self.channel_type = data.get("channelType", None)
        self.channel_id = data.get("channelID", None)
        self.channel_url = data.get("channelURL", None)
        
        self.caster_id = data.get("casterID", None)
        self.caster = data.get("caster", None)
        self._rel_caster_logo = data.get("casterLogo", None)
        self.caster_logo = None
        if self._rel_caster_logo is not None:
            self.caster_logo = BASE_URL + self._rel_caster_logo
            
        self.co_caster_id = data.get("coCasterID", None)
        self.co_caster = data.get("coCaster", None)
        self._rel_co_caster_logo = data.get("coCasterLogo", None)
        self.co_caster_logo = None
        if self._rel_co_caster_logo is not None:
            self.co_caster_logo = BASE_URL + self._rel_co_caster_logo

        self.cameraman_id = data.get("cameramanID", None)
        self.cameraman = data.get("cameraman", None)
        self.cameraman_logo = data.get("cameramanLogo", None)
        if self.cameraman_logo is not None:
            self.cameraman_logo = BASE_URL + self.cameraman_logo

        self.post_game_interview_id = data.get("postGameInterviewID", None)
        self.post_game_interview = data.get("postGameInterview", None)
        self.post_game_interview_logo = data.get("postGameInterviewLogo", None)
        self.post_game_interview_logo = None
        if self.post_game_interview_logo is not None:
            self.post_game_interview_logo = BASE_URL + self.post_game_interview_logo
        
    async def _fetch_caster(self, id): # move to Game / PartialGame
        raise NotImplementedError
        # return http.get_game_caster(self.game, id)

    async def fetch_caster(self):
        return await self._fetch_caster(self.caster_id)
    
    async def fetch_co_caster(self):
        return await self._fetch_caster(self.co_caster_id)
    
    async def fetch_interviewer(self):
        return await self._fetch_caster(self.post_game_interview_id)
        

class Match:
    def __init__(self, data) -> None:
        self.season = data.get("seasonName", None)
        self.winning_team_id = data.get("winningTeamID", None)
        self.losing_team_id = data.get("losingTeamID", None)
        self.home_score = data.get("homeScore", None)
        self.away_score = data.get("awayScore", None)
        self.is_tie = data.get("isTie", None)
        self.is_forfeit = data.get("isForfeit", None)
        self.id = data.get("matchID", None)
        self.week = data.get("week", None)
        self.is_scheduled = data.get("isScheduled", None)
        self.is_specific_division = data.get("isSpecificDivision", None)
        self.is_challenge = data.get("isChallenge", None)
        self.is_cup = data.get("isCup", None)
        self.date_scheduled = data.get("dateScheduledUTC", None)
        if self.date_scheduled is not None:
            aware_date = self.date_scheduled + "+00:00"
            self.date_scheduled = datetime.fromisoformat(aware_date)
        self.date_scheduled_user = data.get("dateScheduledUser", None)
        self.date_scheduled_user_tz = data.get("dateScheduledUserTimezone", None)
        self.vod_url = data.get("vodUrl", None)
        self.home_highlights = data.get("homeHighlights", None)
        self.away_highlights = data.get("awayHighlights", None)
        self.postpone_team_id = data.get("postponeTeamID", None)
        self.mods_review = data.get("modsReview", None)
        self.mods_review_note = data.get("modsReviewNote", None)

        self.casting_info = CastingInfo(data.get("castingInfo", {}))

        home_team_data = data.get("homeTeam", {})
        away_team_data = data.get("awayTeam", {})
        self.home_team_submitted_scores = home_team_data.pop("submittedScores", None)
        self.away_team_submitted_scores = away_team_data.pop("submittedScores", None)
        self.home_team = PartialTeam(home_team_data)
        self.away_team = PartialTeam(away_team_data)

    @property
    def scores_submitted(self):
        return self.home_team_submitted_scores and \
               self.away_team_submitted_scores
