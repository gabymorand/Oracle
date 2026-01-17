from sqlalchemy.orm import Session

from app.models.draft import Draft
from app.schemas.draft import DraftCreate


def get_all_drafts(db: Session) -> list[Draft]:
    return db.query(Draft).order_by(Draft.date.desc()).all()


def get_draft(db: Session, draft_id: int) -> Draft | None:
    return db.query(Draft).filter(Draft.id == draft_id).first()


def create_draft(db: Session, draft: DraftCreate) -> Draft:
    db_draft = Draft(
        date=draft.date,
        opponent_name=draft.opponent_name,
        blue_side=draft.blue_side,
        picks=draft.picks,
        bans=draft.bans,
        result=draft.result,
        notes=draft.notes,
    )
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


def delete_draft(db: Session, draft_id: int) -> bool:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return False

    db.delete(db_draft)
    db.commit()
    return True
