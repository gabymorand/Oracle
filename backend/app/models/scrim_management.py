from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ScrimQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    BAD = "bad"


class OpponentTeam(Base):
    """Teams we've played scrims against - for contact management"""
    __tablename__ = "opponent_teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_name = Column(String, nullable=True)
    contact_discord = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_twitter = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scrim_reviews = relationship("ScrimReview", back_populates="opponent_team", cascade="all, delete")
    scouted_players = relationship("ScoutedPlayer", back_populates="team", cascade="all, delete")


class ScrimReview(Base):
    """Review/rating for a scrim session"""
    __tablename__ = "scrim_reviews"

    id = Column(Integer, primary_key=True, index=True)
    calendar_event_id = Column(
        Integer, ForeignKey("calendar_events.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    opponent_team_id = Column(
        Integer, ForeignKey("opponent_teams.id", ondelete="SET NULL"), nullable=True
    )
    quality = Column(String, nullable=False)  # ScrimQuality enum
    punctuality = Column(Integer, nullable=True)  # 1-5 rating
    communication = Column(Integer, nullable=True)  # 1-5 rating
    competitiveness = Column(Integer, nullable=True)  # 1-5 rating
    would_scrim_again = Column(Integer, nullable=True)  # 1=no, 2=maybe, 3=yes
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    calendar_event = relationship("CalendarEvent", backref="scrim_review")
    opponent_team = relationship("OpponentTeam", back_populates="scrim_reviews")


class ScoutedPlayer(Base):
    """Players we've encountered and want to track for scouting/prospecting"""
    __tablename__ = "scouted_players"

    id = Column(Integer, primary_key=True, index=True)
    summoner_name = Column(String, nullable=False, index=True)
    tag_line = Column(String, nullable=True)
    team_id = Column(Integer, ForeignKey("opponent_teams.id", ondelete="SET NULL"), nullable=True)
    role = Column(String, nullable=True)  # top/jungle/mid/adc/support
    rating = Column(Integer, nullable=True)  # 1-5 stars
    mechanical_skill = Column(Integer, nullable=True)  # 1-5
    game_sense = Column(Integer, nullable=True)  # 1-5
    communication = Column(Integer, nullable=True)  # 1-5
    attitude = Column(Integer, nullable=True)  # 1-5
    potential = Column(String, nullable=True)  # low/medium/high
    notes = Column(Text, nullable=True)
    is_prospect = Column(Integer, default=0)  # 0=no, 1=yes - potential recruit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("OpponentTeam", back_populates="scouted_players")
