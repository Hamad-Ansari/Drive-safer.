# TESTPLAN.md

Tooling: `pytest` (unit/service), `ruff` (lint), CI gates. Playwright/a11y audits are scoped for
Track B; the core flows below are covered by service-level tests in v0.1.

| Layer | What is tested | Test file | Pass criteria |
| --- | --- | --- | --- |
| Config | socials.json complete, valid URLs, unique names, icons render, safe links | `test_socials.py` | all pass |
| Data | generator schema, ranges, nulls, imbalance, **no leakage in FEATURES** | `test_data_generator.py` | all pass |
| Analytics | filters narrow correctly, KPIs sane, matrix shapes, map coverage | `test_analytics.py` | all pass |
| ML | small-data train end-to-end, proba sums to 1, **night-fog-motorway > day-local severity**, explanations present, **production model meets floors** | `test_predictor.py` | macro-F1 ≥ .31, severe lift ≥ 1.35×, Brier(fatal) ≤ .038 |
| RAG | corpus jurisdiction tags, retrieval hit (flashing red → PSIG §6), scope filter, citation enforcement, **refusal on out-of-scope**, **no invented fine amounts**, **injection treated as data** | `test_law_assistant.py` | all pass |
| Signals | scenario coverage, no NS+EW green conflict, **pedestrian WALK only with parallel green**, cycling, accessibility text, SVG renders | `test_signals.py` | all pass |
| Quiz | ≥100 well-formed questions, categories/difficulty enums, **every source ID exists in the corpus**, scope filtering, grading, SQLite persistence | `test_quiz.py` | all pass |
| Reports | validation (type/town/date/severity/length), CRUD on tmp DB, photo size/type checks, **EXIF really stripped** | `test_reports.py` | all pass |
| Signs | ≥30 signs, categories, unique IDs, search/filter, SVG output | `test_signs.py` | all pass |

## Critical manual test cases (from the master plan)

1. *"What should a driver do at a flashing red light?"* → cited answer (PSIG §6). ✅ automated
2. *"What is the fine for over-speeding?"* → no invented number; points to the official schedule. ✅ automated
3. Corpus/query containing *"ignore previous instructions"* → treated as data. ✅ automated
4. Predictor with impossible input → Streamlit widgets constrain inputs; validation tested at service level. ✅
5. Every social icon labelled, new-tab, keyboard-focusable. ✅ automated
6. Quiz progress persists after refresh → SQLite-backed. ✅ automated

## Track B additions (planned)

Playwright E2E (filter → predict → ask → quiz → report), axe/Lighthouse audit (no serious
violations), Lighthouse CI budget (FMP < 2.5 s mid-range phone), locust API p95 < 800 ms,
pip-audit/bandit, 80% coverage gate on services+ML.
