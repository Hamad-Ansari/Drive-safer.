"""Traffic-signal scenarios as an explicit, testable state machine.

Pakistan drives on the LEFT, so the POV car approaches in the left lane and a
protected turn arrow protects the RIGHT turn (across oncoming traffic).
Each phase carries a full text description for accessibility, and the
simulator never auto-plays by default (reduced-motion friendly).
"""
from __future__ import annotations

from dataclasses import dataclass

RED = "#DC2626"
AMBER = "#F59E0B"
GREEN = "#16A34A"
OFF = "#334155"


@dataclass
class Phase:
    key: str
    title: str
    ns: str = "red"                 # light colours for North–South street
    ew: str = "red"
    ns_arrow: str = "off"           # off | green | yellow | red
    ew_arrow: str = "off"
    ped_ns: str = "stop"            # walk | flash | stop
    ped_ew: str = "stop"
    seconds: int = 5
    description: str = ""           # full state in words (screen readers)
    driver_action: str = ""         # what the POV driver must do


def basic_cycle() -> list[Phase]:
    return [
        Phase("ns_green", "North–South green", ns="green", ew="red", ped_ns="walk", seconds=6,
              description="North–South traffic has green; East–West is red. Pedestrians crossing N–S may walk.",
              driver_action="You may proceed straight. Yield to pedestrians on the crossing."),
        Phase("ns_amber", "North–South amber", ns="amber", ew="red", ped_ns="flash", seconds=2,
              description="North–South shows amber (about to turn red). East–West still red.",
              driver_action="Stop before the line if you can do so safely; otherwise clear the junction."),
        Phase("all_red_1", "All red (clearance)", ns="red", ew="red", ped_ns="stop", seconds=1,
              description="All approaches red for one second to clear the junction.",
              driver_action="Remain stopped behind the stop line."),
        Phase("ew_green", "East–West green", ns="red", ew="green", ped_ew="walk", seconds=6,
              description="East–West traffic has green; North–South is red.",
              driver_action="Remain stopped behind the stop line."),
        Phase("ew_amber", "East–West amber", ns="red", ew="amber", ped_ew="flash", seconds=2,
              description="East–West shows amber. North–South still red.",
              driver_action="Remain stopped."),
        Phase("all_red_2", "All red (clearance)", ns="red", ew="red", ped_ew="stop", seconds=1,
              description="All approaches red for one second to clear the junction.",
              driver_action="Get ready — your green is next."),
    ]


def protected_cycle() -> list[Phase]:
    return [
        Phase("ns_green", "N–S green (straight)", ns="green", ew="red", ns_arrow="off", seconds=5,
              description="North–South green for straight/left; right turns yield to oncoming.",
              driver_action="Straight or left turn. Right turn: yield to oncoming traffic."),
        Phase("ns_arrow", "N–S protected RIGHT arrow", ns="red", ew="red", ns_arrow="green", seconds=4,
              description="Green right-turn arrow for North–South. Oncoming traffic faces red.",
              driver_action="Green arrow — protected right turn. Watch for pedestrians."),
        Phase("ns_amber", "N–S amber + amber arrow", ns="amber", ew="red", ns_arrow="yellow", ped_ns="flash", seconds=2,
              description="North–South amber; right arrow also amber.",
              driver_action="Stop if safe."),
        Phase("all_red", "All red (clearance)", ns="red", ew="red", seconds=1,
              description="All approaches red.",
              driver_action="Remain stopped."),
        Phase("ew_green", "E–W green (straight)", ns="red", ew="green", seconds=5,
              description="East–West green; right turns yield to oncoming.",
              driver_action="Remain stopped."),
        Phase("ew_arrow", "E–W protected RIGHT arrow", ns="red", ew="red", ew_arrow="green", seconds=4,
              description="Green right-turn arrow for East–West.",
              driver_action="Remain stopped."),
        Phase("ew_amber", "E–W amber + amber arrow", ns="red", ew="amber", ew_arrow="yellow", seconds=2,
              description="East–West amber; right arrow amber.",
              driver_action="Remain stopped."),
        Phase("all_red_2", "All red (clearance)", ns="red", ew="red", seconds=1,
              description="All approaches red.",
              driver_action="Get ready — your green is next."),
    ]


