"""Analytics service — all dashboard aggregations as pure pandas functions.

The Streamlit page stays thin: filters in, DataFrames/figures out. Everything
here is unit-testable without Streamlit.
"""
from __future__ import annotations

import pandas as pd

from roadsafe.core import config


def apply_filters(df: pd.DataFrame, years=None, towns=None, weather=None,
                  road_types=None, lighting=None, severities=None) -> pd.DataFrame:
    out = df
    if years:
        out = out[out["year"].isin(years)]
    if towns:
        out = out[out["town"].isin(towns)]
    if weather:
        out = out[out["weather"].isin(weather)]
    if road_types:
        out = out[out["road_type"].isin(road_types)]
    if lighting:
        out = out[out["lighting"].isin(lighting)]
    if severities:
        out = out[out["severity"].isin(severities)]
    return out


def kpis(df: pd.DataFrame) -> dict:
    total = int(len(df))
    deaths = int(df["deaths"].sum())
    injured = int(df["injured"].sum())
    injury_rate = float((df["injured"] > 0).mean()) if total else 0.0

    by_hour_deaths = df.groupby("hour")["deaths"].sum()
    by_hour_count = df.groupby("hour").size()
    if total == 0:
        peak_hour = 0
    else:
        peak_hour = int((by_hour_deaths if by_hour_deaths.sum() > 0 else by_hour_count).idxmax())
    top_cause = df["cause"].value_counts().idxmax() if total else "—"

    return {
        "total": total,
        "deaths": deaths,
        "injured": injured,
        "injury_rate": injury_rate,
        "deaths_per_100": round(deaths / total * 100, 1) if total else 0.0,
        "peak_hour": peak_hour,
        "peak_hour_label": _hour_label(peak_hour),
        "top_cause": top_cause,
    }


def _hour_label(hour: int) -> str:
    h = int(hour) % 24
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12:00d} {ampm}–{((h + 1) % 12) or 12} {'AM' if (h + 1) % 24 < 12 else 'PM'}"


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    out = (df.assign(ym=df["date_time"].dt.to_period("M").astype(str))
             .groupby("ym", as_index=False)
             .agg(accidents=("accident_id", "count"), deaths=("deaths", "sum")))
    return out


def severity_by_year(df: pd.DataFrame) -> pd.DataFrame:
    ct = pd.crosstab(df["year"], df["severity"])
    for col in config.SEVERITIES:
        if col not in ct:
            ct[col] = 0
    return ct[config.SEVERITIES].reset_index()


def hour_weekday_matrix(df: pd.DataFrame) -> pd.DataFrame:
    order = list(config.WEEKDAY_NAMES)
    mat = (df.pivot_table(index="weekday_name", columns="hour",
                          values="accident_id", aggfunc="count")
             .reindex(order).fillna(0))
    return mat


def top_causes(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    return df["cause"].value_counts().head(n).rename_axis("cause").reset_index(name="accidents")


def by_town(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("town", as_index=False)
              .agg(accidents=("accident_id", "count"), deaths=("deaths", "sum"))
              .sort_values("accidents", ascending=False))


def severity_mix(df: pd.DataFrame) -> pd.Series:
    return df["severity"].value_counts().reindex(config.SEVERITIES).fillna(0).astype(int)


def town_map_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Accident counts per town joined with schematic tile coordinates."""
    base = pd.DataFrame(
        [{"town": t, "gx": xy[0], "gy": xy[1]} for t, xy in config.TOWNS.items()]
    )
    counts = df.groupby("town").size().rename("accidents").reset_index()
    deaths = df.groupby("town")["deaths"].sum().rename("deaths").reset_index()
    out = base.merge(counts, on="town", how="left").merge(deaths, on="town", how="left")
    out[["accidents", "deaths"]] = out[["accidents", "deaths"]].fillna(0).astype(int)
    return out
