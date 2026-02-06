from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.draft import DraftGame, DraftSeries
from app.schemas.draft import (
    DraftGameCreate,
    DraftGameResponse,
    DraftSeriesCreate,
    DraftSeriesListResponse,
    DraftSeriesResponse,
    DraftSeriesUpdate,
)
from app.services.draft_import_service import import_draft_from_url

router = APIRouter(prefix="/api/v1/draft-series", tags=["draft-series"])


class DraftImportRequest(BaseModel):
    url: str
    is_blue_side: bool = True


class DraftImportResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/import", response_model=DraftImportResponse)
async def import_draft(request: DraftImportRequest):
    """Import a draft from a URL (draftlol.dawe.gg)"""
    result = await import_draft_from_url(request.url, request.is_blue_side)
    return DraftImportResponse(**result)


class DraftImportDebugResponse(BaseModel):
    url: str
    api_responses: list[dict]
    html_sample: Optional[str] = None
    parsed_result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/import/debug")
async def debug_draft_import(request: DraftImportRequest):
    """Debug endpoint to see what happens when importing a draft"""
    import httpx
    from urllib.parse import urlparse

    debug_info = {
        "url": request.url,
        "api_responses": [],
        "html_sample": None,
        "parsed_result": None,
        "error": None,
    }

    try:
        parsed = urlparse(request.url)
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        draft_id = path_parts[0] if path_parts else None

        debug_info["draft_id"] = draft_id

        async with httpx.AsyncClient() as client:
            # Try various API endpoints
            api_urls = [
                f"https://draftlol.dawe.gg/api/{draft_id}",
                f"https://draftlol.dawe.gg/api/draft/{draft_id}",
                f"https://draftlol.dawe.gg/api/drafts/{draft_id}",
                f"https://draftlol.dawe.gg/api/room/{draft_id}",
            ]

            for api_url in api_urls:
                try:
                    response = await client.get(api_url, timeout=10.0)
                    debug_info["api_responses"].append({
                        "url": api_url,
                        "status": response.status_code,
                        "content_type": response.headers.get("content-type", "unknown"),
                        "body_preview": response.text[:500] if response.text else None,
                    })
                except Exception as e:
                    debug_info["api_responses"].append({
                        "url": api_url,
                        "error": str(e),
                    })

            # Try to fetch the page itself
            try:
                page_response = await client.get(request.url, timeout=10.0)
                debug_info["html_sample"] = page_response.text[:2000] if page_response.text else None
            except Exception as e:
                debug_info["html_error"] = str(e)

        # Try the actual import
        result = await import_draft_from_url(request.url, request.is_blue_side)
        debug_info["parsed_result"] = result

    except Exception as e:
        debug_info["error"] = str(e)

    return debug_info


def update_series_scores(db: Session, series: DraftSeries):
    """Recalculate series scores based on game results"""
    our_score = 0
    opponent_score = 0
    for game in series.games:
        if game.result == "win":
            our_score += 1
        elif game.result == "loss":
            opponent_score += 1

    series.our_score = our_score
    series.opponent_score = opponent_score

    # Determine series result
    if series.format == "bo1":
        if our_score == 1:
            series.result = "win"
        elif opponent_score == 1:
            series.result = "loss"
        else:
            series.result = None
    elif series.format == "bo3":
        if our_score >= 2:
            series.result = "win"
        elif opponent_score >= 2:
            series.result = "loss"
        else:
            series.result = None
    elif series.format == "bo5":
        if our_score >= 3:
            series.result = "win"
        elif opponent_score >= 3:
            series.result = "loss"
        else:
            series.result = None

    db.commit()


