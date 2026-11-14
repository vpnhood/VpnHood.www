#!/usr/bin/env python3
"""Draw the products' icons for a row of card icons: each product's hood from its logo, with a small badge.

    python tools/make-product-icons.py

Writes _includes/icons/product-connect.svg, product-client.svg and product-manager.svg on the icon set's 24-unit
grid, to sit in `.vh-feature-icon`'s disc like any other card icon. Each takes the hood from its product's logo
(assets/images/general/connect-logo.svg, client-logo.svg, .sources/images/manager-logo.svg). CONNECT's and CLIENT's,
which are the same hood, sit up and to the right, beside a badge at the bottom left that says what the product is for:
a globe for VpnHood! CONNECT (our servers around the world), a key for VpnHood! CLIENT (it connects with an access
key). MANAGER's hood is its own, so it stands alone, centred. The
logo's ring and name ribbon are left out: at a card icon's size the ribbon's name cannot be read (owner, 2026-11-13:
"remove circle and label, they are not readable, for connect you can put small globe icon ... and for client use a
key"). Everything is `currentColor`.

Run it again after a logo changes; never edit the icons by hand.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERAL = os.path.join(ROOT, "assets", "images", "general")
OUT = os.path.join(ROOT, "_includes", "icons")

# The badges, as the icon set draws them on its 24-unit grid (the globe as the rest of the set would draw one, the key
# is _includes/icons/key.svg).
GLOBE = ('<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/>'
         '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>')
KEY = ('<path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"/><path d="m21 2-9.6 9.6"/>'
       '<circle cx="7.5" cy="15.5" r="5.5"/>')
# Where each hood goes. CONNECT's and CLIENT's hood fills x 62..262, y 60..227 of its logo's 324-unit square: drawn
# up and to the right, clear of the badge (a gap cut out of the hood around an overlapping badge left a thin sliver of
# hood along its edge). MANAGER's hood, x 80..245, y 60..269, has no badge, as it is a hood of its own: centred.
BESIDE_BADGE = "translate(7 1) scale(0.084) translate(-62 -60)"
CENTRED = "translate(3.72 1.5) scale(0.1005) translate(-80.11 -60)"
# The badges in the bottom left corner, each with its line 1.6 thick once scaled. The globe is the 24-unit glyph at
# 0.45. The key lies flat (owner, 2026-11-13: "make vpnhood client key icon horizontal"): turned 45 degrees about its
# ring, it spans x 0.2..28.4, y 8.2..22.8 with its 3.51 line, so at 0.456 it fills x 0.4..13.2, y 16.0..22.6, under
# the hood, whose lowest point is y 15.
GLOBE_BADGE = (GLOBE, "translate(0 13.2) scale(0.45)", "3.56")
KEY_BADGE = (KEY, "translate(0.25 12.23) scale(0.456) rotate(45 7.5 15.5)", "3.51")
PRODUCTS = {
    "connect": (os.path.join(GENERAL, "connect-logo.svg"), BESIDE_BADGE, GLOBE_BADGE),
    "client": (os.path.join(GENERAL, "client-logo.svg"), BESIDE_BADGE, KEY_BADGE),
    "manager": (os.path.join(ROOT, ".sources", "images", "manager-logo.svg"), CENTRED, None),
}

RIBBON = re.compile(r'<g transform="translate\(238 84\) rotate\(40\)')


def hood(svg, name):
    """the hood: the one filled path of the logo's ring group before its name ribbon (the ring is not filled
    with a colour, or is a circle)"""
    group = svg[svg.index('transform="translate(162 162) scale(1.1) translate(-162.5 -160.5)"'):]
    group = group[:RIBBON.search(group).start()]
    paths = [d for d in re.findall(r'<path d="([^"]+)"[^>]*fill="#[0-9A-Fa-f]{6}"', group)
             if not d.startswith("M162.5,160.5m")]
    if len(paths) != 1:
        sys.exit(f"{name}: expected one hood path, found {len(paths)}")
    return paths[0]


def icon(name, svg, place, badge):
    head = ('<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">')
    drawn = f'<path transform="{place}" d="{hood(svg, name)}" fill="currentColor" stroke="none"/>'
    if badge:
        glyph, transform, stroke = badge
        drawn += f'<g transform="{transform}" stroke-width="{stroke}">{glyph}</g>'
    return f"{head}{drawn}</svg>\n"


def main():
    for name, (src, place, badge) in PRODUCTS.items():
        with open(src, encoding="utf-8") as f:
            svg = f.read()
        out = os.path.join(OUT, f"product-{name}.svg")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(icon(name, svg, place, badge))
        print(f"{os.path.relpath(out, ROOT)} from {os.path.relpath(src, ROOT)}")


if __name__ == "__main__":
    main()
