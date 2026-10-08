"""Every social entry must be complete, valid and renderable (F12)."""
from __future__ import annotations

from roadsafe.core.icons import ICON_BODIES, icon_svg, social_links_html
from roadsafe.core.socials import load_socials, socials_path


def test_socials_file_exists_and_loads():
    assert socials_path().exists()
    items = load_socials()
    assert len(items) >= 10


def test_every_entry_is_complete():
    for item in load_socials():
        assert set(item) == {"name", "icon", "url"}, item
        assert item["name"], "missing name"
        url = item["url"]
        assert url.startswith(("https://", "http://", "mailto:")), url
        assert " " not in url, f"spaces in url: {url}"


def test_no_duplicate_names():
    names = [i["name"] for i in load_socials()]
    assert len(names) == len(set(names))


def test_icons_resolve_to_svg():
    for item in load_socials():
        svg = icon_svg(item["icon"])
        assert svg.startswith("<svg"), item
        assert item["icon"] in ICON_BODIES or item["icon"] == "globe"


def test_rendered_links_are_safe_and_labelled():
    html = social_links_html(load_socials())
    assert html.count("target='_blank'") == len(load_socials())
    assert 'rel="noopener noreferrer"'.replace('"', "'") in html
    assert "aria-label=" in html
    assert "title=" in html