@router.get("", response_model=list[DraftSeriesListResponse])
async def list_draft_series(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all draft series"""
    series_list = (
        db.query(DraftSeries)
        .order_by(DraftSeries.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Add games_count to each series
    result = []
    for series in series_list:
        series_dict = {
            "id": series.id,
            "date": series.date,
            "opponent_name": series.opponent_name,
            "format": series.format,
            "our_score": series.our_score,
            "opponent_score": series.opponent_score,
            "result": series.result,
            "notes": series.notes,
            "created_at": series.created_at,
            "games_count": len(series.games),
        }
        result.append(DraftSeriesListResponse(**series_dict))

    return result


@router.get("/with-games", response_model=list[DraftSeriesResponse])
async def list_draft_series_with_games(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all draft series with their games included"""
    series_list = (
        db.query(DraftSeries)
        .order_by(DraftSeries.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return series_list


@router.post("", response_model=DraftSeriesResponse)
async def create_draft_series(
    series_data: DraftSeriesCreate,
    db: Session = Depends(get_db)
):
    """Create a new draft series"""
    series = DraftSeries(
        date=series_data.date,
        opponent_name=series_data.opponent_name,
        format=series_data.format,
        notes=series_data.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(series)
    db.commit()
    db.refresh(series)
    return series


@router.get("/{series_id}", response_model=DraftSeriesResponse)
async def get_draft_series(series_id: int, db: Session = Depends(get_db)):
    """Get a draft series with all its games"""
    series = db.query(DraftSeries).filter(DraftSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Draft series not found")
    return series


@router.patch("/{series_id}", response_model=DraftSeriesResponse)
async def update_draft_series(
    series_id: int,
    series_data: DraftSeriesUpdate,
    db: Session = Depends(get_db)
):
    """Update a draft series"""
    series = db.query(DraftSeries).filter(DraftSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Draft series not found")

    for field, value in series_data.model_dump(exclude_unset=True).items():
        setattr(series, field, value)

    series.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(series)
    return series


@router.delete("/{series_id}")
async def delete_draft_series(series_id: int, db: Session = Depends(get_db)):
    """Delete a draft series and all its games"""
    series = db.query(DraftSeries).filter(DraftSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Draft series not found")

    db.delete(series)
    db.commit()
    return {"message": "Draft series deleted"}


# Game endpoints within a series
@router.post("/{series_id}/games", response_model=DraftGameResponse)
async def add_game_to_series(
    series_id: int,
    game_data: DraftGameCreate,
    db: Session = Depends(get_db)
):
    """Add a game to a draft series"""
    series = db.query(DraftSeries).filter(DraftSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Draft series not found")

    # Check max games based on format
    max_games = {"bo1": 1, "bo3": 3, "bo5": 5}.get(series.format, 1)
    if len(series.games) >= max_games:
        raise HTTPException(
            status_code=400,
            detail=f"Series already has maximum games ({max_games}) for {series.format} format"
        )

    game = DraftGame(
        series_id=series_id,
        game_number=game_data.game_number,
        blue_side=game_data.blue_side,
        our_bans=game_data.our_bans,
        opponent_bans=game_data.opponent_bans,
        our_picks=game_data.our_picks,
        opponent_picks=game_data.opponent_picks,
        pick_order=game_data.pick_order,
        result=game_data.result,
        import_source=game_data.import_source or "manual",
        import_url=game_data.import_url,
        notes=game_data.notes,
        created_at=datetime.utcnow(),
    )
    db.add(game)
    db.commit()

    # Update series scores
    update_series_scores(db, series)

    db.refresh(game)
    return game


@router.patch("/{series_id}/games/{game_id}", response_model=DraftGameResponse)
async def update_game(
    series_id: int,
    game_id: int,
    game_data: DraftGameCreate,
    db: Session = Depends(get_db)
):
    """Update a game in a series"""
    game = (
        db.query(DraftGame)
        .filter(DraftGame.id == game_id, DraftGame.series_id == series_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    for field, value in game_data.model_dump(exclude_unset=True).items():
        setattr(game, field, value)

    db.commit()

    # Update series scores
    series = db.query(DraftSeries).filter(DraftSeries.id == series_id).first()
    update_series_scores(db, series)

    db.refresh(game)
    return game


@router.delete("/{series_id}/games/{game_id}")
async def delete_game(
    series_id: int,
    game_id: int,
    db: Session = Depends(get_db)
):
    """Delete a game from a series"""
    game = (
        db.query(DraftGame)
        .filter(DraftGame.id == game_id, DraftGame.series_id == series_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    series = db.query(DraftSeries).filter(DraftSeries.id == series_id).first()

    db.delete(game)
    db.commit()

    # Update series scores
    update_series_scores(db, series)

    return {"message": "Game deleted"}
