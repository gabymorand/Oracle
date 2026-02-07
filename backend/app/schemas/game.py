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


# --- Match Detail schemas for popup ---


class MatchParticipant(BaseModel):
    """A single participant in a match"""

    puuid: str
    summoner_name: str
    tag_line: str
    champion_id: int
    champion_name: str
    team_id: int  # 100 = blue, 200 = red
    team_position: str  # TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY
    kills: int
    deaths: int
    assists: int
    kda: float
    cs: int
    cs_per_min: float
    vision_score: int
    gold_earned: int
    damage_dealt: int
    damage_taken: int
    summoner_spell1: int
    summoner_spell2: int
    items: list[int]  # 7 item slots (including trinket)
    win: bool
    is_our_player: bool  # True if this is a player from our team
    # Rank info (only populated for our players)
    rank_tier: str | None = None
    rank_division: str | None = None
    rank_lp: int | None = None


class MatchTeam(BaseModel):
    """A team in a match"""

    team_id: int
    win: bool
    bans: list[int]  # Champion IDs banned
    participants: list[MatchParticipant]
    total_kills: int
    total_gold: int
    total_damage: int


class MatchDetailResponse(BaseModel):
    """Full match detail response"""

    match_id: str
    game_date: datetime
    game_duration: int  # seconds
    game_duration_formatted: str  # "26:15"
    queue_id: int
    queue_name: str
    blue_team: MatchTeam
    red_team: MatchTeam


class MatchJsonImportRequest(BaseModel):
    """Request body for importing a game from raw Riot match V5 JSON"""

    match_json: dict
    blue_side: bool = True
    result: Optional[str] = None  # Override: 'win' or 'loss'
    our_bans: list[int] = []
    opponent_bans: list[int] = []
    notes: Optional[str] = None
