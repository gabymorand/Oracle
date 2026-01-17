from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient
from app.schemas.stats import LaneStats, PlayerStats


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


def get_lane_stats(db: Session, lane: str) -> LaneStats | None:
    # For botlane, get ADC + Support
    if lane == "botlane":
        roles = ["adc", "support"]
    else:
        roles = [lane]

    players = db.query(Player).filter(Player.role.in_(roles)).all()
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
    riot_account = db.query(RiotAccount).filter(RiotAccount.id == riot_account_id).first()
    if not riot_account:
        return

    riot_client = RiotAPIClient()
    await riot_client.fetch_and_store_matches(db, riot_account)
