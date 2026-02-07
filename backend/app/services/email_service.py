import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

from app.config import settings


def generate_ics(
    title: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    location: str = "",
    organizer_email: str = "",
    attendees: list[str] = None,
    uid: str = None,
) -> str:
    """Generate an ICS calendar file content"""
    if attendees is None:
        attendees = []

    if uid is None:
        uid = str(uuid.uuid4())

    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    start = start_time.strftime("%Y%m%dT%H%M%SZ")
    end = end_time.strftime("%Y%m%dT%H%M%SZ")

    # Build attendee lines
    attendee_lines = ""
    for email in attendees:
        attendee_lines += f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{email}\n"

    organizer_line = ""
    if organizer_email:
        organizer_line = f"ORGANIZER;CN={settings.smtp_from_name}:mailto:{organizer_email}\n"

    # Escape special characters in description
    description_escaped = description.replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")
    title_escaped = title.replace(",", "\\,").replace(";", "\\;")
    location_escaped = location.replace(",", "\\,").replace(";", "\\;") if location else ""

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Oracle Coaching//Calendar//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}@oracle-coaching.com
DTSTAMP:{now}
DTSTART:{start}
DTEND:{end}
SUMMARY:{title_escaped}
DESCRIPTION:{description_escaped}
LOCATION:{location_escaped}
{organizer_line}{attendee_lines}STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""

    return ics_content


def send_calendar_invitation(
    to_emails: list[str],
    subject: str,
    body: str,
    event_title: str,
    event_description: str,
    event_start: datetime,
    event_end: datetime,
    event_location: str = "",
) -> bool:
    """Send an email with an ICS calendar invitation that appears directly in Gmail"""
    if not settings.smtp_host or not settings.smtp_user:
        print("SMTP not configured, skipping email send")
        return False

    if not to_emails:
        print("No recipients provided")
        return False

    try:
        from email.message import EmailMessage
        import email.utils

        # Generate a unique ID for this event
        event_uid = str(uuid.uuid4())

        # Generate ICS content
        ics_content = generate_ics(
            title=event_title,
            description=event_description,
            start_time=event_start,
            end_time=event_end,
            location=event_location,
            organizer_email=settings.smtp_from_email,
            attendees=to_emails,
            uid=event_uid,
        )

        # Use EmailMessage for better control over MIME structure
        msg = EmailMessage()
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid(domain="oracle-coaching.com")

        # Set the plain text content first
        msg.set_content(body)

        # Add HTML alternative
        html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #3b82f6;">{event_title}</h2>
    <p><strong>Date:</strong> {event_start.strftime('%d/%m/%Y')}</p>
    <p><strong>Heure:</strong> {event_start.strftime('%H:%M')} - {event_end.strftime('%H:%M')}</p>
    {f'<p><strong>Lieu:</strong> {event_location}</p>' if event_location else ''}
    <p>{event_description.replace(chr(10), '<br>')}</p>
    <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
    <p style="color: #6b7280; font-size: 12px;">Envoyé via Oracle Coaching Platform</p>
</body>
</html>"""
        msg.add_alternative(html_body, subtype="html")

        # Add calendar content as alternative - this is key for Gmail
        # The calendar part must have method=REQUEST in the Content-Type
        msg.add_alternative(
            ics_content,
            subtype="calendar",
            params={"method": "REQUEST"},
        )

        # Also add as attachment for other clients
        msg.add_attachment(
            ics_content.encode("utf-8"),
            maintype="application",
            subtype="ics",
            filename="invitation.ics",
        )

        # Connect to SMTP server and send
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        print(f"Calendar invitation sent to {to_emails}")
        return True

    except Exception as e:
        print(f"Failed to send calendar invitation: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_slot_times(date_str: str, slot: str) -> tuple[datetime, datetime]:
    """Convert date and slot to start/end datetime"""
    date = datetime.strptime(date_str, "%Y-%m-%d")

    slot_times = {
        "morning": (9, 0, 12, 0),      # 9:00 - 12:00
        "afternoon": (14, 0, 18, 0),   # 14:00 - 18:00
        "evening": (19, 0, 22, 0),     # 19:00 - 22:00
    }

    start_h, start_m, end_h, end_m = slot_times.get(slot, (12, 0, 14, 0))

    start_time = date.replace(hour=start_h, minute=start_m)
    end_time = date.replace(hour=end_h, minute=end_m)

    return start_time, end_time


def is_smtp_configured() -> bool:
    """Check if SMTP is properly configured"""
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_password)
