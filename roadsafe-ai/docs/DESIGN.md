# DESIGN.md — design system & accessibility

## Tokens (light theme; Streamlit dark mode inherits base colours)

| Token | Value | Use |
| --- | --- | --- |
| Primary (trust blue) | `#1D4ED8` | hero gradient, accents, links, focus rings |
| Danger (red light) | `#DC2626` | fatal, errors, red bulbs |
| Warning (amber) | `#D97706` / `#F59E0B` | serious, amber bulbs |
| Success (green) | `#16A34A` | minor, green bulbs |
| Text | `#0F172A` | body |
| Muted | `#64748B` | captions, social icons at rest |
| Surface radius | 12 px | cards, metrics |
| Motion | 150–250 ms ease-out | hovers; disabled under reduced motion |

Red/amber/green are **never the only signal**: bulbs pair with text descriptions, severity pairs
with labels, risk bands pair with words (Low/Moderate/Elevated/High).

## Components

- **SocialLinks** (`roadsafe/core/icons.py:social_links_html`) — renders from
  `config/socials.json`; variants: footer (compact) and about (large + labels). 44 px target,
  18–22 px glyph, `aria-label` + tooltip (`"Hammad Zahid on GitHub"`), `target="_blank"`
  `rel="noopener noreferrer"`, visible `:focus-visible` ring. Adding/removing a platform is a
  JSON edit; a unit test validates every entry.
- **Sign rendering** — schematic inline SVG (octagon, inverted triangle, red ring, blue disc,
  info rectangles). No CDN assets: fully offline-renderable.
- **Simulator SVG** — intersection with POV car in the left lane (LHT), 4 signal heads, turn
  arrows, pedestrian lights; every phase carries `description` + `driver_action` text.

## Accessibility checklist (v0.1 status)

- [x] Text alternative for every chart (caption summary + data table + CSV export)
- [x] Simulator: no autoplay, Play toggle, step control, per-phase text description
- [x] Colour never the only signal (icons/words paired)
- [x] Keyboard-reachable native Streamlit controls; focus ring on custom social links
- [x] Reduced motion: tips carousel and simulator only move after explicit user opt-in
- [x] Contrast: primary/danger/warning/success on white ≥ 4.5:1 for text usage
- [ ] Urdu RTL (`Noto Nastaliq Urdu`) — v0.2 (F10)
- [ ] Screen-reader pass on the Streamlit chat widgets — v0.2
