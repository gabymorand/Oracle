from calendar import monthrange
from datetime import date as date_type
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.calendar import CalendarEvent, PlayerAvailability
from app.models.draft import DraftSeries
from app.models.player import Player
from app.schemas.calendar import (
    AvailabilityCreate,
    CalendarEventCreate,
    CalendarEventUpdate,
    DayAvailabilitySummary,
    DayDetail,
    DraftSeriesInfo,
    PlayerAvailabilitySummary,
)


# --- Events ---


def get_events_by_month(db: Session, team_id: int, year: int, month: int) -> list[CalendarEvent]:
    """Get all events for a specific month"""
    start_date = date_type(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date_type(year, month, last_day)

    return (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.team_id == team_id,
            CalendarEvent.date >= start_date,
            CalendarEvent.date <= end_date,
        )
        .order_by(CalendarEvent.date, CalendarEvent.slot)
        .all()
    )


def get_events_by_date(db: Session, team_id: int, date: date_type) -> list[CalendarEvent]:
    """Get all events for a specific date"""
    return (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.team_id == team_id,
            CalendarEvent.date == date,
        )
        .order_by(CalendarEvent.slot)
        .all()
    )


def get_event(db: Session, team_id: int, event_id: int) -> CalendarEvent | None:
    """Get event by ID"""
    return db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.team_id == team_id,
    ).first()


def get_event_with_series(db: Session, team_id: int, event_id: int) -> dict | None:
    """Get event with draft series info"""
    event = get_event(db, team_id, event_id)
    if not event:
        return None

    result = {
        "id": event.id,
        "title": event.title,
        "event_type": event.event_type,
        "date": event.date,
        "slot": event.slot,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "draft_series_id": event.draft_series_id,
        "opponent_name": event.opponent_name,
        "opponent_players": event.opponent_players,
        "description": event.description,
        "location": event.location,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
        "draft_series_info": None,
    }

    if event.draft_series_id:
        series = db.query(DraftSeries).filter(
            DraftSeries.id == event.draft_series_id,
            DraftSeries.team_id == team_id,
        ).first()
        if series:
            result["draft_series_info"] = DraftSeriesInfo(
                id=series.id,
                opponent_name=series.opponent_name,
                format=series.format,
                our_score=series.our_score,
                opponent_score=series.opponent_score,
                result=series.result,
            )

    return result


def create_event(db: Session, team_id: int, event_data: CalendarEventCreate) -> CalendarEvent:
    """Create a new calendar event"""
    event = CalendarEvent(
        team_id=team_id,
        title=event_data.title,
        event_type=event_data.event_type.value,
        date=event_data.date,
        slot=event_data.slot.value,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        draft_series_id=event_data.draft_series_id,
        opponent_name=event_data.opponent_name,
        opponent_players=event_data.opponent_players,
        description=event_data.description,
        location=event_data.location,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(
    db: Session, team_id: int, event_id: int, event_update: CalendarEventUpdate
) -> CalendarEvent | None:
    """Update an event"""
    event = get_event(db, team_id, event_id)
    if not event:
        return None

    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None and hasattr(value, "value"):
            # Handle enum values
            setattr(event, field, value.value)
        else:
            setattr(event, field, value)

    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, team_id: int, event_id: int) -> bool:
    """Delete an event"""
    event = get_event(db, team_id, event_id)
    if not event:
        return False

    db.delete(event)
    db.commit()
    return True


def get_scrims(db: Session, team_id: int, limit: int = 50) -> list[dict]:
    """Get all scrims with draft series info"""
    scrims = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.team_id == team_id,
            CalendarEvent.event_type == "scrim",
        )
        .order_by(CalendarEvent.date.desc())
        .limit(limit)
        .all()
    )

    results = []
    for scrim in scrims:
        scrim_dict = {
            "id": scrim.id,
            "title": scrim.title,
            "event_type": scrim.event_type,
            "date": scrim.date,
            "slot": scrim.slot,
            "start_time": scrim.start_time,
            "end_time": scrim.end_time,
            "draft_series_id": scrim.draft_series_id,
            "opponent_name": scrim.opponent_name,
            "opponent_players": scrim.opponent_players,
            "description": scrim.description,
            "location": scrim.location,
            "created_at": scrim.created_at,
            "updated_at": scrim.updated_at,
            "draft_series_info": None,
        }

        if scrim.draft_series_id:
            series = db.query(DraftSeries).filter(
                DraftSeries.id == scrim.draft_series_id,
                DraftSeries.team_id == team_id,
            ).first()
            if series:
                scrim_dict["draft_series_info"] = {
                    "id": series.id,
                    "opponent_name": series.opponent_name,
                    "format": series.format,
                    "our_score": series.our_score,
                    "opponent_score": series.opponent_score,
                    "result": series.result,
                }

        results.append(scrim_dict)

    return results


