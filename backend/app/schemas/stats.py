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
