from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.database import Base


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


class PlayerAvailability(Base):
    """Player availability by half-day slot"""
    __tablename__ = "player_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    slot = Column(String, nullable=False)  # morning/afternoon/evening
    is_available = Column(Boolean, nullable=False, default=True)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    player = relationship("Player", back_populates="availabilities")


class CalendarEvent(Base):
    """Calendar events (scrims, training, matches, meetings)"""
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # scrim/training/official_match/meeting/other
    date = Column(Date, nullable=False, index=True)
    slot = Column(String, nullable=False)  # morning/afternoon/evening
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    # For scrims, link to draft series
    draft_series_id = Column(Integer, ForeignKey("draft_series.id", ondelete="SET NULL"), nullable=True)

    # Opponent name (for scrims/official matches)
    opponent_name = Column(String, nullable=True)

    # Opponent players (comma-separated summoner names for op.gg links)
    opponent_players = Column(Text, nullable=True)

    # Additional details
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    draft_series = relationship("DraftSeries", backref="calendar_events")
