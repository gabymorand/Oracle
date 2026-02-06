from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.player import Player
from app.schemas.tier_list import (
    ChampionStatsWithScore,
    ChampionTierCreate,
    ChampionTierResponse,
    PlayerTierList,
    Tier,
)
from app.services import tier_list_service

router = APIRouter(prefix="/api/v1/tier-list", tags=["tier-list"])


def verify_player_team(db: Session, player_id: int, team_id: int) -> Player:
    """Verify player belongs to team and return player"""
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.team_id == team_id,
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/player/{player_id}", response_model=PlayerTierList)
async def get_player_tier_list(
    player_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get complete tier list for a player with stats and scores"""
    verify_player_team(db, player_id, team_ctx.team_id)
    tier_list = tier_list_service.get_player_tier_list(db, player_id)
    if not tier_list:
        raise HTTPException(status_code=404, detail="Player not found")
    return tier_list


@router.get("/player/{player_id}/champions", response_model=list[ChampionStatsWithScore])
async def get_player_champion_stats(
    player_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get champion stats with scores for a player (without grouping by tier)"""
    verify_player_team(db, player_id, team_ctx.team_id)
    return tier_list_service.get_player_champion_stats(db, player_id)


@router.post("/player/{player_id}/champion/{champion_id}", response_model=ChampionTierResponse)
async def set_champion_tier(
    player_id: int,
    champion_id: int,
    tier_data: ChampionTierCreate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Set or update a champion's tier for a player"""
    verify_player_team(db, player_id, team_ctx.team_id)
    return tier_list_service.set_champion_tier(db, player_id, champion_id, tier_data.tier)


@router.delete("/player/{player_id}/champion/{champion_id}", status_code=204)
async def delete_champion_tier(
    player_id: int,
    champion_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Remove a champion's tier assignment"""
    verify_player_team(db, player_id, team_ctx.team_id)
    success = tier_list_service.delete_champion_tier(db, player_id, champion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tier assignment not found")
