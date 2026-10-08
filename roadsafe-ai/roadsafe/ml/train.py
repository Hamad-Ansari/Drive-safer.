"""Train the severity predictor — reproducible, time-split, calibrated.

Protocol (see docs/MODEL_CARD.md):
- Time-based split: the base model fits 2020–2022, temperature calibration
  uses 2023–2024, test is 2025+. No row ever leaks across its era.
- Inputs are pre-crash conditions ONLY; post-event fields (cause, injured,
  deaths, vehicle counts) are excluded by construction (config.FEATURES).
- Probability calibration: temperature scaling (single global T) fitted on the
  held-out 2023–2024 calibration years — see roadsafe/ml/calibration.py and
  docs/DECISIONS.md for why it beats Platt/isotonic here.
- Severe-vs-minor (the plan's binary framing) is derived as
  P(serious) + P(fatal); it is the headline risk number in the UI.
- Baselines: majority class and multinomial logistic regression.
"""
from __future__ import annotations

import json
import platform
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             classification_report, f1_score, recall_score,
                             roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from roadsafe.core import config
from roadsafe.ml.calibration import TempScaledPredictor

FIT_YEARS = (2020, 2022)
CAL_YEARS = (2023, 2024)


def load_accidents(path=None) -> pd.DataFrame:
    path = path or config.ACCIDENTS_CSV
    return pd.read_csv(path, parse_dates=["date_time"])


def _make_prep() -> ColumnTransformer:
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         config.CATEGORICAL_FEATURES),
        ("num", "passthrough", config.NUMERIC_FEATURES),
    ])


def build_base_pipeline(seed: int = config.RANDOM_SEED) -> Pipeline:
    lgbm = LGBMClassifier(
        n_estimators=350, learning_rate=0.06, num_leaves=31,
        min_child_samples=30, random_state=seed, n_jobs=-1, verbose=-1,
    )
    return Pipeline([("prep", _make_prep()), ("clf", lgbm)])


def _brier_multiclass(y_true, probs, col) -> float:
    return float(sum(
        float(np.mean((probs[:, col[cls]] - (y_true == cls).astype(float)) ** 2))
        for cls in config.SEVERITIES
    ))


def _pr_auc_per_class(y_true, probs, col) -> dict[str, float]:
    return {
        cls: float(average_precision_score((np.asarray(y_true) == cls).astype(int),
                                           probs[:, col[cls]]))
        for cls in config.SEVERITIES
    }


