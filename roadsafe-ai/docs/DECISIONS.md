# DECISIONS.md — what was chosen and why

Append-only. Newest at the bottom.

1. **Streamlit Track A first.** Owner asked for the fastest working MVP; all logic sits in
   `roadsafe/services/*` so the FastAPI+React Track B can reuse it unchanged.

2. **Synthetic accident data, openly labelled.** No license-clean public row-level accident data
   exists for Lahore. Rather than fabricate "real" numbers, we generate 26,460 records
   (2020-01 → 2026-09) from a documented logistic data-generating process that encodes published
   Lahore patterns: Dec–Jan fog season, Jul–Sep monsoon, May–Jun dust, 8–9/17–19 rush peaks,
   motorway/high-speed/night severity amplification, left-hand traffic. Every surface in the app
   labels it as synthetic. Swapping in licensed real data later changes exactly one file.

3. **Time-based split with a dedicated calibration window.** Fit 2020–2022, calibrate 2023–2024,
   test 2025+ (8,409 rows). No leakage across eras; post-event fields (cause, injured, deaths,
   vehicle counts) are excluded from `config.FEATURES` by construction.

4. **Temperature scaling, not Platt/isotonic.** Experimented during the build: cross-fitted
   sigmoid calibration (sklearn `CalibratedClassifierCV`) *halved* probabilities in rare-but-real
   high-risk slices (fog+motorway+night had ~0 calibration rows) because each fold's model is
   weaker. Isotonic plateaued even worse. A single global temperature T preserves ranking exactly,
   can only shrink overconfidence, and the fit found **T = 1.0** — i.e. the raw LightGBM is already
   calibrated within measurement precision on this data. Platt/isotonic remain documented here for
   anyone re-running with real data.

5. **Severe-vs-minor is the headline.** With a 3.8–4% fatal class, 3-class argmax F1 is intrinsically
   capped by noise (Bayes-limited). The product's primary number is **P(serious ∪ fatal)**, a
   calibrated score with a 1.42× PR-AUC lift over the base rate; 3-class metrics are reported as
   diagnostics with baselines.

6. **Explanations: SHAP with an honest fallback.** SHAP `TreeExplainer` runs on the LightGBM with
   one-hot columns grouped back to original features. If SHAP is unavailable, a single-row
   counterfactual attribution (probability change when each feature reverts to its training-typical
   value) is used and is *labelled as approximate* in the UI.

7. **Extractive-by-default law assistant.** The corpus is a **flagged demo paraphrase** (gazette
   texts can't be verified in this session, so inventing "official" wording or fine amounts would
   violate the honesty rules). Extractive quoting + enforced citations + refusal threshold
   (TF-IDF cosine < 0.10) makes hallucination structurally impossible without an LLM. The optional
   LLM mode keeps the citation enforcer and the same refusal path. Document text is treated as
   data — prompt-injection strings inside the corpus are inert (tested).

8. **Quiz sources are checkable.** All 106 questions cite a corpus section ID; a unit test fails if
   any question's source is not in the corpus.

9. **Roundabouts and arrows follow left-hand traffic.** Clockwise flow, yield to the right,
   protected RIGHT-turn arrows — deliberately different from the US-style tutorials most students
   see.

10. **SQLite over SQLite-ORM.** For the MVP scale, `sqlite3` with a schema script and injectable
    path (tests) is simpler than SQLAlchemy; the schema is Postgres-portable.

11. **Accessibility stance.** The simulator never auto-plays (reduced-motion friendly), every
    phase has a text description, charts have text summaries + a data table + CSV export, and
    social icons are 44 px targets with `aria-label`, tooltip and focus ring.

12. **pydantic-settings deferred.** Traded for plain `os.getenv` + a config module in Track A;
    pydantic-settings lands with the FastAPI Track B where request schemas need it anyway.

13. **Model artifacts are version-stamped and self-healing (first real-world bug report).** The
    owner's local run crashed with `AttributeError: Can't get attribute '_RemainderColsList'`:
    the artifact was pickled under scikit-learn 1.6.1 while their conda env has an older sklearn —
    pickled sklearn pipelines reference internal classes that don't exist across versions. Policy:
    `train()` stamps `sklearn_version`/`lightgbm_version`/`python_version` into the bundle;
    `load_predictor()` verifies the stamp and on ANY load/version failure warns and retrains
    deterministically on the seeded data (regenerating the CSV if missing) instead of crashing.
    `requirements.txt` pins `scikit-learn>=1.6`. Rationale: the pickle is a cache, the training
    script is the source of truth — never ship a model that can't be rebuilt from it.
