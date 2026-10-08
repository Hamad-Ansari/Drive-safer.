"""End-to-end model training (small data) + prediction + explanation."""
from __future__ import annotations

import joblib
import pandas as pd

from roadsafe.core import config
from roadsafe.ml.explain import Explainer
from roadsafe.ml.generate_data import generate
from roadsafe.ml.train import train
from roadsafe.services.predictor import RiskPredictor

NIGHT = {"hour": 2, "month": 1, "is_weekend": 1, "weather": "Fog",
         "road_type": "Motorway / Expressway", "lighting": "Dark — Unlit",
         "road_condition": "Dry", "speed_zone": "> 100 km/h",
         "junction_type": "Mid-block", "town": "Wagha"}
DAY = {"hour": 14, "month": 6, "is_weekend": 0, "weather": "Clear",
       "road_type": "Local Street", "lighting": "Daylight", "road_condition": "Dry",
       "speed_zone": "≤ 40 km/h", "junction_type": "Mid-block", "town": "Gulberg"}


def _small_bundle(tmp_path) -> dict:
    """Train on a small synthetic set WITHOUT touching the real model artifact."""
    df = generate(n_override=900, end_date=pd.Timestamp("2026-09-30"), seed=7)
    out = tmp_path / "model_test.joblib"
    train(df, seed=7, out_path=out)
    return joblib.load(out)


def test_training_reports_metrics(tmp_path):
    bundle = _small_bundle(tmp_path)
    metrics = bundle["metrics"]
    assert 0 <= metrics["accuracy"] <= 1
    assert metrics["macro_f1"] > metrics["baseline_majority_macro_f1"] - 0.05
    assert 0 < metrics["severe_base_rate"] < 1
    assert metrics["brier_fatal"] <= 0.25


def test_prediction_shape_and_risk_ordering(tmp_path):
    bundle = _small_bundle(tmp_path)
    predictor = RiskPredictor(bundle)
    res_night = predictor.predict(NIGHT)
    res_day = predictor.predict(DAY)
    assert set(res_night["probabilities"]) == set(config.SEVERITIES)
    assert abs(sum(res_night["probabilities"].values()) - 1) < 1e-6
    assert res_night["risk_band"] in {"Low", "Moderate", "Elevated", "High"}
    # The generator encodes night+fog+motorway+high-speed as far riskier.
    assert res_night["severe_probability"] > res_day["severe_probability"]


def test_explanations_present(tmp_path):
    bundle = _small_bundle(tmp_path)
    ex = Explainer(bundle)
    out = ex.top_factors(NIGHT, k=5)
    assert len(out["factors"]) == 5
    for fac in out["factors"]:
        assert fac["feature"] in config.FEATURES
        assert fac["direction"] in {"increases risk", "lowers risk"}
    assert out["explanation_mode"] in {"shap", "counterfactual (approximate)"}


def test_production_model_exists_and_passes_floors():
    """The artifact shipped with the app must meet the agreed floors."""
    if not config.MODEL_FILE.exists():
        from roadsafe.ml.train import train as _t
        _t()
    bundle = joblib.load(config.MODEL_FILE)
    m = bundle["metrics"]
    assert m["macro_f1"] >= 0.31
    assert m["severe_pr_auc"] / m["severe_base_rate"] >= 1.35
    assert m["brier_fatal"] <= 0.0380


# --------------------------------------------------------- self-heal tests --
def _small_train(original, path):
    """Run a small real training via the ORIGINAL train (never the patched attr)."""
    df = generate(n_override=900, end_date=pd.Timestamp("2026-09-30"), seed=7)
    return original(df, seed=7, out_path=path)


def test_load_predictor_self_heals_on_corrupt_artifact(tmp_path, monkeypatch):
    from roadsafe.ml import train as train_mod
    from roadsafe.services import predictor as pred_mod

    bad = tmp_path / "model.joblib"
    bad.write_bytes(b"definitely not a joblib file")
    real_train = train_mod.train                     # capture BEFORE patching
    monkeypatch.setattr(pred_mod.config, "MODEL_FILE", bad)
    monkeypatch.setattr(train_mod, "train",
                        lambda *a, **k: _small_train(real_train, bad))

    predictor = pred_mod.load_predictor()
    res = predictor.predict(DAY)
    assert 0 <= res["severe_probability"] <= 1
    assert joblib.load(bad).get("sklearn_version")   # artifact rebuilt and stamped


def test_load_predictor_retrains_on_version_mismatch(tmp_path, monkeypatch):
    from roadsafe.ml import train as train_mod
    from roadsafe.services import predictor as pred_mod

    model_path = tmp_path / "model.joblib"
    _small_train(train_mod.train, model_path)
    bundle = joblib.load(model_path)
    bundle["sklearn_version"] = "0.99.fake"          # simulate an old/new sklearn
    joblib.dump(bundle, model_path)
    real_train = train_mod.train
    monkeypatch.setattr(pred_mod.config, "MODEL_FILE", model_path)
    monkeypatch.setattr(train_mod, "train",
                        lambda *a, **k: _small_train(real_train, model_path))

    predictor = pred_mod.load_predictor()
    assert predictor.predict(DAY)["risk_band"]
    assert joblib.load(model_path)["sklearn_version"] != "0.99.fake"  # re-stamped
