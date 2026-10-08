"""Sign Library — searchable grid of schematic signs with rules."""
from __future__ import annotations

import streamlit as st

from roadsafe.services import signs as sign_svc


def _badge(jurisdiction: str) -> str:
    cls = {"National": "rs-badge-national", "Punjab": "rs-badge-punjab"}.get(jurisdiction, "rs-badge-both")
    return f"<span class='rs-badge {cls}'>{jurisdiction}</span>"


def render() -> None:
    st.title("🪧 Sign Library")
    st.caption("Schematic renderings of Pakistan-style signage (left-hand traffic). "
               "Search by name or meaning; filter by category and legal scope.")

    signs = sign_svc.load_signs()
    scope = st.session_state.get("law_scope", "Both")
    c1, c2 = st.columns([3, 2])
    query = c1.text_input("🔍 Search", placeholder="e.g. roundabout, school, parking…",
                          label_visibility="collapsed")
    category = c2.radio("Category", ["All"] + sign_svc.CATEGORIES, horizontal=True,
                        label_visibility="collapsed")

    hits = sign_svc.search_signs(signs, query, category, scope)
    st.caption(f"{len(hits)} sign(s) · scope **{scope}**")

    if not hits:
        st.warning("No signs match. Clear the search or switch the scope.")
        return

    for start in range(0, len(hits), 4):
        cols = st.columns(4)
        for col, sign in zip(cols, hits[start:start + 4]):
            with col:
                st.markdown(
                    f"<div class='rs-card' style='text-align:center'>"
                    f"<div style='margin-bottom:6px'>{sign_svc.render_sign(sign, 66)}</div>"
                    f"<h3 style='font-size:.95rem'>{sign['name']} {_badge(sign['jurisdiction'])}</h3>"
                    f"<p style='margin-bottom:.3rem'>{sign['meaning']}</p>"
                    f"<p style='font-size:.82rem'>{sign['rule']}</p></div>",
                    unsafe_allow_html=True)
