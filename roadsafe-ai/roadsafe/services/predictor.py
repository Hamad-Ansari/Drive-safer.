"""Prediction service — thin, cached access to the trained model bundle."""
from __future__ import annotations

import warnings

import pandas as pd

from roadsafe.core import config
from roadsafe.ml.explain import Explainer


class RiskPredictor:
    """Load the saved bundle once, then answer form submissions."""

    def __init__(self, bundle: dict):
        self.bundle = bundle
        self.predictor = bundle["predictor"]
        self.classes: list[str] = bundle["classes"]
        self.display_order: list[str] = bundle["severity_display_order"]
        self.explainer = Explainer(bundle)

    # ------------------------------------------------------------------ #
    def predict(self, form: dict) -> dict:
        X = pd.DataFrame([form])[config.FEATURES]
        probs = self.predictor.predict_proba(X)[0]
        prob_map = {cls: float(p) for cls, p in zip(self.classes, probs)}
        severe = prob_map["Serious injury"] + prob_map["Fatal"]
        result = self.explainer.top_factors(form, k=5)
        return {
            "predicted_class": result["class"],
            "probabilities": {cls: prob_map[cls] for cls in self.display_order},
            "severe_probability": round(float(severe), 4),
            "risk_band": self._band(severe),
            "factors": result["factors"],
            "explanation_mode": result["explanation_mode"],
        }

    @staticmethod
    def _band(severe: float) -> str:
        if severe >= 0.50:
            return "High"
        if severe >= 0.30:
            return "Elevated"
        if severe >= 0.15:
            return "Moderate"
        return "Low"


_HONESTY = (
    "This estimate is learned from historical patterns in demo data. It describes "
    "risk for similar conditions — it does not predict whether a specific crash "
    "will happen."
)


def _retrain_locally() -> dict:
    """Deterministic rebuild: (re)generate the seeded data if missing, train, reload."""
    if not config.ACCIDENTS_CSV.exists():
        from roadsafe.ml.generate_data import generate
        config.RAW_DIR.mkdir(parents=True, exist_ok=True)
        generate().to_csv(config.ACCIDENTS_CSV, index=False)
    from roadsafe.ml.train import train
    train()
    import joblib
    return joblib.load(config.MODEL_FILE)


def load_predictor() -> RiskPredictor:
    """Load the trained model; verify version compatibility; self-heal if needed."""
    import joblib
    import sklearn

    if not config.MODEL_FILE.exists():
        warnings.warn("No trained model found — training one now (deterministic, ~15 s).")
        return RiskPredictor(_retrain_locally())
    try:
        bundle = joblib.load(config.MODEL_FILE)
        saved = bundle.get("sklearn_version")
        if saved != sklearn.__version__:
            raise RuntimeError(
                f"model.joblib was trained with scikit-learn {saved or 'an unknown version'} "
                f"but this environment has {sklearn.__version__}; persisted sklearn "
                f"pipelines are not portable across versions.")
    except Exception as exc:  # unpickle errors, missing attrs, version mismatch
        warnings.warn(
            f"Could not reuse the saved model ({exc}). Retraining locally on the "
            "seeded demo data — this happens once, then the artifact matches your "
            "environment. (Tip: `pip install -r requirements.txt` also fixes this.)")
        return RiskPredictor(_retrain_locally())
    return RiskPredictor(bundle)


def honesty_notice() -> str:
    return _HONESTY
