from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class SeriesFormat(str, Enum):
    BO1 = "bo1"
    BO3 = "bo3"
    BO5 = "bo5"


class DraftResult(str, Enum):
    WIN = "win"
    LOSS = "loss"


class DraftSeries(Base):
    """A series of games (BO1, BO3, BO5) against an opponent"""
    __tablename__ = "draft_series"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    opponent_name = Column(String, nullable=False)
    format = Column(String, nullable=False, default="bo1")  # bo1, bo3, bo5
    our_score = Column(Integer, default=0)  # Number of games we won
    opponent_score = Column(Integer, default=0)  # Number of games opponent won
    result = Column(String, nullable=True)  # win/loss (calculated from scores)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="draft_series")
    games = relationship("DraftGame", back_populates="series", cascade="all, delete-orphan")


class DraftGame(Base):
    """A single game within a series with its draft"""
    __tablename__ = "draft_games"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("draft_series.id"), nullable=False)
    game_number = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5

    # Side info
    blue_side = Column(Boolean, nullable=False)  # True if we are blue side

    # Bans (in order)
    our_bans = Column(JSON, nullable=False, default=list)  # [champ_id, champ_id, champ_id, champ_id, champ_id]
    opponent_bans = Column(JSON, nullable=False, default=list)  # [champ_id, champ_id, champ_id, champ_id, champ_id]

    # Picks (in draft order)
    our_picks = Column(JSON, nullable=False, default=list)  # [champ_id, ...] 5 picks
    opponent_picks = Column(JSON, nullable=False, default=list)  # [champ_id, ...] 5 picks

    # Pick order details (B1, R1R2, B2B3, etc.)
    pick_order = Column(JSON, nullable=True)  # Full draft order if available

    # Result
    result = Column(String, nullable=True)  # win/loss

    # Import metadata
    import_source = Column(String, nullable=True)  # 'manual', 'image', 'draftlol_link', 'match_json'
    import_url = Column(String, nullable=True)  # Original URL if imported from link
    match_data = Column(JSON, nullable=True)  # Full Riot match V5 JSON for imported games

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    series = relationship("DraftSeries", back_populates="games")


# Keep old Draft model for backwards compatibility (can be removed later)
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
