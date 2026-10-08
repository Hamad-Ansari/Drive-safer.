"""Load and validate the single source of truth for social links."""
from __future__ import annotations

import json
from pathlib import Path

from roadsafe.core import config

REQUIRED_KEYS = {"name", "icon", "url"}


def socials_path() -> Path:
    return config.CONFIG_DIR / "socials.json"


def load_socials(path: Path | None = None) -> list[dict]:
    """Return validated social entries.

    Entries missing a name/icon/url or with an empty URL are skipped, so the
    owner can disable a platform by blanking its URL — no code change needed.
    """
    path = path or socials_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("socials", [])
    valid: list[dict] = []
    for item in items:
        if not REQUIRED_KEYS.issubset(item):
            continue
        if not str(item["url"]).strip() or str(item["url"]).startswith("#"):
            continue
        valid.append({"name": item["name"], "icon": item["icon"], "url": item["url"]})
    return valid
