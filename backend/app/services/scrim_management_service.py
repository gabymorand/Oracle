from datetime import date as date_type

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.calendar import CalendarEvent
from app.models.scrim_management import OpponentTeam, ScoutedPlayer, ScrimReview
from app.schemas.scrim_management import (
    OpponentTeamCreate,
    OpponentTeamUpdate,
    OpponentTeamWithStats,
    ScoutedPlayerCreate,
    ScoutedPlayerUpdate,
    ScoutedPlayerWithTeam,
    ScrimHistoryItem,
    ScrimManagementDashboard,
    ScrimReviewCreate,
    ScrimReviewUpdate,
    ScrimReviewWithTeam,
)


# --- Opponent Teams ---


def get_opponent_teams(db: Session, skip: int = 0, limit: int = 100) -> list[OpponentTeam]:
    return db.query(OpponentTeam).order_by(OpponentTeam.name).offset(skip).limit(limit).all()


def get_opponent_team(db: Session, team_id: int) -> OpponentTeam | None:
    return db.query(OpponentTeam).filter(OpponentTeam.id == team_id).first()


def get_opponent_team_by_name(db: Session, name: str) -> OpponentTeam | None:
    return db.query(OpponentTeam).filter(func.lower(OpponentTeam.name) == name.lower()).first()


def create_opponent_team(db: Session, team: OpponentTeamCreate) -> OpponentTeam:
    db_team = OpponentTeam(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def update_opponent_team(
    db: Session, team_id: int, team_update: OpponentTeamUpdate
) -> OpponentTeam | None:
    db_team = get_opponent_team(db, team_id)
    if not db_team:
        return None
    update_data = team_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_team, key, value)
    db.commit()
    db.refresh(db_team)
    return db_team


def delete_opponent_team(db: Session, team_id: int) -> bool:
    db_team = get_opponent_team(db, team_id)
    if not db_team:
        return False
    db.delete(db_team)
    db.commit()
    return True


def get_opponent_team_with_stats(db: Session, team_id: int) -> OpponentTeamWithStats | None:
    team = get_opponent_team(db, team_id)
    if not team:
        return None

    # Get scrim reviews for this team
    reviews = db.query(ScrimReview).filter(ScrimReview.opponent_team_id == team_id).all()

    # Calculate stats
    total_scrims = len(reviews)
    quality_values = {"excellent": 5, "good": 4, "average": 3, "poor": 2, "bad": 1}
    avg_quality = None
    if reviews:
        avg_quality = sum(quality_values.get(r.quality, 3) for r in reviews) / len(reviews)

    scouted_count = (
        db.query(ScoutedPlayer).filter(ScoutedPlayer.team_id == team_id).count()
    )

    return OpponentTeamWithStats(
        id=team.id,
        name=team.name,
        contact_name=team.contact_name,
        contact_discord=team.contact_discord,
        contact_email=team.contact_email,
        contact_twitter=team.contact_twitter,
        notes=team.notes,
        created_at=team.created_at,
        updated_at=team.updated_at,
        total_scrims=total_scrims,
        wins=0,  # TODO: Calculate from draft series
        losses=0,
        avg_quality=avg_quality,
        scouted_players_count=scouted_count,
    )


def get_all_teams_with_stats(db: Session) -> list[OpponentTeamWithStats]:
    teams = get_opponent_teams(db, limit=500)
    return [get_opponent_team_with_stats(db, t.id) for t in teams if t]


# --- Scrim Reviews ---


