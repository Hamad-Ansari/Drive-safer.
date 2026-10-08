"""Sign library integrity and search (F7)."""
from __future__ import annotations

from roadsafe.services import signs as sign_svc


def test_library_size_and_categories():
    signs = sign_svc.load_signs()
    assert len(signs) >= 30
    for s in signs:
        assert s["category"] in sign_svc.CATEGORIES, s["id"]
        assert s["jurisdiction"] in {"National", "Punjab", "Both"}
        assert s["meaning"] and s["rule"] and s["name"]


def test_unique_ids():
    ids = [s["id"] for s in sign_svc.load_signs()]
    assert len(ids) == len(set(ids))


def test_search_and_filters():
    signs = sign_svc.load_signs()
    hits = sign_svc.search_signs(signs, query="roundabout")
    assert hits
    reg = sign_svc.search_signs(signs, category="Regulatory")
    assert all(s["category"] == "Regulatory" for s in reg)
    assert all(s["jurisdiction"] in {"National", "Both"}
               for s in sign_svc.search_signs(signs, scope="National"))


def test_render_produces_svg():
    sign = sign_svc.load_signs()[0]
    svg = sign_svc.render_sign(sign)
    assert svg.startswith("<svg")
    assert "aria-label" in svg
