"""Quiz bank integrity + filtering + grading (F6)."""
from __future__ import annotations

from roadsafe.services import db as db_mod
from roadsafe.services import law_assistant as la
from roadsafe.services import quiz as quiz_svc


def _bank():
    return quiz_svc.load_bank()


def test_bank_has_at_least_100_questions():
    assert len(_bank()) >= 100


def test_every_question_is_wellformed():
    cats = quiz_svc.categories(_bank())
    assert len(cats) >= 8
    for q in _bank():
        assert len(q["options"]) == 4, q["id"]
        assert 0 <= q["answer"] < 4
        assert q["category"] in cats
        assert q["difficulty"] in {"Easy", "Medium", "Hard"}
        assert q["jurisdiction"] in {"National", "Punjab", "Both"}
        assert len(q["explanation"]) > 10
        assert q["source"], q["id"]


def test_sources_reference_corpus_ids():
    corpus_ids = {s.id for s in la.load_corpus()}
    orphans = [q["id"] for q in _bank() if q["source"] not in corpus_ids]
    assert not orphans, f"quiz sources not in corpus: {orphans[:5]}"


def test_scope_filtering():
    bank = _bank()
    punjab_only = quiz_svc.filter_questions(bank, scope="Punjab")
    assert all(q["jurisdiction"] in {"Punjab", "Both"} for q in punjab_only)
    assert len(quiz_svc.filter_questions(bank, scope="Both")) == len(bank)


def test_make_session_and_grade():
    pool = quiz_svc.filter_questions(_bank(), scope="Both")
    session = quiz_svc.make_session(pool, n=10, seed=42)
    assert len(session) == 10
    picks = [q["options_shuffled"][1] for q in session]          # all correct
    result = quiz_svc.grade(session, picks)
    assert result["score"] == 10
    wrong = [0 if q["options_shuffled"][1] != 0 else 1 for q in session]
    result2 = quiz_svc.grade(session, wrong)
    assert result2["score"] <= 2


def test_scores_persist(tmp_path):
    conn = db_mod.connect(tmp_path / "quiz.db")
    quiz_svc.save_score(conn, "Both", "Traffic Signals", 8, 10)
    quiz_svc.save_score(conn, "Both", "Traffic Signals", 10, 10)
    rows = quiz_svc.progress(conn)
    sig = next(r for r in rows if r["category"] == "Traffic Signals")
    assert sig["attempts"] == 2
    assert sig["best"] == 100.0
