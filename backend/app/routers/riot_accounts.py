from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.riot_account import RiotAccount
from app.models.game import Game
from app.models.rank_history import RankHistory
from app.schemas.riot_account import RiotAccountCreate, RiotAccountResponse
from app.services import riot_account_service

router = APIRouter(prefix="/api/v1", tags=["riot_accounts"])


@router.post("/players/{player_id}/riot-accounts", response_model=RiotAccountResponse, status_code=201)
async def add_riot_account(player_id: int, account: RiotAccountCreate, db: Session = Depends(get_db)):
    return await riot_account_service.create_riot_account(db, player_id, account)


@router.delete("/riot-accounts/{account_id}", status_code=204)
async def delete_riot_account(account_id: int, db: Session = Depends(get_db)):
    """Delete a riot account and all associated data"""
    account = db.query(RiotAccount).filter(RiotAccount.id == account_id).first()
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


@router.patch("/riot-accounts/{account_id}/rank", response_model=RiotAccountResponse, status_code=200)
async def update_riot_account_rank(
    account_id: int,
    rank_data: dict,
    db: Session = Depends(get_db)
):
    """Update rank information manually for a riot account"""
    account = db.query(RiotAccount).filter(RiotAccount.id == account_id).first()
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
