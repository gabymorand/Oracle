from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game import Game
from app.models.rank_history import RankHistory
from app.models.riot_account import RiotAccount
from app.schemas.riot_account import RankHistoryEntry
from app.schemas.stats import ChampionStats, GameStats, LaneStats, PlayerStats, TeamHighlights
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


@router.get("/team/highlights", response_model=TeamHighlights)
async def get_team_highlights(db: Session = Depends(get_db)):
    """Get team highlights for sponsors page"""
    highlights = stats_service.get_team_highlights(db)
    return highlights


@router.get("/rank-history/{riot_account_id}", response_model=list[RankHistoryEntry])
async def get_rank_history(riot_account_id: int, db: Session = Depends(get_db)):
    """Get rank history for a riot account"""
    riot_account = db.query(RiotAccount).filter(RiotAccount.id == riot_account_id).first()
    if not riot_account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    history = (
        db.query(RankHistory)
        .filter(RankHistory.riot_account_id == riot_account_id)
        .order_by(RankHistory.recorded_at.asc())
        .all()
    )
    return history


@router.get("/games/{riot_account_id}", response_model=list[GameStats])
async def get_account_games(
    riot_account_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get recent games for a riot account"""
    riot_account = db.query(RiotAccount).filter(RiotAccount.id == riot_account_id).first()
    if not riot_account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    games = (
        db.query(Game)
        .filter(Game.riot_account_id == riot_account_id)
        .order_by(Game.game_date.desc())
        .limit(limit)
        .all()
    )

    return [GameStats.model_validate(game) for game in games]


@router.get("/champions/{riot_account_id}", response_model=list[ChampionStats])
async def get_champion_stats(riot_account_id: int, db: Session = Depends(get_db)):
    """Get champion statistics for a riot account"""
    riot_account = db.query(RiotAccount).filter(RiotAccount.id == riot_account_id).first()
    if not riot_account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    # Get all games for this account
    games = db.query(Game).filter(Game.riot_account_id == riot_account_id).all()

    # Group by champion_id and calculate stats
    champion_stats_dict = {}
    for game in games:
        champ_id = game.champion_id
        if champ_id not in champion_stats_dict:
            champion_stats_dict[champ_id] = {
                "games": [],
                "wins": 0,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
            }

        champion_stats_dict[champ_id]["games"].append(game)
        if game.stats.get("win"):
            champion_stats_dict[champ_id]["wins"] += 1

        # Extract stats from game.stats dict
        stats = game.stats
        champion_stats_dict[champ_id]["kills"] += stats.get("kills", 0)
        champion_stats_dict[champ_id]["deaths"] += stats.get("deaths", 0)
        champion_stats_dict[champ_id]["assists"] += stats.get("assists", 0)

    # Build response
    result = []
    for champ_id, data in champion_stats_dict.items():
        games_played = len(data["games"])
        wins = data["wins"]
        losses = games_played - wins
        winrate = (wins / games_played * 100) if games_played > 0 else 0

        # Calculate averages
        total_kda = 0
        total_cs_per_min = 0
        total_gold_per_min = 0
        total_vision_per_min = 0
        total_kp = 0

        for game in data["games"]:
            stats = game.stats
            total_kda += stats.get("kda", 0)
            total_cs_per_min += stats.get("cs_per_min", 0)
            total_gold_per_min += stats.get("gold_per_min", 0)
            total_vision_per_min += stats.get("vision_per_min", 0)
            total_kp += stats.get("kp", 0)

        result.append(
            ChampionStats(
                champion_id=champ_id,
                games_played=games_played,
                wins=wins,
                losses=losses,
                winrate=round(winrate, 2),
                avg_kda=round(total_kda / games_played, 2) if games_played > 0 else 0,
                avg_cs_per_min=round(total_cs_per_min / games_played, 2) if games_played > 0 else 0,
                avg_gold_per_min=round(total_gold_per_min / games_played, 2)
                if games_played > 0
                else 0,
                avg_vision_per_min=round(total_vision_per_min / games_played, 2)
                if games_played > 0
                else 0,
                avg_kp=round(total_kp / games_played, 2) if games_played > 0 else 0,
                total_kills=data["kills"],
                total_deaths=data["deaths"],
                total_assists=data["assists"],
            )
        )

    # Sort by games played (most played first)
    result.sort(key=lambda x: x.games_played, reverse=True)

    return result
