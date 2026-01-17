from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stats import LaneStats, PlayerStats
from app.services import stats_service

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/player/{player_id}", response_model=PlayerStats)
async def get_player_stats(player_id: int, db: Session = Depends(get_db)):
    stats = stats_service.get_player_stats(db, player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found or no stats available")
    return stats


@router.get("/lane/{lane}", response_model=LaneStats)
async def get_lane_stats(lane: str, db: Session = Depends(get_db)):
    stats = stats_service.get_lane_stats(db, lane)
    if not stats:
        raise HTTPException(status_code=404, detail="Lane not found or no stats available")
    return stats


@router.post("/refresh/{riot_account_id}", status_code=202)
async def refresh_stats(riot_account_id: int, db: Session = Depends(get_db)):
    await stats_service.refresh_player_stats(db, riot_account_id)
    return {"message": "Stats refresh initiated"}
