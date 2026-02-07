from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.game import Game
from app.models.player import Player
from app.models.rank_history import RankHistory
from app.models.riot_account import RiotAccount
from app.schemas.riot_account import RankHistoryEntry
from app.schemas.stats import (
    ActivityGame,
    ChampionMatchup,
    ChampionStats,
    GameStats,
    LaneStats,
    PlayerActivitySummary,
    PlayerStats,
    TeamActivityResponse,
    TeamHighlights,
)
from app.services import stats_service

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


def verify_player_team(db: Session, player_id: int, team_id: int) -> Player:
    """Verify player belongs to team"""
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.team_id == team_id,
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


def verify_riot_account_team(db: Session, riot_account_id: int, team_id: int) -> RiotAccount:
    """Verify riot account belongs to a player in the team"""
    riot_account = (
        db.query(RiotAccount)
        .join(Player)
        .filter(
            RiotAccount.id == riot_account_id,
            Player.team_id == team_id,
        )
        .first()
    )
    if not riot_account:
        raise HTTPException(status_code=404, detail="Riot account not found")
    return riot_account


@router.get("/player/{player_id}", response_model=PlayerStats)
async def get_player_stats(
    player_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    verify_player_team(db, player_id, team_ctx.team_id)
    stats = stats_service.get_player_stats(db, player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found or no stats available")
    return stats


@router.get("/lane/{lane}", response_model=LaneStats)
async def get_lane_stats(
    lane: str,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    stats = stats_service.get_lane_stats(db, team_ctx.team_id, lane)
    if not stats:
        raise HTTPException(status_code=404, detail="Lane not found or no stats available")
    return stats


@router.post("/refresh/{riot_account_id}", status_code=200)
async def refresh_stats(
    riot_account_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    verify_riot_account_team(db, riot_account_id, team_ctx.team_id)
    await stats_service.refresh_player_stats(db, riot_account_id)
    return {"message": "Stats refreshed successfully"}


@router.post("/refresh-all", status_code=200)
async def refresh_all_stats(
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """
    Refresh stats for ALL riot accounts in the team.
    Optimized: only fetches games newer than the last stored game per account.
    """
    # Get all riot accounts for the team
    riot_accounts = (
        db.query(RiotAccount)
        .join(Player)
        .filter(Player.team_id == team_ctx.team_id)
        .all()
    )

    if not riot_accounts:
        return {
            "message": "No riot accounts found",
            "refreshed": 0,
            "failed": 0,
            "results": [],
        }

    results = []
    refreshed = 0
    failed = 0

    for account in riot_accounts:
        try:
            await stats_service.refresh_player_stats(db, account.id)
            results.append({
                "account": f"{account.summoner_name}#{account.tag_line}",
                "status": "success",
            })
            refreshed += 1
        except Exception as e:
            results.append({
                "account": f"{account.summoner_name}#{account.tag_line}",
                "status": "failed",
                "error": str(e),
            })
            failed += 1

    return {
        "message": f"Refresh complete: {refreshed} success, {failed} failed",
        "refreshed": refreshed,
        "failed": failed,
        "results": results,
    }


@router.get("/team/highlights", response_model=TeamHighlights)
async def get_team_highlights(
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get team highlights for sponsors page"""
    highlights = stats_service.get_team_highlights(db, team_ctx.team_id)
    return highlights


@router.get("/rank-history/{riot_account_id}", response_model=list[RankHistoryEntry])
async def get_rank_history(
    riot_account_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get rank history for a riot account"""
    verify_riot_account_team(db, riot_account_id, team_ctx.team_id)

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
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get recent games for a riot account"""
    verify_riot_account_team(db, riot_account_id, team_ctx.team_id)

    games = (
        db.query(Game)
        .filter(Game.riot_account_id == riot_account_id)
        .order_by(Game.game_date.desc())
        .limit(limit)
        .all()
    )

    return [GameStats.model_validate(game) for game in games]


@router.get("/champions/{riot_account_id}", response_model=list[ChampionStats])
async def get_champion_stats(
    riot_account_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get champion statistics for a riot account"""
    verify_riot_account_team(db, riot_account_id, team_ctx.team_id)

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


@router.get("/activity", response_model=TeamActivityResponse)
async def get_team_activity(
    week_offset: int = Query(0, description="Week offset (0 = current week, -1 = last week, etc.)"),
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """
    Get SoloQ activity for all players for a given week.
    Returns games grouped by player and day for the activity grid view.
    """
    # Calculate week boundaries (Monday to Sunday)
    today = date.today()
    # Find the Monday of the current week
    monday = today - timedelta(days=today.weekday())
    # Apply week offset
    monday = monday + timedelta(weeks=week_offset)
    sunday = monday + timedelta(days=6)

    week_start = datetime.combine(monday, datetime.min.time())
    week_end = datetime.combine(sunday, datetime.max.time())

    # Get all players for the team with their main accounts
    players = (
        db.query(Player)
        .filter(Player.team_id == team_ctx.team_id)
        .order_by(Player.role)  # Order by role (top, jungle, mid, adc, support)
        .all()
    )

    # Role order for sorting
    role_order = {"top": 0, "jungle": 1, "mid": 2, "adc": 3, "support": 4}
    players = sorted(players, key=lambda p: role_order.get(p.role.lower(), 99))

    total_soloq = 0
    total_scrims = 0
    total_wins = 0
    player_summaries = []

    for player in players:
        # Get main riot account (or first one if none marked as main)
        main_account = next(
            (acc for acc in player.riot_accounts if acc.is_main),
            player.riot_accounts[0] if player.riot_accounts else None,
        )

        # Get all games for this player's accounts within the week
        riot_account_ids = [acc.id for acc in player.riot_accounts]
        if not riot_account_ids:
            player_summaries.append(
                PlayerActivitySummary(
                    player_id=player.id,
                    summoner_name=player.summoner_name,
                    role=player.role,
                    riot_account_id=None,
                    total_games=0,
                    wins=0,
                    losses=0,
                    winrate=0.0,
                    scrims=0,
                    duos=0,
                    games_by_day={},
                    matchups=[],
                )
            )
            continue

        games = (
            db.query(Game)
            .filter(
                Game.riot_account_id.in_(riot_account_ids),
                Game.game_date >= week_start,
                Game.game_date <= week_end,
            )
            .order_by(Game.game_date.asc())
            .all()
        )

        # Group games by day
        games_by_day: dict[str, list[ActivityGame]] = {}
        player_wins = 0
        player_scrims = 0
        player_soloq = 0

        for game in games:
            day_key = game.game_date.strftime("%Y-%m-%d")
            if day_key not in games_by_day:
                games_by_day[day_key] = []

            # Calculate start and end time
            start_time = game.game_date.strftime("%H:%M")
            end_time = (game.game_date + timedelta(seconds=game.game_duration)).strftime("%H:%M")

            activity_game = ActivityGame(
                id=game.id,
                match_id=game.match_id,
                game_type=game.game_type,
                champion_id=game.champion_id,
                kills=game.stats.get("kills", 0),
                deaths=game.stats.get("deaths", 0),
                assists=game.stats.get("assists", 0),
                win=game.stats.get("win", False),
                game_date=game.game_date,
                game_duration=game.game_duration,
                start_time=start_time,
                end_time=end_time,
            )
            games_by_day[day_key].append(activity_game)

            if game.stats.get("win"):
                player_wins += 1
                total_wins += 1

            if game.game_type == "competitive":
                player_scrims += 1
                total_scrims += 1
            else:
                player_soloq += 1
                total_soloq += 1

        total_games = len(games)
        winrate = (player_wins / total_games * 100) if total_games > 0 else 0.0

        # Calculate champion matchups (opponents faced)
        # For now, we track the champions the player played against (simplified)
        matchups: list[ChampionMatchup] = []

        player_summaries.append(
            PlayerActivitySummary(
                player_id=player.id,
                summoner_name=player.summoner_name,
                role=player.role,
                riot_account_id=main_account.id if main_account else None,
                rank_tier=main_account.rank_tier if main_account else None,
                rank_division=main_account.rank_division if main_account else None,
                lp=main_account.lp if main_account else None,
                total_games=total_games,
                wins=player_wins,
                losses=total_games - player_wins,
                winrate=round(winrate, 1),
                scrims=player_scrims,
                duos=0,  # Placeholder - would need to detect duo games
                games_by_day=games_by_day,
                matchups=matchups,
                last_refreshed_at=main_account.last_refreshed_at if main_account else None,
            )
        )

    overall_games = total_soloq + total_scrims
    overall_winrate = (total_wins / overall_games * 100) if overall_games > 0 else 0.0

    return TeamActivityResponse(
        week_start=monday.isoformat(),
        week_end=sunday.isoformat(),
        total_soloq=total_soloq,
        total_scrims=total_scrims,
        total_duos=0,
        overall_winrate=round(overall_winrate, 1),
        players=player_summaries,
        last_updated=datetime.utcnow(),
    )
