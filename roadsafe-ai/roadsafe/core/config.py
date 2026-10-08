"""Central configuration: paths, domain vocabularies, ML schema, env settings.

Everything that other modules need to agree on lives here, so the Streamlit UI,
services and ML code never drift apart.
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------- paths ----
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LAWS_DIR = DATA_DIR / "laws"
QUIZ_DIR = DATA_DIR / "quiz"
SIGNS_DIR = DATA_DIR / "signs"

ACCIDENTS_CSV = RAW_DIR / "lahore_accidents_synthetic.csv"
MODEL_FILE = PROCESSED_DIR / "model.joblib"
METRICS_FILE = PROCESSED_DIR / "metrics.json"
DB_PATH = Path(os.getenv("ROADSAFE_DB", str(PROCESSED_DIR / "roadsafe.db")))

# ------------------------------------------------------------------ app ----
APP_NAME = "RoadSafe AI"
APP_TAGLINE = "Understand accidents. Learn the law. Drive safer."
AUTHOR_NAME = "Hammad Zahid"
DATA_NOTE = "Synthetic demo data — Lahore, 2020–2026. Not real statistics."
LAW_NOTE = (
    "Law content is a clearly-flagged demo paraphrase of Pakistani national and "
    "Punjab traffic rules. Not legal advice — verify with official sources."
)
LAW_SCOPES = ["Both", "National", "Punjab"]
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

# Lahore administrative towns with schematic tile-map coordinates (west→east x,
# north→south y). Coordinates are for the schematic map only — not GIS-accurate.
TOWNS: dict[str, tuple[float, float]] = {
    "Ravi": (2.5, 1.5),
    "Wagha": (7.5, 1.0),
    "Shalimar": (6.5, 2.5),
    "Data Ganj Bakhsh": (4.0, 3.0),
    "Aziz Bhatti": (7.8, 3.8),
    "Samanabad": (2.2, 4.2),
    "Gulberg": (5.2, 4.6),
    "Cantonment": (8.2, 5.0),
    "Allama Iqbal": (6.6, 5.8),
    "Model Town": (5.4, 7.0),
    "Nishtar": (4.2, 8.4),
}

ROAD_TYPES = [
    "Motorway / Expressway",
    "National Highway (N-5)",
    "Main Boulevard",
    "Arterial Road",
    "Collector Road",
    "Local Street",
]
WEATHER_TYPES = ["Clear", "Haze / Smog", "Fog", "Overcast", "Light Rain", "Heavy Rain", "Dust Storm"]
LIGHTING_TYPES = ["Daylight", "Dawn / Dusk", "Dark — Street Lit", "Dark — Unlit"]
ROAD_CONDITIONS = ["Dry", "Wet", "Potholed", "Under Construction"]
SPEED_ZONES = ["≤ 40 km/h", "50–60 km/h", "70–80 km/h", "90–100 km/h", "> 100 km/h"]
JUNCTION_TYPES = ["Mid-block", "Signalized Intersection", "Unsignalized Intersection", "Roundabout", "U-Turn Point"]
SEVERITIES = ["Minor injury", "Serious injury", "Fatal"]
INCIDENT_TYPES = [
    "Near miss",
    "Crash — minor",
    "Crash — serious",
    "Road hazard",
    "Malfunctioning signal",
    "Blocked road",
    "Reckless driving",
    "Other",
]

# ------------------------------------------------------------------ ML -----
FEATURES = [
    "hour", "month", "is_weekend",
    "weather", "road_type", "lighting", "road_condition",
    "speed_zone", "junction_type", "town",
]
NUMERIC_FEATURES = ["hour", "month", "is_weekend"]
CATEGORICAL_FEATURES = [
    "weather", "road_type", "lighting", "road_condition",
    "speed_zone", "junction_type", "town",
]
TARGET = "severity"
TRAIN_YEARS = (2020, 2024)   # inclusive — time-based split, test is 2025+
RANDOM_SEED = 42

# ------------------------------------------------------------ validation ---
MAX_PHOTO_MB = 2.0
ALLOWED_PHOTO_TYPES = {"image/png", "image/jpeg"}

# ------------------------------------------------------------------ quiz ---
QUIZ_SESSION_SIZE = 10

# ------------------------------------------------------------------ LLM ----
def get_llm_config() -> dict | None:
    """Return OpenAI-compatible LLM settings from env, or None for extractive mode.

    The law assistant works fully offline by default (extractive, cited answers).
    Set ROADSAFE_LLM_BASE_URL, ROADSAFE_LLM_API_KEY and ROADSAFE_LLM_MODEL to
    enable generative answers on top of the same retrieved context.
    """
    base = os.getenv("ROADSAFE_LLM_BASE_URL")
    key = os.getenv("ROADSAFE_LLM_API_KEY")
    model = os.getenv("ROADSAFE_LLM_MODEL")
    if base and key and model:
        return {"base_url": base.rstrip("/"), "api_key": key, "model": model}
    return None
