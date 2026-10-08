"""Incident report service — validation, storage (SQLite), listing.

Privacy by design: the form collects no names or phone numbers. The optional
photo is type/size checked and re-encoded without EXIF (location stripping)
before storage.
"""
from __future__ import annotations

import io
from datetime import datetime, timezone

from roadsafe.core import config


def validate_report(incident_type: str, town: str, when_seen: datetime | str,
                    severity: str, description: str) -> list[str]:
    errors: list[str] = []
    if incident_type not in config.INCIDENT_TYPES:
        errors.append("Choose a valid incident type.")
    if town not in config.TOWNS:
        errors.append("Choose a valid Lahore town/zone.")
    try:
        when = when_seen if isinstance(when_seen, datetime) else datetime.fromisoformat(str(when_seen))
        if when > datetime.now(timezone.utc).replace(tzinfo=None):
            errors.append("When seen cannot be in the future.")
        if when < datetime(2020, 1, 1):
            errors.append("When seen looks too far in the past.")
    except ValueError:
        errors.append("Provide a valid date and time.")
    if severity not in {"Property damage only", "Minor injury", "Serious injury", "Not sure"}:
        errors.append("Choose a valid severity.")
    text = (description or "").strip()
    if len(text) < 10:
        errors.append("Describe what happened in at least 10 characters.")
    if len(text) > 1000:
        errors.append("Keep the description under 1000 characters.")
    return errors


def check_photo(file_bytes: bytes, mime: str) -> str | None:
    """Return an error string, or None if the photo is acceptable."""
    if len(file_bytes) > config.MAX_PHOTO_MB * 1024 * 1024:
        return f"Photo must be under {config.MAX_PHOTO_MB:.0f} MB."
    if mime not in config.ALLOWED_PHOTO_TYPES:
        return "Only PNG or JPEG photos are accepted."
    return None


def strip_exif(data: bytes, mime: str) -> bytes:
    """Re-encode through Pillow so EXIF (incl. GPS) is dropped."""
    from PIL import Image

    fmt = "PNG" if mime == "image/png" else "JPEG"
    img = Image.open(io.BytesIO(data))
    clean = io.BytesIO()
    img.save(clean, format=fmt)
    return clean.getvalue()


def save_report(conn, incident_type: str, town: str, when_seen: str, severity: str,
                description: str, photo: bytes | None = None,
                photo_mime: str | None = None) -> int:
    cur = conn.execute(
        "INSERT INTO reports (created_at, incident_type, town, when_seen, severity, "
        "description, photo_blob, photo_mime) VALUES (?,?,?,?,?,?,?,?)",
        (datetime.now(timezone.utc).isoformat(), incident_type, town, str(when_seen),
         severity, description.strip(),
         photo if photo is not None else None, photo_mime))
    conn.commit()
    return int(cur.lastrowid)


def list_reports(conn, limit: int = 50) -> list[dict]:
    rows = conn.execute(
        "SELECT id, created_at, incident_type, town, when_seen, severity, description, "
        "photo_blob IS NOT NULL AND LENGTH(photo_blob) > 0 FROM reports "
        "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    keys = ["id", "created_at", "incident_type", "town", "when_seen", "severity",
            "description", "has_photo"]
    return [dict(zip(keys, r)) for r in rows]


def count_reports(conn) -> int:
    return int(conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0])


def clear_reports(conn) -> None:
    conn.execute("DELETE FROM reports")
    conn.commit()
