from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ScrimQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    BAD = "bad"


class Potential(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# --- OpponentTeam Schemas ---


class OpponentTeamBase(BaseModel):
    name: str
    contact_name: str | None = None
    contact_discord: str | None = None
    contact_email: str | None = None
    contact_twitter: str | None = None
    notes: str | None = None


class OpponentTeamCreate(OpponentTeamBase):
    pass


class OpponentTeamUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    contact_discord: str | None = None
    contact_email: str | None = None
    contact_twitter: str | None = None
    notes: str | None = None


class OpponentTeamResponse(OpponentTeamBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class OpponentTeamWithStats(OpponentTeamResponse):
    """Team with aggregated scrim stats"""
    total_scrims: int = 0
    wins: int = 0
    losses: int = 0
    avg_quality: float | None = None
    scouted_players_count: int = 0


# --- ScrimReview Schemas ---


class ScrimReviewBase(BaseModel):
    quality: ScrimQuality
    punctuality: int | None = Field(None, ge=1, le=5)
    communication: int | None = Field(None, ge=1, le=5)
    competitiveness: int | None = Field(None, ge=1, le=5)
    would_scrim_again: int | None = Field(None, ge=1, le=3)  # 1=no, 2=maybe, 3=yes
    notes: str | None = None


class ScrimReviewCreate(ScrimReviewBase):
    calendar_event_id: int
    opponent_team_id: int | None = None


class ScrimReviewUpdate(BaseModel):
    quality: ScrimQuality | None = None
    punctuality: int | None = Field(None, ge=1, le=5)
    communication: int | None = Field(None, ge=1, le=5)
    competitiveness: int | None = Field(None, ge=1, le=5)
    would_scrim_again: int | None = Field(None, ge=1, le=3)
    notes: str | None = None
    opponent_team_id: int | None = None


class ScrimReviewResponse(ScrimReviewBase):
    id: int
    calendar_event_id: int
    opponent_team_id: int | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ScrimReviewWithTeam(ScrimReviewResponse):
    """Review with team info"""
    opponent_team_name: str | None = None


# --- ScoutedPlayer Schemas ---


class ScoutedPlayerBase(BaseModel):
    summoner_name: str
    tag_line: str | None = None
    opponent_team_id: int | None = None
    role: str | None = None
    rating: int | None = Field(None, ge=1, le=5)
    mechanical_skill: int | None = Field(None, ge=1, le=5)
    game_sense: int | None = Field(None, ge=1, le=5)
    communication: int | None = Field(None, ge=1, le=5)
    attitude: int | None = Field(None, ge=1, le=5)
    potential: Potential | None = None
    notes: str | None = None
    is_prospect: bool = False


class ScoutedPlayerCreate(ScoutedPlayerBase):
    pass


class ScoutedPlayerUpdate(BaseModel):
    summoner_name: str | None = None
    tag_line: str | None = None
    opponent_team_id: int | None = None
    role: str | None = None
    rating: int | None = Field(None, ge=1, le=5)
    mechanical_skill: int | None = Field(None, ge=1, le=5)
    game_sense: int | None = Field(None, ge=1, le=5)
    communication: int | None = Field(None, ge=1, le=5)
    attitude: int | None = Field(None, ge=1, le=5)
    potential: Potential | None = None
    notes: str | None = None
    is_prospect: bool | None = None


class ScoutedPlayerResponse(BaseModel):
    id: int
    summoner_name: str
    tag_line: str | None = None
    opponent_team_id: int | None = None
    role: str | None = None
    rating: int | None = None
    mechanical_skill: int | None = None
    game_sense: int | None = None
    communication: int | None = None
    attitude: int | None = None
    potential: str | None = None
    notes: str | None = None
    is_prospect: bool = False
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ScoutedPlayerWithTeam(ScoutedPlayerResponse):
    """Player with team name"""
    team_name: str | None = None


# --- Aggregated Views ---


class ScrimHistoryItem(BaseModel):
    """A scrim event with its review and team info"""
    event_id: int
    title: str
    date: str
    slot: str
    opponent_name: str | None
    opponent_team_id: int | None
    review: ScrimReviewResponse | None
    draft_series_result: str | None  # win/loss/null
    our_score: int | None
    opponent_score: int | None


class ScrimManagementDashboard(BaseModel):
    """Dashboard data for managers"""
    total_scrims: int
    reviewed_scrims: int
    total_teams: int
    total_scouted_players: int
    prospects_count: int
    recent_scrims: list[ScrimHistoryItem]
    top_teams: list[OpponentTeamWithStats]
