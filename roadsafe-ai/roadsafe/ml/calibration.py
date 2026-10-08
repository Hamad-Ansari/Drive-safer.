"""Probability calibration by temperature scaling.

Why temperature scaling (and not Platt/isotonic)? Evaluated in
docs/DECISIONS.md: per-class sigmoid and isotonic calibration on the held-out
years heavily flattened rare-but-real high-risk slices (e.g. fog + motorway +
night) toward the base rate, because those slices have almost no calibration
rows. Temperature scaling fits ONE global parameter T on held-out years — it
can only shrink overconfidence, it preserves ranking exactly (PR-AUC unchanged),
and it leaves well-separated slices visibly separated.
"""
from __future__ import annotations

import numpy as np


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class TempScaledPredictor:
    """Wrap a fitted pipeline with a single temperature parameter T."""

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.classes_ = pipeline.classes_
        self.temperature = 1.0

    def fit_temperature(self, X, y) -> float:
        from scipy.optimize import minimize_scalar
        from sklearn.metrics import log_loss

        base_p = np.clip(self.pipeline.predict_proba(X), 1e-9, 1.0)
        logits = np.log(base_p)

        def nll(log_t: float) -> float:
            t = float(np.exp(log_t))
            return float(log_loss(y, _softmax(logits / t), labels=self.classes_))

        res = minimize_scalar(nll, bounds=(-1.0, 1.5), method="bounded")
        self.temperature = float(np.exp(res.x))
        return self.temperature

    def predict_proba(self, X) -> np.ndarray:
        base_p = np.clip(self.pipeline.predict_proba(X), 1e-9, 1.0)
        return _softmax(np.log(base_p) / self.temperature)

    def predict(self, X) -> np.ndarray:
        return np.asarray(self.classes_)[self.predict_proba(X).argmax(axis=1)]
