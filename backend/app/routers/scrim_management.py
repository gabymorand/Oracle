from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scrim_management import (
    OpponentTeamCreate,
    OpponentTeamResponse,
    OpponentTeamUpdate,
    OpponentTeamWithStats,
    ScoutedPlayerCreate,
    ScoutedPlayerResponse,
    ScoutedPlayerUpdate,
    ScoutedPlayerWithTeam,
    ScrimHistoryItem,
    ScrimManagementDashboard,
    ScrimReviewCreate,
    ScrimReviewResponse,
    ScrimReviewUpdate,
    ScrimReviewWithTeam,
)
from app.services import scrim_management_service as service

router = APIRouter(prefix="/api/v1/scrim-management", tags=["scrim-management"])


# --- Dashboard ---


@router.get("/dashboard", response_model=ScrimManagementDashboard)
async def get_dashboard(db: Session = Depends(get_db)):
    """Get manager dashboard with aggregated stats"""
    return service.get_manager_dashboard(db)


@router.get("/history", response_model=list[ScrimHistoryItem])
async def get_scrim_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get scrim history with reviews and results"""
    return service.get_scrim_history(db, limit)


# --- Opponent Teams ---


@router.get("/teams", response_model=list[OpponentTeamResponse])
async def list_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all opponent teams"""
    return service.get_opponent_teams(db, skip, limit)


@router.get("/teams/with-stats", response_model=list[OpponentTeamWithStats])
async def list_teams_with_stats(db: Session = Depends(get_db)):
    """List all teams with aggregated stats"""
    return service.get_all_teams_with_stats(db)


@router.get("/teams/{team_id}", response_model=OpponentTeamWithStats)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get team details with stats"""
    team = service.get_opponent_team_with_stats(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/teams", response_model=OpponentTeamResponse, status_code=201)
async def create_team(team: OpponentTeamCreate, db: Session = Depends(get_db)):
    """Create a new opponent team"""
    existing = service.get_opponent_team_by_name(db, team.name)
    if existing:
        raise HTTPException(status_code=400, detail="Team with this name already exists")
    return service.create_opponent_team(db, team)


@router.patch("/teams/{team_id}", response_model=OpponentTeamResponse)
async def update_team(
    team_id: int,
    team_update: OpponentTeamUpdate,
    db: Session = Depends(get_db),
):
    """Update team info"""
    team = service.update_opponent_team(db, team_id, team_update)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.delete("/teams/{team_id}", status_code=204)
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Delete a team"""
    success = service.delete_opponent_team(db, team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")


# --- Scrim Reviews ---


@router.get("/reviews", response_model=list[ScrimReviewResponse])
async def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all scrim reviews"""
    return service.get_scrim_reviews(db, skip, limit)


@router.get("/reviews/event/{event_id}", response_model=ScrimReviewWithTeam | None)
async def get_review_by_event(event_id: int, db: Session = Depends(get_db)):
    """Get review for a specific calendar event"""
    review = service.get_scrim_review_by_event(db, event_id)
    if not review:
        return None
    return service.get_scrim_review_with_team(db, review.id)


@router.get("/reviews/{review_id}", response_model=ScrimReviewWithTeam)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get review details"""
    review = service.get_scrim_review_with_team(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/reviews", response_model=ScrimReviewResponse, status_code=201)
async def create_review(review: ScrimReviewCreate, db: Session = Depends(get_db)):
    """Create a scrim review"""
    existing = service.get_scrim_review_by_event(db, review.calendar_event_id)
    if existing:
        raise HTTPException(status_code=400, detail="Review already exists for this event")
    return service.create_scrim_review(db, review)


@router.patch("/reviews/{review_id}", response_model=ScrimReviewResponse)
async def update_review(
    review_id: int,
    review_update: ScrimReviewUpdate,
    db: Session = Depends(get_db),
):
    """Update a review"""
    review = service.update_scrim_review(db, review_id, review_update)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a review"""
    success = service.delete_scrim_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")


# --- Scouted Players ---


@router.get("/scouted-players", response_model=list[ScoutedPlayerResponse])
async def list_scouted_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    prospects_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List scouted players"""
    return service.get_scouted_players(db, skip, limit, prospects_only)


@router.get("/scouted-players/team/{team_id}", response_model=list[ScoutedPlayerResponse])
async def get_scouted_by_team(team_id: int, db: Session = Depends(get_db)):
    """Get scouted players from a specific team"""
    return service.get_scouted_players_by_team(db, team_id)


@router.get("/scouted-players/{player_id}", response_model=ScoutedPlayerWithTeam)
async def get_scouted_player(player_id: int, db: Session = Depends(get_db)):
    """Get scouted player details"""
    player = service.get_scouted_player_with_team(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Scouted player not found")
    return player


@router.post("/scouted-players", response_model=ScoutedPlayerResponse, status_code=201)
async def create_scouted_player(
    player: ScoutedPlayerCreate,
    db: Session = Depends(get_db),
):
    """Add a scouted player"""
    return service.create_scouted_player(db, player)


@router.patch("/scouted-players/{player_id}", response_model=ScoutedPlayerResponse)
async def update_scouted_player(
    player_id: int,
    player_update: ScoutedPlayerUpdate,
    db: Session = Depends(get_db),
):
    """Update a scouted player"""
    player = service.update_scouted_player(db, player_id, player_update)
    if not player:
        raise HTTPException(status_code=404, detail="Scouted player not found")
    return player


@router.delete("/scouted-players/{player_id}", status_code=204)
async def delete_scouted_player(player_id: int, db: Session = Depends(get_db)):
    """Delete a scouted player"""
    success = service.delete_scouted_player(db, player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scouted player not found")
