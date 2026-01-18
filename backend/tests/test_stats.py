import pytest
from datetime import datetime

from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.services.stats_service import get_player_stats


def test_get_player_stats_no_games(db):
    """Test stats for player with no games"""
    player = Player(summoner_name="TestPlayer", role="top")
    db.add(player)
    db.commit()

    stats = get_player_stats(db, player.id)

    assert stats is not None
    assert stats.player_id == player.id
    assert stats.summoner_name == "TestPlayer"
    assert stats.role == "top"
    assert stats.total_games == 0
    assert stats.avg_kda == 0.0
    assert stats.avg_cs_per_min == 0.0
    assert stats.avg_gold_per_min == 0.0
    assert stats.avg_vision_score_per_min == 0.0
    assert stats.avg_kill_participation == 0.0
    assert stats.winrate == 0.0


def test_get_player_stats_with_games(db):
    """Test stats calculation with actual games"""
    # Create player and riot account
    player = Player(summoner_name="TestPlayer", role="mid")
    db.add(player)
    db.commit()  # Commit player first to get ID

    riot_account = RiotAccount(
        player_id=player.id,
        puuid="test-puuid",
        summoner_name="TestSummoner",
        tag_line="TEST"
    )
    db.add(riot_account)
    db.commit()

    # Create test games with known stats
    games_data = [
        {
            "match_id": "match1",
            "champion_id": 1,
            "role": "middle",
            "stats": {
                "kills": 5, "deaths": 2, "assists": 10, "kda": 7.5,
                "cs": 200, "cs_per_min": 6.67,
                "gold": 12000, "gold_per_min": 400.0,
                "vision": 25, "vision_per_min": 0.83,
                "kp": 60.0, "win": True
            },
            "game_duration": 1800,  # 30 minutes
            "game_date": datetime.utcnow(),
            "is_pentakill": False
        },
        {
            "match_id": "match2",
            "champion_id": 2,
            "role": "middle",
            "stats": {
                "kills": 3, "deaths": 4, "assists": 5, "kda": 2.0,
                "cs": 180, "cs_per_min": 6.0,
                "gold": 10000, "gold_per_min": 333.33,
                "vision": 20, "vision_per_min": 0.67,
                "kp": 40.0, "win": False
            },
            "game_duration": 1800,
            "game_date": datetime.utcnow(),
            "is_pentakill": False
        }
    ]

    for game_data in games_data:
        game = Game(
            riot_account_id=riot_account.id,
            game_type="soloq",
            **game_data
        )
        db.add(game)
    db.commit()

    # Test stats calculation
    stats = get_player_stats(db, player.id)

    assert stats is not None
    assert stats.total_games == 2
    assert stats.avg_kda == 4.75  # (7.5 + 2.0) / 2
    assert abs(stats.avg_cs_per_min - 6.33) < 0.01  # (6.67 + 6.0) / 2
    assert abs(stats.avg_gold_per_min - 366.67) < 0.01  # (400.0 + 333.33) / 2
    assert abs(stats.avg_vision_score_per_min - 0.75) < 0.01  # (0.83 + 0.67) / 2
    assert stats.avg_kill_participation == 50.0  # (60.0 + 40.0) / 2
    assert stats.winrate == 50.0  # 1 win out of 2 games


def test_get_player_stats_multiple_accounts(db):
    """Test stats aggregation across multiple riot accounts"""
    player = Player(summoner_name="TestPlayer", role="adc")
    db.add(player)
    db.commit()  # Commit player first

    # Create two riot accounts
    account1 = RiotAccount(player_id=player.id, puuid="puuid1", summoner_name="Summoner1", tag_line="T1")
    account2 = RiotAccount(player_id=player.id, puuid="puuid2", summoner_name="Summoner2", tag_line="T2")
    db.add_all([account1, account2])
    db.commit()

    # Add games to both accounts
    game1 = Game(
        riot_account_id=account1.id,
        match_id="match1",
        game_type="soloq",
        champion_id=1,
        role="bottom",
        stats={"kills": 10, "deaths": 2, "assists": 5, "kda": 7.5, "cs": 250, "cs_per_min": 8.33,
               "gold": 14000, "gold_per_min": 466.67, "vision": 30, "vision_per_min": 1.0,
               "kp": 75.0, "win": True},
        game_duration=1800,
        game_date=datetime.utcnow(),
        is_pentakill=False
    )

    game2 = Game(
        riot_account_id=account2.id,
        match_id="match2",
        game_type="soloq",
        champion_id=2,
        role="bottom",
        stats={"kills": 2, "deaths": 6, "assists": 8, "kda": 1.67, "cs": 150, "cs_per_min": 5.0,
               "gold": 9000, "gold_per_min": 300.0, "vision": 15, "vision_per_min": 0.5,
               "kp": 33.33, "win": False},
        game_duration=1800,
        game_date=datetime.utcnow(),
        is_pentakill=False
    )

    db.add_all([game1, game2])
    db.commit()

    stats = get_player_stats(db, player.id)

    assert stats is not None
    assert stats.total_games == 2  # Games from both accounts
    assert abs(stats.avg_kda - 4.58) < 0.01  # (7.5 + 1.67) / 2
    assert stats.winrate == 50.0