import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient


@pytest.fixture
def sample_match_data():
    """Sample match data from Riot API"""
    return {
        "metadata": {
            "matchId": "EUW1_123456789",
            "participants": ["test-puuid"]
        },
        "info": {
            "gameCreation": 1672531200000,  # 2023-01-01 (before season 26)
            "gameDuration": 1800,  # 30 minutes
            "queueId": 420,  # Ranked Solo/Duo
            "participants": [
                {
                    "puuid": "test-puuid",
                    "championId": 1,
                    "teamPosition": "MIDDLE",
                    "kills": 5,
                    "deaths": 2,
                    "assists": 10,
                    "totalMinionsKilled": 180,
                    "neutralMinionsKilled": 20,
                    "goldEarned": 12000,
                    "visionScore": 25,
                    "win": True,
                    "pentaKills": 0,
                    "teamId": 100
                },
                {
                    "puuid": "other-puuid",
                    "championId": 2,
                    "teamPosition": "TOP",
                    "kills": 3,
                    "deaths": 1,
                    "assists": 7,
                    "totalMinionsKilled": 200,
                    "neutralMinionsKilled": 10,
                    "goldEarned": 11000,
                    "visionScore": 15,
                    "win": True,
                    "pentaKills": 0,
                    "teamId": 100
                }
            ]
        }
    }


@pytest.fixture
def season_26_match_data():
    """Sample match data from Season 26"""
    return {
        "metadata": {
            "matchId": "EUW1_987654321",
            "participants": ["test-puuid"]
        },
        "info": {
            "gameCreation": 1772531200000,  # 2026-01-10 (after Season 26 start)
            "gameDuration": 2100,  # 35 minutes
            "queueId": 420,
            "participants": [
                {
                    "puuid": "test-puuid",
                    "championId": 3,
                    "teamPosition": "BOTTOM",
                    "kills": 8,
                    "deaths": 3,
                    "assists": 12,
                    "totalMinionsKilled": 220,
                    "neutralMinionsKilled": 15,
                    "goldEarned": 13500,
                    "visionScore": 35,
                    "win": True,
                    "pentaKills": 1,  # Pentakill!
                    "teamId": 100
                },
                {
                    "puuid": "teammate1-puuid",
                    "championId": 4,
                    "teamPosition": "TOP",
                    "kills": 3,
                    "deaths": 1,
                    "assists": 7,
                    "totalMinionsKilled": 200,
                    "neutralMinionsKilled": 10,
                    "goldEarned": 11000,
                    "visionScore": 15,
                    "win": True,
                    "pentaKills": 0,
                    "teamId": 100
                },
                {
                    "puuid": "teammate2-puuid",
                    "championId": 6,
                    "teamPosition": "MIDDLE",
                    "kills": 7,
                    "deaths": 2,
                    "assists": 8,
                    "totalMinionsKilled": 190,
                    "neutralMinionsKilled": 12,
                    "goldEarned": 12000,
                    "visionScore": 25,
                    "win": True,
                    "pentaKills": 0,
                    "teamId": 100
                },
                {
                    "puuid": "teammate3-puuid",
                    "championId": 8,
                    "teamPosition": "JUNGLE",
                    "kills": 12,
                    "deaths": 1,
                    "assists": 15,
                    "totalMinionsKilled": 50,
                    "neutralMinionsKilled": 150,
                    "goldEarned": 14000,
                    "visionScore": 40,
                    "win": True,
                    "pentaKills": 0,
                    "teamId": 100
                },
                {
                    "puuid": "enemy1-puuid",
                    "championId": 5,
                    "teamPosition": "MIDDLE",
                    "kills": 2,
                    "deaths": 4,
                    "assists": 5,
                    "totalMinionsKilled": 180,
                    "neutralMinionsKilled": 20,
                    "goldEarned": 10000,
                    "visionScore": 20,
                    "win": False,
                    "pentaKills": 0,
                    "teamId": 200
                },
                {
                    "puuid": "enemy2-puuid",
                    "championId": 7,
                    "teamPosition": "BOTTOM",
                    "kills": 1,
                    "deaths": 5,
                    "assists": 3,
                    "totalMinionsKilled": 170,
                    "neutralMinionsKilled": 8,
                    "goldEarned": 9500,
                    "visionScore": 18,
                    "win": False,
                    "pentaKills": 0,
                    "teamId": 200
                }
            ]
        }
    }


