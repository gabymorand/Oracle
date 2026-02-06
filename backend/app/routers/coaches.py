from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.schemas.coach import CoachCreate, CoachResponse, CoachUpdate
from app.services import coach_service

router = APIRouter(prefix="/api/v1/coaches", tags=["coaches"])


@router.get("", response_model=list[CoachResponse])
async def list_coaches(
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    return coach_service.get_all_coaches(db, team_ctx.team_id)


@router.post("", response_model=CoachResponse, status_code=201)
async def create_coach(
    coach: CoachCreate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    # Check if coach with same name already exists in this team
    existing = coach_service.get_coach_by_name(db, team_ctx.team_id, coach.name)
    if existing:
        raise HTTPException(status_code=400, detail="Coach with this name already exists")
    return coach_service.create_coach(db, team_ctx.team_id, coach)


@router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(
    coach_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    coach = coach_service.get_coach(db, team_ctx.team_id, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach


@router.patch("/{coach_id}", response_model=CoachResponse)
async def update_coach(
    coach_id: int,
    coach_update: CoachUpdate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    coach = coach_service.update_coach(db, team_ctx.team_id, coach_id, coach_update)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach


@router.delete("/{coach_id}", status_code=204)
async def delete_coach(
    coach_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    success = coach_service.delete_coach(db, team_ctx.team_id, coach_id)
    if not success:
        raise HTTPException(status_code=404, detail="Coach not found")
