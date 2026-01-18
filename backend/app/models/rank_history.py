from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RankHistory(Base):
    __tablename__ = "rank_history"

    id = Column(Integer, primary_key=True, index=True)
    riot_account_id = Column(Integer, ForeignKey("riot_accounts.id"), nullable=False)
    tier = Column(String, nullable=False)  # IRON, BRONZE, SILVER, etc.
    division = Column(String, nullable=True)  # I, II, III, IV (null for Master/Grandmaster/Challenger)
    lp = Column(Integer, nullable=False)  # League Points
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    riot_account = relationship("RiotAccount", back_populates="rank_history")
