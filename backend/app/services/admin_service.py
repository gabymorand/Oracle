from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.coach import Coach
from app.models.draft import DraftSeries
from app.models.calendar import CalendarEvent
from app.models.player import Player
from app.models.team import Team
from app.schemas.admin import (
    AdminDashboard,
    CoachSummary,
    PlayerSummary,
    TeamCreate,
    TeamDetails,
    TeamStats,
    TeamUpdate,
)


def get_dashboard(db: Session) -> AdminDashboard:
    """Get admin dashboard with all teams and stats"""
    teams = db.query(Team).all()

    team_stats = []
    for team in teams:
        players_count = db.query(Player).filter(Player.team_id == team.id).count()
        coaches_count = db.query(Coach).filter(Coach.team_id == team.id).count()
        drafts_count = db.query(DraftSeries).filter(DraftSeries.team_id == team.id).count()
        events_count = db.query(CalendarEvent).filter(CalendarEvent.team_id == team.id).count()

        team_stats.append(
            TeamStats(
                id=team.id,
                name=team.name,
                access_code=team.access_code,
                players_count=players_count,
                coaches_count=coaches_count,
                drafts_count=drafts_count,
                events_count=events_count,
                created_at=team.created_at,
            )
        )

    total_players = db.query(Player).count()
    total_coaches = db.query(Coach).count()
    total_drafts = db.query(DraftSeries).count()

    return AdminDashboard(
        total_teams=len(teams),
        total_players=total_players,
        total_coaches=total_coaches,
        total_drafts=total_drafts,
        teams=team_stats,
    )


def get_team_details(db: Session, team_id: int) -> TeamDetails | None:
    """Get detailed info about a specific team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return None

    players = db.query(Player).filter(Player.team_id == team_id).all()
    coaches = db.query(Coach).filter(Coach.team_id == team_id).all()

    player_summaries = [
        PlayerSummary(
            id=p.id,
            summoner_name=p.summoner_name,
            role=p.role,
            riot_accounts_count=len(p.riot_accounts),
        )
        for p in players
    ]

    coach_summaries = [
        CoachSummary(
            id=c.id,
            name=c.name,
            role=c.role,
        )
        for c in coaches
    ]

    return TeamDetails(
        id=team.id,
        name=team.name,
        access_code=team.access_code,
        created_at=team.created_at,
        players=player_summaries,
        coaches=coach_summaries,
    )


def create_team(db: Session, team_data: TeamCreate) -> Team:
    """Create a new team"""
    team = Team(
        name=team_data.name,
        access_code=team_data.access_code,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def update_team(db: Session, team_id: int, team_data: TeamUpdate) -> Team | None:
    """Update a team's name or access code"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return None

    if team_data.name is not None:
        team.name = team_data.name
    if team_data.access_code is not None:
        team.access_code = team_data.access_code

    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, team_id: int) -> bool:
    """Delete a team and all its data (cascade)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return False

    db.delete(team)
    db.commit()
    return True


def delete_player(db: Session, player_id: int) -> bool:
    """Delete a player from any team"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return False

    db.delete(player)
    db.commit()
    return True


def delete_coach(db: Session, coach_id: int) -> bool:
    """Delete a coach from any team"""
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        return False

    db.delete(coach)
    db.commit()
    return True


def check_access_code_available(db: Session, access_code: str, exclude_team_id: int | None = None) -> bool:
    """Check if an access code is available"""
    query = db.query(Team).filter(Team.access_code == access_code)
    if exclude_team_id:
        query = query.filter(Team.id != exclude_team_id)
    return query.first() is None
