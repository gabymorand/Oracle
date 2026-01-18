from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class GameType(str, Enum):
    SOLOQ = "soloq"
    COMPETITIVE = "competitive"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    riot_account_id = Column(Integer, ForeignKey("riot_accounts.id"), nullable=False)
    match_id = Column(String, unique=True, index=True, nullable=False)
    game_type = Column(String, nullable=False, default="soloq")
    champion_id = Column(Integer, nullable=False)
    role = Column(String, nullable=False)
    stats = Column(JSON, nullable=False)  # kda, cs, vision, etc.
    game_duration = Column(Integer, nullable=False)  # seconds
    game_date = Column(DateTime, nullable=False)
    is_pentakill = Column(Boolean, default=False, nullable=False)  # Pentakill tracker
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    riot_account = relationship("RiotAccount", back_populates="games")
