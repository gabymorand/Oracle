from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RiotAccount(Base):
    __tablename__ = "riot_accounts"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    puuid = Column(String, unique=True, index=True, nullable=False)
    summoner_name = Column(String, nullable=False)
    tag_line = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    player = relationship("Player", back_populates="riot_accounts")
    games = relationship("Game", back_populates="riot_account", cascade="all, delete")
