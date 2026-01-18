from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RiotAccount(Base):
    __tablename__ = "riot_accounts"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    puuid = Column(String, unique=True, index=True, nullable=False)
    summoner_id = Column(String, nullable=True)  # Needed for rank API calls
    summoner_name = Column(String, nullable=False)
    tag_line = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)
    # Current rank tracking
    rank_tier = Column(String, nullable=True)  # e.g., "DIAMOND"
    rank_division = Column(String, nullable=True)  # e.g., "II"
    lp = Column(Integer, nullable=True)  # League Points
    wins = Column(Integer, nullable=True)  # Total wins this season
    losses = Column(Integer, nullable=True)  # Total losses this season
    # Peak rank tracking
    peak_tier = Column(String, nullable=True)
    peak_division = Column(String, nullable=True)
    peak_lp = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    player = relationship("Player", back_populates="riot_accounts")
    games = relationship("Game", back_populates="riot_account", cascade="all, delete")
    rank_history = relationship("RankHistory", back_populates="riot_account", cascade="all, delete")
