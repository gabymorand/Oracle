from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.calendar import (
    AvailabilityCreate,
    AvailabilityResponse,
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarEventUpdate,
    CalendarEventWithSeries,
    DayAvailabilitySummary,
    DayDetail,
)
from app.services import calendar_service

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])


# --- Events ---


@router.get("/events", response_model=list[CalendarEventResponse])
async def list_events(
    year: int = Query(..., description="Year (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
):
    """Get all events for a specific month"""
    return calendar_service.get_events_by_month(db, year, month)


@router.get("/events/{event_id}", response_model=CalendarEventWithSeries)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event details with linked draft series"""
    event = calendar_service.get_event_with_series(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=CalendarEventResponse, status_code=201)
async def create_event(event: CalendarEventCreate, db: Session = Depends(get_db)):
    """Create a new calendar event"""
    return calendar_service.create_event(db, event)


@router.patch("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_update: CalendarEventUpdate,
    db: Session = Depends(get_db),
):
    """Update an event"""
    event = calendar_service.update_event(db, event_id, event_update)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    success = calendar_service.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")


# --- Scrims ---


@router.get("/scrims", response_model=list[CalendarEventWithSeries])
async def list_scrims(
    limit: int = Query(50, ge=1, le=200, description="Max number of scrims to return"),
    db: Session = Depends(get_db),
):
    """Get all scrims with draft series info"""
    return calendar_service.get_scrims(db, limit)


# --- Availabilities ---


@router.get("/availabilities", response_model=DayAvailabilitySummary)
async def get_day_availabilities(
    date: date_type = Query(..., description="Date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Get all players' availability for a specific date"""
    return calendar_service.get_day_availabilities(db, date)


@router.get("/availabilities/month", response_model=list[DayAvailabilitySummary])
async def get_month_availabilities(
    year: int = Query(..., description="Year (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
):
    """Get all availabilities for a month (for calendar overview)"""
    return calendar_service.get_month_availabilities(db, year, month)


@router.post(
    "/availabilities/player/{player_id}", response_model=AvailabilityResponse, status_code=201
)
async def set_player_availability(
    player_id: int,
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
):
    """Set a player's availability for a specific date/slot"""
    return calendar_service.set_player_availability(db, player_id, availability)


@router.post("/availabilities/player/{player_id}/bulk", response_model=list[AvailabilityResponse])
async def set_player_availability_bulk(
    player_id: int,
    availabilities: list[AvailabilityCreate],
    db: Session = Depends(get_db),
):
    """Set multiple availability slots at once"""
    return calendar_service.set_player_availability_bulk(db, player_id, availabilities)


@router.delete("/availabilities/{availability_id}", status_code=204)
async def delete_availability(availability_id: int, db: Session = Depends(get_db)):
    """Delete an availability entry"""
    success = calendar_service.delete_availability(db, availability_id)
    if not success:
        raise HTTPException(status_code=404, detail="Availability not found")


# --- Day Detail (combined view) ---


@router.get("/day", response_model=DayDetail)
async def get_day_detail(
    date: date_type = Query(..., description="Date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Get complete day detail: events + availabilities"""
    return calendar_service.get_day_detail(db, date)
