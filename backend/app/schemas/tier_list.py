from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# --- Champion Tier Schemas ---


class ChampionTierBase(BaseModel):
    champion_id: int
    tier: Tier


class ChampionTierCreate(ChampionTierBase):
    pass


class ChampionTierUpdate(BaseModel):
    tier: Tier


class ChampionTierResponse(ChampionTierBase):
    id: int
    player_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Champion Stats with Score ---


class ChampionStatsWithScore(BaseModel):
    """Champion stats with calculated performance score"""
    champion_id: int
    champion_name: str
    games_played: int
    wins: int
    losses: int
    winrate: float

    # Average stats
    avg_kda: float
    avg_cs_per_min: float
    avg_gold_per_min: float
    avg_vision_per_min: float
    avg_damage_per_min: float
    avg_kill_participation: float

    # Calculated score (0-100)
    performance_score: int

    # Assigned tier (if any)
    tier: Optional[Tier] = None


class PlayerTierList(BaseModel):
    """Complete tier list for a player"""
    player_id: int
    player_name: str
    champions: list[ChampionStatsWithScore]

    # Champions grouped by tier
    tier_s: list[ChampionStatsWithScore] = []
    tier_a: list[ChampionStatsWithScore] = []
    tier_b: list[ChampionStatsWithScore] = []
    tier_c: list[ChampionStatsWithScore] = []
    tier_d: list[ChampionStatsWithScore] = []
    unranked: list[ChampionStatsWithScore] = []
