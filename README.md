# 🚦 RoadSafe AI

**Understand accidents. Learn the law. Drive safer.** A road-safety platform for Pakistan
(National + Punjab law), built as a working Streamlit MVP with a real ML pipeline, a
citation-enforced law assistant, and an accessible signal academy.

> **Honesty first.** All accident figures are **synthetic demo data** calibrated to published
> road-safety *patterns* — not real statistics. Law content is a clearly-flagged paraphrase with
> demo section IDs. The assistant refuses rather than invents. Educational use only — not legal advice.
linke: https://drive-safer-fb8xkhk6suq9y6xwhj9bie.streamlit.app/
## Features (requirement IDs from docs/PRD.md)

| ID | Feature | Where |
| --- | --- | --- |
| F1 | Linked dashboard filters (year, town, weather, road, lighting, severity) | **Accident Insights** |
| F2 | KPI cards: totals, fatalities, injury rate, most dangerous hour, top cause | **Accident Insights** |
| F3 | Risk predictor: calibrated probability + risk band + top-5 SHAP factors | **Risk Predictor** |
| F4 | Law assistant: citations on every claim, refusal path, injection-safe | **Law Assistant** |
| F5 | Signal simulator: red/amber/green, protected arrows (LHT), flashing, pedestrian, roundabout | **Signal Academy** |
| F6 | 106-question quiz: categories, difficulty, explanations, SQLite-saved progress | **Signal Academy** |
| F7 | Sign library: search + category filter, schematic SVG signage | **Sign Library** |
| F8 | Incident reports: validation, local SQLite, EXIF-stripped optional photo | **Report Incident** |
| F12 | Social icon bar (footer on every page) + About page from one JSON config | **About & Connect** |

Optional follow-ups (F9 sign recognition, F10 Urdu/RTL, F11 PDF export) are scoped in the PRD.

## Architecture

```
Streamlit UI (app_pages/*)  ──  services/  ──  ml/
                                │  analytics.py   │  generate_data.py (synthetic, seeded)
        config/socials.json ────┤  predictor.py   │  train.py (time-split + temperature scaling)
        data/laws/corpus.json ──┤  law_assistant  │  explain.py (SHAP → counterfactual fallback)
        data/quiz/quiz_bank.json┤  quiz.py        │  calibration.py (TempScaledPredictor)
        data/signs/*.json       │  signals.py     └── data/raw/lahore_accidents_synthetic.csv
        SQLite (reports, scores)└  reports.py
```

## The law assistant cannot hallucinate (F4 design)

1. **Retrieval**: TF-IDF over the flagged demo corpus (National + Punjab sections).
2. **Default answer mode is extractive** — it quotes retrieved sections verbatim and cites them
   `[Document — Section, Jurisdiction]`. No generation, no invented fines or section numbers.
3. **Refusal path**: below a similarity threshold it answers *"I could not find this in the
   available legal documents…"* and points to official sources.
4. **Optional LLM mode** (`ROADSAFE_LLM_*` env vars): a generative draft, but a **citation
   enforcer** replaces any reply that fails to cite a retrieved section.
5. Document text is treated as **data, never instructions** — prompt injection inside the corpus
   is inert in extractive mode (tested).

## Model card (summary — full version in docs/MODEL_CARD.md)

Time-based split: fit 2020–2022 · temperature-calibrate 2023–2024 · test 2025+ (8,409 rows).

| Metric | Value | Agreed floor |
| --- | --- | --- |
| Macro-F1 (3-class argmax) | 0.358 (majority baseline 0.276, logreg 0.354) | ≥ 0.31 ✅ |
| Severe-vs-minor PR-AUC | 0.419 @ 29.5% base rate → **1.42× lift** | ≥ 1.35× ✅ |
| Brier (fatal) | 0.0375 | ≤ 0.0380 ✅ |
| Calibration | Temperature T = 1.0 (raw LGBM already calibrated) | — |

The headline product number is **P(serious-or-fatal)** — a calibrated severe-risk score — not the
raw argmax class. The UI says what each number does and does not mean.

## Run it

```bash
pip install -r requirements.txt
make data        # regenerate the synthetic dataset (seeded, reproducible)
make train       # train + calibrate + write model card metrics
make test        # pytest — 48 tests
make run         # streamlit run app.py --server.address 0.0.0.0
```

CI (`.github/workflows/ci.yml`) runs lint → data → train (floors enforced) → tests on every push.

## Troubleshooting

**`AttributeError: Can't get attribute '_RemainderColsList' …` (or any unpickle error on `model.joblib`)**
The bundled model artifact was saved with a different scikit-learn version than your environment
(pickled sklearn pipelines reference internal classes that only exist in the version that trained
them — `_RemainderColsList` is new in sklearn 1.6; your env is older). Either fix works:

1. `pip install -r requirements.txt` (pins `scikit-learn>=1.6`) in the env you run Streamlit from, **or**
2. just run the app anyway — it detects the mismatch, prints a warning, and **retrains deterministically
   on the seeded demo data** (~15 s, once). The artifact is version-stamped; retraining also happens
   automatically if the data file is missing.

If Streamlit itself is old (`st.navigation` missing), upgrade it: `pip install -U "streamlit>=1.49"`.

## Relationship to the reference project

The earlier *RoadSafe AI — Enterprise* build (YOLOv8 dashcam analytics, RF/XGBoost risk
classifier, NLP report analyzer, multi-modal fusion, FastAPI service) is mapped module-by-module
against this repo in **[docs/ALIGNMENT.md](docs/ALIGNMENT.md)** — what's covered, what's beyond it,
and how to merge without giving up calibrated probabilities and honest metrics.

## Connect

All of Hammad Zahid's platforms live in one file — `config/socials.json`. Blank a URL to hide a
platform; add one to show it. Footer (every page) and About both render from it, with
`aria-label`s, tooltips, 44 px touch targets and `rel="noopener noreferrer"`.

## Roadmap

- **v0.2** — FastAPI + React Track B sharing the same services; Urdu/RTL (F10); PDF export (F11)
- **v0.3** — Sign recognition from photos (F9); real (licensed) accident data swap-in; LLM gold-set evaluation at scale
