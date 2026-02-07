"""Service for parsing raw Riot match JSON and building match detail responses.

Supports two formats:
1. Match V5 (from Riot API): has `info.participants` with flat fields
2. Custom game (from client export): has `participantIdentities` + `participants` with nested `stats`
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.schemas.game import MatchDetailResponse, MatchParticipant, MatchTeam


ROLE_ORDER = {"TOP": 0, "JUNGLE": 1, "MIDDLE": 2, "BOTTOM": 3, "UTILITY": 4, "UNKNOWN": 5}

QUEUE_NAMES = {
    0: "Custom Game",
    420: "Ranked Solo/Duo",
    440: "Ranked Flex",
    400: "Normal Draft",
    430: "Normal Blind",
    450: "ARAM",
    3100: "Custom Game",
}


def _lane_role_to_position(lane: str, role: str) -> str:
    """Convert old-format lane+role to V5 teamPosition."""
    lane = (lane or "").upper()
    role = (role or "").upper()
    if lane == "TOP":
        return "TOP"
    if lane == "JUNGLE":
        return "JUNGLE"
    if lane == "MIDDLE" or lane == "MID":
        return "MIDDLE"
    if lane == "BOTTOM" and role == "CARRY":
        return "BOTTOM"
    if lane == "BOTTOM" and role in ("SUPPORT", "DUO_SUPPORT"):
        return "UTILITY"
    if lane == "BOTTOM":
        return "BOTTOM"
    return "UNKNOWN"


def _normalize_to_v5(raw_json: dict) -> dict:
    """
    Normalize a custom game JSON (old format) into V5-like structure.
    If already V5, returns as-is.
    """
    # Already V5 format (has `info` wrapper with flat participants)
    if "info" in raw_json:
        return raw_json

    # Custom game format: no `info` wrapper, has `participantIdentities`
    if "participantIdentities" not in raw_json or "participants" not in raw_json:
        raise ValueError(
            "Format JSON non reconnu. Attendu: format Match V5 ou export custom game."
        )

    identities = raw_json["participantIdentities"]
    participants_raw = raw_json["participants"]
    teams_raw = raw_json.get("teams", [])

    # Build identity lookup: participantId -> player info
    id_to_player = {}
    for ident in identities:
        pid = ident["participantId"]
        player = ident.get("player", {})
        id_to_player[pid] = player

    # Normalize participants
    normalized_participants = []
    for p in participants_raw:
        pid = p["participantId"]
        player_info = id_to_player.get(pid, {})
        stats = p.get("stats", {})
        timeline = p.get("timeline", {})

        # Map lane+role to teamPosition
        team_position = _lane_role_to_position(
            timeline.get("lane", ""), timeline.get("role", "")
        )

        # stats.win can be boolean already
        win = stats.get("win", False)
        if isinstance(win, str):
            win = win.lower() == "true"

        normalized_participants.append({
            "puuid": player_info.get("puuid", ""),
            "riotIdGameName": player_info.get("gameName", ""),
            "riotIdTagline": player_info.get("tagLine", ""),
            "summonerName": player_info.get("summonerName", ""),
            "championId": p.get("championId", 0),
            "championName": "",  # Not available in old format
            "teamId": p.get("teamId", 0),
            "teamPosition": team_position,
            "kills": stats.get("kills", 0),
            "deaths": stats.get("deaths", 0),
            "assists": stats.get("assists", 0),
            "totalMinionsKilled": stats.get("totalMinionsKilled", 0),
            "neutralMinionsKilled": stats.get("neutralMinionsKilled", 0),
            "visionScore": stats.get("visionScore", 0),
            "goldEarned": stats.get("goldEarned", 0),
            "totalDamageDealtToChampions": stats.get("totalDamageDealtToChampions", 0),
            "totalDamageTaken": stats.get("totalDamageTaken", 0),
            "summoner1Id": p.get("spell1Id", 0),
            "summoner2Id": p.get("spell2Id", 0),
            "item0": stats.get("item0", 0),
            "item1": stats.get("item1", 0),
            "item2": stats.get("item2", 0),
            "item3": stats.get("item3", 0),
            "item4": stats.get("item4", 0),
            "item5": stats.get("item5", 0),
            "item6": stats.get("item6", 0),
            "win": win,
            "pentaKills": stats.get("pentaKills", 0),
        })

    # Normalize teams - win field is "Win"/"Fail" string in old format
    normalized_teams = []
    for t in teams_raw:
        win_val = t.get("win", False)
        if isinstance(win_val, str):
            win_val = win_val.lower() == "win"
        normalized_teams.append({
            "teamId": t.get("teamId", 0),
            "win": win_val,
            "bans": t.get("bans", []),
        })

    # Build V5-like structure
    match_id = str(raw_json.get("gameId", "CUSTOM"))
    return {
        "metadata": {
            "matchId": f"EUW1_{match_id}",
            "participants": [p["puuid"] for p in normalized_participants],
        },
        "info": {
            "gameCreation": raw_json.get("gameCreation", 0),
            "gameDuration": raw_json.get("gameDuration", 0),
            "queueId": raw_json.get("queueId", 0),
            "participants": normalized_participants,
            "teams": normalized_teams,
        },
    }


def parse_match_json(
    match_json: dict,
    team_puuids: set[str],
    blue_side: bool | None = None,
) -> dict:
    """
    Parse raw Riot match JSON (V5 or custom) and identify our team.

    Args:
        match_json: Raw match JSON (V5 or custom format)
        team_puuids: Set of PUUIDs for team players
        blue_side: Fallback side selection if PUUID matching fails.
                   If None and no PUUIDs match, raises ValueError.

    Returns:
        Dict with: blue_side, our_picks, opponent_picks, result, our_team_id
    """
    normalized = _normalize_to_v5(match_json)
    info = normalized.get("info")
    if not info:
        raise ValueError("JSON invalide: champ 'info' manquant")

    participants = info.get("participants", [])
    if len(participants) != 10:
        raise ValueError(
            f"JSON invalide: attendu 10 participants, trouve {len(participants)}"
        )

    teams = info.get("teams", [])
    if len(teams) != 2:
        raise ValueError(f"JSON invalide: attendu 2 equipes, trouve {len(teams)}")

    # Try to identify our team by matching PUUIDs
    blue_count = 0
    red_count = 0
    for p in participants:
        if p.get("puuid") in team_puuids:
            if p["teamId"] == 100:
                blue_count += 1
            else:
                red_count += 1

    if blue_count > 0 or red_count > 0:
        # PUUIDs matched - use that to determine side
        our_team_id = 100 if blue_count >= red_count else 200
        blue_side = our_team_id == 100
    elif blue_side is not None:
        # No PUUIDs matched - use the provided side as fallback
        our_team_id = 100 if blue_side else 200
    else:
        raise ValueError(
            "Aucun joueur de votre equipe n'a ete trouve dans ce match. "
            "Verifiez que les comptes Riot des joueurs sont correctement configures."
        )

    # Extract picks sorted by role
    our_picks = []
    opponent_picks = []
    for p in sorted(
        participants,
        key=lambda x: ROLE_ORDER.get(x.get("teamPosition", "UNKNOWN"), 5),
    ):
        if p["teamId"] == our_team_id:
            our_picks.append(p["championId"])
        else:
            opponent_picks.append(p["championId"])

    # Determine result
    our_team_data = next((t for t in teams if t["teamId"] == our_team_id), None)
    result = "win" if our_team_data and our_team_data.get("win") else "loss"

    return {
        "blue_side": blue_side,
        "our_picks": our_picks,
        "opponent_picks": opponent_picks,
        "result": result,
        "our_team_id": our_team_id,
    }


def build_match_detail_response(
    match_json: dict,
    match_id: str,
    team_puuids: set[str],
    puuid_to_rank: dict[str, dict],
) -> MatchDetailResponse:
    """
    Build a MatchDetailResponse from raw Riot match JSON (V5 or custom format).

    This is the shared logic used by both:
    - GET /api/v1/games/{game_id}/details (SoloQ games)
    - GET /api/v1/draft-series/{series_id}/games/{game_id}/match-details (imported)
    """
    normalized = _normalize_to_v5(match_json)
    info = normalized["info"]
    game_duration = info["gameDuration"]
    minutes = game_duration // 60
    seconds = game_duration % 60
    duration_formatted = f"{minutes}:{seconds:02d}"

    queue_name = QUEUE_NAMES.get(
        info.get("queueId", 0), f"Queue {info.get('queueId', 0)}"
    )

    # Parse participants into teams
    blue_participants = []
    red_participants = []

    for p in info["participants"]:
        duration_minutes = game_duration / 60
        cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
        deaths = p.get("deaths", 0)
        kills = p.get("kills", 0)
        assists = p.get("assists", 0)
        kda = ((kills + assists) / deaths) if deaths > 0 else (kills + assists)

        puuid = p.get("puuid", "")
        is_our_player = puuid in team_puuids and puuid != ""
        rank_info = puuid_to_rank.get(puuid, {}) if is_our_player else {}

        participant = MatchParticipant(
            puuid=puuid,
            summoner_name=p.get("riotIdGameName") or p.get("summonerName") or "Unknown",
            tag_line=p.get("riotIdTagline", ""),
            champion_id=p.get("championId", 0),
            champion_name=p.get("championName", ""),
            team_id=p.get("teamId", 0),
            team_position=p.get("teamPosition") or "UNKNOWN",
            kills=kills,
            deaths=deaths,
            assists=assists,
            kda=round(kda, 2),
            cs=cs,
            cs_per_min=round(cs / duration_minutes, 1) if duration_minutes > 0 else 0,
            vision_score=p.get("visionScore", 0),
            gold_earned=p.get("goldEarned", 0),
            damage_dealt=p.get("totalDamageDealtToChampions", 0),
            damage_taken=p.get("totalDamageTaken", 0),
            summoner_spell1=p.get("summoner1Id", 0),
            summoner_spell2=p.get("summoner2Id", 0),
            items=[
                p.get("item0", 0), p.get("item1", 0), p.get("item2", 0),
                p.get("item3", 0), p.get("item4", 0), p.get("item5", 0),
                p.get("item6", 0),
            ],
            win=p.get("win", False),
            is_our_player=is_our_player,
            rank_tier=rank_info.get("tier"),
            rank_division=rank_info.get("division"),
            rank_lp=rank_info.get("lp"),
        )

        if p.get("teamId") == 100:
            blue_participants.append(participant)
        else:
            red_participants.append(participant)

    # Sort by role order
    blue_participants.sort(key=lambda x: ROLE_ORDER.get(x.team_position, 5))
    red_participants.sort(key=lambda x: ROLE_ORDER.get(x.team_position, 5))

    # Get team data
    blue_team_data = next((t for t in info["teams"] if t["teamId"] == 100), None)
    red_team_data = next((t for t in info["teams"] if t["teamId"] == 200), None)

    def get_bans(team_data):
        if not team_data or "bans" not in team_data:
            return []
        return [
            b["championId"] for b in team_data["bans"] if b.get("championId", 0) > 0
        ]

    def team_win(team_data) -> bool:
        if not team_data:
            return False
        w = team_data.get("win", False)
        if isinstance(w, str):
            return w.lower() == "win"
        return bool(w)

    blue_team = MatchTeam(
        team_id=100,
        win=team_win(blue_team_data),
        bans=get_bans(blue_team_data),
        participants=blue_participants,
        total_kills=sum(p.kills for p in blue_participants),
        total_gold=sum(p.gold_earned for p in blue_participants),
        total_damage=sum(p.damage_dealt for p in blue_participants),
    )

    red_team = MatchTeam(
        team_id=200,
        win=team_win(red_team_data),
        bans=get_bans(red_team_data),
        participants=red_participants,
        total_kills=sum(p.kills for p in red_participants),
        total_gold=sum(p.gold_earned for p in red_participants),
        total_damage=sum(p.damage_dealt for p in red_participants),
    )

    # Convert game date to Paris timezone
    paris_tz = ZoneInfo("Europe/Paris")
    game_creation = info.get("gameCreation", 0)
    if game_creation > 0:
        game_date_utc = datetime.fromtimestamp(game_creation / 1000, tz=timezone.utc)
        game_date_paris = game_date_utc.astimezone(paris_tz)
    else:
        game_date_paris = datetime.now(tz=paris_tz)

    # Use match_id from metadata or parameter
    final_match_id = (
        normalized.get("metadata", {}).get("matchId") or match_id
    )

    return MatchDetailResponse(
        match_id=final_match_id,
        game_date=game_date_paris,
        game_duration=game_duration,
        game_duration_formatted=duration_formatted,
        queue_id=info.get("queueId", 0),
        queue_name=queue_name,
        blue_team=blue_team,
        red_team=red_team,
    )
