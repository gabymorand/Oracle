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
                    print(f"Riot API HTTP Error: {e.response.status_code} - {e.response.text}")
                    if e.response.status_code == 404:
                        raise ValueError("Resource not found")
                    if e.response.status_code == 401:
                        raise ValueError(f"401 Unauthorized - API key is invalid or expired")
                    if e.response.status_code == 403:
                        raise ValueError(f"403 Forbidden - API key doesn't have required permissions")
                    if attempt == retries - 1:
                        raise ValueError(f"HTTP {e.response.status_code}: {e.response.text}")
                    await asyncio.sleep(2**attempt)
                except Exception as e:
                    print(f"Riot API Request Error: {str(e)}")
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

    async def get_match_ids_by_puuid(self, puuid: str, start: int = 0, count: int = 100) -> list[str]:
        url = f"{self.base_url_europe}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        return await self._request(url)

    async def get_match_details(self, match_id: str) -> dict:
        url = f"{self.base_url_europe}/lol/match/v5/matches/{match_id}"
        return await self._request(url)

    async def get_rank_info(self, summoner_id: str) -> dict:
        """Get ranked info for a summoner by summoner_id (legacy method)"""
        url = f"{self.base_url_region}/lol/league/v4/entries/by-summoner/{summoner_id}"
        data = await self._request(url)
        # Find Solo/Duo queue rank
        for entry in data:
            if entry["queueType"] == "RANKED_SOLO_5x5":
                return {
                    "tier": entry["tier"],  # IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER
                    "rank": entry["rank"],  # I, II, III, IV
                    "lp": entry["leaguePoints"],
                    "wins": entry["wins"],
                    "losses": entry["losses"],
                }
        return None

    async def get_rank_info_by_puuid(self, puuid: str) -> dict:
        """Get ranked info directly by PUUID (preferred method with new API keys)"""
        url = f"{self.base_url_region}/lol/league/v4/entries/by-puuid/{puuid}"
        data = await self._request(url)
        # Find Solo/Duo queue rank
        for entry in data:
            if entry["queueType"] == "RANKED_SOLO_5x5":
                return {
                    "tier": entry["tier"],
                    "rank": entry["rank"],
                    "lp": entry["leaguePoints"],
                    "wins": entry["wins"],
                    "losses": entry["losses"],
                }
        return None

    async def fetch_and_update_rank(self, db: Session, riot_account):
        """Fetch and update rank information for a riot account"""
        from app.models.rank_history import RankHistory

        print(f"Starting rank update for {riot_account.summoner_name}#{riot_account.tag_line}")
        
        # Store old values for history comparison
        old_tier = riot_account.rank_tier
        old_division = riot_account.rank_division
        old_lp = riot_account.lp
        
        try:
            # Check if PUUID looks like a fallback (not a real Riot PUUID)
            # Real PUUIDs are 78 chars and contain specific patterns
            puuid = riot_account.puuid
            
            # If PUUID doesn't look valid or API returns error, try to fetch real PUUID
            try:
                print(f"Fetching rank info directly by PUUID: {puuid}")
                rank_info = await self.get_rank_info_by_puuid(puuid)
            except ValueError as e:
                if "400" in str(e) or "decrypting" in str(e).lower():
                    # PUUID is invalid - fetch the real one
                    print(f"PUUID appears invalid, fetching real PUUID for {riot_account.summoner_name}#{riot_account.tag_line}")
                    try:
                        real_puuid = await self.get_puuid_by_riot_id(riot_account.summoner_name, riot_account.tag_line)
                        print(f"Got real PUUID: {real_puuid}")
                        riot_account.puuid = real_puuid
                        db.commit()
                        puuid = real_puuid
                        rank_info = await self.get_rank_info_by_puuid(puuid)
                    except Exception as e2:
                        raise ValueError(f"Failed to fetch real PUUID: {str(e2)}")
                else:
                    raise
            
            print(f"Rank info result: {rank_info}")

            if rank_info:
                # Update current rank
                riot_account.rank_tier = rank_info["tier"]
                riot_account.rank_division = rank_info["rank"]
                riot_account.lp = rank_info["lp"]
                riot_account.wins = rank_info["wins"]
                riot_account.losses = rank_info["losses"]

                print(f"Updated rank: {riot_account.rank_tier} {riot_account.rank_division} {riot_account.lp} LP")

                # Update peak rank if this is higher
                def rank_value(tier, division, lp):
                    """Convert rank to comparable number"""
                    tier_values = {
                        "IRON": 0, "BRONZE": 1, "SILVER": 2, "GOLD": 3,
                        "PLATINUM": 4, "EMERALD": 5, "DIAMOND": 6,
                        "MASTER": 7, "GRANDMASTER": 8, "CHALLENGER": 9
                    }
                    division_values = {"IV": 0, "III": 1, "II": 2, "I": 3}
                    base = tier_values.get(tier, 0) * 400
                    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
                        return base + lp
                    return base + division_values.get(division, 0) * 100 + lp

                current_value = rank_value(rank_info["tier"], rank_info["rank"], rank_info["lp"])

                if riot_account.peak_tier:
                    peak_value = rank_value(riot_account.peak_tier, riot_account.peak_division, riot_account.peak_lp)
                    if current_value > peak_value:
                        riot_account.peak_tier = rank_info["tier"]
                        riot_account.peak_division = rank_info["rank"]
                        riot_account.peak_lp = rank_info["lp"]
                else:
                    riot_account.peak_tier = rank_info["tier"]
                    riot_account.peak_division = rank_info["rank"]
                    riot_account.peak_lp = rank_info["lp"]

                # Store in history if rank changed
                if (old_tier != rank_info["tier"] or
                    old_division != rank_info["rank"] or
                    old_lp != rank_info["lp"]):
                    history_entry = RankHistory(
                        riot_account_id=riot_account.id,
                        tier=rank_info["tier"],
                        division=rank_info["rank"],
                        lp=rank_info["lp"],
                        wins=rank_info["wins"],
                        losses=rank_info["losses"],
                    )
                    db.add(history_entry)

                db.commit()
                print(f"Updated rank for {riot_account.summoner_name}: {rank_info['tier']} {rank_info['rank']} {rank_info['lp']} LP")
            else:
                print(f"No ranked data found for {riot_account.summoner_name}")

        except Exception as e:
            print(f"Failed to update rank: {str(e)}")
            db.rollback()
            raise  # Re-raise the exception so frontend can handle it

    async def fetch_and_store_matches(self, db: Session, riot_account):
        """Fetch recent matches and store in database"""
        from datetime import datetime

        # Season 26 start date: 2026-01-09 00:00:00 UTC
        SEASON_26_START = datetime(2026, 1, 9, 0, 0, 0)

        try:
            match_ids = await self.get_match_ids_by_puuid(riot_account.puuid, start=0, count=100)

            for match_id in match_ids:
                # Check if match already exists
                existing = db.query(Game).filter(Game.match_id == match_id).first()
                if existing:
                    continue

                # Fetch match details
                match_data = await self.get_match_details(match_id)

                # Filter: Only Ranked Solo/Duo (queueId 420)
                queue_id = match_data["info"]["queueId"]
                if queue_id != 420:
                    print(f"Skipping match {match_id} - queueId {queue_id} is not Ranked Solo/Duo (420)")
                    continue

                # Filter: Only Season 26 games (from 2026-01-09)
                game_timestamp = match_data["info"]["gameCreation"] / 1000  # Convert ms to seconds
                game_date = datetime.fromtimestamp(game_timestamp)
                if game_date < SEASON_26_START:
                    print(f"Skipping match {match_id} - game date {game_date} is before Season 26 (2026-01-09)")
                    continue

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

                # Check for pentakill
                is_pentakill = participant.get("pentaKills", 0) > 0

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
                    "queue_id": queue_id,
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
                    is_pentakill=is_pentakill,
                )
                db.add(game)

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
