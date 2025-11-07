from pydantic import BaseModel
from typing import Optional


class Config(BaseModel):
    """
    Domain entity representing application configuration
    """
    check_in_open: bool
    leaderboard_open: bool
    info_title: Optional[str] = None
    info_content: Optional[str] = None
    winner_room: Optional[str] = None
    winner_time: Optional[str] = None
    timer_duration: Optional[int] = None  # Quiz timer duration in milliseconds

