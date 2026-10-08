"""Page registry for st.navigation. url_path must be unique per page."""
from __future__ import annotations

import streamlit as st

from app_pages import about, academy, home, insights, law, predictor, report, signs


def build_pages() -> list[st.Page]:
    return [
        st.Page(home.render, title="Home", icon="🏠", url_path="home", default=True),
        st.Page(insights.render, title="Accident Insights", icon="📊", url_path="insights"),
        st.Page(predictor.render, title="Risk Predictor", icon="🧭", url_path="predictor"),
        st.Page(law.render, title="Law Assistant", icon="⚖️", url_path="law"),
        st.Page(academy.render, title="Signal Academy", icon="🚦", url_path="academy"),
        st.Page(signs.render, title="Sign Library", icon="🪧", url_path="signs"),
        st.Page(report.render, title="Report Incident", icon="📝", url_path="report"),
        st.Page(about.render, title="About & Connect", icon="👤", url_path="about"),
    ]
