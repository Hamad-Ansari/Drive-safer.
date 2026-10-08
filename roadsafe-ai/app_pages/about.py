"""About & Connect — author bio and the full social icon row."""
from __future__ import annotations

import streamlit as st

from roadsafe.core import config
from roadsafe.core.icons import social_links_html
from roadsafe.core.socials import load_socials


def render() -> None:
    st.title("👤 About & Connect")

    left, right = st.columns([2, 3])
    with left:
        st.markdown(
            f"""
            <div class='rs-card' style='text-align:center'>
              <div style='font-size:4rem;line-height:1'>🧑‍💻</div>
              <h2 style='margin:.4rem 0 .1rem'>{config.AUTHOR_NAME}</h2>
              <p>Machine-learning & road-safety enthusiast. Built RoadSafe AI to make
              Pakistan's traffic rules understandable and accident risk discussable —
              with honest data, cited answers and accessible design.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("#### 🔗 Connect — every platform, one config file")
        st.caption("Rendered from `config/socials.json`. Add or blank a URL there and "
                   "this page, the header and the footer all update — no code change.")
        socials = load_socials()
        if socials:
            st.markdown(social_links_html(socials, size=22, with_labels=True),
                        unsafe_allow_html=True)
        st.write("")
        st.markdown(
            """
            #### 🛠️ How this is built
            | Layer | Choice |
            | --- | --- |
            | UI | Streamlit (Track A MVP), custom design tokens |
            | ML | LightGBM + temperature calibration, time-split, SHAP |
            | Law assistant | TF-IDF retrieval → extractive cited answers, refusal path |
            | Storage | SQLite (reports, quiz progress) + CSV data |
            | Tests | pytest — data, ML, RAG guardrails, quiz, signals, socials |
            """
        )
        st.caption("RoadSafe AI is educational. Accident data is synthetic demo data; "
                   "law content is a flagged paraphrase — verify with official sources. "
                   "Not legal advice.")