def get_scrim_reviews(db: Session, skip: int = 0, limit: int = 100) -> list[ScrimReview]:
    return (
        db.query(ScrimReview)
        .order_by(ScrimReview.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_scrim_review(db: Session, review_id: int) -> ScrimReview | None:
    return db.query(ScrimReview).filter(ScrimReview.id == review_id).first()


def get_scrim_review_by_event(db: Session, event_id: int) -> ScrimReview | None:
    return db.query(ScrimReview).filter(ScrimReview.calendar_event_id == event_id).first()


def create_scrim_review(db: Session, review: ScrimReviewCreate) -> ScrimReview:
    db_review = ScrimReview(**review.model_dump())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_scrim_review(
    db: Session, review_id: int, review_update: ScrimReviewUpdate
) -> ScrimReview | None:
    db_review = get_scrim_review(db, review_id)
    if not db_review:
        return None
    update_data = review_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review


def delete_scrim_review(db: Session, review_id: int) -> bool:
    db_review = get_scrim_review(db, review_id)
    if not db_review:
        return False
    db.delete(db_review)
    db.commit()
    return True


def get_scrim_review_with_team(db: Session, review_id: int) -> ScrimReviewWithTeam | None:
    review = get_scrim_review(db, review_id)
    if not review:
        return None

    team_name = None
    if review.opponent_team_id:
        team = get_opponent_team(db, review.opponent_team_id)
        if team:
            team_name = team.name

    return ScrimReviewWithTeam(
        id=review.id,
        calendar_event_id=review.calendar_event_id,
        opponent_team_id=review.opponent_team_id,
        quality=review.quality,
        punctuality=review.punctuality,
        communication=review.communication,
        competitiveness=review.competitiveness,
        would_scrim_again=review.would_scrim_again,
        notes=review.notes,
        created_at=review.created_at,
        updated_at=review.updated_at,
        opponent_team_name=team_name,
    )


# --- Scouted Players ---


def get_scouted_players(
    db: Session, skip: int = 0, limit: int = 100, prospects_only: bool = False
) -> list[ScoutedPlayer]:
    query = db.query(ScoutedPlayer)
    if prospects_only:
        query = query.filter(ScoutedPlayer.is_prospect == 1)
    return query.order_by(ScoutedPlayer.rating.desc().nullslast()).offset(skip).limit(limit).all()


def get_scouted_player(db: Session, player_id: int) -> ScoutedPlayer | None:
    return db.query(ScoutedPlayer).filter(ScoutedPlayer.id == player_id).first()


def get_scouted_players_by_team(db: Session, team_id: int) -> list[ScoutedPlayer]:
    return (
        db.query(ScoutedPlayer)
        .filter(ScoutedPlayer.team_id == team_id)
        .order_by(ScoutedPlayer.rating.desc().nullslast())
        .all()
    )


def create_scouted_player(db: Session, player: ScoutedPlayerCreate) -> ScoutedPlayer:
    db_player = ScoutedPlayer(
        summoner_name=player.summoner_name,
        tag_line=player.tag_line,
        team_id=player.team_id,
        role=player.role,
        rating=player.rating,
        mechanical_skill=player.mechanical_skill,
        game_sense=player.game_sense,
        communication=player.communication,
        attitude=player.attitude,
        potential=player.potential.value if player.potential else None,
        notes=player.notes,
        is_prospect=1 if player.is_prospect else 0,
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def update_scouted_player(
    db: Session, player_id: int, player_update: ScoutedPlayerUpdate
) -> ScoutedPlayer | None:
    db_player = get_scouted_player(db, player_id)
    if not db_player:
        return None
    update_data = player_update.model_dump(exclude_unset=True)
    if "is_prospect" in update_data:
        update_data["is_prospect"] = 1 if update_data["is_prospect"] else 0
    if "potential" in update_data and update_data["potential"]:
        update_data["potential"] = update_data["potential"].value
    for key, value in update_data.items():
        setattr(db_player, key, value)
    db.commit()
    db.refresh(db_player)
    return db_player


def delete_scouted_player(db: Session, player_id: int) -> bool:
    db_player = get_scouted_player(db, player_id)
    if not db_player:
        return False
    db.delete(db_player)
    db.commit()
    return True


def get_scouted_player_with_team(db: Session, player_id: int) -> ScoutedPlayerWithTeam | None:
    player = get_scouted_player(db, player_id)
    if not player:
        return None

    team_name = None
    if player.team_id:
        team = get_opponent_team(db, player.team_id)
        if team:
            team_name = team.name

    return ScoutedPlayerWithTeam(
        id=player.id,
        summoner_name=player.summoner_name,
        tag_line=player.tag_line,
        team_id=player.team_id,
        role=player.role,
        rating=player.rating,
        mechanical_skill=player.mechanical_skill,
        game_sense=player.game_sense,
        communication=player.communication,
        attitude=player.attitude,
        potential=player.potential,
        notes=player.notes,
        is_prospect=player.is_prospect == 1,
        created_at=player.created_at,
        updated_at=player.updated_at,
        team_name=team_name,
    )


# --- Dashboard ---


def get_scrim_history(db: Session, limit: int = 50) -> list[ScrimHistoryItem]:
    """Get recent scrims with reviews and results"""
    scrims = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.event_type == "scrim")
        .order_by(CalendarEvent.date.desc())
        .limit(limit)
        .all()
    )

    history = []
    for scrim in scrims:
        review = get_scrim_review_by_event(db, scrim.id)

        # Get draft series result if linked
        draft_result = None
        our_score = None
        opponent_score = None
        if scrim.draft_series_id:
            from app.models.draft import DraftSeries

            series = db.query(DraftSeries).filter(DraftSeries.id == scrim.draft_series_id).first()
            if series:
                draft_result = series.result
                our_score = series.our_score
                opponent_score = series.opponent_score

        history.append(
            ScrimHistoryItem(
                event_id=scrim.id,
                title=scrim.title,
                date=str(scrim.date),
                slot=scrim.slot,
                opponent_name=scrim.opponent_name,
                opponent_team_id=review.opponent_team_id if review else None,
                review=review,
                draft_series_result=draft_result,
                our_score=our_score,
                opponent_score=opponent_score,
            )
        )

    return history


def get_manager_dashboard(db: Session) -> ScrimManagementDashboard:
    """Get aggregated dashboard data for managers"""
    total_scrims = (
        db.query(CalendarEvent).filter(CalendarEvent.event_type == "scrim").count()
    )
    reviewed_scrims = db.query(ScrimReview).count()
    total_teams = db.query(OpponentTeam).count()
    total_scouted = db.query(ScoutedPlayer).count()
    prospects = db.query(ScoutedPlayer).filter(ScoutedPlayer.is_prospect == 1).count()

    recent = get_scrim_history(db, limit=10)
    top_teams = get_all_teams_with_stats(db)[:5]

    return ScrimManagementDashboard(
        total_scrims=total_scrims,
        reviewed_scrims=reviewed_scrims,
        total_teams=total_teams,
        total_scouted_players=total_scouted,
        prospects_count=prospects,
        recent_scrims=recent,
        top_teams=top_teams,
    )
