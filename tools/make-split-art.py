#!/usr/bin/env python3
"""Draw the split-tunneling art variants: one gate, with bubbles that say what is split.

Every split-tunneling page opens on the same gate: the up arrow is traffic that goes around
the VPN, the arrow through the gate is traffic inside it, and the bubbles name what is split.
Two variants came as illustrations, split-by-ip.webp (8.8.8.8 / 1.1.1.1 pills) and
split-local-network.webp (TV, laptop and printer coins, a shield on the right). The gate and
both arrows are pixel-identical in the two, and every bubble floats on transparent ground, so
wherever the two differ inside the bubble zones the pixel is a bubble: clearing those leaves
the clean gate. This script draws the other variants on it, in the originals' style, with
tools/make-split-art.js (teal coins with a white line glyph, tilted pills holding text); a
variant with no bubble on the right keeps the local-network art's own shield, cut from it as
it is.

    python tools/make-split-art.py            # writes the VARIANTS below
    python tools/make-split-art.py --check    # report variants that differ from a fresh draw

Writes assets/images/features/art/<name>.webp. Never edit those by hand; to add or change a
variant, edit VARIANTS and rerun. The art sits on a transparent ground, so it needs no light
counterpart (see make-light-art.py). Needs Pillow, Node and the VpnHood.AppUi.Spa repo beside
this one, for its Playwright. Run from the repo root.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "images" / "features" / "art"
PLAYWRIGHT = ROOT.parent / "VpnHood.AppUi.Spa" / "src" / "VpnHood.AppUi.Presentation.Classic.Spa" / "node_modules" / "playwright"

# Coins sit where the local-network art has its three; pills where the IP art has its two.
C1 = {"x": 28, "y": 47, "w": 50, "h": 68}
C2 = {"x": 83, "y": 80, "w": 53, "h": 73}
C3 = {"x": 37, "y": 123, "w": 44, "h": 60}
VARIANTS = {
    "split-overview": [["coin", C1, "play"], ["coin", C2, "www"], ["coin", C3, "flag"]],
    "split-by-app": [["coin", C1, "play"], ["coin", C2, "bank"], ["coin", C3, "chat"]],
    "split-by-country": [["coin", C1, "flag"], ["coin", C2, "pin"], ["coin", C3, "map"]],
    "split-by-domain": [["pill", {"x": 26, "y": 88, "w": 118}, "bank.com", "violet"],
                        ["pill", {"x": 343, "y": 122, "w": 118}, "news.com", "teal"]],
    "split-dns": [["pill", {"x": 52, "y": 96, "w": 82}, "DNS", "violet"]],
}
# The bubble zones of the two originals: left above the up arrow, right above the through arrow.
LEFT, RIGHT = (slice(30, 192), slice(10, 150)), (slice(110, 225), slice(355, 468))


def clean_gate() -> tuple[Image.Image, Image.Image]:
    ip = np.array(Image.open(ART / "split-by-ip.webp").convert("RGBA")).astype(int)
    ln = np.array(Image.open(ART / "split-local-network.webp").convert("RGBA"))
    differ = np.abs(ip - ln.astype(int)).sum(axis=2) > 25
    zone = np.zeros(differ.shape, bool)
    zone[LEFT] = zone[RIGHT] = True
    grown = np.array(Image.fromarray(((differ & zone) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    base = ip.copy()
    base[grown & zone] = 0
    shield = np.zeros_like(ln)
    shield[RIGHT] = ln[RIGHT]
    return Image.fromarray(base.astype(np.uint8)), Image.fromarray(shield)


def draw(tmp: Path) -> dict[str, Image.Image]:
    if not PLAYWRIGHT.is_dir():
        sys.exit(f"Playwright not found at {PLAYWRIGHT}: the VpnHood.AppUi.Spa repo must sit beside this one, with its npm packages installed.")
    spec = tmp / "variants.json"
    spec.write_text(json.dumps(VARIANTS), encoding="utf-8")
    subprocess.run(["node", str(ROOT / "tools" / "make-split-art.js"), str(PLAYWRIGHT), str(tmp), str(spec)], check=True)
    base, shield = clean_gate()
    out = {}
    for name, parts in VARIANTS.items():
        img = base.copy()
        # The shield stands for "inside the VPN" wherever a variant puts no bubble of its own on the right.
        if all(at["x"] + at["w"] < RIGHT[1].start for _, at, *_ in parts):
            img.alpha_composite(shield)
        img.alpha_composite(Image.open(tmp / f"{name}-bubbles.png").convert("RGBA").resize((468, 480), Image.LANCZOS))
        out[name] = img
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report variants that differ from a fresh draw; write nothing")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        drawn = draw(tmp)
        stale = []
        for name, img in drawn.items():
            path = ART / f"{name}.webp"
            fresh = tmp / f"{name}.webp"
            img.save(fresh, quality=88, method=6)
            if not path.exists() or path.read_bytes() != fresh.read_bytes():
                stale.append(name)
                if not args.check:
                    path.write_bytes(fresh.read_bytes())
    if args.check:
        print("stale: " + ", ".join(stale) if stale else "all variants current")
        sys.exit(1 if stale else 0)
    print(f"wrote {len(stale)} of {len(drawn)} variants" + (f": {', '.join(stale)}" if stale else ""))


if __name__ == "__main__":
    main()
