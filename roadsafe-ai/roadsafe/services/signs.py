"""Sign library service — load, search, filter, render."""
from __future__ import annotations

import json
from pathlib import Path

from roadsafe.core import config
from roadsafe.core.icons import sign_svg

CATEGORIES = ["Regulatory", "Warning", "Information"]


def load_signs(path: Path | None = None) -> list[dict]:
    path = path or config.SIGNS_DIR / "sign_library.json"
    return json.loads(path.read_text(encoding="utf-8"))["signs"]


def search_signs(signs: list[dict], query: str = "", category: str | None = None,
                 scope: str = "Both") -> list[dict]:
    q = (query or "").strip().lower()
    out = signs
    if category and category != "All":
        out = [s for s in out if s["category"] == category]
    if scope in {"National", "Punjab"}:
        out = [s for s in out if s["jurisdiction"] in {scope, "Both"}]
    if q:
        out = [s for s in out
               if q in s["name"].lower() or q in s["meaning"].lower() or q in s["rule"].lower()]
    return out


def render_sign(sign: dict, size: int = 72) -> str:
    return sign_svg(sign["shape"], sign.get("symbol", ""),
                    sign.get("symbol_color", "#111827"), size)
