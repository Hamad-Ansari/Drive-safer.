"""Generate a realistic *synthetic* accident dataset for Lahore (2020–2026).

Why synthetic: no license-clean, public accident micro-data exists for Lahore at
the row level, and RoadSafe AI must never publish guessed real statistics. This
generator encodes published road-safety *patterns* (fog season, monsoon, rush
hours, motorway severity, night risk) with a known logistic data-generating
process, so the ML module has honest structure to learn. The dataset is clearly
labelled synthetic everywhere it appears.

Every distribution choice below is documented in docs/DECISIONS.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from roadsafe.core import config

BASE_PER_YEAR = 3_300
YEAR_GROWTH = 1.045          # accidents grow ~4.5%/yr with traffic volume
END_DATE = pd.Timestamp("2026-09-30")

HOUR_WEIGHTS = np.array([
    2.0, 1.6, 1.2, 1.1, 1.2, 2.2,          # 00–05 quiet night
    4.0, 7.0, 11.0, 10.0, 7.0, 6.0,        # 06–11 morning rush peak at 8–9
    6.0, 6.5, 6.0, 6.5, 7.0, 10.0,         # 12–17
    11.0, 9.0, 7.0, 5.0, 3.5, 2.5,         # 18–23 evening rush peak at 18
])

TOWN_WEIGHTS = {
    "Gulberg": 0.12, "Data Ganj Bakhsh": 0.12, "Cantonment": 0.12,
    "Shalimar": 0.10, "Model Town": 0.10, "Ravi": 0.09,
    "Allama Iqbal": 0.09, "Samanabad": 0.08, "Aziz Bhatti": 0.08,
    "Wagha": 0.06, "Nishtar": 0.04,
}

# Weather probabilities by month index (1–12). Encodes Lahore's climate:
# Dec–Jan fog/smog season, Jul–Sep monsoon, May–Jun dust storms.
WEATHER_BY_MONTH: dict[int, list[tuple[str, float]]] = {
    12: [("Clear", .34), ("Haze / Smog", .30), ("Fog", .22), ("Overcast", .10), ("Light Rain", .04)],
    1:  [("Clear", .32), ("Haze / Smog", .30), ("Fog", .24), ("Overcast", .10), ("Light Rain", .04)],
    2:  [("Clear", .45), ("Haze / Smog", .33), ("Fog", .08), ("Overcast", .10), ("Light Rain", .04)],
    11: [("Clear", .45), ("Haze / Smog", .35), ("Fog", .08), ("Overcast", .10), ("Light Rain", .02)],
    7:  [("Clear", .40), ("Overcast", .18), ("Light Rain", .24), ("Heavy Rain", .15), ("Dust Storm", .03)],
    8:  [("Clear", .40), ("Overcast", .18), ("Light Rain", .24), ("Heavy Rain", .15), ("Dust Storm", .03)],
    9:  [("Clear", .46), ("Overcast", .16), ("Light Rain", .22), ("Heavy Rain", .13), ("Dust Storm", .03)],
    5:  [("Clear", .48), ("Haze / Smog", .14), ("Dust Storm", .14), ("Overcast", .07), ("Light Rain", .10), ("Heavy Rain", .07)],
    6:  [("Clear", .45), ("Haze / Smog", .15), ("Dust Storm", .15), ("Overcast", .07), ("Light Rain", .10), ("Heavy Rain", .08)],
    3:  [("Clear", .62), ("Haze / Smog", .14), ("Overcast", .11), ("Light Rain", .09), ("Heavy Rain", .04)],
    4:  [("Clear", .60), ("Haze / Smog", .15), ("Overcast", .12), ("Light Rain", .08), ("Heavy Rain", .03), ("Dust Storm", .02)],
    10: [("Clear", .62), ("Haze / Smog", .15), ("Overcast", .12), ("Light Rain", .08), ("Heavy Rain", .03)],
}

# Road-type mix per town (motorway access and highways concentrate in the east).
ROAD_MIX: dict[str, list[tuple[str, float]]] = {
    "Cantonment": [("Main Boulevard", .28), ("Arterial Road", .24), ("Collector Road", .20), ("Local Street", .16), ("Motorway / Expressway", .08), ("National Highway (N-5)", .04)],
    "Gulberg": [("Main Boulevard", .32), ("Arterial Road", .26), ("Collector Road", .20), ("Local Street", .18), ("National Highway (N-5)", .04)],
    "Data Ganj Bakhsh": [("Main Boulevard", .26), ("Arterial Road", .24), ("Collector Road", .24), ("Local Street", .24), ("National Highway (N-5)", .02)],
    "Shalimar": [("Arterial Road", .26), ("Collector Road", .26), ("Local Street", .26), ("Main Boulevard", .14), ("National Highway (N-5)", .05), ("Motorway / Expressway", .03)],
    "Ravi": [("Collector Road", .30), ("Local Street", .30), ("Arterial Road", .20), ("National Highway (N-5)", .14), ("Main Boulevard", .06)],
    "Model Town": [("Main Boulevard", .30), ("Arterial Road", .22), ("Collector Road", .24), ("Local Street", .20), ("National Highway (N-5)", .04)],
    "Allama Iqbal": [("Main Boulevard", .28), ("Arterial Road", .26), ("Collector Road", .22), ("Local Street", .20), ("Motorway / Expressway", .04)],
    "Samanabad": [("Collector Road", .30), ("Local Street", .28), ("Main Boulevard", .24), ("Arterial Road", .18)],
    "Aziz Bhatti": [("Arterial Road", .26), ("Main Boulevard", .24), ("Collector Road", .26), ("Local Street", .18), ("Motorway / Expressway", .06)],
    "Wagha": [("Collector Road", .30), ("Local Street", .30), ("Arterial Road", .18), ("National Highway (N-5)", .18), ("Motorway / Expressway", .04)],
    "Nishtar": [("Collector Road", .32), ("Local Street", .30), ("Arterial Road", .20), ("Main Boulevard", .12), ("National Highway (N-5)", .06)],
}

SPEED_BY_ROAD: dict[str, list[tuple[int, float]]] = {
    # index into config.SPEED_ZONES
    "Motorway / Expressway": [(1, .06), (2, .16), (3, .30), (4, .48)],
    "National Highway (N-5)": [(1, .14), (2, .36), (3, .34), (4, .16)],
    "Main Boulevard": [(0, .16), (1, .55), (2, .29)],
    "Arterial Road": [(0, .22), (1, .52), (2, .26)],
    "Collector Road": [(0, .42), (1, .48), (2, .10)],
    "Local Street": [(0, .72), (1, .26), (2, .02)],
}

JUNCTION_BY_ROAD: dict[str, list[tuple[str, float]]] = {
    "Motorway / Expressway": [("Mid-block", .72), ("U-Turn Point", .16), ("Unsignalized Intersection", .12)],
    "National Highway (N-5)": [("Mid-block", .50), ("Unsignalized Intersection", .28), ("U-Turn Point", .16), ("Roundabout", .06)],
    "Main Boulevard": [("Signalized Intersection", .34), ("Mid-block", .34), ("Unsignalized Intersection", .22), ("Roundabout", .06), ("U-Turn Point", .04)],
    "Arterial Road": [("Signalized Intersection", .30), ("Mid-block", .34), ("Unsignalized Intersection", .26), ("Roundabout", .06), ("U-Turn Point", .04)],
    "Collector Road": [("Mid-block", .42), ("Unsignalized Intersection", .34), ("Signalized Intersection", .16), ("Roundabout", .08)],
    "Local Street": [("Mid-block", .62), ("Unsignalized Intersection", .32), ("Roundabout", .06)],
}

CAUSES = [
    "Overspeeding", "Wrong-side / Wrong-lane driving", "Red-light jumping",
    "Tailgating", "Mobile phone use", "Fatigue / Drowsy driving",
    "Overtaking violation", "Mechanical failure", "Weather / Low visibility",
    "Pedestrian sudden crossing", "Animal on road", "Unlicensed / Novice driver",
]


def _pick(rng: np.random.Generator, options: list[tuple[str, float]]) -> str:
    labels = [o[0] for o in options]
    probs = np.array([o[1] for o in options], dtype=float)
    probs = probs / probs.sum()
    return str(rng.choice(labels, p=probs))


def _lighting(rng: np.random.Generator, hour: int, town: str) -> str:
    affluent = town in {"Gulberg", "Cantonment", "Model Town"}
    if 8 <= hour <= 16:
        return _pick(rng, [("Daylight", .95), ("Dawn / Dusk", .05)])
    if hour in (6, 7, 17, 18):
        return _pick(rng, [("Daylight", .40), ("Dawn / Dusk", .45), ("Dark — Street Lit", .12), ("Dark — Unlit", .03)])
    lit = .72 if affluent else .52
    return _pick(rng, [("Dark — Street Lit", lit), ("Dark — Unlit", 1 - lit)])


def _severity(rng: np.random.Generator, speed_idx: int, lighting: str, weather: str,
              road_type: str, junction: str, condition: str, hour: int, is_weekend: bool) -> str:
    """Two-logit multinomial severity with known coefficients + noise.

    Keeps the signal learnable but imperfect — realistic class overlap.
    """
    night = hour <= 5 or hour >= 21
    unlit = lighting == "Dark — Unlit"
    fog = weather == "Fog"
    heavy_rain = weather == "Heavy Rain"
    mway = road_type == "Motorway / Expressway"
    highway = road_type == "National Highway (N-5)"
    midblock = junction == "Mid-block"

    serious = (
        -1.55
        + 0.55 * (speed_idx >= 2) + 0.75 * (speed_idx >= 3) + 0.65 * (speed_idx >= 4)
        + 0.70 * unlit + 0.35 * (lighting == "Dark — Street Lit")
        + 0.55 * fog + 0.45 * heavy_rain
        + 0.45 * mway + 0.30 * highway
        + 0.35 * (condition == "Potholed")
        + 0.30 * night + 0.25 * (is_weekend and night)
    )
    fatal = (
        -3.60
        + 0.85 * (speed_idx >= 3) + 0.95 * (speed_idx >= 4)
        + 0.85 * unlit + 0.35 * (lighting == "Dawn / Dusk")
        + 0.70 * fog + 0.45 * heavy_rain
        + 0.85 * mway + 0.40 * highway
        + 0.45 * midblock
        + 0.35 * night + 0.40 * (is_weekend and night)
    )
    serious += float(rng.normal(0, 0.42))
    fatal += float(rng.normal(0, 0.36))
    logits = np.array([0.0, serious, fatal])
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()
    return str(rng.choice(config.SEVERITIES, p=probs))


def _cause(rng: np.random.Generator, road_type: str, junction: str, weather: str,
           hour: int, speed_idx: int) -> str:
    night = hour <= 5 or hour >= 21
    weights = {
        "Overspeeding": .16 + .12 * (speed_idx >= 3),
        "Wrong-side / Wrong-lane driving": .09,
        "Red-light jumping": .18 if junction == "Signalized Intersection" else .02,
        "Tailgating": .10 + .08 * (road_type == "Motorway / Expressway"),
        "Mobile phone use": .08,
        "Fatigue / Drowsy driving": .04 + .07 * night,
        "Overtaking violation": .09,
        "Mechanical failure": .07,
        "Weather / Low visibility": .26 if weather in {"Fog", "Heavy Rain", "Dust Storm"} else .02,
        "Pedestrian sudden crossing": 0.0 if road_type == "Motorway / Expressway" else .12,
        "Animal on road": .08 if road_type in {"Motorway / Expressway", "National Highway (N-5)"} else .02,
        "Unlicensed / Novice driver": .07,
    }
    opts = [(c, w) for c, w in weights.items()]
    return _pick(rng, opts)


def generate(n_override: int | None = None, end_date: pd.Timestamp | None = None,
            seed: int = config.RANDOM_SEED) -> pd.DataFrame:
    """Return the full synthetic accidents DataFrame (deterministic by seed)."""
    rng = np.random.default_rng(seed)
    end_date = end_date or END_DATE
    towns = list(TOWN_WEIGHTS)
    rows: list[dict] = []
    aid = 0
    years = range(2020, end_date.year + 1)
    for year in years:
        n_year = n_override or int(BASE_PER_YEAR * YEAR_GROWTH ** (year - 2020))
        start = pd.Timestamp(f"{year}-01-01")
        stop = min(pd.Timestamp(f"{year}-12-31"), end_date)
        span_days = (stop - start).days + 1
        day_offsets = rng.integers(0, span_days, size=n_year)
        hours = rng.choice(24, size=n_year, p=HOUR_WEIGHTS / HOUR_WEIGHTS.sum())
        for i in range(n_year):
            aid += 1
            date = start + pd.Timedelta(days=int(day_offsets[i]))
            hour = int(hours[i])
            month = int(date.month)
            is_weekend = int(date.dayofweek >= 5)
            weekday_name = config.WEEKDAY_NAMES[date.dayofweek]
            town = str(rng.choice(towns, p=np.array([TOWN_WEIGHTS[t] for t in towns]) /
                                  np.array([TOWN_WEIGHTS[t] for t in towns]).sum()))
            weather = _pick(rng, WEATHER_BY_MONTH[month])
            lighting = _lighting(rng, hour, town)
            road_type = _pick(rng, ROAD_MIX[town])
            speed_idx = int(rng.choice(5, p=np.array(
                [next((p for s, p in SPEED_BY_ROAD[road_type] if s == k), 0.0) for k in range(5)])))
            speed_idx = min(max(speed_idx, 0), 4)
            junction = _pick(rng, JUNCTION_BY_ROAD[road_type])
            if weather in {"Light Rain", "Heavy Rain"}:
                condition = _pick(rng, [("Wet", .78), ("Potholed", .10), ("Dry", .08), ("Under Construction", .04)])
            else:
                cond_p = .16 if town in {"Ravi", "Wagha", "Nishtar"} else .09
                condition = _pick(rng, [("Dry", .74 - cond_p), ("Potholed", cond_p),
                                        ("Under Construction", .06), ("Wet", .10)])
            severity = _severity(rng, speed_idx, lighting, weather, road_type, junction,
                                 condition, hour, bool(is_weekend))
            cause = _cause(rng, road_type, junction, weather, hour, speed_idx)
            vehicles = int(rng.poisson(1.2)) + 1
            if severity == "Minor injury":
                injured = int(rng.integers(0, 3))
                deaths = 0
            elif severity == "Serious injury":
                injured = int(rng.integers(1, 4))
                deaths = int(rng.random() < 0.04)
            else:
                injured = int(rng.integers(1, 5))
                deaths = 1 + int(rng.poisson(0.35))
            gx, gy = config.TOWNS[town]
            dt = date.replace(hour=hour, minute=int(rng.integers(0, 60)))
            rows.append({
                "accident_id": f"LA-{aid:06d}",
                "date_time": dt.isoformat(sep=" "),
                "year": year, "month": month, "hour": hour,
                "weekday": int(date.dayofweek), "weekday_name": weekday_name,
                "is_weekend": is_weekend, "town": town,
                "road_type": road_type, "speed_zone": config.SPEED_ZONES[speed_idx],
                "junction_type": junction, "weather": weather, "lighting": lighting,
                "road_condition": condition, "cause": cause,
                "vehicles_involved": vehicles, "severity": severity,
                "injured": injured, "deaths": deaths,
                "grid_x": round(gx + float(rng.normal(0, .55)), 3),
                "grid_y": round(gy + float(rng.normal(0, .55)), 3),
            })
    return pd.DataFrame(rows)


def main() -> None:
    df = generate()
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = config.ACCIDENTS_CSV
    df.to_csv(out, index=False)
    print(f"wrote {len(df):,} rows -> {out}")
    print(df["severity"].value_counts(normalize=True).round(3).to_dict())
    print(df["deaths"].sum(), "fatalities |", df["injured"].sum(), "injured")
    print("leakage check — post-event cols NOT in FEATURES:",
          [c for c in ("cause", "injured", "deaths", "vehicles_involved") if c not in config.FEATURES])


if __name__ == "__main__":
    main()