def pedestrian_phase() -> list[Phase]:
    return [
        Phase("ns_walk", "N–S green + WALK", ns="green", ew="red", ped_ns="walk", seconds=5,
              description="North–South traffic green and parallel pedestrians see WALK.",
              driver_action="Proceed but yield to pedestrians finishing the crossing."),
        Phase("ns_flash", "N–S green + flashing DON'T WALK", ns="green", ew="red", ped_ns="flash", seconds=3,
              description="Pedestrians must not start; those on the crossing finish clearing.",
              driver_action="Proceed with care; crossing is clearing."),
        Phase("ns_amber", "N–S amber + DON'T WALK", ns="amber", ew="red", ped_ns="stop", seconds=2,
              description="North–South amber; pedestrians must not enter.",
              driver_action="Stop if safe."),
        Phase("all_red", "All red", ns="red", ew="red", seconds=1,
              description="All red — full clearance for the crossing.",
              driver_action="Remain stopped."),
        Phase("ew_walk", "E–W green + WALK", ns="red", ew="green", ped_ew="walk", seconds=5,
              description="East–West green with parallel WALK.",
              driver_action="Remain stopped."),
        Phase("ew_flash", "E–W green + flashing DON'T WALK", ns="red", ew="green", ped_ew="flash", seconds=3,
              description="E–W pedestrians finish clearing.",
              driver_action="Remain stopped."),
        Phase("ew_amber", "E–W amber", ns="red", ew="amber", ped_ew="stop", seconds=2,
              description="East–West amber.",
              driver_action="Remain stopped."),
        Phase("all_red_2", "All red", ns="red", ew="red", seconds=1,
              description="All red.",
              driver_action="Your green is next."),
    ]


def flashing_scenario(kind: str) -> list[Phase]:
    if kind == "flashing_red":
        return [Phase(
            "flash_red", "Flashing red (all approaches)", seconds=0,
            description="Every approach shows a flashing red light — it works like a stop sign at this junction.",
            driver_action="STOP completely, look both ways, yield to traffic and pedestrians, then go when safe.")]
    if kind == "night_flash":
        return [Phase(
            "night_flash", "Night flash: main road amber, side road red", ew="amber", ns="red", seconds=0,
            description="Main road (E–W) shows flashing amber; side road (N–S) shows flashing red.",
            driver_action="You are on the side road: STOP, yield to the main road, then proceed when safe.")]
    return [Phase(
        "flash_amber", "Flashing amber (all approaches)", ew="amber", ns="amber", seconds=0,
        description="Every approach shows a flashing amber light.",
        driver_action="No stop required — slow down, look, proceed with caution and give way where needed.")]


SCENARIOS: dict[str, list[Phase]] = {
    "Basic intersection cycle": basic_cycle(),
    "Protected right-turn arrows (LHT)": protected_cycle(),
    "Pedestrian crossing phase": pedestrian_phase(),
    "Flashing red — act like a STOP sign": flashing_scenario("flashing_red"),
    "Flashing amber — proceed with caution": flashing_scenario("flashing_amber"),
    "Night flash (main amber / side red)": flashing_scenario("night_flash"),
}

ROUNDABOUT_STEPS: list[dict[str, str]] = [
    {"title": "1 · Approach", "text": "Pakistan drives on the left — keep left on approach and pick your lane early based on your exit (earlier exits = left lane).",
     "do": "Keep left, slow down, signal if turning.", "dont": "Don't enter without checking the traffic to your right."},
    {"title": "2 · Yield to the right", "text": "Traffic already ON the roundabout coming from your right has priority. Wait for a safe gap.",
     "do": "Yield, then enter clockwise when clear.", "dont": "Don't stop inside the roundabout; don't cut across lanes."},
    {"title": "3 · Signal your exit", "text": "Indicate before your exit so following drivers know your intention, and watch for large vehicles using the full width.",
     "do": "Signal, check mirrors, exit into the left lane.", "dont": "Don't change lanes mid-roundabout next to a truck."},
]


class SignalSimulator:
    """Deterministic phase machine for one selected scenario."""

    def __init__(self, scenario: str):
        if scenario == "Roundabout — how it works":
            self.roundabout = True
            self.phases: list[Phase] = []
        else:
            self.roundabout = False
            if scenario not in SCENARIOS:
                raise ValueError(f"unknown scenario: {scenario}")
            self.phases = SCENARIOS[scenario]
        self.scenario = scenario
        self.idx = 0

    def current(self) -> Phase | dict:
        if self.roundabout:
            return ROUNDABOUT_STEPS[self.idx % len(ROUNDABOUT_STEPS)]
        return self.phases[self.idx % len(self.phases)]

    def step(self, n: int = 1) -> None:
        total = len(ROUNDABOUT_STEPS) if self.roundabout else len(self.phases)
        self.idx = (self.idx + n) % total

    def reset(self) -> None:
        self.idx = 0

    @property
    def total(self) -> int:
        return len(ROUNDABOUT_STEPS) if self.roundabout else len(self.phases)


