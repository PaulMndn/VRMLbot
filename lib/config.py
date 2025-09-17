import json
from pathlib import Path
import logging
from typing import Optional

__all__ = [
    "get_config"
]

log = logging.getLogger(__name__)

class Config:
    def __init__(self) -> None:
        self._path = Path("config.json")
        if not self._path.exists():
            log.critical("No config file found. Exiting.")
            raise FileNotFoundError("Config file not found in root folder")
        with open(str(self._path), "r") as f:
            self._data = json.load(f)
        
        self.token: Optional[str] = self._data.get("token", None)
        self.dev: Optional[bool] = self._data.get("dev", None)
        self.debug_guilds: Optional[list[int]] = self._data.get("debug_guilds", None)
        self.admin_id: Optional[int] = self._data.get("admin_id", None)

def get_config() -> Config:
    return Config()