from datetime import datetime, timezone

class Season:
    def __init__(self, data) -> None:
        self.id = data.get("seasonID", None)
        self.name = data.get("seasonName", None)
        self.is_current = data.get("isCurrent", None)
        self.championship_url = data.get("championshipUrl", None)

        self.start = data.get("dateStartUTC", None)
        if self.start is not None:
            self.start = datetime.fromisoformat(self.start + "+00:00") # timezone aware
        self.end_date = data.get("dateEndUTC", None)
        if self.end_date is not None:
            self.end_date = datetime.fromisoformat(self.end_date + "+00:00") # timezone aware
        self.championship_start = data.get("dateChampionshipStartUTC", None)
        if self.championship_start is not None:
            self.championship_start = datetime.fromisoformat(self.championship_start + "+00:00") # timezone aware


