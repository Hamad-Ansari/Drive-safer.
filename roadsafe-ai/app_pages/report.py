"""Report Incident — validated local form with optional (EXIF-stripped) photo."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from roadsafe.core import config
from roadsafe.services import db as db_mod
from roadsafe.services import reports as reports_svc


def render() -> None:
    st.title("📝 Report an Incident")
    st.caption("Stored locally in SQLite on this device. No names, no phone numbers — "
               "the form cannot collect them. This demo does not transmit reports anywhere.")

    left, right = st.columns([3, 2])
    with left:
        with st.container(border=True):
            incident_type = st.selectbox("What happened?", config.INCIDENT_TYPES)
            c1, c2 = st.columns(2)
            town = c1.selectbox("Town / zone", list(config.TOWNS))
            when_seen = c2.date_input("When did you see it?",
                                      value=datetime.now().date(),
                                      min_value=datetime(2020, 1, 1).date())
            hh = c2.number_input("Hour (24h)", 0, 23, datetime.now().hour)
            severity = st.radio("Severity", ["Property damage only", "Minor injury",
                                             "Serious injury", "Not sure"], horizontal=True)
            description = st.text_area(
                "Describe it (10–1000 characters)",
                placeholder="Where exactly, what was wrong, what happened…",
                max_chars=1000, height=110)
            photo = st.file_uploader("Optional photo (≤2 MB, PNG/JPG — EXIF/GPS stripped)",
                                     type=["png", "jpg", "jpeg"])
            submit = st.button("📨 Submit report", type="primary", use_container_width=True)

        if submit:
            when = f"{when_seen}T{int(hh):02d}:00"
            errors = reports_svc.validate_report(incident_type, town, when, severity, description)
            photo_bytes, photo_mime, photo_err = None, None, None
            if photo is not None:
                photo_bytes = photo.getvalue()
                photo_mime = photo.type
                photo_err = reports_svc.check_photo(photo_bytes, photo_mime)
                if photo_err is None:
                    photo_bytes = reports_svc.strip_exif(photo_bytes, photo_mime)
            if errors or photo_err:
                for e in errors + ([photo_err] if photo_err else []):
                    st.error(e)
            else:
                conn = db_mod.connect()
                rid = reports_svc.save_report(conn, incident_type, town, when, severity,
                                              description, photo_bytes, photo_mime)
                st.success(f"✅ Report #{rid} saved locally. Thank you — safer roads start "
                           "with citizens reporting.")
                st.balloons()

    with right:
        st.markdown("#### Recent reports (this device)")
        conn = db_mod.connect()
        rows = reports_svc.list_reports(conn, limit=25)
        if rows:
            df = pd.DataFrame(rows)[["id", "when_seen", "incident_type", "town",
                                     "severity", "has_photo"]]
            df.columns = ["#", "When", "Type", "Town", "Severity", "📷"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            n = reports_svc.count_reports(conn)
            st.caption(f"{n} report(s) stored locally.")
            if st.checkbox("Delete all my reports"):
                if st.button("⚠️ Confirm delete"):
                    reports_svc.clear_reports(conn)
                    st.success("All reports deleted.")
                    st.rerun()
        else:
            st.info("No reports yet.")
