from sqlalchemy.orm import Session

from app.models.coach import Coach
from app.schemas.coach import CoachCreate, CoachUpdate


def get_all_coaches(db: Session, team_id: int) -> list[Coach]:
    return db.query(Coach).filter(Coach.team_id == team_id).all()


def get_coach(db: Session, team_id: int, coach_id: int) -> Coach | None:
    return db.query(Coach).filter(
        Coach.id == coach_id,
        Coach.team_id == team_id,
    ).first()


def get_coach_by_name(db: Session, team_id: int, name: str) -> Coach | None:
    return db.query(Coach).filter(
        Coach.name == name,
        Coach.team_id == team_id,
    ).first()


def create_coach(db: Session, team_id: int, coach: CoachCreate) -> Coach:
    db_coach = Coach(name=coach.name, role=coach.role, team_id=team_id)
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    return db_coach


def update_coach(db: Session, team_id: int, coach_id: int, coach_update: CoachUpdate) -> Coach | None:
    db_coach = get_coach(db, team_id, coach_id)
    if not db_coach:
        return None

    update_data = coach_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_coach, field, value)

    db.commit()
    db.refresh(db_coach)
    return db_coach


def delete_coach(db: Session, team_id: int, coach_id: int) -> bool:
    db_coach = get_coach(db, team_id, coach_id)
    if not db_coach:
        return False

    db.delete(db_coach)
    db.commit()
    return True
