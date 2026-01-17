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
    created_at: datetime

    class Config:
        from_attributes = True
