from datetime import date as date_type
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


# Legacy Draft schemas (backwards compatibility)
class DraftBase(BaseModel):
    date: date_type
    opponent_name: str
    blue_side: bool
    picks: list[int]  # Champion IDs
    bans: list[int]  # Champion IDs
    result: Optional[str] = None
    notes: Optional[str] = None


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
    pick_order: Optional[list[dict]] = None
    result: Optional[str] = None
    import_source: Optional[str] = None
    import_url: Optional[str] = None
    notes: Optional[str] = None


class DraftGameCreate(DraftGameBase):
    pass


class DraftGameResponse(DraftGameBase):
    id: int
    series_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DraftSeriesBase(BaseModel):
    date: date_type
    opponent_name: str
    format: str = "bo1"
    notes: Optional[str] = None


class DraftSeriesCreate(DraftSeriesBase):
    pass


class DraftSeriesUpdate(BaseModel):
    date: Optional[date_type] = None
    opponent_name: Optional[str] = None
    format: Optional[str] = None
    notes: Optional[str] = None
    result: Optional[str] = None


class DraftSeriesResponse(DraftSeriesBase):
    id: int
    our_score: int
    opponent_score: int
    result: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    games: list[DraftGameResponse] = []

    class Config:
        from_attributes = True


class DraftSeriesListResponse(DraftSeriesBase):
    """Lighter response for list view without games"""
    id: int
    our_score: int
    opponent_score: int
    result: Optional[str]
    created_at: datetime
    games_count: int = 0

    class Config:
        from_attributes = True


# Import from URL/Image
class DraftImportRequest(BaseModel):
    url: Optional[str] = None
    image_base64: Optional[str] = None


class DraftImportResponse(BaseModel):
    success: bool
    message: str
    data: Optional[DraftGameBase] = None