# --- Availabilities ---


def get_player_availability(
    db: Session, player_id: int, date: date_type, slot: str
) -> PlayerAvailability | None:
    """Get specific availability entry"""
    return (
        db.query(PlayerAvailability)
        .filter(
            PlayerAvailability.player_id == player_id,
            PlayerAvailability.date == date,
            PlayerAvailability.slot == slot,
        )
        .first()
    )


def set_player_availability(
    db: Session, team_id: int, player_id: int, availability: AvailabilityCreate
) -> PlayerAvailability:
    """Set or update a player's availability"""
    # Verify player belongs to team
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.team_id == team_id,
    ).first()
    if not player:
        raise ValueError("Player not found")

    existing = get_player_availability(db, player_id, availability.date, availability.slot.value)

    if existing:
        existing.is_available = availability.is_available
        existing.note = availability.note
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    new_availability = PlayerAvailability(
        player_id=player_id,
        date=availability.date,
        slot=availability.slot.value,
        is_available=availability.is_available,
        note=availability.note,
    )
    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)
    return new_availability


def set_player_availability_bulk(
    db: Session, team_id: int, player_id: int, availabilities: list[AvailabilityCreate]
) -> list[PlayerAvailability]:
    """Set multiple availability slots"""
    results = []
    for availability in availabilities:
        result = set_player_availability(db, team_id, player_id, availability)
        results.append(result)
    return results


def delete_availability(db: Session, team_id: int, availability_id: int) -> bool:
    """Delete an availability entry"""
    # Join with player to verify team ownership
    availability = (
        db.query(PlayerAvailability)
        .join(Player)
        .filter(
            PlayerAvailability.id == availability_id,
            Player.team_id == team_id,
        )
        .first()
    )
    if not availability:
        return False

    db.delete(availability)
    db.commit()
    return True


def get_day_availabilities(db: Session, team_id: int, date: date_type) -> DayAvailabilitySummary:
    """Get all players' availability for a specific date"""
    players = db.query(Player).filter(Player.team_id == team_id).all()
    player_ids = [p.id for p in players]

    availabilities_db = (
        db.query(PlayerAvailability)
        .filter(
            PlayerAvailability.date == date,
            PlayerAvailability.player_id.in_(player_ids),
        )
        .all()
    )

    # Build lookup: player_id -> slot -> is_available
    avail_lookup: dict[int, dict[str, bool]] = {}
    for a in availabilities_db:
        if a.player_id not in avail_lookup:
            avail_lookup[a.player_id] = {}
        avail_lookup[a.player_id][a.slot] = a.is_available

    summaries = []
    for player in players:
        player_avail = avail_lookup.get(player.id, {})
        summaries.append(
            PlayerAvailabilitySummary(
                player_id=player.id,
                player_name=player.summoner_name,
                morning=player_avail.get("morning", True),
                afternoon=player_avail.get("afternoon", True),
                evening=player_avail.get("evening", True),
            )
        )

    return DayAvailabilitySummary(date=date, availabilities=summaries)


def get_month_availabilities(
    db: Session, team_id: int, year: int, month: int
) -> list[DayAvailabilitySummary]:
    """Get all availabilities for a month"""
    _, last_day = monthrange(year, month)
    results = []
    for day in range(1, last_day + 1):
        date = date_type(year, month, day)
        results.append(get_day_availabilities(db, team_id, date))
    return results


def get_day_detail(db: Session, team_id: int, date: date_type) -> DayDetail:
    """Get complete day detail: events + availabilities"""
    events = get_events_by_date(db, team_id, date)
    availabilities = get_day_availabilities(db, team_id, date)

    return DayDetail(
        date=date,
        events=events,
        availabilities=availabilities.availabilities,
    )
