from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.admin import (
    AdminDashboard,
    AdminLoginRequest,
    AdminLoginResponse,
    TeamCreate,
    TeamDetails,
    TeamStats,
    TeamUpdate,
)
from app.services import admin_service

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def get_admin_token(authorization: str = Header(...)) -> dict:
    """Dependency to validate admin JWT token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Authenticate with admin code"""
    if request.code != settings.admin_code:
        raise HTTPException(status_code=401, detail="Invalid admin code")

    expiration = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    payload = {
        "is_admin": True,
        "exp": expiration,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return AdminLoginResponse(access_token=token)


@router.get("/dashboard", response_model=AdminDashboard)
async def get_dashboard(
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Get admin dashboard with all teams and stats"""
    return admin_service.get_dashboard(db)


@router.get("/teams/{team_id}", response_model=TeamDetails)
async def get_team_details(
    team_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Get detailed info about a specific team"""
    team = admin_service.get_team_details(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/teams", response_model=TeamStats)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Create a new team"""
    if not admin_service.check_access_code_available(db, team_data.access_code):
        raise HTTPException(status_code=400, detail="Access code already in use")

    team = admin_service.create_team(db, team_data)
    return TeamStats(
        id=team.id,
        name=team.name,
        access_code=team.access_code,
        players_count=0,
        coaches_count=0,
        drafts_count=0,
        events_count=0,
        created_at=team.created_at,
    )


@router.patch("/teams/{team_id}", response_model=TeamDetails)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Update a team's name or access code"""
    if team_data.access_code:
        if not admin_service.check_access_code_available(db, team_data.access_code, team_id):
            raise HTTPException(status_code=400, detail="Access code already in use")

    team = admin_service.update_team(db, team_id, team_data)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return admin_service.get_team_details(db, team_id)


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Delete a team and all its data"""
    if not admin_service.delete_team(db, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted successfully"}


@router.delete("/players/{player_id}")
async def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Delete a player"""
    if not admin_service.delete_player(db, player_id):
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully"}


@router.delete("/coaches/{coach_id}")
async def delete_coach(
    coach_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_admin_token),
):
    """Delete a coach"""
    if not admin_service.delete_coach(db, coach_id):
        raise HTTPException(status_code=404, detail="Coach not found")
    return {"message": "Coach deleted successfully"}
