from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient
from app.schemas.game import GameTagUpdate, GameResponse, MatchDetailResponse
from app.services.match_import_service import build_match_detail_response

router = APIRouter(prefix="/api/v1/games", tags=["games"])
riot_client = RiotAPIClient()


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


@router.get("/{game_id}/details", response_model=MatchDetailResponse)
async def get_game_details(
    game_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get full match details from Riot API"""
    # Verify game belongs to team
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

    # Get all team player accounts with their rank info
    team_accounts = (
        db.query(RiotAccount)
        .join(Player)
        .filter(Player.team_id == team_ctx.team_id)
        .all()
    )

    # Build lookup dict: puuid -> rank info
    team_puuids = set(acc.puuid for acc in team_accounts)
    puuid_to_rank = {
        acc.puuid: {
            "tier": acc.rank_tier,
            "division": acc.rank_division,
            "lp": acc.lp,
        }
        for acc in team_accounts
    }

    # Fetch full match details from Riot API
    try:
        match_data = await riot_client.get_match_details(game.match_id)
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch match from Riot API: {str(e)}"
        )

    return build_match_detail_response(match_data, game.match_id, team_puuids, puuid_to_rank)
