from datetime import date as date_type
from datetime import datetime
from datetime import time as time_type
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TimeSlot(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class EventType(str, Enum):
    SCRIM = "scrim"
    TRAINING = "training"
    OFFICIAL_MATCH = "official_match"
    MEETING = "meeting"
    OTHER = "other"


# --- Availability Schemas ---


class AvailabilityBase(BaseModel):
    date: date_type
    slot: TimeSlot
    is_available: bool = True
    note: Optional[str] = None


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    is_available: Optional[bool] = None
    note: Optional[str] = None


class AvailabilityResponse(AvailabilityBase):
    id: int
    player_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PlayerAvailabilitySummary(BaseModel):
    """Summary of a player's availability for a specific date"""
    player_id: int
    player_name: str
    morning: bool
    afternoon: bool
    evening: bool


class DayAvailabilitySummary(BaseModel):
    """All players' availability for a specific date"""
    date: date_type
    availabilities: list[PlayerAvailabilitySummary]


# --- Event Schemas ---


class CalendarEventBase(BaseModel):
    title: str
    event_type: EventType
    date: date_type
    slot: TimeSlot
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    draft_series_id: Optional[int] = None
    opponent_name: Optional[str] = None
    opponent_players: Optional[str] = None  # Comma-separated summoner names
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[EventType] = None
    date: Optional[date_type] = None
    slot: Optional[TimeSlot] = None
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    draft_series_id: Optional[int] = None
    opponent_name: Optional[str] = None
    opponent_players: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DraftSeriesInfo(BaseModel):
    """Lightweight draft series info for event response"""
    id: int
    opponent_name: str
    format: str
    our_score: int
    opponent_score: int
    result: Optional[str]


class CalendarEventWithSeries(CalendarEventResponse):
    """Event response with linked draft series info"""
    draft_series_info: Optional[DraftSeriesInfo] = None


# --- Combined Views ---


class DayDetail(BaseModel):
    """Detailed info for a single day"""
    date: date_type
    events: list[CalendarEventResponse]
    availabilities: list[PlayerAvailabilitySummary]
