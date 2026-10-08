"""Incident reports: validation, storage, photo checks (F8)."""
from __future__ import annotations

import io

from roadsafe.services import db as db_mod
from roadsafe.services import reports as rep


def test_validation_catches_bad_input():
    errors = rep.validate_report("Unknown type", "Mars", "2026-01-01T10:00",
                                 "Minor injury", "too short")
    assert errors
    errors = rep.validate_report("Near miss", "Gulberg", "2099-01-01T10:00",
                                 "Minor injury", "A perfectly fine description here")
    assert any("future" in e.lower() for e in errors)


def test_valid_report_passes():
    assert rep.validate_report("Near miss", "Gulberg", "2026-01-01T10:00",
                               "Minor injury", "Signal stuck on red for 10 minutes") == []


def test_save_list_clear(tmp_path):
    conn = db_mod.connect(tmp_path / "reports.db")
    rid = rep.save_report(conn, "Near miss", "Gulberg", "2026-01-01T10:00",
                          "Minor injury", "Signal stuck on red for 10 minutes")
    rows = rep.list_reports(conn)
    assert rows[0]["id"] == rid
    assert rows[0]["town"] == "Gulberg"
    assert rep.count_reports(conn) == 1
    rep.clear_reports(conn)
    assert rep.count_reports(conn) == 0


def test_photo_checks():
    assert rep.check_photo(b"x" * (3 * 1024 * 1024), "image/png") is not None  # too big
    assert rep.check_photo(b"data", "image/gif") is not None                   # wrong type
    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000d49444154789c6260000000060005"
        "27de39bc0000000049454e44ae426082")
    assert rep.check_photo(png, "image/png") is None


def test_exif_stripped():
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new("RGB", (4, 4), (200, 30, 30))
    exif = img.getexif()
    exif[0x010F] = "SecretCamera"          # Make tag
    img.save(buf, format="JPEG", exif=exif.tobytes())
    cleaned = rep.strip_exif(buf.getvalue(), "image/jpeg")
    assert b"SecretCamera" not in cleaned
