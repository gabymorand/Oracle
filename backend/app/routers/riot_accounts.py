from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.game import Game
from app.models.player import Player
from app.models.rank_history import RankHistory
from app.models.riot_account import RiotAccount
from app.schemas.riot_account import RiotAccountCreate, RiotAccountResponse
from app.services import riot_account_service

router = APIRouter(prefix="/api/v1", tags=["riot_accounts"])


@router.post("/players/{player_id}/riot-accounts", response_model=RiotAccountResponse, status_code=201)
async def add_riot_account(
    player_id: int,
    account: RiotAccountCreate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    # Verify player belongs to team
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.team_id == team_ctx.team_id,
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return await riot_account_service.create_riot_account(db, player_id, account)


@router.delete("/riot-accounts/{account_id}", status_code=204)
async def delete_riot_account(
    account_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Delete a riot account and all associated data"""
    # Join with player to verify team ownership
    account = (
        db.query(RiotAccount)
        .join(Player)
        .filter(
            RiotAccount.id == account_id,
            Player.team_id == team_ctx.team_id,
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    # Delete associated games
    db.query(Game).filter(Game.riot_account_id == account_id).delete()

    # Delete associated rank history
    db.query(RankHistory).filter(RankHistory.riot_account_id == account_id).delete()

    # Delete the account
    db.delete(account)
    db.commit()
    return None


@router.patch("/riot-accounts/{account_id}/set-main", response_model=RiotAccountResponse)
async def set_main_account(
    account_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Set a riot account as the main account, unsetting all others for the same player."""
    account = (
        db.query(RiotAccount)
        .join(Player)
        .filter(
            RiotAccount.id == account_id,
            Player.team_id == team_ctx.team_id,
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    # Unset all other accounts for this player
    db.query(RiotAccount).filter(
        RiotAccount.player_id == account.player_id,
        RiotAccount.id != account_id,
    ).update({"is_main": False})

    account.is_main = True
    db.commit()
    db.refresh(account)
    return account


@router.patch("/riot-accounts/{account_id}/rank", response_model=RiotAccountResponse, status_code=200)
async def update_riot_account_rank(
    account_id: int,
    rank_data: dict,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Update rank information manually for a riot account"""
    # Join with player to verify team ownership
    account = (
        db.query(RiotAccount)
        .join(Player)
        .filter(
            RiotAccount.id == account_id,
            Player.team_id == team_ctx.team_id,
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    # Update rank fields
    if "rank_tier" in rank_data:
        account.rank_tier = rank_data["rank_tier"] or None
    if "rank_division" in rank_data:
        account.rank_division = rank_data["rank_division"] or None
    if "lp" in rank_data:
        account.lp = rank_data["lp"]
    if "wins" in rank_data:
        account.wins = rank_data["wins"]
    if "losses" in rank_data:
        account.losses = rank_data["losses"]
    if "peak_tier" in rank_data:
        account.peak_tier = rank_data["peak_tier"] or None
    if "peak_division" in rank_data:
        account.peak_division = rank_data["peak_division"] or None
    if "peak_lp" in rank_data:
        account.peak_lp = rank_data["peak_lp"]
    if "summoner_id" in rank_data and rank_data["summoner_id"]:
        account.summoner_id = rank_data["summoner_id"]

    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    return account
