# RoadSafe AI — PRD (Track A MVP)

Owner: Hammad Zahid · Jurisdiction: Pakistan National + Punjab · Demo city: Lahore · v0.1 (Oct 2026)

## 1. Vision

Help citizens, learner drivers and students (a) explore accident risk honestly, (b) learn traffic
law with citations, (c) master signals and signs, and (d) report incidents — in one accessible app.

## 2. Personas

- **Learner driver (18–25, Lahore)** — wants signals/signs fluency and a licence-prep quiz.
- **Commuter** — wants quick "is this route/condition risky?" answers and rule lookups.
- **Student/analyst** — wants the dashboard, the data dictionary and the honest model card.

## 3. Functional requirements

| ID | Requirement | Priority | Status in v0.1 |
| --- | --- | --- | --- |
| F1 | Dashboard filters (year, town, weather, road type, lighting, severity) update all charts together | Must | ✅ |
| F2 | KPI cards: total accidents, fatalities, injury rate, most dangerous hour, top cause | Must | ✅ |
| F3 | Risk predictor returns band + calibrated probability + top-5 factors | Must | ✅ |
| F4 | Law assistant answers with citations and a refusal path | Must | ✅ |
| F5 | Signal simulator: R/A/G, protected right arrows, flashing, pedestrian, roundabout | Must | ✅ |
| F6 | Quiz ≥100 questions, categories, difficulty, explanations, saved scores | Must | ✅ (106) |
| F7 | Sign library with search + category filter | Should | ✅ |
| F8 | Incident report with validation + list view | Should | ✅ |
| F9 | Sign recognition from photo | Could | ⏳ v0.3 |
| F10 | English/Urdu toggle with RTL | Could | ⏳ v0.2 |
| F11 | Export dashboard view as PDF/CSV | Could | ✅ CSV (PDF in v0.2) |
| F12 | Social icon bar + About page from config | Must | ✅ |

## 4. Non-functional requirements

- **Honesty**: synthetic data labelled in-product; model metrics published; assistant cites or refuses.
- **Accessibility**: text descriptions for every chart/simulator state; keyboard-reachable controls;
  colour never the only signal; no autoplay without consent.
- **Privacy**: reports carry no personal identifiers; photos type/size checked and EXIF-stripped.
- **Performance**: filtered aggregates over ~26k rows render in well under a second (cached loader).

## 5. Out of scope (v0.1)

Real (licensed) accident micro-data, user accounts, multi-city data, live enforcement data.
