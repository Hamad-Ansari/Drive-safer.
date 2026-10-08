"""Accident Insights — filters, KPIs, trends, heatmap, causes, schematic map."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from roadsafe.core import config
from roadsafe.services import analytics

ACCENT = "#1D4ED8"
SEQ = px.colors.sequential.YlOrRd


@st.cache_data
def load_data() -> "object":
    import pandas as pd
    return pd.read_csv(config.ACCIDENTS_CSV, parse_dates=["date_time"])


def _fig(fig, height: int = 320) -> None:
    fig.update_layout(margin=dict(l=10, r=10, t=36, b=10), height=height,
                      template="plotly_white", title_font_size=13)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


def _render_filters(df) -> dict:
    with st.expander("🔎 Filters", expanded=True):
        c1, c2, c3 = st.columns(3)
        years = c1.multiselect("Year", sorted(df["year"].unique()),
                               default=sorted(df["year"].unique()))
        towns = c2.multiselect("Town / zone", sorted(df["town"].unique()))
        weather = c3.multiselect("Weather", config.WEATHER_TYPES)
        c4, c5, c6 = st.columns(3)
        road_types = c4.multiselect("Road type", config.ROAD_TYPES)
        lighting = c5.multiselect("Lighting", config.LIGHTING_TYPES)
        severities = c6.multiselect("Severity", config.SEVERITIES)
        if st.button("↺ Reset filters"):
            st.rerun()
    return {"years": years, "towns": towns, "weather": weather,
            "road_types": road_types, "lighting": lighting, "severities": severities}


def render() -> None:
    st.title("📊 Accident Insights — Lahore (synthetic demo)")
    st.caption(config.DATA_NOTE + " Charts have text summaries below them; "
               "a data table + CSV export are provided for accessibility.")

    df = load_data()
    f = _render_filters(df)
    view = analytics.apply_filters(df, **f)

    if view.empty:
        st.warning("No accidents match these filters. Reset or widen the filters.")
        return

    k = analytics.kpis(view)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total accidents", f"{k['total']:,}")
    c2.metric("Fatalities", f"{k['deaths']:,}", help="Deaths recorded at scene (demo field)")
    c3.metric("Injury rate", f"{k['injury_rate'] * 100:.0f}%",
              help="Share of accidents where at least one person was injured")
    c4.metric("Most dangerous hour", k["peak_hour_label"],
              help="Hour with the most fatalities (falls back to most accidents)")
    c5.metric("Top cause", k["top_cause"])

    st.write("")

    # --- trend + severity mix ---
    left, right = st.columns([3, 2])
    with left:
        trend = analytics.monthly_trend(view)
        fig = go.Figure()
        fig.add_bar(x=trend["ym"], y=trend["accidents"], name="Accidents",
                    marker_color=ACCENT, opacity=.85)
        fig.add_scatter(x=trend["ym"], y=trend["deaths"], name="Deaths",
                        mode="lines+markers", line=dict(color="#DC2626", width=2), yaxis="y2")
        fig.update_layout(
            title="Accidents per month (bars) and deaths (line)",
            yaxis=dict(title="Accidents"), yaxis2=dict(overlaying="y", side="right",
                                                       title="Deaths", showgrid=False))
        _fig(fig, 330)
        st.caption(f"Text summary: {k['total']:,} accidents across "
                   f"{trend['ym'].nunique()} months; {k['deaths']:,} deaths total.")
    with right:
        mix = analytics.severity_mix(view)
        colors = {"Minor injury": "#16A34A", "Serious injury": "#D97706", "Fatal": "#DC2626"}
        fig = px.pie(names=mix.index, values=mix.values, hole=.55,
                     color=mix.index, color_discrete_map=colors, title="Severity mix")
        _fig(fig, 330)
        st.caption("Text summary: " + ", ".join(
            f"{i} = {v:,} ({v / mix.sum() * 100:.0f}%)" for i, v in mix.items()))

    # --- heatmap + causes ---
    left, right = st.columns(2)
    with left:
        mat = analytics.hour_weekday_matrix(view)
        fig = px.imshow(mat, aspect="auto", color_continuous_scale=SEQ,
                        labels=dict(x="Hour of day", y="", color="Accidents"),
                        title="When accidents happen (weekday × hour)")
        fig.update_layout(yaxis=dict(ticks=""))
        _fig(fig, 320)
        worst = mat.sum(axis=1).idxmax() if len(mat) else "—"
        st.caption(f"Text summary: {worst} is the worst weekday overall; evening "
                   f"hours 17–19 form the consistent hot band.")
    with right:
        causes = analytics.top_causes(view)
        fig = px.bar(causes.iloc[::-1], x="accidents", y="cause", orientation="h",
                     title="Top causes", color_discrete_sequence=[ACCENT])
        fig.update_layout(yaxis=dict(title=""))
        _fig(fig, 320)
        st.caption(f"Text summary: “{k['top_cause']}” leads with "
                   f"{int(causes.iloc[0]['accidents']):,} records.")

    # --- town map + town bar ---
    left, right = st.columns(2)
    with left:
        tm = analytics.town_map_counts(view)
        fig = go.Figure(go.Scatter(
            x=tm["gx"], y=tm["gy"], mode="markers+text",
            marker=dict(size=tm["accidents"].clip(lower=14) ** .5 * 4.2,
                        color=tm["accidents"], colorscale=SEQ,
                        line=dict(width=1, color="#0F172A"), opacity=.92),
            text=tm["town"], textposition="bottom center",
            textfont=dict(size=9),
            hovertemplate="<b>%{text}</b><br>Accidents: %{marker.color:,}"
                          "<extra></extra>",
        ))
        fig.update_layout(title="Schematic tile map — Lahore towns (size/colour = accidents)",
                          xaxis=dict(visible=False), yaxis=dict(visible=False, autorange="reversed"),
                          plot_bgcolor="#f1f5f9")
        _fig(fig, 340)
        st.caption("Text summary (schematic, not to scale): busiest town is "
                   f"**{tm.sort_values('accidents', ascending=False).iloc[0]['town']}** "
                   f"with {int(tm['accidents'].max()):,} accidents.")
    with right:
        bt = analytics.by_town(view).iloc[::-1]
        fig = px.bar(bt, x="accidents", y="town", orientation="h",
                     color="deaths", color_continuous_scale=SEQ,
                     title="Accidents and deaths by town", height=380)
        fig.update_layout(yaxis=dict(title=""))
        _fig(fig, 340)
        top_death = bt.sort_values("deaths", ascending=False).iloc[0]
        st.caption(f"Text summary: most deaths in **{top_death['town']}** "
                   f"({int(top_death['deaths']):,}).")

    # --- severity by year + data table ---
    left, right = st.columns([2, 3])
    with left:
        sy = analytics.severity_by_year(view)
        fig = go.Figure()
        for sev, color in zip(config.SEVERITIES,
                              ["#16A34A", "#D97706", "#DC2626"]):
            fig.add_bar(x=sy["year"], y=sy[sev], name=sev, marker_color=color)
        fig.update_layout(barmode="stack", title="Severity by year")
        _fig(fig, 300)
    with right:
        with st.expander("🗂️ View as data table (accessibility alternative)", expanded=False):
            sample = view[["date_time", "town", "road_type", "weather", "lighting",
                           "severity", "cause", "deaths"]].head(400)
            st.dataframe(sample, use_container_width=True, height=300)
            st.download_button(
                "⬇️ Download filtered view (CSV)",
                view.drop(columns=["grid_x", "grid_y"]).to_csv(index=False).encode("utf-8"),
                file_name="roadsafe_filtered.csv", mime="text/csv")
