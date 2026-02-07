from datetime import datetime

from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    code: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TeamCreate(BaseModel):
    name: str
    access_code: str


class TeamUpdate(BaseModel):
    name: str | None = None
    access_code: str | None = None


class TeamStats(BaseModel):
    id: int
    name: str
    access_code: str
    players_count: int
    coaches_count: int
    drafts_count: int
    events_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlayerSummary(BaseModel):
    id: int
    summoner_name: str
    role: str
    riot_accounts_count: int

    class Config:
        from_attributes = True


class CoachSummary(BaseModel):
    id: int
    name: str
    role: str | None

    class Config:
        from_attributes = True


class TeamDetails(BaseModel):
    id: int
    name: str
    access_code: str
    created_at: datetime
    players: list[PlayerSummary]
    coaches: list[CoachSummary]

    class Config:
        from_attributes = True


class AdminDashboard(BaseModel):
    total_teams: int
    total_players: int
    total_coaches: int
    total_drafts: int
    teams: list[TeamStats]
