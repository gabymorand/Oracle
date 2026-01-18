from datetime import datetime

from pydantic import BaseModel


class CoachBase(BaseModel):
    name: str
    role: str | None = None


class CoachCreate(CoachBase):
    pass


class CoachUpdate(BaseModel):
    name: str | None = None
    role: str | None = None


class CoachResponse(CoachBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
