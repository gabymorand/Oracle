from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameTagUpdate(BaseModel):
    """Schema for updating game tags"""

    game_type: Optional[str] = None  # "soloq" or "competitive"
    is_pentakill: Optional[bool] = None


class GameResponse(BaseModel):
    """Schema for game response"""

    id: int
    riot_account_id: int
    match_id: str
    game_type: str
    champion_id: int
    role: str
    stats: dict
    game_duration: int
    game_date: datetime
    is_pentakill: bool
    created_at: datetime

    class Config:
        from_attributes = True
