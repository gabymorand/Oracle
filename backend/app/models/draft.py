from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Integer, String, Text

from app.database import Base


class DraftResult(str, Enum):
    WIN = "win"
    LOSS = "loss"


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    opponent_name = Column(String, nullable=False)
    blue_side = Column(Boolean, nullable=False)
    picks = Column(JSON, nullable=False)  # Array of champion IDs
    bans = Column(JSON, nullable=False)  # Array of champion IDs
    result = Column(String, nullable=True)  # win/loss or null
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
