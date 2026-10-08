"""RoadSafe AI — Streamlit entry point (Track A MVP).

Runs:  streamlit run app.py
Shared chrome (sidebar scope toggle, footer with socials) lives here so every
page inherits it; page bodies live in app_pages/.
"""
from __future__ import annotations

import streamlit as st

from app_pages.registry import build_pages
from roadsafe.core import config
from roadsafe.core.icons import social_links_html
from roadsafe.core.socials import load_socials

st.set_page_config(
    page_title=f"{config.APP_NAME} — {config.APP_TAGLINE}",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
  :root {
    --rs-bg:#F8FAFC; --rs-surface:#FFFFFF; --rs-primary:#1D4ED8;
    --rs-danger:#DC2626; --rs-warning:#D97706; --rs-success:#16A34A;
    --rs-text:#0F172A; --rs-muted:#64748B; --rs-radius:12px;
  }
  .block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1200px;}
  h1 {letter-spacing: -0.02em;}

  /* socials (footer + about) */
  .socials {display:flex; flex-wrap:wrap; gap:8px; align-items:center;}
  .social-icon {
    display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; padding:0 10px; border-radius:10px;
    color:var(--rs-muted); background:rgba(100,116,139,.08);
    text-decoration:none; border:1px solid rgba(100,116,139,.15);
    transition:all .18s ease-out;
  }
  .social-icon:hover {color:#fff; background:var(--rs-primary); transform:translateY(-1px);}
  .social-icon:focus-visible {outline:3px solid var(--rs-primary); outline-offset:2px;}
  .social-label {font-size:.82rem; font-weight:600; margin-left:6px;}
  .socials-labeled .social-icon {padding:0 16px;}

  /* hero + cards */
  .rs-hero {
    border-radius:16px; padding:2.2rem 2rem; color:#fff;
    background:linear-gradient(120deg,#1D4ED8 0%,#0B1220 90%);
    border:1px solid rgba(255,255,255,.08);
  }
  .rs-hero h1 {color:#fff; margin:0 0 .4rem;}
  .rs-hero p {color:#dbeafe; font-size:1.05rem; margin:0 0 1rem; max-width:640px;}
  .rs-chip {display:inline-block; padding:.25rem .7rem; border-radius:999px;
    font-size:.75rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase;
    background:rgba(255,255,255,.14); color:#fff; margin-right:.4rem;}
  .rs-card {border:1px solid rgba(100,116,139,.2); border-radius:var(--rs-radius);
    padding:1.1rem 1.2rem; height:100%; background:var(--rs-surface);}
  .rs-card h3 {margin:.15rem 0 .4rem;}
  .rs-card p {color:var(--rs-muted); font-size:.92rem; margin:0;}
  .rs-badge {display:inline-block; padding:.15rem .6rem; border-radius:999px;
    font-size:.72rem; font-weight:700;}
  .rs-badge-national {background:#dbeafe; color:#1e40af;}
  .rs-badge-punjab {background:#dcfce7; color:#166534;}
  .rs-badge-both {background:#fef3c7; color:#92400e;}
  .rs-factor {display:flex; align-items:center; justify-content:space-between;
    padding:.45rem .7rem; border-radius:8px; margin-bottom:.4rem;
    background:rgba(100,116,139,.08); font-size:.92rem;}
  .rs-up {color:var(--rs-danger); font-weight:700;}
  .rs-down {color:var(--rs-success); font-weight:700;}
  [data-testid="stMetric"] {background:rgba(100,116,139,.06); border-radius:var(--rs-radius);
    border:1px solid rgba(100,116,139,.12); padding:.8rem 1rem;}
  footer {visibility:hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- sidebar --
with st.sidebar:
    st.markdown(f"### 🚦 {config.APP_NAME}")
    st.caption(config.APP_TAGLINE)
    st.radio(
        "Legal scope",
        config.LAW_SCOPES,
        index=0,
        key="law_scope",
        help="Filters the law assistant, quiz bank and sign library.",
    )
    st.divider()
    st.caption(f"📊 {config.DATA_NOTE}")
    st.caption(f"⚖️ {config.LAW_NOTE}")
    st.caption("Educational demo · v0.1.0")

# ------------------------------------------------------------------- pages -
pages = build_pages()
# Registered page objects, keyed for st.page_link / st.switch_page from pages.
st.session_state["rs_pages"] = dict(zip(
    ["home", "insights", "predictor", "law", "academy", "signs", "report", "about"], pages))
st.navigation(pages).run()

# ------------------------------------------------------------------ footer -
socials = load_socials()
st.divider()
foot_left, foot_right = st.columns([3, 2], vertical_alignment="center")
with foot_left:
    if socials:
        st.markdown(social_links_html(socials, size=18), unsafe_allow_html=True)
with foot_right:
    st.markdown(
        f"<div style='text-align:right;color:var(--rs-muted);font-size:.8rem'>"
        f"© 2026 {config.AUTHOR_NAME} · Educational demo · Synthetic data · "
        f"Not legal advice</div>",
        unsafe_allow_html=True,
    )
