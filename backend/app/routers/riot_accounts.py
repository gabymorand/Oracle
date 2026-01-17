from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.riot_account import RiotAccountCreate, RiotAccountResponse
from app.services import riot_account_service

router = APIRouter(prefix="/api/v1", tags=["riot_accounts"])


@router.post("/players/{player_id}/riot-accounts", response_model=RiotAccountResponse, status_code=201)
async def add_riot_account(player_id: int, account: RiotAccountCreate, db: Session = Depends(get_db)):
    return await riot_account_service.create_riot_account(db, player_id, account)


@router.delete("/riot-accounts/{account_id}", status_code=204)
async def delete_riot_account(account_id: int, db: Session = Depends(get_db)):
    success = riot_account_service.delete_riot_account(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Riot account not found")