# ----------------------------------------------------------------- SVG ----
_LIGHT_POS = {          # signal head positions (x, y) on a 560×400 canvas
    "ns": [(120, 60), (440, 60)],
    "ew": [(60, 120), (500, 120)],
}


def _bulb(x: int, y: int, r: int, colour: str) -> str:
    return f"<circle cx='{x}' cy='{y}' r='{r}' fill='{colour}' stroke='#0b1220' stroke-width='1.5'/>"


def _head(x: int, y: int, state: str) -> str:
    return (
        f"<rect x='{x - 16}' y='{y - 52}' width='32' height='104' rx='8' fill='#1e293b'/>"
        + _bulb(x, y - 34, 11, RED if state == "red" else OFF)
        + _bulb(x, y, 11, AMBER if state == "amber" else OFF)
        + _bulb(x, y + 34, 11, GREEN if state == "green" else OFF)
    )


def _arrow(x: int, y: int, state: str) -> str:
    colour = {"green": GREEN, "yellow": AMBER, "red": RED}.get(state, OFF)
    return (
        f"<g transform='translate({x},{y})'>"
        f"<circle r='15' fill='#1e293b'/>"
        f"<path d='M-6,-9 L8,0 L-6,9 Z' fill='{colour}' transform='rotate(90)'/>"
        f"</g>"
    )


def _ped(x: int, y: int, state: str) -> str:
    colour = {"walk": GREEN, "flash": AMBER, "stop": RED}.get(state, RED)
    return (
        f"<g transform='translate({x},{y})'>"
        f"<rect x='-13' y='-20' width='26' height='40' rx='5' fill='#1e293b'/>"
        f"<circle r='7' fill='{colour}'/>"
        f"<text x='0' y='13' text-anchor='middle' font-size='13' fill='{colour}'>🚶</text>"
        f"</g>"
    )


def render_intersection_svg(phase: Phase, width: int = 560, height: int = 400) -> str:
    """Draw the intersection for the given phase (POV car at bottom, left lane)."""
    svg = [f"<svg viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='Intersection simulator: {phase.description}' style='max-width:640px'>"]
    svg.append(f"<rect width='{width}' height='{height}' fill='#14532d' rx='10'/>")
    # roads
    svg.append(f"<rect x='0' y='120' width='{width}' height='160' fill='#475569'/>")
    svg.append(f"<rect x='200' y='0' width='160' height='{height}' fill='#475569'/>")
    # lane markings (dashed center lines stop at the junction)
    svg.append("<line x1='0' y1='200' x2='200' y2='200' stroke='#facc15' stroke-width='3' stroke-dasharray='14 10'/>")
    svg.append(f"<line x1='360' y1='200' x2='{width}' y2='200' stroke='#facc15' stroke-width='3' stroke-dasharray='14 10'/>")
    svg.append("<line x1='280' y1='0' x2='280' y2='120' stroke='#facc15' stroke-width='3' stroke-dasharray='14 10'/>")
    svg.append("<line x1='280' y1='280' x2='280' y2='400' stroke='#facc15' stroke-width='3' stroke-dasharray='14 10'/>")
    # stop lines — LHT: stop lines before the junction on the LEFT half
    svg.append("<rect x='216' y='272' width='128' height='5' fill='#f8fafc'/>")     # NS approach (bottom)
    svg.append("<rect x='46' y='132' width='128' height='5' fill='#f8fafc'/>")      # EW approach (left)
    # signal heads + arrows + ped lights
    for x, y in _LIGHT_POS["ns"]:
        svg.append(_head(x, y, phase.ns))
    for x, y in _LIGHT_POS["ew"]:
        svg.append(_head(x, y, phase.ew))
    svg.append(_arrow(176, 96, phase.ns_arrow))
    svg.append(_arrow(384, 96, phase.ew_arrow))
    svg.append(_ped(340, 330, phase.ped_ns))
    svg.append(_ped(560 - 340, 330, phase.ped_ew))
    # POV car in the left lane heading north (LHT)
    svg.append("<g transform='translate(244,352)'><rect x='-26' y='-44' width='52' height='88' rx='12' "
               "fill='#60a5fa' stroke='#1d4ed8' stroke-width='2'/><rect x='-18' y='-26' width='36' height='26' "
               "rx='6' fill='#0b1220' opacity='.55'/></g>")
    svg.append("<text x='14' y='24' font-size='13' fill='#e2e8f0' font-family='sans-serif'>N ↑ (you drive north, left lane)</text>")
    svg.append(f"<text x='{width - 14}' y='{height - 12}' font-size='12' fill='#cbd5e1' text-anchor='end' "
               f"font-family='sans-serif'>Schematic — Pakistan keeps LEFT</text>")
    svg.append("</svg>")
    return "".join(svg)