def train(df: pd.DataFrame | None = None, seed: int = config.RANDOM_SEED,
          out_path=None) -> dict:
    t0 = time.time()
    df = df if df is not None else load_accidents()
    train_fit = df[df["year"].between(*FIT_YEARS)]
    calib = df[df["year"].between(*CAL_YEARS)]
    test = df[df["year"] > CAL_YEARS[1]]

    base = build_base_pipeline(seed).fit(train_fit[config.FEATURES], train_fit[config.TARGET])
    predictor = TempScaledPredictor(base)
    temperature = predictor.fit_temperature(calib[config.FEATURES], calib[config.TARGET])

    classes = list(predictor.classes_)          # probability column order
    col = {cls: i for i, cls in enumerate(classes)}
    probs = predictor.predict_proba(test[config.FEATURES])
    preds = np.array(classes, dtype=object)[probs.argmax(axis=1)]
    y_test = test[config.TARGET].to_numpy()

    report = classification_report(y_test, preds, labels=config.SEVERITIES,
                                   output_dict=True, zero_division=0)

    # Headline severe-vs-minor view: P(serious) + P(fatal).
    severe_true = (y_test != "Minor injury").astype(int)
    severe_prob = probs[:, col["Serious injury"]] + probs[:, col["Fatal"]]

    metrics = {
        "accuracy": float(report["accuracy"]),
        "macro_f1": float(f1_score(y_test, preds, average="macro",
                                   labels=config.SEVERITIES, zero_division=0)),
        "per_class": {
            cls: {k: float(report[cls][k]) for k in ("precision", "recall", "f1-score", "support")}
            for cls in config.SEVERITIES
        },
        "pr_auc_per_class": _pr_auc_per_class(y_test, probs, col),
        "brier_multiclass": _brier_multiclass(y_test, probs, col),
        "brier_fatal": float(brier_score_loss((y_test == "Fatal").astype(int),
                                              probs[:, col["Fatal"]])),
        "roc_auc_ovr_macro": float(roc_auc_score(y_test, probs, multi_class="ovr",
                                                 average="macro")),
        "severe_recall_at_0p5": float(recall_score(severe_true, (severe_prob >= 0.5).astype(int),
                                                   zero_division=0)),
        "severe_pr_auc": float(average_precision_score(severe_true, severe_prob)),
        "severe_base_rate": float(severe_true.mean()),
        "confusion_matrix": {
            "labels": config.SEVERITIES,
            "matrix": [[int(((preds == r) & (y_test == c)).sum()) for c in config.SEVERITIES]
                       for r in config.SEVERITIES],
        },
        "n_train": int(len(train_fit)), "n_calibration": int(len(calib)),
        "n_test": int(len(test)),
        "class_share_train": train_fit[config.TARGET].value_counts(normalize=True).round(4).to_dict(),
        "split": {"fit_years": list(FIT_YEARS), "calibration_years": list(CAL_YEARS),
                  "test_years": f"{CAL_YEARS[1] + 1}+"},
    }

    # ---- baselines for honesty ----
    dummy = DummyClassifier(strategy="most_frequent").fit(train_fit[config.FEATURES],
                                                          train_fit[config.TARGET])
    metrics["baseline_majority_macro_f1"] = float(
        f1_score(y_test, dummy.predict(test[config.FEATURES]), average="macro",
                 labels=config.SEVERITIES, zero_division=0))
    logreg = Pipeline([
        ("prep", _make_prep()),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)),
    ]).fit(train_fit[config.FEATURES], train_fit[config.TARGET])
    metrics["baseline_logreg_macro_f1"] = float(
        f1_score(y_test, logreg.predict(test[config.FEATURES]), average="macro",
                 labels=config.SEVERITIES, zero_division=0))

    # Background row for the counterfactual explainer fallback (typical values).
    background: dict = {}
    for feat in config.NUMERIC_FEATURES:
        background[feat] = 0 if feat == "is_weekend" else float(train_fit[feat].median())
    for feat in config.CATEGORICAL_FEATURES:
        background[feat] = str(train_fit[feat].mode().iloc[0])

    bundle = {
        "predictor": predictor,                 # calibrated predict_proba over raw features
        "prep": base.named_steps["prep"],       # fitted transformer (for SHAP space)
        "clf": base.named_steps["clf"],         # fitted LightGBM (for TreeExplainer)
        "features": config.FEATURES,
        "classes": classes,                     # probability column order
        "severity_display_order": config.SEVERITIES,
        "background": background,
        "metrics": {k: v for k, v in metrics.items() if k != "confusion_matrix"},
        "confusion_matrix": metrics["confusion_matrix"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "split": metrics["split"],
        "temperature": temperature,
        # Persisted sklearn objects are NOT portable across versions — stamp and verify.
        "sklearn_version": __import__("sklearn").__version__,
        "lightgbm_version": __import__("lightgbm").__version__,
        "python_version": platform.python_version(),
        "data_note": config.DATA_NOTE,
    }

    model_path = out_path or config.MODEL_FILE
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    if out_path is None:  # only publish metrics for the real artifact
        config.METRICS_FILE.write_text(json.dumps(metrics, indent=2))
    metrics["fit_seconds"] = round(time.time() - t0, 1)
    return metrics


def main() -> None:
    metrics = train()
    # Agreed floors (docs/MODEL_CARD.md): the model must beat the majority
    # baseline on hard classes AND beat the base rate on severe-risk ranking.
    floors = {"macro_f1": 0.31, "severe_pr_auc_vs_base": 1.35, "brier_fatal_max": 0.0380}
    severe_lift = metrics["severe_pr_auc"] / metrics["severe_base_rate"]
    ok = (metrics["macro_f1"] >= floors["macro_f1"]
          and severe_lift >= floors["severe_pr_auc_vs_base"]
          and metrics["brier_fatal"] <= floors["brier_fatal_max"])
    print("temperature T:", round(metrics.get("temperature", 1.0), 3))
    print("macro-F1:", round(metrics["macro_f1"], 3),
          "(majority baseline:", round(metrics["baseline_majority_macro_f1"], 3),
          "| logreg:", round(metrics["baseline_logreg_macro_f1"], 3), ")")
    print("accuracy:", round(metrics["accuracy"], 3),
          "| Brier(fatal):", round(metrics["brier_fatal"], 4))
    print("Severe PR-AUC:", round(metrics["severe_pr_auc"], 3),
          "| base rate:", round(metrics["severe_base_rate"], 3),
          "| lift:", round(severe_lift, 2),
          "| recall@0.5:", round(metrics["severe_recall_at_0p5"], 3))
    print("FLOORS:", floors, "→", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
