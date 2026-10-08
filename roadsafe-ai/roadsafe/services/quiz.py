"""Quiz service — filtering, sessions, grading, persisted progress."""
from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

from roadsafe.core import config


def load_bank(path: Path | None = None) -> list[dict]:
    path = path or config.QUIZ_DIR / "quiz_bank.json"
    return json.loads(path.read_text(encoding="utf-8"))["questions"]


def categories(bank: list[dict]) -> list[str]:
    return sorted({q["category"] for q in bank})


def filter_questions(bank: list[dict], scope: str = "Both",
                     category: str | None = None) -> list[dict]:
    out = bank
    if scope in {"National", "Punjab"}:
        out = [q for q in out if q["jurisdiction"] in {scope, "Both"}]
    if category and category != "All":
        out = [q for q in out if q["category"] == category]
    return out


def make_session(pool: list[dict], n: int = config.QUIZ_SESSION_SIZE,
                 seed: int | None = None) -> list[dict]:
    rng = random.Random(seed)
    picked = pool[:] if len(pool) <= n else rng.sample(pool, n)
    out = []
    for q in picked:
        out.append({**q, "options_shuffled": _shuffle_options(q, rng)})
    return out


def _shuffle_options(q: dict, rng: random.Random) -> tuple[list[str], int]:
    idx = list(range(len(q["options"])))
    rng.shuffle(idx)
    opts = [q["options"][i] for i in idx]
    return opts, idx.index(q["answer"])


def grade(questions: list[dict], picks: list[int | None]) -> dict:
    per = []
    score = 0
    for q, pick in zip(questions, picks):
        shuffled = q.get("options_shuffled")
        if shuffled:
            opts, correct = shuffled
        else:
            opts, correct = q["options"], q["answer"]
        ok = pick is not None and pick == correct
        score += int(ok)
        per.append({
            "id": q["id"], "q": q["q"], "ok": ok,
            "correct_text": opts[correct], "picked_text": opts[pick] if pick is not None else None,
            "explanation": q["explanation"], "source": q["source"],
        })
    return {"score": score, "total": len(questions), "per": per}


def save_score(conn, scope: str, category: str, score: int, total: int) -> None:
    conn.execute(
        "INSERT INTO quiz_scores (ts, scope, category, score, total) VALUES (?,?,?,?,?)",
        (datetime.now(timezone.utc).isoformat(), scope, category, score, total))
    conn.commit()


def progress(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT category, COUNT(*) attempts, MAX(score * 100.0 / total) best, "
        "AVG(score * 100.0 / total) avg_pct FROM quiz_scores GROUP BY category ORDER BY category"
    ).fetchall()
    return [{"category": r[0], "attempts": r[1], "best": round(r[2], 1),
             "avg": round(r[3], 1)} for r in rows]
