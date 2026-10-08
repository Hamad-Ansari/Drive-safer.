"""Signal state machine + scenario invariants (F5)."""
from __future__ import annotations

import pytest

from roadsafe.services.signals import (ROUNDABOUT_STEPS, SCENARIOS,
                                       SignalSimulator, render_intersection_svg)


def test_scenarios_exist_and_nonempty():
    expected_fragments = ["Basic", "Protected", "Pedestrian", "Flashing red",
                          "Flashing amber", "Night flash"]
    for fragment in expected_fragments:
        assert any(fragment in s for s in SCENARIOS), fragment
    for phases in SCENARIOS.values():
        assert len(phases) >= 1


def test_basic_cycle_is_safe():
    phases = SCENARIOS["Basic intersection cycle"]
    for phase in phases:
        assert not (phase.ns == "green" and phase.ew == "green"), phase.title


def test_walk_only_with_parallel_green():
    for phases in SCENARIOS.values():
        for phase in phases:
            if phase.ped_ns == "walk":
                assert phase.ns == "green", phase.title
            if phase.ped_ew == "walk":
                assert phase.ew == "green", phase.title


def test_simulator_cycles_and_resets():
    sim = SignalSimulator("Basic intersection cycle")
    seen = {sim.current().key}
    for _ in range(sim.total * 2):
        sim.step()
        seen.add(sim.current().key)
    assert len(seen) == sim.total
    sim.reset()
    assert sim.idx == 0


def test_unknown_scenario_raises():
    with pytest.raises(ValueError):
        SignalSimulator("Teleportation lights")


def test_every_phase_has_accessibility_text():
    for phases in SCENARIOS.values():
        for phase in phases:
            assert phase.description, phase.key
            assert phase.driver_action, phase.key


def test_roundabout_steps_complete():
    assert len(ROUNDABOUT_STEPS) >= 3
    sim = SignalSimulator("Roundabout — how it works")
    assert sim.roundabout
    titles = [ROUNDABOUT_STEPS[i % len(ROUNDABOUT_STEPS)]["title"]
              for i in range(sim.total)]
    assert len(set(titles)) == sim.total


def test_svg_renders_state():
    phase = SCENARIOS["Basic intersection cycle"][0]
    svg = render_intersection_svg(phase)
    assert svg.startswith("<svg")
    assert "#16A34A" in svg  # a green bulb is on
    assert "left lane" in svg
