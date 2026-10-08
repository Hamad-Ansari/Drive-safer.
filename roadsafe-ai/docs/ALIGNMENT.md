# ALIGNMENT.md — reference “Enterprise RoadSafe AI” ↔ this repo

Mapping of the reference project's modules (from its README: YOLOv8 vision, ML risk classifier,
NLP report analyzer, multi-modal fusion, FastAPI microservice) onto RoadSafe AI v0.1, plus merge
guidance. Status: ✅ covered · 🔜 natural next build · 🧩 partial/adjacent.

| Reference module | What it does | Equivalent here | Status & notes |
| --- | --- | --- | --- |
| Executive Dashboard | KPIs, active AI disciplines, architecture view | **Accident Insights** page | ✅ Ours goes further: 6 linked filters, weekday×hour heatmap, schematic town map, CSV export, accessibility text |
| Module A — Traffic Vision | YOLOv8n on images/dashcam video; car/truck/bus/motorcycle/bicycle/pedestrian counts; density timeline; peak timestamps; FPS | — | 🔜 Not built. Fits as `roadsafe/services/vision.py` + an upload page; needs `ultralytics`/torch + OpenCV. Density output would feed fusion (Module D) and could calibrate our town-level exposure |
| Module B — Accident Risk | LogReg / RF (82.6% acc, 0.826 F1) / XGBoost on weather, surface, visibility (miles), temp, humidity, wind, speed limit, signals; Low/Med/High bands | **Risk Predictor** | ✅ Deliberately different protocol: calibrated **P(serious-or-fatal)** via time-split LightGBM + temperature scaling + SHAP + published floors and baselines. An "82.6% accuracy" on imbalanced accident data is usually the majority class — keep our metric discipline when merging |
| Module C — NLP Report Analyzer | Regex/NER over incident narratives: collision type, vehicles, hazards, weather, severity cues; 0–100 severity/urgency | Reports page stores narratives but doesn't parse them | 🔜 Easy add as `roadsafe/services/nlp.py` (pure regex — no heavy deps); would plug into Report Incident and fusion. Pairs well with our "text is data, never instructions" stance |
| Module D — Multi-Modal Fusion | Composite Safety Risk Index 0–100 from CV density + ML risk + NLP severity; safety protocols; Markdown/JSON audit reports | — | 🔜 Straightforward once A/C exist: fuse `severe_probability` + density + NLP score with documented weights; protocols map to our predictor's risk-reduction tips |
| FastAPI Microservice (`api.py`) | `/predict-risk`, `/detect-objects`, `/analyze-report`, `/integrated-risk`, health | Streamlit Track A only; Track B (FastAPI+React) planned | 🧩 `/predict-risk` maps 1:1 onto `services/predictor.py`; law/quiz/analytics endpoints are trivial adds because all logic already lives in services/ |

## Where this repo goes beyond the reference

- **Calibrated, time-split ML with published floors** (macro-F1 vs baselines, severe-risk PR-AUC
  lift, Brier) instead of a single headline accuracy; honesty notices in-product.
- **Citation-enforced law assistant** with a structural refusal path — the reference has no legal Q&A.
- **Signal & Sign Academy** (accessible LHT simulator + 106-question corpus-linked quiz with saved progress).
- **Test suite (52) + CI with metric gates**, accessibility alternates (text summaries, tables, CSV),
  privacy-aware reports (EXIF stripping), and a single-config socials system.

## Merge guidance (if the two codebases combine)

1. Keep Pakistan scope (National + Punjab) and LHT conventions; treat the reference's
   visibility-in-miles/US-schema features as an alternate **dataset adapter**, not the product default.
2. Keep calibrated probabilities; express bands as Low/Moderate/Elevated/High (map their
   Low/Med/High onto it) and always show the number alongside the band.
3. Any YOLOv8/NLP outputs enter the UI with the same honesty labeling (model names, confidence,
   limitations) and tests with invariants, like everything else here.
