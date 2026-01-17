from datetime import datetime

from pydantic import BaseModel


class PlayerNoteBase(BaseModel):
    author_role: str
    note_type: str
    content: str


class PlayerNoteCreate(PlayerNoteBase):
    pass


class PlayerNoteUpdate(BaseModel):
    content: str | None = None
    note_type: str | None = None


class PlayerNoteResponse(PlayerNoteBase):
    id: int
    player_id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
