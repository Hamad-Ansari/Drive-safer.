# MODEL CARD — RoadSafe AI severity/risk model

Trained: 2026-10-08 · artefact: `data/processed/model.joblib` · metrics: `data/processed/metrics.json`

## Intended use

Estimate the **probability of a serious-or-fatal outcome** for given road/condition inputs
(hour, month, weekend, weather, road type, lighting, road condition, speed zone, junction type,
town in Lahore). Educational decision-support. **Not** a prediction that a specific crash will
occur, **not** for enforcement, insurance pricing, or any safety-critical use.

## Data

26,460 **synthetic** records (Lahore, 2020-01 → 2026-09) from a documented generator
(`roadsafe/ml/generate_data.py`) encoding published road-safety patterns. Class mix:
70.0% minor / 26.2% serious / 3.8% fatal (train years). Limitations of the data transfer directly
to the model: patterns are as real as the generator's assumptions.

## Protocol

- Time split: **fit 2020–2022** (10,351) · **calibrate 2023–2024** (7,700) · **test 2025+** (8,409).
- Pre-crash inputs only; post-event fields (cause, injured, deaths, vehicle counts) excluded.
- LightGBM (350 trees, lr 0.06, 31 leaves) · **temperature scaling** on 2023–24 → **T = 1.0**
  (raw probabilities already calibrated within measurement precision; Platt/isotonic evaluated and
  rejected — see docs/DECISIONS.md #4).

## Metrics on the 2025+ test window (agreed floors)

| Metric | Value | Floor | Verdict |
| --- | --- | --- | --- |
| Macro-F1 (3-class argmax) | **0.358** | ≥ 0.31 | ✅ |
| — majority baseline | 0.276 | — | beaten |
| — logistic baseline (balanced) | 0.354 | — | matched/exceeded |
| Accuracy | 0.703 | — | — |
| **Severe-vs-minor PR-AUC** | **0.419** @ 29.5% base | lift ≥ 1.35× → **1.42×** | ✅ |
| Severe recall @ 0.5 threshold | 0.218 | informational | threshold is conservative |
| Brier score (fatal) | **0.0375** | ≤ 0.0380 | ✅ |
| PR-AUC fatal / serious / minor | 0.049 / 0.361 / 0.766 | — | fatal ranking is weak |
| ROC-AUC OVR macro | 0.586 | — | — |

## Known limitations (read before trusting numbers)

1. **Fatal-class argmax recall ≈ 0.** With a calibrated 3.8% base rate the argmax almost never
   says "Fatal". By design the UI surfaces **probabilities** (P(fatal), P(serious∪fatal)) and a
   risk band, not a hard class.
2. Rare joint slices (fog + motorway + night) have few training rows; the model leans on additive
   effects there, so it **under-states** extreme slices relative to the generator's truth.
3. SHAP shows associations in the model, not causal effects.
4. All results inherit the synthetic data's assumptions; re-calibrate and re-evaluate before any
   real-data deployment.

## Reproducibility

`make data && make train` — fixed seed 42 (generator + model), versioned artefacts, floors
enforced in `train.main()` and re-checked in `tests/test_predictor.py::test_production_model_exists_and_passes_floors`.
