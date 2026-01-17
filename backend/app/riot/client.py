import asyncio
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.game import Game


class RiotAPIClient:
    def __init__(self):
        self.api_key = settings.riot_api_key
        self.region = settings.riot_api_region
        self.base_url_europe = "https://europe.api.riotgames.com"
        self.base_url_region = f"https://{self.region}.api.riotgames.com"
        self.headers = {"X-Riot-Token": self.api_key}

    async def _request(self, url: str, retries: int = 3) -> dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(retries):
                try:
                    response = await client.get(url, headers=self.headers, timeout=10.0)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 5))
                        await asyncio.sleep(retry_after)
                        continue
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise ValueError("Resource not found")
                    if attempt == retries - 1:
                        raise
                    await asyncio.sleep(2**attempt)
            raise Exception("Max retries exceeded")

    async def get_puuid_by_riot_id(self, game_name: str, tag_line: str) -> str:
        url = f"{self.base_url_europe}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        data = await self._request(url)
        return data["puuid"]

    async def get_summoner_by_puuid(self, puuid: str) -> dict:
        url = f"{self.base_url_region}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self._request(url)

    async def get_match_ids_by_puuid(self, puuid: str, start: int = 0, count: int = 20) -> list[str]:
        url = f"{self.base_url_europe}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        return await self._request(url)

    async def get_match_details(self, match_id: str) -> dict:
        url = f"{self.base_url_europe}/lol/match/v5/matches/{match_id}"
        return await self._request(url)

    async def fetch_and_store_matches(self, db: Session, riot_account):
        """Fetch recent matches and store in database"""
        try:
            match_ids = await self.get_match_ids_by_puuid(riot_account.puuid, start=0, count=20)

            for match_id in match_ids:
                # Check if match already exists
                existing = db.query(Game).filter(Game.match_id == match_id).first()
                if existing:
                    continue

                # Fetch match details
                match_data = await self.get_match_details(match_id)
                participant = next(
                    (p for p in match_data["info"]["participants"] if p["puuid"] == riot_account.puuid), None
                )

                if not participant:
                    continue

                # Extract stats
                duration_seconds = match_data["info"]["gameDuration"]
                duration_minutes = duration_seconds / 60
                kills = participant["kills"]
                deaths = participant["deaths"]
                assists = participant["assists"]
                kda = ((kills + assists) / deaths) if deaths > 0 else (kills + assists)

                cs = participant["totalMinionsKilled"] + participant.get("neutralMinionsKilled", 0)
                cs_per_min = cs / duration_minutes if duration_minutes > 0 else 0

                gold = participant["goldEarned"]
                gold_per_min = gold / duration_minutes if duration_minutes > 0 else 0

                vision = participant["visionScore"]
                vision_per_min = vision / duration_minutes if duration_minutes > 0 else 0

                team_kills = sum(p["kills"] for p in match_data["info"]["participants"] if p["teamId"] == participant["teamId"])
                kp = ((kills + assists) / team_kills * 100) if team_kills > 0 else 0

                stats = {
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "kda": round(kda, 2),
                    "cs": cs,
                    "cs_per_min": round(cs_per_min, 2),
                    "gold": gold,
                    "gold_per_min": round(gold_per_min, 2),
                    "vision": vision,
                    "vision_per_min": round(vision_per_min, 2),
                    "kp": round(kp, 2),
                    "win": participant["win"],
                }

                game = Game(
                    riot_account_id=riot_account.id,
                    match_id=match_id,
                    game_type="soloq",
                    champion_id=participant["championId"],
                    role=participant["teamPosition"].lower(),
                    stats=stats,
                    game_duration=duration_seconds,
                    game_date=datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000),
                )
                db.add(game)

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
