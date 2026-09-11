#!/usr/bin/env python3
"""Generate the site's dotted-world land data from Natural Earth.

Two outputs, both equirectangular (x is longitude, y is latitude, linear on both
axes), both without Antarctica:

    _includes/globe-land-points.json      the home globe's land dots, on the
                                          2048x1024 canvas globe.js maps onto the
                                          sphere: x = (lng + 180) * 2048/360,
                                          y = (90 - lat) * 1024/180.
    assets/images/general/world-dots.svg  the flat map behind the pins on
                                          /free-vpn/, viewBox 0 0 360 140 =
                                          longitude -180..180 by latitude 84..-56,
                                          used as a CSS mask so one file serves
                                          both colour themes.

Because both are true equirectangular, a country's dot or pin is a plain linear
function of its lat/lng in _data/locations.yml (the Liquid in
assets/js/globe-points.json and _includes/location-map.html). The previous land
dots were traced from a decorative map that was NOT equirectangular (the Pacific
was narrowed, the Americas squeezed), so every American city projected into the
sea; this replaces them.

Source: tools/ne_110m_land.geojson, Natural Earth 1:110m "land" (public domain,
https://www.naturalearthdata.com/, mirrored from
https://github.com/nvkelso/natural-earth-vector). Run from the repo root:

    python tools/make-land-dots.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "tools", "ne_110m_land.geojson")
GLOBE_OUT = os.path.join(ROOT, "_includes", "globe-land-points.json")
SVG_OUT = os.path.join(ROOT, "assets", "images", "general", "world-dots.svg")

# Globe canvas (globe.js props.mapSize is half of this; the JSON is in these units).
GLOBE_W, GLOBE_H = 2048, 1024
GLOBE_STEP = 9              # px between dots, same pitch as the traced set had
# Flat map: crop the poles (nothing to show above Greenland or below Cape Horn).
MAP_TOP, MAP_BOTTOM = 84.0, -56.0
MAP_PITCH = 1.6             # degrees between dots, rows offset by half a pitch
MAP_DOT = 1.05              # dot diameter in degrees (stroke width of the path)
SOUTH_LIMIT = -56.0         # drop Antarctica from both outputs


def load_polygons(path):
    """Return [(bbox, [rings])] for every polygon; a point is land when it lies
    inside an odd number of a polygon's rings (outer ring plus holes)."""
    with open(path, encoding="utf-8") as fh:
        geo = json.load(fh)
    polys = []
    for feature in geo["features"]:
        geom = feature["geometry"]
        shapes = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for rings in shapes:
            xs = [p[0] for p in rings[0]]
            ys = [p[1] for p in rings[0]]
            if max(ys) < SOUTH_LIMIT:
                continue  # Antarctica
            polys.append(((min(xs), min(ys), max(xs), max(ys)), rings))
    return polys


def in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def is_land(polys, lng, lat):
    for (x0, y0, x1, y1), rings in polys:
        if lng < x0 or lng > x1 or lat < y0 or lat > y1:
            continue
        hits = 0
        for ring in rings:
            if in_ring(lng, lat, ring):
                hits ^= 1
        if hits:
            return True
    return False


def globe_points(polys):
    px_per_deg = GLOBE_W / 360.0
    out = []
    y = GLOBE_STEP / 2.0
    while y < GLOBE_H:
        lat = 90.0 - y / px_per_deg
        if lat >= SOUTH_LIMIT:
            x = GLOBE_STEP / 2.0
            while x < GLOBE_W:
                lng = x / px_per_deg - 180.0
                if is_land(polys, lng, lat):
                    out.append({"x": int(round(x)), "y": int(round(y))})
                x += GLOBE_STEP
        y += GLOBE_STEP
    return out


def map_path(polys):
    """One path: an absolute move per row start, relative moves along the row,
    'h0' after each so the zero-length segment is stroked as a round dot."""
    rows = []
    count = 0
    lat = MAP_TOP - MAP_PITCH / 2.0
    row = 0
    while lat > MAP_BOTTOM:
        offset = MAP_PITCH / 2.0 if row % 2 else 0.0
        lng = -180.0 + MAP_PITCH / 2.0 + offset
        segs = []
        prev = None
        while lng < 180.0:
            if is_land(polys, lng, lat):
                x = round(lng + 180.0, 2)
                y = round(MAP_TOP - lat, 2)
                if prev is None:
                    segs.append("M%s %sh0" % (fmt(x), fmt(y)))
                else:
                    segs.append("m%s 0h0" % fmt(round(x - prev, 2)))
                prev = x
                count += 1
            lng += MAP_PITCH
        if segs:
            rows.append("".join(segs))
        lat -= MAP_PITCH
        row += 1
    return "".join(rows), count


def fmt(n):
    s = ("%.2f" % n).rstrip("0").rstrip(".")
    return s if s else "0"


def main():
    if not os.path.exists(SOURCE):
        sys.exit("missing %s" % SOURCE)
    polys = load_polygons(SOURCE)

    points = globe_points(polys)
    with open(GLOBE_OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(points, separators=(",", ":")) + "\n")
    print("%s: %d dots" % (os.path.relpath(GLOBE_OUT, ROOT), len(points)))

    d, count = map_path(polys)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 %s">'
        "<!-- Generated by tools/make-land-dots.py from Natural Earth 1:110m land "
        "(public domain). Equirectangular: x = longitude + 180, y = 84 - latitude. "
        "Used as a CSS mask, so the colour here is irrelevant. -->"
        '<path fill="none" stroke="#000" stroke-width="%s" stroke-linecap="round" d="%s"/></svg>\n'
        % (fmt(MAP_TOP - MAP_BOTTOM), fmt(MAP_DOT), d)
    )
    os.makedirs(os.path.dirname(SVG_OUT), exist_ok=True)
    with open(SVG_OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("%s: %d dots, %d bytes" % (os.path.relpath(SVG_OUT, ROOT), count, len(svg.encode("utf-8"))))


if __name__ == "__main__":
    main()
