from datetime import datetime

from pydantic import BaseModel


class RiotAccountBase(BaseModel):
    summoner_name: str
    tag_line: str
    is_main: bool = False


class RiotAccountCreate(RiotAccountBase):
    pass


class RiotAccountResponse(RiotAccountBase):
    id: int
    player_id: int
    puuid: str
    rank_tier: str | None = None
    rank_division: str | None = None
    lp: int | None = None
    wins: int | None = None
    losses: int | None = None
    peak_tier: str | None = None
    peak_division: str | None = None
    peak_lp: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class RankHistoryEntry(BaseModel):
    id: int
    tier: str
    division: str
    lp: int
    wins: int
    losses: int
    recorded_at: datetime

    class Config:
        from_attributes = True
