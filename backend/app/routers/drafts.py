from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.draft import DraftCreate, DraftResponse
from app.services import draft_service

router = APIRouter(prefix="/api/v1/drafts", tags=["drafts"])


@router.get("", response_model=list[DraftResponse])
async def list_drafts(db: Session = Depends(get_db)):
    return draft_service.get_all_drafts(db)


@router.post("", response_model=DraftResponse, status_code=201)
async def create_draft(draft: DraftCreate, db: Session = Depends(get_db)):
    return draft_service.create_draft(db, draft)


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: int, db: Session = Depends(get_db)):
    draft = draft_service.get_draft(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@router.delete("/{draft_id}", status_code=204)
async def delete_draft(draft_id: int, db: Session = Depends(get_db)):
    success = draft_service.delete_draft(db, draft_id)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")
