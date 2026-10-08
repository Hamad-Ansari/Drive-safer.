"""App smoke tests — every page must render without raising (Streamlit AppTest).

from_function() only ships the function body, so we write tiny wrapper scripts
that import the real page module and call render() with full module context.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit.testing.v1 as stt

REPO_ROOT = Path(__file__).resolve().parents[1]
APP = REPO_ROOT / "app.py"

WRAPPER = """import sys
sys.path.insert(0, {root!r})
from app_pages import {mod}
{mod}.render()
"""


def _run_page(mod: str) -> None:
    wrapper = WRAPPER.format(root=str(REPO_ROOT), mod=mod)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"page_{mod}.py"
        path.write_text(wrapper, encoding="utf-8")
        at = stt.AppTest.from_file(str(path), default_timeout=300)
        at.run()
        assert not at.exception, f"page '{mod}' raised: {at.exception}"


def test_full_app_home_renders():
    at = stt.AppTest.from_file(str(APP), default_timeout=300)
    at.run()
    assert not at.exception, str(at.exception)


def test_each_page_renders_without_exception():
    for mod in ("insights", "predictor", "law", "academy", "signs", "report", "about"):
        _run_page(mod)
