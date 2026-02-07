from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.game import Game
from app.models.player import Player
from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient
from app.schemas.game import (
    GameTagUpdate,
    GameResponse,
    MatchDetailResponse,
    MatchTeam,
    MatchParticipant,
)

router = APIRouter(prefix="/api/v1/games", tags=["games"])
riot_client = RiotAPIClient()


@router.patch("/{game_id}/tag", response_model=GameResponse)
async def update_game_tag(
    game_id: int,
    update: GameTagUpdate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Update game type tag (soloq/competitive) and pentakill status"""
    # Join with RiotAccount and Player to verify team ownership
    game = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(
            Game.id == game_id,
            Player.team_id == team_ctx.team_id,
        )
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if update.game_type is not None:
        game.game_type = update.game_type
    if update.is_pentakill is not None:
        game.is_pentakill = update.is_pentakill

    db.commit()
    db.refresh(game)
    return game


@router.get("/pentakills", response_model=list[GameResponse])
async def get_pentakills(
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get all games with pentakills for the team"""
    games = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(
            Game.is_pentakill == True,
            Player.team_id == team_ctx.team_id,
        )
        .all()
    )
    return games


@router.get("/{game_id}/details", response_model=MatchDetailResponse)
async def get_game_details(
    game_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get full match details from Riot API"""
    # Verify game belongs to team
    game = (
        db.query(Game)
        .join(RiotAccount)
        .join(Player)
        .filter(
            Game.id == game_id,
            Player.team_id == team_ctx.team_id,
        )
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Get all team player accounts with their rank info
    team_accounts = (
        db.query(RiotAccount)
        .join(Player)
        .filter(Player.team_id == team_ctx.team_id)
        .all()
    )

    # Build lookup dict: puuid -> rank info
    team_puuids = set(acc.puuid for acc in team_accounts)
    puuid_to_rank = {
        acc.puuid: {
            "tier": acc.rank_tier,
            "division": acc.rank_division,
            "lp": acc.lp,
        }
        for acc in team_accounts
    }

    # Fetch full match details from Riot API
    try:
        match_data = await riot_client.get_match_details(game.match_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch match from Riot API: {str(e)}")

    # Parse match data
    info = match_data["info"]
    game_duration = info["gameDuration"]
    minutes = game_duration // 60
    seconds = game_duration % 60
    duration_formatted = f"{minutes}:{seconds:02d}"

    # Queue name mapping
    queue_names = {
        420: "Ranked Solo/Duo",
        440: "Ranked Flex",
        400: "Normal Draft",
        430: "Normal Blind",
        450: "ARAM",
    }
    queue_name = queue_names.get(info["queueId"], f"Queue {info['queueId']}")

    # Parse participants into teams
    blue_participants = []
    red_participants = []

    for p in info["participants"]:
        duration_minutes = game_duration / 60
        cs = p["totalMinionsKilled"] + p.get("neutralMinionsKilled", 0)
        deaths = p["deaths"]
        kda = ((p["kills"] + p["assists"]) / deaths) if deaths > 0 else (p["kills"] + p["assists"])

        # Get rank info if this is our player
        puuid = p["puuid"]
        is_our_player = puuid in team_puuids
        rank_info = puuid_to_rank.get(puuid, {}) if is_our_player else {}

        participant = MatchParticipant(
            puuid=puuid,
            summoner_name=p.get("riotIdGameName", p.get("summonerName", "Unknown")),
            tag_line=p.get("riotIdTagline", ""),
            champion_id=p["championId"],
            champion_name=p["championName"],
            team_id=p["teamId"],
            team_position=p["teamPosition"] or "UNKNOWN",
            kills=p["kills"],
            deaths=p["deaths"],
            assists=p["assists"],
            kda=round(kda, 2),
            cs=cs,
            cs_per_min=round(cs / duration_minutes, 1) if duration_minutes > 0 else 0,
            vision_score=p["visionScore"],
            gold_earned=p["goldEarned"],
            damage_dealt=p["totalDamageDealtToChampions"],
            damage_taken=p["totalDamageTaken"],
            summoner_spell1=p["summoner1Id"],
            summoner_spell2=p["summoner2Id"],
            items=[p["item0"], p["item1"], p["item2"], p["item3"], p["item4"], p["item5"], p["item6"]],
            win=p["win"],
            is_our_player=is_our_player,
            rank_tier=rank_info.get("tier"),
            rank_division=rank_info.get("division"),
            rank_lp=rank_info.get("lp"),
        )

        if p["teamId"] == 100:
            blue_participants.append(participant)
        else:
            red_participants.append(participant)

    # Sort participants by role order
    role_order = {"TOP": 0, "JUNGLE": 1, "MIDDLE": 2, "BOTTOM": 3, "UTILITY": 4, "UNKNOWN": 5}
    blue_participants.sort(key=lambda x: role_order.get(x.team_position, 5))
    red_participants.sort(key=lambda x: role_order.get(x.team_position, 5))

    # Get team data
    blue_team_data = next((t for t in info["teams"] if t["teamId"] == 100), None)
    red_team_data = next((t for t in info["teams"] if t["teamId"] == 200), None)

    def get_bans(team_data):
        if not team_data or "bans" not in team_data:
            return []
        return [b["championId"] for b in team_data["bans"] if b["championId"] > 0]

    blue_team = MatchTeam(
        team_id=100,
        win=blue_team_data["win"] if blue_team_data else False,
        bans=get_bans(blue_team_data),
        participants=blue_participants,
        total_kills=sum(p.kills for p in blue_participants),
        total_gold=sum(p.gold_earned for p in blue_participants),
        total_damage=sum(p.damage_dealt for p in blue_participants),
    )

    red_team = MatchTeam(
        team_id=200,
        win=red_team_data["win"] if red_team_data else False,
        bans=get_bans(red_team_data),
        participants=red_participants,
        total_kills=sum(p.kills for p in red_participants),
        total_gold=sum(p.gold_earned for p in red_participants),
        total_damage=sum(p.damage_dealt for p in red_participants),
    )

    return MatchDetailResponse(
        match_id=game.match_id,
        game_date=datetime.fromtimestamp(info["gameCreation"] / 1000),
        game_duration=game_duration,
        game_duration_formatted=duration_formatted,
        queue_id=info["queueId"],
        queue_name=queue_name,
        blue_team=blue_team,
        red_team=red_team,
    )
