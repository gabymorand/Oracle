from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.services import player_service

router = APIRouter(prefix="/api/v1/players", tags=["players"])


@router.get("", response_model=list[PlayerResponse])
async def list_players(db: Session = Depends(get_db)):
    return player_service.get_all_players(db)


@router.post("", response_model=PlayerResponse, status_code=201)
async def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    return player_service.create_player(db, player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    player = player_service.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.patch("/{player_id}", response_model=PlayerResponse)
async def update_player(player_id: int, player_update: PlayerUpdate, db: Session = Depends(get_db)):
    player = player_service.update_player(db, player_id, player_update)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: int, db: Session = Depends(get_db)):
    success = player_service.delete_player(db, player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found")
