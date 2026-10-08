"""SQLite access for incident reports and quiz scores (path injectable for tests)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    town TEXT NOT NULL,
    when_seen TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    photo_blob BLOB,
    photo_mime TEXT
);
CREATE TABLE IF NOT EXISTS quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    scope TEXT NOT NULL,
    category TEXT NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL
);
"""


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    from roadsafe.core import config

    path = Path(path) if path else config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.executescript(_SCHEMA)
    return conn
