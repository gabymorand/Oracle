from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.tier_list import (
    ChampionStatsWithScore,
    ChampionTierCreate,
    ChampionTierResponse,
    PlayerTierList,
    Tier,
)
from app.services import tier_list_service

router = APIRouter(prefix="/api/v1/tier-list", tags=["tier-list"])


@router.get("/player/{player_id}", response_model=PlayerTierList)
async def get_player_tier_list(player_id: int, db: Session = Depends(get_db)):
    """Get complete tier list for a player with stats and scores"""
    tier_list = tier_list_service.get_player_tier_list(db, player_id)
    if not tier_list:
        raise HTTPException(status_code=404, detail="Player not found")
    return tier_list


@router.get("/player/{player_id}/champions", response_model=list[ChampionStatsWithScore])
async def get_player_champion_stats(player_id: int, db: Session = Depends(get_db)):
    """Get champion stats with scores for a player (without grouping by tier)"""
    return tier_list_service.get_player_champion_stats(db, player_id)


@router.post("/player/{player_id}/champion/{champion_id}", response_model=ChampionTierResponse)
async def set_champion_tier(
    player_id: int,
    champion_id: int,
    tier_data: ChampionTierCreate,
    db: Session = Depends(get_db),
):
    """Set or update a champion's tier for a player"""
    return tier_list_service.set_champion_tier(db, player_id, champion_id, tier_data.tier)


@router.delete("/player/{player_id}/champion/{champion_id}", status_code=204)
async def delete_champion_tier(
    player_id: int,
    champion_id: int,
    db: Session = Depends(get_db),
):
    """Remove a champion's tier assignment"""
    success = tier_list_service.delete_champion_tier(db, player_id, champion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tier assignment not found")
