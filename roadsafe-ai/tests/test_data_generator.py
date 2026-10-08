"""Synthetic data generator: schema, ranges, leakage guards."""
from __future__ import annotations

import pandas as pd

from roadsafe.core import config
from roadsafe.ml.generate_data import generate


def test_schema_and_ranges():
    df = generate(n_override=400, end_date=pd.Timestamp("2023-12-31"))
    assert len(df) > 0
    for col in ("accident_id", "date_time", "year", "hour", "town", "road_type",
                "weather", "lighting", "severity", "cause"):
        assert col in df.columns
    assert df["hour"].between(0, 23).all()
    assert df["month"].between(1, 12).all()
    assert df["severity"].isin(config.SEVERITIES).all()
    assert df["town"].isin(config.TOWNS).all()
    assert df["weather"].isin(config.WEATHER_TYPES).all()
    assert df["speed_zone"].isin(config.SPEED_ZONES).all()
    assert df["deaths"].ge(0).all() and df["injured"].ge(0).all()
    assert df.isna().sum().sum() == 0


def test_severity_imbalance_exists():
    df = generate(n_override=2000, end_date=pd.Timestamp("2023-12-31"))
    shares = df["severity"].value_counts(normalize=True)
    assert shares["Minor injury"] > 0.5, "minor should dominate"
    assert shares["Fatal"] < 0.15, "fatal should be rare"


def test_no_leakage_in_model_features():
    post_event = {"cause", "injured", "deaths", "vehicles_involved"}
    assert not post_event & set(config.FEATURES)
