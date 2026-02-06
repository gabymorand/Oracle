from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.models.tier_list import ChampionTier
from app.schemas.tier_list import (
    ChampionStatsWithScore,
    ChampionTierCreate,
    PlayerTierList,
    Tier,
)


# Champion name lookup (simplified - in production would use Data Dragon)
CHAMPION_NAMES = {
    1: "Annie", 2: "Olaf", 3: "Galio", 4: "Twisted Fate", 5: "Xin Zhao",
    6: "Urgot", 7: "LeBlanc", 8: "Vladimir", 9: "Fiddlesticks", 10: "Kayle",
    11: "Master Yi", 12: "Alistar", 13: "Ryze", 14: "Sion", 15: "Sivir",
    16: "Soraka", 17: "Teemo", 18: "Tristana", 19: "Warwick", 20: "Nunu",
    21: "Miss Fortune", 22: "Ashe", 23: "Tryndamere", 24: "Jax", 25: "Morgana",
    26: "Zilean", 27: "Singed", 28: "Evelynn", 29: "Twitch", 30: "Karthus",
    # Add more as needed...
}


def get_champion_name(champion_id: int) -> str:
    """Get champion name from ID"""
    return CHAMPION_NAMES.get(champion_id, f"Champion {champion_id}")


def calculate_performance_score(
    winrate: float,
    avg_kda: float,
    avg_cs_per_min: float,
    avg_gold_per_min: float,
    avg_vision_per_min: float,
    avg_damage_per_min: float,
    avg_kp: float,
) -> int:
    """
    Calculate performance score from 0-100.

    Weights:
    - Winrate: 20%
    - KDA: 20%
    - CS/min: 15%
    - Gold/min: 15%
    - Vision/min: 10%
    - Damage/min: 10%
    - Kill Participation: 10%

    Benchmarks (100 points each):
    - Winrate: 60% = 100
    - KDA: 4.0 = 100
    - CS/min: 8.0 = 100
    - Gold/min: 450 = 100
    - Vision/min: 1.5 = 100
    - Damage/min: 600 = 100
    - KP: 70% = 100
    """
    # Normalize each stat to 0-100 (capped at 100)
    winrate_score = min(100, (winrate / 60) * 100)
    kda_score = min(100, (avg_kda / 4.0) * 100)
    cs_score = min(100, (avg_cs_per_min / 8.0) * 100)
    gold_score = min(100, (avg_gold_per_min / 450) * 100)
    vision_score = min(100, (avg_vision_per_min / 1.5) * 100)
    damage_score = min(100, (avg_damage_per_min / 600) * 100)
    kp_score = min(100, (avg_kp / 70) * 100)

    # Weighted average
    score = (
        winrate_score * 0.20 +
        kda_score * 0.20 +
        cs_score * 0.15 +
        gold_score * 0.15 +
        vision_score * 0.10 +
        damage_score * 0.10 +
        kp_score * 0.10
    )

    return int(round(score))


