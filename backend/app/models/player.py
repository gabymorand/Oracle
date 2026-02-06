from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Role(str, Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    ADC = "adc"
    SUPPORT = "support"


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("team_id", "summoner_name", name="uq_player_team_summoner"),
    )

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    summoner_name = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="players")
    riot_accounts = relationship("RiotAccount", back_populates="player", cascade="all, delete")
    notes = relationship("PlayerNote", back_populates="player", cascade="all, delete")
    availabilities = relationship("PlayerAvailability", back_populates="player", cascade="all, delete")
    champion_tiers = relationship("ChampionTier", back_populates="player", cascade="all, delete")
