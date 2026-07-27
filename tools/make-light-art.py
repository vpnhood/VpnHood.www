#!/usr/bin/env python3
"""Derive the light theme's decorative art from the dark originals.

The site's backdrops are all "bright glow on a near-black field", authored for the dark
theme. The light theme needs the same artwork reading the other way round, so this script
generates a `<name>-light.<ext>` sibling for each one; /assets/js/theme.js and
_sass/theme/_light.scss point at those when <html data-theme="light">.

THIS SCRIPT IS THE ONLY WAY LIGHT ART IS PRODUCED. Every `*-light.*` file under
assets/images/ is generated output. Do not hand-author one, do not hand-edit one, and do
not reach for a per-image CSS filter instead — the next run overwrites hand edits, and
`filter: invert()` on this art turns dark indigo into pale yellow. To give a dark image a
light counterpart:

    1. register the source below — RASTERS for bitmaps, SVGS for vectors
    2. python tools/make-light-art.py            # regenerate everything
    3. reference the generated file: a background-image override in
       _sass/theme/_light.scss, or data-vh-light-src="…" on the <img>

    python tools/make-light-art.py --check      # missing/stale report, writes nothing

See the "Light-mode art" section of CLAUDE.md for the same workflow in context.

Rasters are inverted in HSL — *lightness* flips while hue and saturation survive, because
a plain RGB invert turns dark indigo into pale yellow. The inverted lightness is remapped
into [LO, HI] so the brightest core lands on a mid purple rather than black, and the flat
field is cross-faded into the light theme's page background so a full-bleed backdrop has
no seam where the image stops. SVGs are recoloured through an explicit per-file map —
they are hand-authored vector art, so guessing is worse than naming the swaps.

DELIBERATELY NOT CONVERTED: anything depicting the real (dark) app UI — the CONNECT
screenshots, the phone mockup, and `vpnhood-connect/download-pending-bg.webp`, which looks
like a backdrop but is a phone running the app. Those must render identically in both
themes. Also skipped: the brand logos and flag/brand marks, and art that already reads on
a light page (the soft purple/green hero glows, the resilient underline, the guarantee
ring, the rocket, the two `light-bg-*` blurs, the open-source swirl).

Requires Pillow + NumPy (`pip install pillow numpy`). Run from the repo root.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"

LO = 0.34                   # what the brightest source pixel becomes
HI = 0.985                  # what the darkest source pixel becomes
SAT = 1.12                  # colour reads weaker against white
# Must match --purple-800 under [data-theme="light"] in _sass/theme/_light.scss: it is
# what the flat field melts into, so if one changes without the other every full-bleed
# backdrop grows a visible seam where the image stops.
PAGE_BG = (244, 242, 251)
FADE = (0.80, 1.0)          # lightness band over which the field melts into the page

# source -> blur radius applied to the SOURCE before inverting. The dark originals are
# heavily compressed, and blocks that hide inside a near-black field (or inside a blown-out
# glow core) turn into visible mottling once lightness is flipped and saturation is pushed.
# Smoothing the input kills that at the root; smoothing the output only smears it. These
# are all soft gradients, so nothing sharp is lost — keep it low for art with fine detail.
RASTERS = {
    "home/banner-bg.webp": 0.8,
    "home/features-bg.webp": 0.8,
    "home/steadfast-bg.webp": 2.0,    # blown-out glow core, heavily blocked
    "home/download-bg.webp": 0.8,
    "home/options-bg.webp": 1.5,      # near-transparent circuit grid; inverts noisy
    "home/commiunity-bg.webp": 3.0,   # magenta fringing along the arc without this
    "home/enhance-security-bg.webp": 0.3,
    "general/manager-bg.webp": 0.8,
    "general/purple-hole.webp": 0.4,  # keep the funnel's radial lines readable
    "general/purple-hole-overlap.webp": 0.4,
}

QUALITY = 88
# Per-file WebP quality override, for art whose inverted form compresses badly and whose
# detail nobody can see anyway.
QUALITY_OVERRIDES = {"home/options-bg.webp": 75}

# source -> {dark colour: light colour}. Case-insensitive on the hex digits.
SVGS = {
    # Opaque dark tile behind the download platform icons.
    "general/purple-hexagon.svg": {
        "#030216": "#f4f2fb",   # the tile itself
        "#BAB3FF": "#4b3f8f",   # hairline hex outlines
        "#CDB4FF": "#5b3fbd",   # gradient strokes
    },
    # Wireframe globe: white nodes and pale lat/long lines.
    "general/purple-line-globe.svg": {
        "white": "#2b1f63",
        "#BAB3FF": "#6d61c4",
        "#8566FF": "#5a3fd6",
        "#CB8FFF": "#8a3fd6",
        "#7096FF": "#3f63d6",
    },
    # Reseller half-globe: bright brand purples/mint on black.
    "general/half-globe-purple.svg": {
        "#9066FB": "#6a3fe0",
        "#B79AFF": "#7d6bd2",
        "#3FF6A9": "#12a071",
        "#605393": "#7c6cc6",
    },
    # Platform glyphs: a white -> brand-purple vertical gradient, so their top half
    # dissolves into a light page. Flip the top stop the same way the gradient headings
    # flip (near-black into the brand purple).
    "general/android-icon-grad-purple-300.svg": {"white": "#241858"},
    "general/android-tv-icon-grad-purple-300.svg": {"white": "#241858"},
    "general/windows-icon-grad-purple-300.svg": {"white": "#241858"},
    # Off-canvas "Log In" glyph. It rides a .vh-btn-secondary, which is a light chip in
    # light mode. (go-premium-icon.svg is NOT here: its button stays brand purple.)
    "general/login-icon.svg": {"#fff": "#17123a"},
}


def light_raster(im: Image.Image, blur: float = 0.0) -> Image.Image:
    im = im.convert("RGBA")
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im).astype(np.float32) / 255.0
    r, g, b, alpha = a[..., 0], a[..., 1], a[..., 2], a[..., 3]

    mx = np.max(a[..., :3], axis=-1)
    mn = np.min(a[..., :3], axis=-1)
    lightness = (mx + mn) / 2
    chroma = mx - mn
    sat = np.where(chroma == 0, 0, chroma / (1 - np.abs(2 * lightness - 1) + 1e-6))

    hue = np.zeros_like(lightness)
    m = chroma != 0
    rm = m & (mx == r)
    gm = m & (mx == g) & ~rm
    bm = m & (mx == b) & ~rm & ~gm
    hue[rm] = ((g - b)[rm] / chroma[rm]) % 6
    hue[gm] = ((b - r)[gm] / chroma[gm]) + 2
    hue[bm] = ((r - g)[bm] / chroma[bm]) + 4
    hue /= 6

    l2 = LO + (HI - LO) * (1 - lightness)
    s2 = np.clip(sat * SAT, 0, 1)

    c = (1 - np.abs(2 * l2 - 1)) * s2
    hp = hue * 6
    x = c * (1 - np.abs(hp % 2 - 1))
    z = np.zeros_like(c)
    conds = [hp < 1, hp < 2, hp < 3, hp < 4, hp < 5, hp <= 6]
    r2 = np.select(conds, [c, x, z, z, x, c])
    g2 = np.select(conds, [x, c, c, x, z, z])
    b2 = np.select(conds, [z, z, x, c, c, x])
    off = l2 - c / 2
    rgb = np.clip(np.stack([r2 + off, g2 + off, b2 + off], axis=-1), 0, 1)

    f0, f1 = FADE
    t = np.clip((l2 - f0) / (f1 - f0), 0, 1)
    t = (t * t * (3 - 2 * t))[..., None]  # smoothstep
    rgb = rgb * (1 - t) + (np.array(PAGE_BG, dtype=np.float32) / 255.0) * t

    out = np.concatenate([rgb, alpha[..., None]], axis=-1)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")


def light_name(rel: str) -> str:
    p = Path(rel)
    return str(p.with_name(p.stem + "-light" + p.suffix))


def recolour_svg(text: str, swaps: dict[str, str]) -> str:
    for dark, light in swaps.items():
        if dark.startswith("#"):
            for form in (dark.lower(), dark.upper()):
                text = text.replace(form, light)
        else:
            # bare keyword: only inside a fill=/stroke=/stop-color= value
            for attr in ("fill", "stroke", "stop-color"):
                text = text.replace(f'{attr}="{dark}"', f'{attr}="{light}"')
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="only report what would change")
    args = ap.parse_args()

    missing = []
    for rel, blur in RASTERS.items():
        src, dst = IMAGES / rel, IMAGES / light_name(rel)
        if not src.exists():
            print(f"missing source: {rel}", file=sys.stderr)
            return 2
        if args.check:
            if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                missing.append(light_name(rel))
            continue
        quality = QUALITY_OVERRIDES.get(rel, QUALITY)
        light_raster(Image.open(src), blur).save(dst, "WEBP", quality=quality, method=6)
        print(f"{rel} -> {light_name(rel)}  ({dst.stat().st_size // 1024} KB)")

    for rel, swaps in SVGS.items():
        src, dst = IMAGES / rel, IMAGES / light_name(rel)
        if not src.exists():
            print(f"missing source: {rel}", file=sys.stderr)
            return 2
        if args.check:
            if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                missing.append(light_name(rel))
            continue
        text = src.read_text(encoding="utf-8")
        out = recolour_svg(text, swaps)
        if out == text:
            print(f"WARNING: no colour matched in {rel}", file=sys.stderr)
        dst.write_text(out, encoding="utf-8")
        print(f"{rel} -> {light_name(rel)}")

    if missing:
        print("stale or missing light art:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
