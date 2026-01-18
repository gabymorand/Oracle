from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AuthorRole(str, Enum):
    COACH = "coach"
    HEAD_COACH = "head_coach"


class NoteType(str, Enum):
    OBJECTIVE = "objective"
    NOTE = "note"


class PlayerNote(Base):
    __tablename__ = "player_notes"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True)  # Nouveau champ
    author_role = Column(String, nullable=False)
    note_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    player = relationship("Player", back_populates="notes")
    coach = relationship("Coach")  # Nouvelle relation
