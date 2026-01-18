import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient


@pytest.fixture
def riot_client():
    """Create RiotAPIClient with test settings"""
    client = RiotAPIClient()
    client.api_key = "test-api-key"
    client.region = "euw1"
    return client


class TestRiotAPIClient:

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_puuid_by_riot_id_success(self, mock_request, riot_client):
        """Test successful PUUID retrieval"""
        mock_request.return_value = {"puuid": "test-puuid-123"}

        result = await riot_client.get_puuid_by_riot_id("TestPlayer", "EUW")

        assert result == "test-puuid-123"
        mock_request.assert_called_once()

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_puuid_by_riot_id_not_found(self, mock_request, riot_client):
        """Test PUUID retrieval for non-existent account"""
        mock_request.side_effect = ValueError("Resource not found")

        with pytest.raises(ValueError, match="Resource not found"):
            await riot_client.get_puuid_by_riot_id("NonExistent", "EUW")

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_summoner_by_puuid(self, mock_request, riot_client):
        """Test summoner data retrieval"""
        mock_data = {
            "id": "summoner-id-123",
            "accountId": "account-id-123",
            "puuid": "test-puuid",
            "name": "TestSummoner",
            "profileIconId": 123,
            "revisionDate": 1234567890,
            "summonerLevel": 50
        }
        mock_request.return_value = mock_data

        result = await riot_client.get_summoner_by_puuid("test-puuid")

        assert result == mock_data
        assert result["name"] == "TestSummoner"

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_match_ids_by_puuid(self, mock_request, riot_client):
        """Test match IDs retrieval"""
        mock_match_ids = ["EUW1_123456789", "EUW1_987654321"]
        mock_request.return_value = mock_match_ids

        result = await riot_client.get_match_ids_by_puuid("test-puuid", start=0, count=20)

        assert result == mock_match_ids
        assert len(result) == 2

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_match_details_ranked_solo(self, mock_request, riot_client):
        """Test match details retrieval for ranked solo game"""
        mock_match_data = {
            "metadata": {
                "matchId": "EUW1_123456789",
                "participants": ["puuid1", "puuid2"]
            },
            "info": {
                "gameCreation": 1672531200000,  # 2023-01-01 00:00:00 UTC
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
                    }
                ]
            }
        }
        mock_request.return_value = mock_match_data

        result = await riot_client.get_match_details("EUW1_123456789")

        assert result == mock_match_data
        assert result["info"]["queueId"] == 420

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_rank_info_solo_duo(self, mock_request, riot_client):
        """Test rank info retrieval for Solo/Duo queue"""
        mock_rank_data = [
            {
                "queueType": "RANKED_SOLO_5x5",
                "tier": "DIAMOND",
                "rank": "II",
                "leaguePoints": 75,
                "wins": 45,
                "losses": 32
            },
            {
                "queueType": "RANKED_FLEX_SR",
                "tier": "PLATINUM",
                "rank": "I",
                "leaguePoints": 50,
                "wins": 20,
                "losses": 15
            }
        ]
        mock_request.return_value = mock_rank_data

        result = await riot_client.get_rank_info("summoner-id-123")

        assert result is not None
        assert result["tier"] == "DIAMOND"
        assert result["rank"] == "II"
        assert result["lp"] == 75
        assert result["wins"] == 45
        assert result["losses"] == 32

    @patch('app.riot.client.RiotAPIClient._request')
    async def test_get_rank_info_no_solo_duo(self, mock_request, riot_client):
        """Test rank info when no Solo/Duo queue found"""
        mock_rank_data = [
            {
                "queueType": "RANKED_FLEX_SR",
                "tier": "GOLD",
                "rank": "IV",
                "leaguePoints": 25,
                "wins": 10,
                "losses": 8
            }
        ]
        mock_request.return_value = mock_rank_data

        result = await riot_client.get_rank_info("summoner-id-123")

        assert result is None

    @patch('httpx.AsyncClient')
    async def test_request_with_rate_limit_retry(self, mock_client_class, riot_client):
        """Test rate limit handling with retry"""
        # Mock the client and response
        mock_client = mock_client_class.return_value.__aenter__.return_value
        mock_response = mock_client.get.return_value

        # First call returns 429 with Retry-After header
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        mock_response.raise_for_status.side_effect = Exception("429 Client Error")

        # Second call succeeds
        def side_effect(*args, **kwargs):
            if mock_response.status_code == 429:
                mock_response.status_code = 200
                mock_response.headers = {}
                mock_response.raise_for_status.side_effect = None
                mock_response.json.return_value = {"data": "success"}
            return mock_response

        mock_client.get.side_effect = side_effect

        with patch('asyncio.sleep') as mock_sleep:
            result = await riot_client._request("test-url")

        assert result == {"data": "success"}
        assert mock_sleep.called  # Should have waited due to rate limit

    @patch('httpx.AsyncClient')
    async def test_request_max_retries_exceeded(self, mock_client_class, riot_client):
        """Test max retries exceeded"""
        mock_client = mock_client_class.return_value.__aenter__.return_value
        mock_response = mock_client.get.return_value

        # Always return an error
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("500 Server Error")

        with pytest.raises(Exception) as exc_info:
            await riot_client._request("test-url", retries=2)

        # Should contain the original error message
        assert "500 Server Error" in str(exc_info.value)