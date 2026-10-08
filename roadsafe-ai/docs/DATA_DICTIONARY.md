# DATA_DICTIONARY.md — `data/raw/lahore_accidents_synthetic.csv`

26,460 rows × 22 columns · seed 42 · **synthetic demo data (CC0-style: no license restrictions,
do not present as real statistics)**.

| Column | Type | Values / range | Notes |
| --- | --- | --- | --- |
| accident_id | str | `LA-000001…` | stable key |
| date_time | datetime | 2020-01-01 → 2026-09-30 | |
| year | int | 2020–2026 | split field (fit ≤2022, calib 23–24, test 25+) |
| month / hour | int | 1–12 / 0–23 | rush-hour & seasonal patterns encoded |
| weekday / weekday_name | int/str | 0=Mon…6=Sun | |
| is_weekend | int | 0/1 | Sat–Sun |
| town | str | 11 Lahore towns | weights in generator |
| road_type | str | Motorway / N-5 / Boulevard / Arterial / Collector / Local | |
| speed_zone | str | ≤40, 50–60, 70–80, 90–100, >100 km/h | index used in severity logits |
| junction_type | str | Mid-block, Signalized, Unsignalized, Roundabout, U-Turn | |
| weather | str | Clear, Haze/Smog, Fog, Overcast, Light/Heavy Rain, Dust Storm | month-conditional |
| lighting | str | Daylight, Dawn/Dusk, Dark — Street Lit, Dark — Unlit | hour-conditional |
| road_condition | str | Dry, Wet, Potholed, Under Construction | weather-conditional |
| cause | str | 12 causes | **post-event — never a model input** |
| vehicles_involved | int | 1–~6 | post-event |
| severity | str | Minor injury / Serious injury / Fatal | target (two-logit multinomial + noise) |
| injured / deaths | int | ≥ 0 | post-event |
| grid_x, grid_y | float | town centroid + jitter | schematic map only, **not GIS** |

## Licenses & credits

- Accident dataset: **synthetic, generated in-repo** — no external license constraints; label it
  as demo data whenever shown.
- Law corpus: **demo paraphrases** with source pointers to Punjab Traffic Police /
  NHMP official sites. Replace with verified gazette texts (with version dates) before any
  non-educational use.
- Quiz bank: written for this demo; every item links to a corpus section ID (test-enforced).
- Sign renderings: schematic, original SVGs; conventions follow regional LHT signage practice.
