from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    """Represents a team organization using the app (multi-tenancy)"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    access_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships to all team-owned data
    players = relationship("Player", back_populates="team", cascade="all, delete")
    coaches = relationship("Coach", back_populates="team", cascade="all, delete")
    draft_series = relationship("DraftSeries", back_populates="team", cascade="all, delete")
    calendar_events = relationship("CalendarEvent", back_populates="team", cascade="all, delete")
    opponent_teams = relationship("OpponentTeam", back_populates="team", cascade="all, delete")