def get_player_champion_stats(db: Session, player_id: int) -> list[ChampionStatsWithScore]:
    """Get champion stats with scores for a player"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return []

    # Get all riot account IDs for this player
    riot_account_ids = [acc.id for acc in player.riot_accounts]
    if not riot_account_ids:
        return []

    # Get all games grouped by champion
    games = (
        db.query(Game)
        .filter(Game.riot_account_id.in_(riot_account_ids))
        .all()
    )

    if not games:
        return []

    # Get existing tier assignments
    tier_assignments = {
        ct.champion_id: ct.tier
        for ct in db.query(ChampionTier).filter(ChampionTier.player_id == player_id).all()
    }

    # Group games by champion
    champion_games: dict[int, list[Game]] = {}
    for game in games:
        if game.champion_id not in champion_games:
            champion_games[game.champion_id] = []
        champion_games[game.champion_id].append(game)

    # Calculate stats for each champion
    results = []
    for champion_id, champ_games in champion_games.items():
        games_played = len(champ_games)
        wins = sum(1 for g in champ_games if g.stats.get("win", False))
        losses = games_played - wins
        winrate = (wins / games_played * 100) if games_played > 0 else 0.0

        # Calculate averages
        avg_kda = sum(g.stats.get("kda", 0) for g in champ_games) / games_played
        avg_cs_per_min = sum(g.stats.get("cs_per_min", 0) for g in champ_games) / games_played
        avg_gold_per_min = sum(g.stats.get("gold_per_min", 0) for g in champ_games) / games_played
        avg_vision_per_min = sum(g.stats.get("vision_per_min", 0) for g in champ_games) / games_played
        avg_kp = sum(g.stats.get("kp", 0) for g in champ_games) / games_played

        # Calculate damage per min
        total_damage = 0
        total_duration = 0
        for g in champ_games:
            damage = g.stats.get("damage_dealt", 0)
            duration = g.game_duration / 60  # Convert to minutes
            total_damage += damage
            total_duration += duration
        avg_damage_per_min = (total_damage / total_duration) if total_duration > 0 else 0

        # Calculate performance score
        score = calculate_performance_score(
            winrate=winrate,
            avg_kda=avg_kda,
            avg_cs_per_min=avg_cs_per_min,
            avg_gold_per_min=avg_gold_per_min,
            avg_vision_per_min=avg_vision_per_min,
            avg_damage_per_min=avg_damage_per_min,
            avg_kp=avg_kp,
        )

        # Get tier if assigned
        tier = tier_assignments.get(champion_id)

        results.append(ChampionStatsWithScore(
            champion_id=champion_id,
            champion_name=get_champion_name(champion_id),
            games_played=games_played,
            wins=wins,
            losses=losses,
            winrate=round(winrate, 1),
            avg_kda=round(avg_kda, 2),
            avg_cs_per_min=round(avg_cs_per_min, 2),
            avg_gold_per_min=round(avg_gold_per_min, 2),
            avg_vision_per_min=round(avg_vision_per_min, 2),
            avg_damage_per_min=round(avg_damage_per_min, 2),
            avg_kill_participation=round(avg_kp, 1),
            performance_score=score,
            tier=tier,
        ))

    # Sort by performance score descending
    results.sort(key=lambda x: x.performance_score, reverse=True)
    return results


def get_player_tier_list(db: Session, player_id: int) -> PlayerTierList | None:
    """Get complete tier list for a player"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None

    # Get champions with stats (played champions)
    champions_with_stats = get_player_champion_stats(db, player_id)
    champions_with_stats_ids = {c.champion_id for c in champions_with_stats}

    # Get all tier assignments for this player (including unplayed champions)
    tier_assignments = (
        db.query(ChampionTier)
        .filter(ChampionTier.player_id == player_id)
        .all()
    )

    # Add champions that have tiers but weren't played
    all_champions = list(champions_with_stats)
    for tier_assignment in tier_assignments:
        if tier_assignment.champion_id not in champions_with_stats_ids:
            # Create a placeholder entry for unplayed champion
            all_champions.append(ChampionStatsWithScore(
                champion_id=tier_assignment.champion_id,
                champion_name=get_champion_name(tier_assignment.champion_id),
                games_played=0,
                wins=0,
                losses=0,
                winrate=0.0,
                avg_kda=0.0,
                avg_cs_per_min=0.0,
                avg_gold_per_min=0.0,
                avg_vision_per_min=0.0,
                avg_damage_per_min=0.0,
                avg_kill_participation=0.0,
                performance_score=0,
                tier=tier_assignment.tier,
            ))

    # Group by tier
    tier_s = [c for c in all_champions if c.tier == "S"]
    tier_a = [c for c in all_champions if c.tier == "A"]
    tier_b = [c for c in all_champions if c.tier == "B"]
    tier_c = [c for c in all_champions if c.tier == "C"]
    tier_d = [c for c in all_champions if c.tier == "D"]
    unranked = [c for c in all_champions if c.tier is None]

    return PlayerTierList(
        player_id=player.id,
        player_name=player.summoner_name,
        champions=all_champions,
        tier_s=tier_s,
        tier_a=tier_a,
        tier_b=tier_b,
        tier_c=tier_c,
        tier_d=tier_d,
        unranked=unranked,
    )


def set_champion_tier(
    db: Session, player_id: int, champion_id: int, tier: Tier
) -> ChampionTier:
    """Set or update a champion's tier for a player"""
    existing = (
        db.query(ChampionTier)
        .filter(
            ChampionTier.player_id == player_id,
            ChampionTier.champion_id == champion_id,
        )
        .first()
    )

    if existing:
        existing.tier = tier.value
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    new_tier = ChampionTier(
        player_id=player_id,
        champion_id=champion_id,
        tier=tier.value,
    )
    db.add(new_tier)
    db.commit()
    db.refresh(new_tier)
    return new_tier


def delete_champion_tier(db: Session, player_id: int, champion_id: int) -> bool:
    """Remove a champion's tier assignment"""
    existing = (
        db.query(ChampionTier)
        .filter(
            ChampionTier.player_id == player_id,
            ChampionTier.champion_id == champion_id,
        )
        .first()
    )

    if not existing:
        return False

    db.delete(existing)
    db.commit()
    return True
