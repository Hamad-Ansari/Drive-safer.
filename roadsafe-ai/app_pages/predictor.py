"""Risk Predictor — step form, calibrated result, factor attribution."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from roadsafe.core import config
from roadsafe.services.predictor import honesty_notice, load_predictor

BAND_COLORS = {"Low": "#16A34A", "Moderate": "#D97706", "Elevated": "#EA580C", "High": "#DC2626"}
TIPS = {
    "speed_zone": "Choose a lower speed zone — speed amplifies every other risk.",
    "lighting": "Prefer lit routes at night; unlit roads raise severity sharply.",
    "road_type": "Local streets at modest speeds carry the least severe-outcome risk.",
    "weather": "In fog or heavy rain, delay the trip or cut speed well below the limit.",
    "hour": "Late night (after 10 PM) and evening rush (5–8 PM) carry the most risk.",
}


@st.cache_resource(show_spinner="Loading model…")
def get_predictor():
    return load_predictor()


def render() -> None:
    st.title("🧭 Accident Risk & Severity Predictor")
    st.caption("Calibrated estimates from a time-split LightGBM model — "
               + honesty_notice())

    predictor = get_predictor()
    with st.container(border=True):
        st.subheader("1 · Conditions")
        c1, c2, c3 = st.columns(3)
        hour = c1.slider("Hour of day", 0, 23, 18, format="%02d:00")
        month = c2.select_slider("Month", options=list(range(1, 13)),
                                 format_func=lambda m: config.MONTH_NAMES[m - 1], value=8)
        is_weekend = c3.toggle("Weekend", value=False)

        c1, c2, c3 = st.columns(3)
        weather = c1.selectbox("Weather", config.WEATHER_TYPES, index=0)
        road_type = c2.selectbox("Road type", config.ROAD_TYPES, index=3)
        lighting = c3.selectbox("Lighting", config.LIGHTING_TYPES, index=0)

        c1, c2, c3 = st.columns(3)
        road_condition = c1.selectbox("Road condition", config.ROAD_CONDITIONS, index=0)
        speed_zone = c2.select_slider("Speed zone", options=config.SPEED_ZONES, value=config.SPEED_ZONES[1])
        junction_type = c3.selectbox("Junction type", config.JUNCTION_TYPES, index=0)
        town = st.selectbox("Town / zone (Lahore)", list(config.TOWNS), index=6)

        go_btn = st.button("🔮 Estimate risk", type="primary", use_container_width=True)

    if go_btn:
        form = {"hour": hour, "month": month, "is_weekend": int(is_weekend),
                "weather": weather, "road_type": road_type, "lighting": lighting,
                "road_condition": road_condition, "speed_zone": speed_zone,
                "junction_type": junction_type, "town": town}
        res = predictor.predict(form)
        st.session_state["pred_result"] = {"res": res, "form": form}

    if "pred_result" in st.session_state:
        res = st.session_state["pred_result"]["res"]
        st.write("")
        st.subheader("2 · Result")
        band_color = BAND_COLORS[res["risk_band"]]
        left, right = st.columns([2, 3])
        with left:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=res["severe_probability"] * 100,
                number={"suffix": "%"},
                title={"text": f"Risk band: <b>{res['risk_band']}</b><br>"
                               f"<span style='font-size:.7em'>serious-or-fatal outcome</span>"},
                gauge={"axis": {"range": [0, 100]},
                       "bar": {"color": band_color},
                       "steps": [{"range": [0, 15], "color": "#dcfce7"},
                                 {"range": [15, 30], "color": "#fef3c7"},
                                 {"range": [30, 50], "color": "#ffedd5"},
                                 {"range": [50, 100], "color": "#fee2e2"}]}))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            probs = res["probabilities"]
            st.caption(" · ".join(f"{cls}: {p * 100:.1f}%" for cls, p in probs.items())
                       + f"  \nPredicted class: **{res['predicted_class']}**")
        with right:
            st.markdown("**Top contributing factors** "
                        f"({ 'SHAP' if res['explanation_mode'] == 'shap' else 'approximate attribution' })")
            for fac in res["factors"]:
                arrow = "▲" if fac["contribution"] > 0 else "▽"
                cls = "rs-up" if fac["contribution"] > 0 else "rs-down"
                st.markdown(
                    f"<div class='rs-factor'><span><b>{fac['label']}</b> = {fac['value']}</span>"
                    f"<span class='{cls}'>{arrow} {fac['direction']}</span></div>",
                    unsafe_allow_html=True)
            st.caption("Factors show what pushes this prediction up or down for the "
                       "model's leading class — associations, not causation.")

        with st.expander("🛡️ How to reduce risk in these conditions"):
            for key in ("speed_zone", "lighting", "weather", "hour", "road_type"):
                st.markdown(f"- {TIPS[key]}")
        st.info(honesty_notice(), icon="ℹ️")
