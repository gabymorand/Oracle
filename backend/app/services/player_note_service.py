from sqlalchemy.orm import Session

from app.models.player_note import PlayerNote
from app.schemas.player_note import PlayerNoteCreate, PlayerNoteUpdate


def get_player_notes(db: Session, player_id: int) -> list[PlayerNote]:
    return db.query(PlayerNote).filter(PlayerNote.player_id == player_id).all()


def create_note(db: Session, player_id: int, note: PlayerNoteCreate) -> PlayerNote:
    db_note = PlayerNote(
        player_id=player_id,
        author_role=note.author_role,
        note_type=note.note_type,
        content=note.content,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note_update: PlayerNoteUpdate) -> PlayerNote | None:
    db_note = db.query(PlayerNote).filter(PlayerNote.id == note_id).first()
    if not db_note:
        return None

    update_data = note_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int) -> bool:
    db_note = db.query(PlayerNote).filter(PlayerNote.id == note_id).first()
    if not db_note:
        return False

    db.delete(db_note)
    db.commit()
    return True
