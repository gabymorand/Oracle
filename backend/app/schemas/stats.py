from datetime import datetime

from pydantic import BaseModel


class PlayerStats(BaseModel):
    player_id: int
    summoner_name: str
    role: str
    total_games: int
    avg_kda: float
    avg_cs_per_min: float
    avg_gold_per_min: float
    avg_vision_score_per_min: float
    avg_kill_participation: float
    winrate: float


class LaneStats(BaseModel):
    lane: str
    players: list[PlayerStats]
    combined_winrate: float
    total_games: int


class GameStats(BaseModel):
    """Simplified game stats for recent matches"""

    id: int
    match_id: str
    game_type: str
    champion_id: int
    role: str
    stats: dict
    game_duration: int
    game_date: datetime
    is_pentakill: bool

    class Config:
        from_attributes = True


class TeamHighlights(BaseModel):
    """Team highlights for sponsors page"""

    total_games: int
    total_wins: int
    winrate: float
    competitive_games: int
    competitive_wins: int
    competitive_winrate: float
    total_pentakills: int
    recent_matches: list[GameStats]


class ChampionStats(BaseModel):
    """Stats for a specific champion"""

    champion_id: int
    games_played: int
    wins: int
    losses: int
    winrate: float
    avg_kda: float
    avg_cs_per_min: float
    avg_gold_per_min: float
    avg_vision_per_min: float
    avg_kp: float
    total_kills: int
    total_deaths: int
    total_assists: int
