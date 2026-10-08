"""Home — hero, action cards, rotating safety tips, honest-data banner."""
from __future__ import annotations

import streamlit as st

from roadsafe.core import config

TIPS = [
    "In fog, use LOW beams — high beams reflect back and blind you. 🌫️",
    "The 3-second rule: keep 3 seconds behind the car ahead; double it in rain. ⏱️",
    "Flashing red light = a stop sign. Full stop, look, then go. 🛑",
    "Helmets for rider AND pillion — both, every ride. 🪖",
    "Roundabouts flow clockwise in Pakistan; yield to traffic from your right. 🔄",
    "Never overtake at junctions, crossings, bridges or blind curves. 🚫",
    "Hands off the phone: park first, then call. 📵",
    "On the motorway the hard shoulder is for emergencies only. 🛟",
    "First rain is the slickest — oil and dust float until washed away. 🌧️",
    "Stop, help, report: after any crash, call Rescue 1122 if anyone is hurt. 🚑",
]


@st.fragment(run_every=6.0)
def _tip_carousel() -> None:
    idx = st.session_state.get("tip_idx", 0)
    st.markdown(
        f"<div class='rs-card' style='border-left:4px solid var(--rs-warning)'>"
        f"<span class='rs-chip'>Safety tip</span>"
        f"<p style='font-size:1.02rem;color:var(--rs-text);margin-top:.5rem'>{TIPS[idx % len(TIPS)]}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    btn_col, hint_col = st.columns([1, 3])
    if btn_col.button("Next tip ↻", use_container_width=True):
        st.session_state["tip_idx"] = (idx + 1) % len(TIPS)
        st.rerun(scope="fragment")
    hint_col.caption("Auto-rotates every 6 s · pause by navigating away · reduced-motion friendly")


def _page(key: str):
    return st.session_state["rs_pages"][key]


def render() -> None:
    st.markdown(
        f"""
        <div class='rs-hero'>
          <span class='rs-chip'>RoadSafe AI</span><span class='rs-chip'>Lahore demo</span>
          <span class='rs-chip'>National + Punjab</span>
          <h1>Understand accidents. Learn the law. Drive safer.</h1>
          <p>Explore {config.DATA_NOTE.split('—')[0].strip().lower()} through an interactive
          dashboard, estimate your route's risk conditions, ask a citation-backed traffic-law
          assistant, and master signals and signs in the Academy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "<div class='rs-card'><div style='font-size:1.6rem'>📊</div>"
            "<h3>Explore accidents</h3><p>Filter 26,000+ synthetic records by year, area, "
            "weather, road and severity. Trend charts, heatmaps and a schematic town map.</p></div>",
            unsafe_allow_html=True)
        st.page_link(_page("insights"), label="Open Accident Insights →", use_container_width=True)
    with c2:
        st.markdown(
            "<div class='rs-card'><div style='font-size:1.6rem'>⚖️</div>"
            "<h3>Ask a law question</h3><p>A retrieval assistant that answers ONLY from its "
            "corpus, always cites the section, and honestly refuses when it doesn't know.</p></div>",
            unsafe_allow_html=True)
        st.page_link(_page("law"), label="Ask the Law Assistant →", use_container_width=True)
    with c3:
        st.markdown(
            "<div class='rs-card'><div style='font-size:1.6rem'>🚦</div>"
            "<h3>Learn signals & signs</h3><p>An accessible intersection simulator, a sign "
            "library and a 100+ question quiz with explanations and saved progress.</p></div>",
            unsafe_allow_html=True)
        st.page_link(_page("academy"), label="Enter the Signal Academy →", use_container_width=True)

    st.write("")
    st.markdown("#### 🧭 Try the risk predictor")
    st.page_link(_page("predictor"), label="Estimate risk for given conditions →",
                 use_container_width=True)

    st.write("")
    _tip_carousel()

    st.write("")
    st.info(
        "ℹ️ **Honesty notice.** All accident figures are **synthetic demo data** calibrated to "
        "published road-safety *patterns* — they are not real statistics. Law content is a "
        "flagged paraphrase for the demo. RoadSafe AI is educational; it is not legal advice.",
        icon="ℹ️",
    )