class TestRiotIntegration:

    async def test_fetch_and_store_matches_season_26_only(self, db, season_26_match_data):
        """Test that only Season 26 matches are stored"""
        # Create test data
        player = Player(summoner_name="TestPlayer", role="adc")
        db.add(player)
        db.commit()
        
        riot_account = RiotAccount(
            player_id=player.id,
            puuid="test-puuid",
            summoner_name="TestSummoner",
            tag_line="TEST"
        )
        db.add(riot_account)
        db.commit()

        client = RiotAPIClient()
        client.api_key = "test-key"
        client.region = "euw1"

        # Mock the API calls
        with patch.object(client, 'get_match_ids_by_puuid', new_callable=AsyncMock) as mock_get_ids, \
             patch.object(client, 'get_match_details', new_callable=AsyncMock) as mock_get_details:

            mock_get_ids.return_value = ["EUW1_987654321"]
            mock_get_details.return_value = season_26_match_data

            # Execute
            await client.fetch_and_store_matches(db, riot_account)

            # Verify game was stored
            games = db.query(Game).filter(Game.riot_account_id == riot_account.id).all()
            assert len(games) == 1

            game = games[0]
            assert game.match_id == "EUW1_987654321"
            assert game.champion_id == 3
            assert game.role == "bottom"
            assert game.game_duration == 2100
            assert game.is_pentakill == True

            # Verify stats calculations
            stats = game.stats
            assert stats["kills"] == 8
            assert stats["deaths"] == 3
            assert stats["assists"] == 12
            assert abs(stats["kda"] - 6.67) < 0.01  # (8+12)/3
            assert stats["cs"] == 235  # 220 + 15
            assert abs(stats["cs_per_min"] - 6.71) < 0.01  # 235/35
            assert stats["gold"] == 13500
            assert abs(stats["gold_per_min"] - 385.71) < 0.01  # 13500/35
            assert stats["vision"] == 35
            assert abs(stats["vision_per_min"] - 1.0) < 0.01  # 35/35
            assert abs(stats["kp"] - 66.67) < 0.01  # (8+12)/(8+12+3+7) * 100 for team
            assert stats["win"] == True

    async def test_skip_old_season_matches(self, db, sample_match_data):
        """Test that pre-Season 26 matches are skipped"""
        # Create test data
        player = Player(summoner_name="TestPlayer", role="mid")
        db.add(player)
        db.commit()
        
        riot_account = RiotAccount(
            player_id=player.id,
            puuid="test-puuid",
            summoner_name="TestSummoner",
            tag_line="TEST"
        )
        db.add(riot_account)
        db.commit()

        client = RiotAPIClient()
        client.api_key = "test-key"
        client.region = "euw1"

        # Mock the API calls
        with patch.object(client, 'get_match_ids_by_puuid', new_callable=AsyncMock) as mock_get_ids, \
             patch.object(client, 'get_match_details', new_callable=AsyncMock) as mock_get_details:

            mock_get_ids.return_value = ["EUW1_123456789"]
            mock_get_details.return_value = sample_match_data

            # Execute
            await client.fetch_and_store_matches(db, riot_account)

            # Verify no games were stored (old season)
            games = db.query(Game).filter(Game.riot_account_id == riot_account.id).all()
            assert len(games) == 0

    async def test_skip_non_ranked_matches(self, db):
        """Test that non-ranked matches are skipped"""
        # Create test data
        player = Player(summoner_name="TestPlayer", role="top")
        db.add(player)
        db.commit()
        
        riot_account = RiotAccount(
            player_id=player.id,
            puuid="test-puuid",
            summoner_name="TestSummoner",
            tag_line="TEST"
        )
        db.add(riot_account)
        db.commit()

        client = RiotAPIClient()
        client.api_key = "test-key"
        client.region = "euw1"

        # Mock match data for ARAM (queueId 450)
        aram_match_data = {
            "metadata": {"matchId": "EUW1_999999999", "participants": ["test-puuid"]},
            "info": {
                "gameCreation": 1704758400000,
                "gameDuration": 1200,
                "queueId": 450,  # ARAM
                "participants": [{
                    "puuid": "test-puuid",
                    "championId": 1,
                    "teamPosition": "",
                    "kills": 5, "deaths": 2, "assists": 10,
                    "totalMinionsKilled": 50, "neutralMinionsKilled": 0,
                    "goldEarned": 10000, "visionScore": 10,
                    "win": True, "pentaKills": 0, "teamId": 100
                }]
            }
        }

        with patch.object(client, 'get_match_ids_by_puuid', new_callable=AsyncMock) as mock_get_ids, \
             patch.object(client, 'get_match_details', new_callable=AsyncMock) as mock_get_details:

            mock_get_ids.return_value = ["EUW1_999999999"]
            mock_get_details.return_value = aram_match_data

            # Execute
            await client.fetch_and_store_matches(db, riot_account)

            # Verify no games were stored (not ranked)
            games = db.query(Game).filter(Game.riot_account_id == riot_account.id).all()
            assert len(games) == 0

    async def test_skip_duplicate_matches(self, db, season_26_match_data):
        """Test that duplicate matches are not stored twice"""
        # Create test data
        player = Player(summoner_name="TestPlayer", role="mid")
        db.add(player)
        db.commit()
        
        riot_account = RiotAccount(
            player_id=player.id,
            puuid="test-puuid",
            summoner_name="TestSummoner",
            tag_line="TEST"
        )
        db.add(riot_account)
        db.commit()

        client = RiotAPIClient()
        client.api_key = "test-key"
        client.region = "euw1"

        # First, store the game
        with patch.object(client, 'get_match_ids_by_puuid', new_callable=AsyncMock) as mock_get_ids, \
             patch.object(client, 'get_match_details', new_callable=AsyncMock) as mock_get_details:

            mock_get_ids.return_value = ["EUW1_987654321"]
            mock_get_details.return_value = season_26_match_data

            await client.fetch_and_store_matches(db, riot_account)

            games = db.query(Game).filter(Game.riot_account_id == riot_account.id).all()
            assert len(games) == 1

        # Try to store the same game again
        with patch.object(client, 'get_match_ids_by_puuid', new_callable=AsyncMock) as mock_get_ids, \
             patch.object(client, 'get_match_details', new_callable=AsyncMock) as mock_get_details:

            mock_get_ids.return_value = ["EUW1_987654321"]  # Same match ID
            mock_get_details.return_value = season_26_match_data

            await client.fetch_and_store_matches(db, riot_account)

            # Should still be only 1 game
            games = db.query(Game).filter(Game.riot_account_id == riot_account.id).all()
            assert len(games) == 1