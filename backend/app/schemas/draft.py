from datetime import date, datetime

from pydantic import BaseModel


class DraftBase(BaseModel):
    date: date
    opponent_name: str
    blue_side: bool
    picks: list[int]  # Champion IDs
    bans: list[int]  # Champion IDs
    result: str | None = None
    notes: str | None = None


class DraftCreate(DraftBase):
    pass


class DraftResponse(DraftBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
