from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.schemas.game import GameTagUpdate, GameResponse

router = APIRouter(prefix="/api/v1/games", tags=["games"])


@router.patch("/{game_id}/tag", response_model=GameResponse)
async def update_game_tag(
    game_id: int,
    update: GameTagUpdate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Update game type tag (soloq/competitive) and pentakill status"""
    # Join with RiotAccount and Player to verify team ownership
    game = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(
            Game.id == game_id,
            Player.team_id == team_ctx.team_id,
        )
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if update.game_type is not None:
        game.game_type = update.game_type
    if update.is_pentakill is not None:
        game.is_pentakill = update.is_pentakill

    db.commit()
    db.refresh(game)
    return game


@router.get("/pentakills", response_model=list[GameResponse])
async def get_pentakills(
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get all games with pentakills for the team"""
    games = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(
            Game.is_pentakill == True,
            Player.team_id == team_ctx.team_id,
        )
        .all()
    )
    return games
