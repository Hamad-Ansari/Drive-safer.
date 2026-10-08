"""Signal Academy — intersection simulator, scored quiz, saved progress."""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from roadsafe.services import quiz as quiz_svc
from roadsafe.services import db as db_mod
from roadsafe.services.signals import (ROUNDABOUT_STEPS, SCENARIOS,
                                       SignalSimulator, render_intersection_svg)

TICK_SECONDS = 1.6


def _simulator() -> None:
    st.markdown("#### 🚦 Intersection simulator")
    st.caption("Pakistan keeps LEFT. Play advances one phase every "
               f"{TICK_SECONDS:.0f} s; every state has a text description, and "
               "nothing moves until you press Play (reduced-motion friendly).")

    c1, c2, c3 = st.columns([3, 1, 1])
    scenario = c1.selectbox("Scenario", list(SCENARIOS) + ["Roundabout — how it works"],
                            key="sim_scenario")
    playing = c2.toggle("▶ Play", value=False, key="sim_playing")
    if c3.button("⏭ Next phase", use_container_width=True):
        st.session_state["sim_idx"] = st.session_state.get("sim_idx", 0) + 1
        st.rerun()

    if scenario == "Roundabout — how it works":
        idx = st.session_state.get("sim_idx", 0) % len(ROUNDABOUT_STEPS)
        step = ROUNDABOUT_STEPS[idx]
        st.progress((idx + 1) / len(ROUNDABOUT_STEPS), text=f"Step {idx + 1} of {len(ROUNDABOUT_STEPS)}")
        st.markdown(f"##### {step['title']}")
        st.markdown(step["text"])
        good, bad = st.columns(2)
        good.success(f"✅ {step['do']}")
        bad.error(f"⛔ {step['dont']}")
        return

    sim = SignalSimulator(scenario)

    @st.fragment(run_every=TICK_SECONDS if playing else None)
    def _view() -> None:
        idx = st.session_state.get("sim_idx", 0) % sim.total
        sim.idx = idx
        phase = sim.current()
        st.markdown(render_intersection_svg(phase), unsafe_allow_html=True)
        st.progress((idx + 1) / sim.total, text=f"Phase {idx + 1} of {sim.total} — {phase.title}")
        col_a, col_b = st.columns(2)
        col_a.info(f"**State (described):** {phase.description}")
        col_b.success(f"**You (POV car, left lane):** {phase.driver_action}")
        st.session_state["sim_idx"] = idx

    _view()


def _quiz() -> None:
    st.markdown("#### 🧠 Signal & rules quiz")
    bank = quiz_svc.load_bank()
    scope = st.session_state.get("law_scope", "Both")

    if not st.session_state.get("quiz_active"):
        c1, c2 = st.columns(2)
        category = c1.selectbox("Category", ["All"] + quiz_svc.categories(bank), key="quiz_cat")
        st.caption(f"Scope **{scope}** (change in the sidebar) · "
                   f"{len(quiz_svc.filter_questions(bank, scope, category))} questions available · "
                   "10 per session")
        if st.button("▶ Start quiz", type="primary"):
            pool = quiz_svc.filter_questions(bank, scope, category)
            if pool:
                st.session_state["quiz_qs"] = quiz_svc.make_session(pool)
                st.session_state["quiz_idx"] = 0
                st.session_state["quiz_picks"] = []
                st.session_state["quiz_cat_saved"] = category
                st.session_state["quiz_active"] = True
                st.session_state["quiz_submitted"] = False
                st.rerun()
            else:
                st.warning("No questions for this scope/category.")
        return

    qs = st.session_state["quiz_qs"]
    idx = st.session_state["quiz_idx"]
    if idx >= len(qs):
        picks = st.session_state["quiz_picks"]
        result = quiz_svc.grade(qs, picks)
        pct = result["score"] / result["total"] * 100
        st.success(f"🎉 Score: {result['score']}/{result['total']} ({pct:.0f}%)")
        conn = db_mod.connect()
        quiz_svc.save_score(conn, scope, st.session_state.get("quiz_cat_saved", "All"),
                            result["score"], result["total"])
        for item in result["per"]:
            icon = "✅" if item["ok"] else "❌"
            st.markdown(
                f"{icon} **{item['q']}**  \n"
                f"Correct: {item['correct_text']} — *{item['explanation']}*  \n"
                f"<small>Source: {item['source']}</small>",
                unsafe_allow_html=True)
        if st.button("↺ Back to quiz setup"):
            st.session_state["quiz_active"] = False
            st.rerun()
        return

    q = qs[idx]
    opts, correct_idx = q["options_shuffled"]
    st.progress((idx + 1) / len(qs),
                text=f"Question {idx + 1} of {len(qs)} · {q['category']} · {q['difficulty']}")
    st.markdown(f"**{q['q']}**")
    pick = st.radio("Your answer", opts, index=None, key=f"q_{q['id']}_{idx}",
                    label_visibility="collapsed")
    if not st.session_state.get("quiz_submitted"):
        if st.button("Submit answer", type="primary"):
            st.session_state["quiz_picks"].append(opts.index(pick) if pick is not None else None)
            st.session_state["quiz_submitted"] = True
            st.rerun()
    else:
        last = st.session_state["quiz_picks"][-1]
        if last == correct_idx:
            st.success(f"✅ Correct! {q['explanation']}")
        else:
            st.error(f"❌ Not quite. Correct: **{opts[correct_idx]}** — {q['explanation']}")
        st.caption(f"Source: {q['source']} · {q['jurisdiction']}")
        if st.button("Next →"):
            st.session_state["quiz_idx"] += 1
            st.session_state["quiz_submitted"] = False
            st.rerun()


def _progress() -> None:
    st.markdown("#### 📈 Progress (saved across refreshes)")
    conn = db_mod.connect()
    rows = quiz_svc.progress(conn)
    if not rows:
        st.info("No attempts yet — finish a quiz to build your progress ring.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta("best:Q", stack=True),
        color=alt.Color("category:N", legend=alt.Legend(title="Category")),
        tooltip=["category", "attempts", "best", "avg"])
    st.altair_chart(chart, use_container_width=True)
    st.caption("Best score % per category, persisted in SQLite (survives refresh).")


def render() -> None:
    st.title("🚦 Signal & Sign Academy")
    st.caption("Learn the lights, the signs, and the rules — then prove it in the quiz. "
               "Quiz items are linked to the demo corpus sections.")
    tab_sim, tab_quiz, tab_prog = st.tabs(["🎛️ Simulator", "🧠 Quiz", "📈 Progress"])
    with tab_sim:
        _simulator()
    with tab_quiz:
        _quiz()
    with tab_prog:
        _progress()
