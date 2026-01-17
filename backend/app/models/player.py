from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String
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

    id = Column(Integer, primary_key=True, index=True)
    summoner_name = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    riot_accounts = relationship("RiotAccount", back_populates="player", cascade="all, delete")
    notes = relationship("PlayerNote", back_populates="player", cascade="all, delete")
