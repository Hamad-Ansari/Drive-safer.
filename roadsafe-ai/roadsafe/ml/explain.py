"""Local explanations for predictions — SHAP when available, honest fallback.

Uses SHAP's TreeExplainer on the calibrated model's underlying LightGBM, with
one-hot columns grouped back to original features. If SHAP is unavailable or
errors, falls back to a transparent single-row counterfactual attribution
(probability change when each feature is set to its training-typical value),
which is labelled as approximate in the UI.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from roadsafe.core import config

FRIENDLY = {
    "hour": "Time of day",
    "month": "Month",
    "is_weekend": "Weekend",
    "weather": "Weather",
    "road_type": "Road type",
    "lighting": "Lighting",
    "road_condition": "Road condition",
    "speed_zone": "Speed zone",
    "junction_type": "Junction type",
    "town": "Area",
}


def _fmt_value(feature: str, value) -> str:
    if feature == "hour":
        h = int(value)
        return f"{(h % 12) or 12} {'AM' if h < 12 else 'PM'} ({h:02d}:00)"
    if feature == "month":
        return config.MONTH_NAMES[int(value) - 1]
    if feature == "is_weekend":
        return "Weekend" if int(value) else "Weekday"
    return str(value)


class Explainer:
    """Wrap a trained bundle to produce per-prediction factor attributions."""

    def __init__(self, bundle: dict):
        self.bundle = bundle
        self.predictor = bundle["predictor"]     # calibrated predict_proba (raw features)
        self.prep = bundle["prep"]               # fitted ColumnTransformer
        self.clf = bundle["clf"]                 # fitted LightGBM
        self.classes: list[str] = bundle["classes"]
        self.background: dict = bundle["background"]
        self._group_map = self._build_group_map()
        try:
            import shap  # noqa: PLC0415 — optional heavy import
            self._tree = shap.TreeExplainer(self.clf)
            self.mode = "shap"
        except Exception:  # pragma: no cover - exercised only without shap
            self._tree = None
            self.mode = "counterfactual"

    # ------------------------------------------------------------------ #
    def _build_group_map(self) -> list[tuple[int, str]]:
        """Map each transformed column index -> original feature name."""
        names = list(self.prep.get_feature_names_out())
        mapping: list[tuple[int, str]] = []
        cats = config.CATEGORICAL_FEATURES
        for idx, col in enumerate(names):
            stem = col.split("__", 1)[-1]
            hit = None
            for feat in cats:
                if stem.startswith(f"{feat}_"):
                    hit = feat
                    break
            if hit is None:
                hit = stem  # numeric passthrough keeps its name
            mapping.append((idx, hit))
        return mapping

    def _shap_contributions(self, X: pd.DataFrame, class_idx: int) -> dict[str, float]:
        transformed = self.prep.transform(X)
        sv = self._tree.shap_values(transformed)
        if isinstance(sv, list):                      # old shap: list per class
            values = np.asarray(sv[class_idx])[0]
        else:
            arr = np.asarray(sv)
            values = arr[0, :, class_idx] if arr.ndim == 3 else arr[0]
        out: dict[str, float] = {}
        for (idx, feat), val in zip(self._group_map, values):
            out[feat] = out.get(feat, 0.0) + float(val)
        return out

    def _counterfactual_contributions(self, X: pd.DataFrame, class_idx: int) -> dict[str, float]:
        base_p = float(self.predictor.predict_proba(X)[0, class_idx])
        out: dict[str, float] = {}
        row = X.iloc[0].to_dict()
        for feat in config.FEATURES:
            if row[feat] == self.background[feat]:
                out[feat] = 0.0
                continue
            shifted = dict(row)
            shifted[feat] = self.background[feat]
            p = float(self.predictor.predict_proba(pd.DataFrame([shifted]))[0, class_idx])
            out[feat] = base_p - p   # how much this feature moved us TOWARD the class
        return out

    def contributions(self, X: pd.DataFrame, class_idx: int) -> tuple[dict[str, float], str]:
        if self._tree is not None:
            try:
                return self._shap_contributions(X, class_idx), "shap"
            except Exception:
                pass
        return self._counterfactual_contributions(X, class_idx), "counterfactual (approximate)"

    def top_factors(self, input_row: dict, k: int = 5) -> dict:
        """Return top-k factors pushing the prediction toward its class."""
        X = pd.DataFrame([input_row])[config.FEATURES]
        probs = self.predictor.predict_proba(X)[0]
        class_idx = int(np.argmax(probs))
        contribs, mode = self.contributions(X, class_idx)
        ranked = sorted(contribs.items(), key=lambda kv: abs(kv[1]), reverse=True)[:k]
        factors = [
            {
                "feature": feat,
                "label": FRIENDLY.get(feat, feat),
                "value": _fmt_value(feat, X.iloc[0][feat]),
                "contribution": round(float(c), 4),
                "direction": "increases risk" if c > 0 else "lowers risk",
            }
            for feat, c in ranked
        ]
        return {
            "class": self.classes[class_idx],
            "class_index": class_idx,
            "probabilities": {cls: round(float(p), 4) for cls, p in zip(self.classes, probs)},
            "factors": factors,
            "explanation_mode": mode,
        }
