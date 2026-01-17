from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.player_note import PlayerNoteCreate, PlayerNoteResponse, PlayerNoteUpdate
from app.services import player_note_service

router = APIRouter(prefix="/api/v1", tags=["player_notes"])


@router.get("/players/{player_id}/notes", response_model=list[PlayerNoteResponse])
async def list_player_notes(player_id: int, db: Session = Depends(get_db)):
    return player_note_service.get_player_notes(db, player_id)


@router.post("/players/{player_id}/notes", response_model=PlayerNoteResponse, status_code=201)
async def create_note(player_id: int, note: PlayerNoteCreate, db: Session = Depends(get_db)):
    return player_note_service.create_note(db, player_id, note)


@router.patch("/notes/{note_id}", response_model=PlayerNoteResponse)
async def update_note(note_id: int, note_update: PlayerNoteUpdate, db: Session = Depends(get_db)):
    note = player_note_service.update_note(db, note_id, note_update)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    success = player_note_service.delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
