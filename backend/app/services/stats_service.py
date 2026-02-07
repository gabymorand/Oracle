from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient
from app.schemas.stats import GameStats, LaneStats, PlayerStats, TeamHighlights


def get_player_stats(db: Session, player_id: int) -> PlayerStats | None:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None

    # Get all games for all riot accounts of this player
    riot_account_ids = [acc.id for acc in player.riot_accounts]
    games = db.query(Game).filter(Game.riot_account_id.in_(riot_account_ids)).all()

    if not games:
        return PlayerStats(
            player_id=player.id,
            summoner_name=player.summoner_name,
            role=player.role,
            total_games=0,
            avg_kda=0.0,
            avg_cs_per_min=0.0,
            avg_gold_per_min=0.0,
            avg_vision_score_per_min=0.0,
            avg_kill_participation=0.0,
            winrate=0.0,
        )

    # Compute stats (stub for now)
    total_games = len(games)
    wins = sum(1 for g in games if g.stats.get("win", False))
    winrate = (wins / total_games * 100) if total_games > 0 else 0.0

    # Average stats
    avg_kda = sum(g.stats.get("kda", 0) for g in games) / total_games
    avg_cs_per_min = sum(g.stats.get("cs_per_min", 0) for g in games) / total_games
    avg_gold_per_min = sum(g.stats.get("gold_per_min", 0) for g in games) / total_games
    avg_vision_score_per_min = sum(g.stats.get("vision_per_min", 0) for g in games) / total_games
    avg_kill_participation = sum(g.stats.get("kp", 0) for g in games) / total_games

    return PlayerStats(
        player_id=player.id,
        summoner_name=player.summoner_name,
        role=player.role,
        total_games=total_games,
        avg_kda=round(avg_kda, 2),
        avg_cs_per_min=round(avg_cs_per_min, 2),
        avg_gold_per_min=round(avg_gold_per_min, 2),
        avg_vision_score_per_min=round(avg_vision_score_per_min, 2),
        avg_kill_participation=round(avg_kill_participation, 2),
        winrate=round(winrate, 2),
    )


def get_lane_stats(db: Session, team_id: int, lane: str) -> LaneStats | None:
    # For botlane, get ADC + Support
    if lane == "botlane":
        roles = ["adc", "support"]
    else:
        roles = [lane]

    players = db.query(Player).filter(
        Player.team_id == team_id,
        Player.role.in_(roles),
    ).all()
    if not players:
        return None

    player_stats = [get_player_stats(db, p.id) for p in players]
    player_stats = [ps for ps in player_stats if ps is not None]

    total_games = sum(ps.total_games for ps in player_stats)
    if total_games == 0:
        combined_winrate = 0.0
    else:
        total_wins = sum(ps.winrate * ps.total_games / 100 for ps in player_stats)
        combined_winrate = (total_wins / total_games * 100) if total_games > 0 else 0.0

    return LaneStats(
        lane=lane, players=player_stats, combined_winrate=round(combined_winrate, 2), total_games=total_games
    )


async def refresh_player_stats(db: Session, riot_account_id: int):
    from datetime import datetime

    from fastapi import HTTPException

    riot_account = db.query(RiotAccount).filter(RiotAccount.id == riot_account_id).first()
    if not riot_account:
        raise HTTPException(status_code=404, detail="Riot account not found")

    print(f"Starting stats refresh for account {riot_account.summoner_name}#{riot_account.tag_line}")
    riot_client = RiotAPIClient()
    try:
        # Update rank first
        print("Fetching and updating rank...")
        await riot_client.fetch_and_update_rank(db, riot_account)
        print("Rank updated successfully")
        # Then fetch matches
        print("Fetching and storing matches...")
        await riot_client.fetch_and_store_matches(db, riot_account, max_matches=20)
        print("Matches fetched and stored successfully")

        # Update last_refreshed_at timestamp
        riot_account.last_refreshed_at = datetime.utcnow()
        db.commit()
    except ValueError as e:
        error_msg = str(e)
        print(f"ValueError during stats refresh: {error_msg}")
        if "Invalid summoner data received from Riot API" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="❌ Riot API Error: Invalid or incomplete response from Riot API. This usually indicates an invalid API key. Please check your RIOT_API_KEY in the .env file.",
            )
        if "Unable to retrieve summoner ID from Riot API" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="❌ Riot API Error: Unable to retrieve summoner information. This may indicate API key restrictions or the summoner data is not publicly available. Please use the 'Manual Entry' button to add rank information manually, and optionally enter the Summoner ID if known to enable automatic refresh.",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Data validation error: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        print(f"Error during stats refresh: {error_msg}")
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Riot API is unavailable (401 Unauthorized). The API key may be invalid or expired.",
            )
        elif "403" in error_msg or "Forbidden" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Riot API access forbidden (403). Please check API key permissions.",
            )
        elif "404" in error_msg:
            raise HTTPException(
                status_code=404,
                detail="Account not found on Riot servers. This account may have been created with a fallback PUUID. Please delete and re-add the account when Riot API is available.",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to fetch stats from Riot API: {error_msg}")


def get_team_highlights(db: Session, team_id: int) -> TeamHighlights:
    """Get team highlights for sponsors page"""
    # Get all games for this team's players
    all_games = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(Player.team_id == team_id)
        .all()
    )
    total_games = len(all_games)
    total_wins = sum(1 for g in all_games if g.stats.get("win", False))
    winrate = (total_wins / total_games * 100) if total_games > 0 else 0.0

    # Get competitive games
    comp_games = [g for g in all_games if g.game_type == "competitive"]
    competitive_games = len(comp_games)
    competitive_wins = sum(1 for g in comp_games if g.stats.get("win", False))
    competitive_winrate = (competitive_wins / competitive_games * 100) if competitive_games > 0 else 0.0

    # Get pentakills
    total_pentakills = sum(1 for g in all_games if g.is_pentakill)

    # Get recent matches (last 10)
    recent_matches = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(Player.team_id == team_id)
        .order_by(Game.game_date.desc())
        .limit(10)
        .all()
    )

    return TeamHighlights(
        total_games=total_games,
        total_wins=total_wins,
        winrate=round(winrate, 2),
        competitive_games=competitive_games,
        competitive_wins=competitive_wins,
        competitive_winrate=round(competitive_winrate, 2),
        total_pentakills=total_pentakills,
        recent_matches=[GameStats.model_validate(g) for g in recent_matches],
    )
