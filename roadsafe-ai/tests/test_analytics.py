"""Analytics service correctness against the generator's invariants."""
from __future__ import annotations

import pandas as pd

from roadsafe.services import analytics


def _df() -> pd.DataFrame:
    from roadsafe.ml.generate_data import generate
    return generate(n_override=1500, end_date=pd.Timestamp("2023-12-31"))


def test_filters_narrow_the_frame():
    df = _df()
    some_year = int(df["year"].iloc[0])
    out = analytics.apply_filters(df, years=[some_year])
    assert len(out) <= len(df)
    assert (out["year"] == some_year).all()
    out2 = analytics.apply_filters(df, severities=["Fatal"])
    assert (out2["severity"] == "Fatal").all()


def test_kpis_are_sane():
    k = analytics.kpis(_df())
    assert k["total"] > 0
    assert 0 <= k["injury_rate"] <= 1
    assert 0 <= k["peak_hour"] <= 23
    assert k["top_cause"]
    assert k["deaths_per_100"] >= 0


def test_hour_weekday_matrix_shape():
    mat = analytics.hour_weekday_matrix(_df())
    assert mat.shape[0] == 7
    assert mat.shape[1] <= 24
    assert (mat >= 0).all().all()


def test_town_map_counts_cover_all_towns():
    tm = analytics.town_map_counts(_df())
    assert len(tm) == 11
    assert (tm["accidents"] >= 0).all()
