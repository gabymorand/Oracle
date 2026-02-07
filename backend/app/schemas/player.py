from datetime import datetime

from pydantic import BaseModel

from app.schemas.riot_account import RiotAccountResponse


class PlayerBase(BaseModel):
    summoner_name: str
    role: str
    email: str | None = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    summoner_name: str | None = None
    role: str | None = None
    email: str | None = None


class PlayerResponse(PlayerBase):
    id: int
    created_at: datetime
    updated_at: datetime | None
    riot_accounts: list[RiotAccountResponse] = []

    class Config:
        from_attributes = True
