from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import TeamContext, get_current_team
from app.models.player import Player
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
from app.services import email_service

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])


class SendInvitationRequest(BaseModel):
    player_ids: list[int] | None = None  # If None, send to all players with email


class SendInvitationResponse(BaseModel):
    sent_to: list[str]
    failed: list[str]
    smtp_configured: bool


# --- Events ---


@router.get("/events", response_model=list[CalendarEventResponse])
async def list_events(
    year: int = Query(..., description="Year (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get all events for a specific month"""
    return calendar_service.get_events_by_month(db, team_ctx.team_id, year, month)


@router.get("/events/{event_id}", response_model=CalendarEventWithSeries)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get event details with linked draft series"""
    event = calendar_service.get_event_with_series(db, team_ctx.team_id, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=CalendarEventResponse, status_code=201)
async def create_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Create a new calendar event"""
    return calendar_service.create_event(db, team_ctx.team_id, event)


@router.patch("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_update: CalendarEventUpdate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Update an event"""
    event = calendar_service.update_event(db, team_ctx.team_id, event_id, event_update)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Delete an event"""
    success = calendar_service.delete_event(db, team_ctx.team_id, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")


# --- Scrims ---


@router.get("/scrims", response_model=list[CalendarEventWithSeries])
async def list_scrims(
    limit: int = Query(50, ge=1, le=200, description="Max number of scrims to return"),
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get all scrims with draft series info"""
    return calendar_service.get_scrims(db, team_ctx.team_id, limit)


# --- Availabilities ---


@router.get("/availabilities", response_model=DayAvailabilitySummary)
async def get_day_availabilities(
    date: date_type = Query(..., description="Date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get all players' availability for a specific date"""
    return calendar_service.get_day_availabilities(db, team_ctx.team_id, date)


@router.get("/availabilities/month", response_model=list[DayAvailabilitySummary])
async def get_month_availabilities(
    year: int = Query(..., description="Year (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get all availabilities for a month (for calendar overview)"""
    return calendar_service.get_month_availabilities(db, team_ctx.team_id, year, month)


@router.post(
    "/availabilities/player/{player_id}", response_model=AvailabilityResponse, status_code=201
)
async def set_player_availability(
    player_id: int,
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Set a player's availability for a specific date/slot"""
    return calendar_service.set_player_availability(db, team_ctx.team_id, player_id, availability)


@router.post("/availabilities/player/{player_id}/bulk", response_model=list[AvailabilityResponse])
async def set_player_availability_bulk(
    player_id: int,
    availabilities: list[AvailabilityCreate],
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Set multiple availability slots at once"""
    return calendar_service.set_player_availability_bulk(
        db, team_ctx.team_id, player_id, availabilities
    )


@router.delete("/availabilities/{availability_id}", status_code=204)
async def delete_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Delete an availability entry"""
    success = calendar_service.delete_availability(db, team_ctx.team_id, availability_id)
    if not success:
        raise HTTPException(status_code=404, detail="Availability not found")


# --- Day Detail (combined view) ---


@router.get("/day", response_model=DayDetail)
async def get_day_detail(
    date: date_type = Query(..., description="Date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Get complete day detail: events + availabilities"""
    return calendar_service.get_day_detail(db, team_ctx.team_id, date)


# --- Calendar Invitations ---


@router.get("/smtp-status")
async def get_smtp_status():
    """Check if SMTP is configured for sending invitations"""
    return {"configured": email_service.is_smtp_configured()}


@router.post("/events/{event_id}/send-invitation", response_model=SendInvitationResponse)
async def send_event_invitation(
    event_id: int,
    request: SendInvitationRequest,
    db: Session = Depends(get_db),
    team_ctx: TeamContext = Depends(get_current_team),
):
    """Send calendar invitation to players for an event"""
    # Check SMTP config
    if not email_service.is_smtp_configured():
        return SendInvitationResponse(
            sent_to=[],
            failed=[],
            smtp_configured=False,
        )

    # Get the event
    event = calendar_service.get_event(db, team_ctx.team_id, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get players to invite
    if request.player_ids:
        players = (
            db.query(Player)
            .filter(
                Player.team_id == team_ctx.team_id,
                Player.id.in_(request.player_ids),
                Player.email.isnot(None),
                Player.email != "",
            )
            .all()
        )
    else:
        # Get all players with email
        players = (
            db.query(Player)
            .filter(
                Player.team_id == team_ctx.team_id,
                Player.email.isnot(None),
                Player.email != "",
            )
            .all()
        )

    if not players:
        return SendInvitationResponse(
            sent_to=[],
            failed=["No players with email addresses found"],
            smtp_configured=True,
        )

    # Get event times
    start_time, end_time = email_service.get_slot_times(event.date.isoformat(), event.slot)

    # If event has specific times, use those
    if event.start_time:
        start_time = start_time.replace(
            hour=int(event.start_time.split(":")[0]),
            minute=int(event.start_time.split(":")[1]) if ":" in event.start_time else 0,
        )
    if event.end_time:
        end_time = end_time.replace(
            hour=int(event.end_time.split(":")[0]),
            minute=int(event.end_time.split(":")[1]) if ":" in event.end_time else 0,
        )

    # Prepare email content
    event_type_labels = {
        "scrim": "Scrim",
        "training": "Training",
        "official_match": "Official Match",
        "meeting": "Meeting",
        "other": "Event",
    }
    event_type_label = event_type_labels.get(event.event_type, "Event")

    subject = f"[Oracle] {event_type_label}: {event.title}"

    body = f"""You are invited to: {event.title}

Type: {event_type_label}
Date: {event.date}
Time: {event.slot.capitalize()}"""

    if event.opponent_name:
        body += f"\nOpponent: {event.opponent_name}"
    if event.location:
        body += f"\nLocation: {event.location}"
    if event.description:
        body += f"\n\nDescription:\n{event.description}"

    body += "\n\n---\nSent via Oracle Coaching Platform"

    # Send invitations
    emails = [p.email for p in players]
    sent_to = []
    failed = []

    success = email_service.send_calendar_invitation(
        to_emails=emails,
        subject=subject,
        body=body,
        event_title=event.title,
        event_description=event.description or f"{event_type_label} - {event.title}",
        event_start=start_time,
        event_end=end_time,
        event_location=event.location or "",
    )

    if success:
        sent_to = emails
    else:
        failed = emails

    return SendInvitationResponse(
        sent_to=sent_to,
        failed=failed,
        smtp_configured=True,
    )
