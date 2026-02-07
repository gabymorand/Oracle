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


# --- SoloQ Activity View schemas ---


class ActivityGame(BaseModel):
    """A single game for the activity grid"""

    id: int
    match_id: str
    game_type: str
    champion_id: int
    kills: int
    deaths: int
    assists: int
    win: bool
    game_date: datetime
    game_duration: int
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format


class ChampionMatchup(BaseModel):
    """Stats against a specific champion"""

    champion_id: int
    games: int
    wins: int
    losses: int
    winrate: float
    avg_kills: float
    avg_deaths: float
    avg_assists: float


class PlayerActivitySummary(BaseModel):
    """Player summary for activity view"""

    player_id: int
    summoner_name: str
    role: str
    # Main account info
    riot_account_id: int | None = None
    rank_tier: str | None = None
    rank_division: str | None = None
    lp: int | None = None
    # Weekly stats
    total_games: int
    wins: int
    losses: int
    winrate: float
    scrims: int  # Number of competitive/scrim games
    duos: int  # Number of duo queue games (placeholder)
    # Games grouped by day (ISO date string -> list of games)
    games_by_day: dict[str, list[ActivityGame]]
    # Champion matchup stats (most played against)
    matchups: list[ChampionMatchup]
    # Last refresh timestamp
    last_refreshed_at: datetime | None = None


class TeamActivityResponse(BaseModel):
    """Full team activity response"""

    week_start: str  # ISO date
    week_end: str  # ISO date
    total_soloq: int
    total_scrims: int
    total_duos: int
    overall_winrate: float
    players: list[PlayerActivitySummary]
    last_updated: datetime
