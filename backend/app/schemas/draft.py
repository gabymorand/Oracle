from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


# Legacy Draft schemas (backwards compatibility)
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


# New Draft Series schemas
class SeriesFormat(str, Enum):
    BO1 = "bo1"
    BO3 = "bo3"
    BO5 = "bo5"


class DraftGameBase(BaseModel):
    game_number: int
    blue_side: bool
    our_bans: list[int] = []
    opponent_bans: list[int] = []
    our_picks: list[int] = []
    opponent_picks: list[int] = []
    pick_order: list[dict] | None = None
    result: str | None = None
    import_source: str | None = None
    import_url: str | None = None
    notes: str | None = None


class DraftGameCreate(DraftGameBase):
    pass


class DraftGameResponse(DraftGameBase):
    id: int
    series_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DraftSeriesBase(BaseModel):
    date: date
    opponent_name: str
    format: str = "bo1"
    notes: str | None = None


class DraftSeriesCreate(DraftSeriesBase):
    pass


class DraftSeriesUpdate(BaseModel):
    date: date | None = None
    opponent_name: str | None = None
    format: str | None = None
    notes: str | None = None
    result: str | None = None


class DraftSeriesResponse(DraftSeriesBase):
    id: int
    our_score: int
    opponent_score: int
    result: str | None
    created_at: datetime
    updated_at: datetime | None
    games: list[DraftGameResponse] = []

    class Config:
        from_attributes = True


class DraftSeriesListResponse(DraftSeriesBase):
    """Lighter response for list view without games"""
    id: int
    our_score: int
    opponent_score: int
    result: str | None
    created_at: datetime
    games_count: int = 0

    class Config:
        from_attributes = True


# Import from URL/Image
class DraftImportRequest(BaseModel):
    url: str | None = None
    image_base64: str | None = None


class DraftImportResponse(BaseModel):
    success: bool
    message: str
    data: DraftGameBase | None = None
