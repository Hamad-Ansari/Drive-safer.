"""Inline SVG icons — social brands, road signs, misc glyphs.

Everything is inline SVG on purpose: no CDN, no external assets, so the app
renders identically offline and inside sandboxed previews. Brand paths follow
the Simple Icons 24×24 convention; a few (Kaggle, Hugging Face) use styled text
glyphs as recognisable fallbacks.
"""
from __future__ import annotations

from roadsafe.core import config

# Each entry: whether the body uses stroke style, and the inner SVG markup.
ICON_BODIES: dict[str, dict] = {
    "github": {"stroke": False, "body": (
        "<path d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 "
        "0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 "
        "1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 "
        "0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 "
        "2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 "
        "0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/>"
    )},
    "linkedin": {"stroke": False, "body": (
        "<path d='M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 "
        "1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 "
        "2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 "
        "23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'/>"
    )},
    "twitter": {"stroke": False, "body": (
        "<path d='M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 "
        "3.24H4.298Z'/>"
    )},
    "facebook": {"stroke": False, "body": (
        "<path d='M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 "
        "4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z'/>"
    )},
    "whatsapp": {"stroke": False, "body": (
        "<path d='M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z'/>"
    )},
    "instagram": {"stroke": False, "body": (
        "<path d='M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 "
        "3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 "
        "0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 "
        "2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 "
        "3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 "
        "5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 "
        "0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z'/>"
    )},
    "youtube": {"stroke": False, "body": (
        "<path d='M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 "
        "3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 "
        "15.568V8.432L15.818 12l-6.273 3.568z'/>"
    )},
    "medium": {"stroke": False, "body": (
        "<path d='M13.54 12a6.8 6.8 0 0 1-6.77 6.82A6.8 6.8 0 0 1 0 12a6.8 6.8 0 0 1 6.77-6.82A6.8 6.8 0 0 1 13.54 12zm7.42 0c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 "
        "3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75S24 8.83 24 12z'/>"
    )},
    "mail": {"stroke": True, "body": "<rect x='2' y='4' width='20' height='16' rx='2'/><path d='m22 7-10 5L2 7'/>"},
    "globe": {"stroke": True, "body": (
        "<circle cx='12' cy='12' r='10'/><path d='M2 12h20'/><path d='M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z'/>"
    )},
    "kaggle": {"stroke": False, "body": (
        "<text x='12' y='18' text-anchor='middle' font-family='Arial, sans-serif' font-size='17' font-weight='800' fill='currentColor'>K</text>"
    )},
    "huggingface": {"stroke": False, "body": (
        "<text x='12' y='17' text-anchor='middle' font-size='14'>🤗</text>"
    )},
}


def icon_svg(name: str, size: int = 20) -> str:
    """Return an inline <svg> for a known icon name (globe as fallback)."""
    spec = ICON_BODIES.get(name, ICON_BODIES["globe"])
    attrs = (
        "fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'"
        if spec["stroke"]
        else "fill='currentColor'"
    )
    return (
        f"<svg viewBox='0 0 24 24' width='{size}' height='{size}' {attrs} "
        f"aria-hidden='true' focusable='false'>{spec['body']}</svg>"
    )


def social_links_html(items: list[dict], size: int = 20, with_labels: bool = False) -> str:
    """Render social links as accessible anchor icons, straight from socials.json.

    Accessibility contract (see docs/DESIGN.md): every link has an aria-label and
    tooltip, 44px touch target, visible focus ring (CSS), target=_blank +
    rel=noopener noreferrer.
    """
    anchors: list[str] = []
    for item in items:
        name = item["name"]
        label = f"{config.AUTHOR_NAME} on {name}"
        icon = icon_svg(item.get("icon", "globe"), size)
        label_html = (
            f"<span class='social-label'>{name}</span>" if with_labels else ""
        )
        anchors.append(
            f"<a class='social-icon' href='{item['url']}' target='_blank' rel='noopener noreferrer' "
            f"aria-label='{label}' title='{label}'>{icon}{label_html}</a>"
        )
    cls = "socials socials-labeled" if with_labels else "socials"
    return f"<div class='{cls}'>{''.join(anchors)}</div>"


# ------------------------------------------------------------------ signs --
def sign_svg(shape: str, symbol: str = "", symbol_color: str = "#111827", size: int = 72) -> str:
    """Render a schematic road sign as inline SVG.

    Shapes: octagon | inv_triangle | circle_red | no_entry | circle_blue |
    rect_blue | rect_green. Pakistan follows the left-hand-traffic signage
    conventions used across the region (red ring = prohibition, blue = mandatory
    or information, red-bordered triangle = warning).
    """
    text = (
        f"<text x='36' y='{34 if len(symbol) <= 2 else 40}' text-anchor='middle' "
        f"font-family='Arial, sans-serif' font-weight='700' font-size='{28 if len(symbol) <= 2 else 20}' "
        f"fill='{symbol_color}'>{symbol}</text>"
    ) if symbol else ""
    body = {
        "octagon": (
            "<polygon points='19,2 45,2 62,19 62,45 45,62 19,62 2,45 2,19' fill='#C1121F' "
            "stroke='#7f0d16' stroke-width='1'/>"
            f"<text x='36' y='40' text-anchor='middle' font-family='Arial' font-weight='800' font-size='16' fill='#ffffff'>{symbol or 'STOP'}</text>"
        ),
        "inv_triangle": (
            "<polygon points='36,60 66,8 6,8' fill='#ffffff' stroke='#C1121F' stroke-width='7' stroke-linejoin='round'/>" + text
        ),
        "circle_red": (
            "<circle cx='36' cy='36' r='31' fill='#ffffff' stroke='#C1121F' stroke-width='8'/>" + text
        ),
        "no_entry": (
            "<circle cx='36' cy='36' r='31' fill='#C1121F'/>"
            "<rect x='10' y='29' width='52' height='14' fill='#ffffff'/>"
        ),
        "circle_blue": (
            "<circle cx='36' cy='36' r='31' fill='#1D4ED8'/>"
            f"<text x='36' y='{44 if len(symbol) <= 2 else 41}' text-anchor='middle' font-family='Arial' font-weight='700' font-size='{30 if len(symbol) <= 2 else 22}' fill='#ffffff'>{symbol}</text>"
        ),
        "rect_blue": (
            "<rect x='3' y='13' width='66' height='46' rx='5' fill='#1D4ED8'/>"
            f"<text x='36' y='{43 if len(symbol) <= 3 else 40}' text-anchor='middle' font-family='Arial' font-weight='700' font-size='{26 if len(symbol) <= 3 else 18}' fill='#ffffff'>{symbol}</text>"
        ),
        "rect_green": (
            "<rect x='3' y='13' width='66' height='46' rx='5' fill='#15803D'/>"
            f"<text x='36' y='{43 if len(symbol) <= 3 else 40}' text-anchor='middle' font-family='Arial' font-weight='700' font-size='{26 if len(symbol) <= 3 else 18}' fill='#ffffff'>{symbol}</text>"
        ),
    }.get(shape, "<rect x='6' y='6' width='60' height='60' fill='#e5e7eb'/>")
    return (
        f"<svg viewBox='0 0 72 72' width='{size}' height='{size}' role='img' aria-label='{shape} sign' "
        f"focusable='false'>{body}</svg>"
    )
