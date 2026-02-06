from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class ChampionTier(Base):
    """Player's tier assignment for a champion"""
    __tablename__ = "champion_tiers"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    champion_id = Column(Integer, nullable=False)
    tier = Column(String, nullable=False)  # S/A/B/C/D
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    player = relationship("Player", back_populates="champion_tiers")

    __table_args__ = (
        UniqueConstraint('player_id', 'champion_id', name='uq_player_champion_tier'),
    )
