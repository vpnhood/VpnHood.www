#!/usr/bin/env python3
"""Draw the split-tunneling art: one gate, bubbles that say what is split, and our hood carved in its door.

Every split-tunneling page opens on the same gate: the up arrow is traffic that goes around
the VPN, the arrow through the gate is traffic inside it, and the bubbles name what is split.
Two variants came as illustrations, kept untouched in tools/split-art/ as this script's
sources: gate-ip.webp (8.8.8.8 / 1.1.1.1 pills) and gate-local-network.webp (TV, laptop and
printer coins, a shield on the right). The gate and both arrows are pixel-identical in the
two, and every bubble floats on transparent ground, so wherever the two differ inside the
bubble zones the pixel is a bubble: clearing those leaves the clean gate. The other variants
are drawn on it, in the originals' style, with tools/make-split-art.js (teal coins with a
white line glyph, tilted pills holding text); a variant with no bubble on the right keeps the
local-network art's own shield, cut from it as it is.

The door bore a raised hexagon; every published image has our hood carved there instead, as
old weathered stone: the hexagon and the shadow it cast are filled from the stone around them,
and the site's own mark (the path in assets/images/favicon.svg) is laid onto the door's plane
and cut in, with worn edges, a few chips, walls rounded by time and a pitted floor. Only the
door is drawn anew; the rest of each image is the source's, re-encoded (about one level of
WebP noise).

    python tools/make-split-art.py            # writes every image below
    python tools/make-split-art.py --check    # report images that differ from a fresh draw
    python tools/make-split-art.py --app      # the app's own two copies (--app --check to check them)

Writes assets/images/features/art/<name>.webp for the VARIANTS below and for FROM_SOURCE,
the two original drawings. split-overview.webp, the Split Tunneling page's hero, is also its
card on the home page, the features index and CLIENT's page. Never edit those by hand; to add
or change one, edit this script and rerun. The art sits on a transparent ground,
so it needs no light counterpart (see make-light-art.py). Needs Pillow, numpy, Node and the
VpnHood.AppUi.Spa repo beside this one, for its Playwright. Run from the repo root.

The app shows the same two drawings, sharper (640x656): split-ip.webp on its Split Tunneling
screen and access-local-network.webp on Local network, in its asset store in the VpnHood repo
(src/AppUi/VpnHood.AppUi.Assets.Classic/assets/images). --app carves them the same way, from
their untouched originals in tools/split-art/app/, and writes them there. Then run the store's
_zip-assets.ps1, as its assets/ and ui.zip are committed together, and redraw the site's pictures
of those screens: make-app-shots.py --only split-tunneling,split-local-network,connect-split-tunneling.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "images" / "features" / "art"
SRC = ROOT / "tools" / "split-art"
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
FROM_SOURCE = {"split-by-ip": "gate-ip.webp", "split-local-network": "gate-local-network.webp"}
# The app's own copies of the two drawings: untouched in tools/split-art/app/, carved into the app's asset store.
APP_ART = ROOT.parent / "VpnHood" / "src" / "AppUi" / "VpnHood.AppUi.Assets.Classic" / "assets" / "images"
APP_SOURCE = ["split-ip.webp", "access-local-network.webp"]
# The bubble zones of the two originals: left above the up arrow, right above the through arrow.
LEFT, RIGHT = (slice(30, 192), slice(10, 150)), (slice(110, 225), slice(355, 468))


def clean_gate() -> tuple[Image.Image, Image.Image]:
    ip = np.array(Image.open(SRC / "gate-ip.webp").convert("RGBA")).astype(int)
    ln = np.array(Image.open(SRC / "gate-local-network.webp").convert("RGBA"))
    differ = np.abs(ip - ln.astype(int)).sum(axis=2) > 25
    zone = np.zeros(differ.shape, bool)
    zone[LEFT] = zone[RIGHT] = True
    grown = np.array(Image.fromarray(((differ & zone) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    base = ip.copy()
    base[grown & zone] = 0
    shield = np.zeros_like(ln)
    shield[RIGHT] = ln[RIGHT]
    return Image.fromarray(base.astype(np.uint8)), Image.fromarray(shield)


def carve_door(gate: Image.Image, hood_png: Path, out_size: tuple[int, int] = (468, 480)) -> tuple[Image.Image, np.ndarray]:
    """The gate with the hexagon gone and the hood carved in its place, and how much of each pixel that is (0..1).

    The work is done on the drawing at four times 468x480, whatever its own size, so every measure below is in
    468x480 pixels; the result comes out at `out_size`, the app's 640x656 copies as sharp as they came in."""
    S = 4
    big = np.array(gate.resize((468 * S, 480 * S), Image.LANCZOS)).astype(float)
    H, W = big.shape[:2]

    def blur(a, r):
        return np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(float) / 255

    def vnoise(cells, seed):
        n = np.random.default_rng(seed).random((cells, cells))
        return np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(float) / 255

    # 1. Erase the hexagon: a polygon around it, filled from a quadratic fitted to the teal stone just outside it.
    hexpoly = [(199, 112), (222, 101), (250, 139), (251, 173), (229, 195), (198, 156)]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in hexpoly], fill=255)
    hole = np.array(m.filter(ImageFilter.MaxFilter(4 * S + 1))) > 0
    ring = (np.array(m.filter(ImageFilter.MaxFilter(22 * S + 1))) > 0) & ~hole
    r, g, a = big[..., 0], big[..., 1], big[..., 3]
    face = ring & (a > 240) & (g > r + 30) & (g > 120)  # teal stone only, not the rim, arch or circuit lines
    ys, xs = np.nonzero(face)
    nrm = np.array([1, W, H, W * W, W * H, H * H], float)

    def design(px, py):
        return np.stack([np.ones_like(px), px, py, px * px, px * py, py * py], 1).astype(float) / nrm

    coefs = [np.linalg.lstsq(design(xs, ys), big[ys, xs, c], rcond=None)[0] for c in range(3)]
    # The hexagon cast a shadow just past its lower-right edge: any pixel near it darker than the fitted stone is that
    # shadow and joins the hole. The door's own drawings are lighter than the stone, so they stay.
    near = (np.array(m.filter(ImageFilter.MaxFilter(14 * S + 1))) > 0) & ~hole & (a > 240)
    ny, nx = np.nonzero(near)
    fit = np.stack([design(nx, ny) @ coefs[c] for c in range(3)], 1)
    dark = (fit.sum(1) - big[ny, nx, :3].sum(1)) > 30
    shadow = np.zeros_like(hole)
    shadow[ny[dark], nx[dark]] = True
    shadow = np.array(Image.fromarray((shadow * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * S + 1))) > 0
    hole = hole | (shadow & (a > 240))
    hy, hx = np.nonzero(hole)
    rng = np.random.default_rng(7)
    for c in range(3):
        resid = big[ys, xs, c] - design(xs, ys) @ coefs[c]
        big[hy, hx, c] = design(hx, hy) @ coefs[c] + rng.normal(0, resid.std() * 0.6, len(hy))
    big[hy, hx, 3] = 255
    fill = Image.fromarray(np.clip(big, 0, 255).astype(np.uint8))
    blurred = np.array(fill.filter(ImageFilter.GaussianBlur(1.2 * S))).astype(float)
    hm = Image.fromarray((hole * 255).astype(np.uint8))
    seam = (np.array(hm.filter(ImageFilter.MaxFilter(3 * S + 1))) > 0) & ~(np.array(hm.filter(ImageFilter.MinFilter(3 * S + 1))) > 0)
    big[seam, :3] = blurred[seam, :3]

    # 2. The hood on the door's plane: x foreshortened to 0.61, level lines falling 31.8 degrees to the right, centred
    # where the hexagon sat. Its thinnest tips (the cloak's tails) are slivers at this size and would read as a stray
    # line, so an opening of about 1.2 px removes them.
    size = 96 * S
    hood = Image.open(hood_png).convert("L").resize((size, size), Image.LANCZOS)
    sx, k = 0.61, np.tan(np.radians(31.8))
    cx, cy = 226 * S, 139 * S
    inv = (1 / sx, 0, -cx / sx + size / 2, -k, 1, k * cx - cy + size / 2)
    plane = hood.transform((W, H), Image.AFFINE, inv, resample=Image.BICUBIC)
    plane = plane.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    M = np.array(plane).astype(float) / 255

    # 3. Carve it, as old weathered stone: worn wobbly edges with a few chips, walls rounded by time, a pitted floor a
    # little darker and greyer than the stone with grime in its corners, the stone around faintly pitted, fading out.
    soft = blur(M, 1.0 * S)
    wob = (vnoise(46, 11) - 0.5) * 0.3 + (vnoise(140, 12) - 0.5) * 0.22
    Mo = np.clip((soft + wob * 0.5 - 0.5) * 7 + 0.5, 0, 1)
    Mo = np.array(Image.fromarray((Mo * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7))).astype(float) / 255
    rim = (blur(Mo, 0.8 * S) > 0.2) & (blur(Mo, 0.8 * S) < 0.8)
    ry, rx = np.nonzero(rim)
    crng = np.random.default_rng(21)
    chips = Image.new("L", (W, H), 0)
    cd = ImageDraw.Draw(chips)
    for i in crng.choice(len(ry), size=min(14, len(ry)), replace=False):
        rr = crng.uniform(0.5, 1.1) * S
        cd.ellipse([rx[i] - rr, ry[i] - rr * crng.uniform(0.6, 1.0), rx[i] + rr, ry[i] + rr * crng.uniform(0.6, 1.0)], fill=255)
    Mo = np.maximum(Mo, np.array(chips.filter(ImageFilter.GaussianBlur(0.4 * S))).astype(float) / 255)
    around = np.clip(blur(Mo, 7 * S) * 3.2, 0, 1)
    depth = blur(Mo, 1.25 * S)
    pits = (vnoise(170, 13) - 0.5) + (vnoise(60, 14) - 0.5) * 0.6
    rough = vnoise(220, 15) - 0.5
    gy, gx = np.gradient(-depth + Mo * pits * 0.2 + (1 - Mo) * around * rough * 0.08)
    light = np.array([-0.62, -0.78])  # from the top left, as the rest of the art is lit
    shade = np.clip(-(gx * light[0] + gy * light[1]) * 1.35 * S, -1, 1)
    grime = np.clip(Mo - blur(Mo, 2.8 * S), 0, 1) * 1.2
    floor = np.array([30, 114, 104], float)
    lum = big[..., :3].mean(axis=2)
    for c in range(3):
        greyed = big[..., c] * 0.75 + lum * 0.25
        big[..., c] = big[..., c] * (1 - Mo) + (greyed * 0.56 + floor[c] * 0.44) * Mo - grime * 18 + shade * 72
    grain = rng.normal(0, 1, (H, W))
    coarse = (vnoise(90, 16) - 0.5) * 2
    for c in range(3):
        big[..., c] += grain * (Mo * 8 + (1 - Mo) * around * 4) + coarse * Mo * 8

    carved = Image.fromarray(np.clip(big, 0, 255).astype(np.uint8)).resize(out_size, Image.LANCZOS)
    touched = (np.array(hm.filter(ImageFilter.MaxFilter(4 * S + 1))) > 0) | (around > 0.004) | (Mo > 0)
    region = Image.fromarray((touched * 255).astype(np.uint8)).resize(out_size, Image.BOX).point(lambda v: 255 if v else 0)
    k = out_size[0] / 468  # the region's margin and feather, 2px and 1px at 468, in the output's pixels
    region = region.filter(ImageFilter.MaxFilter(2 * round(2 * k) + 1)).filter(ImageFilter.GaussianBlur(k))
    return carved, np.array(region).astype(float) / 255


def render(tmp: Path) -> None:
    """The bubbles of every variant and the hood's mask, drawn by make-split-art.js into tmp."""
    if not PLAYWRIGHT.is_dir():
        sys.exit(f"Playwright not found at {PLAYWRIGHT}: the VpnHood.AppUi.Spa repo must sit beside this one, with its npm packages installed.")
    spec = tmp / "variants.json"
    spec.write_text(json.dumps(VARIANTS), encoding="utf-8")
    subprocess.run(["node", str(ROOT / "tools" / "make-split-art.js"), str(PLAYWRIGHT), str(tmp), str(spec)], check=True)


def draw_app(tmp: Path) -> dict[str, Image.Image]:
    """The app's two copies, each carved at its own size and laid over itself: no bubble reaches the door."""
    render(tmp)
    out = {}
    for source in APP_SOURCE:
        img = Image.open(SRC / "app" / source).convert("RGBA")
        carved, region = carve_door(img, tmp / "hood-mask.png", img.size)
        px = np.array(img).astype(float) * (1 - region[..., None]) + np.array(carved).astype(float) * region[..., None]
        out[Path(source).stem] = Image.fromarray(np.clip(np.rint(px), 0, 255).astype(np.uint8))
    return out


def draw(tmp: Path) -> dict[str, Image.Image]:
    render(tmp)
    base, shield = clean_gate()
    carved, region = carve_door(base, tmp / "hood-mask.png")
    images = {}
    for name, parts in VARIANTS.items():
        img = base.copy()
        # The shield stands for "inside the VPN" wherever a variant puts no bubble of its own on the right.
        if all(at["x"] + at["w"] < RIGHT[1].start for _, at, *_ in parts):
            img.alpha_composite(shield)
        img.alpha_composite(Image.open(tmp / f"{name}-bubbles.png").convert("RGBA").resize((468, 480), Image.LANCZOS))
        images[name] = img
    for name, source in FROM_SOURCE.items():
        images[name] = Image.open(SRC / source).convert("RGBA")
    # The door is the same in every image and no bubble reaches it: lay the carved door over each one.
    door = np.array(carved).astype(float)
    out = {}
    for name, img in images.items():
        px = np.array(img).astype(float)
        px = px * (1 - region[..., None]) + door * region[..., None]
        out[name] = Image.fromarray(np.clip(np.rint(px), 0, 255).astype(np.uint8))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report images that differ from a fresh draw; write nothing")
    ap.add_argument("--app", action="store_true", help="the app's own two copies, in the VpnHood repo, not the site's")
    args = ap.parse_args()
    if args.app and not APP_ART.is_dir():
        sys.exit(f"The app's asset store is not at {APP_ART}: the VpnHood repo must sit beside this one.")
    # The app's copies keep near their old weight: they came at a quality well above the site's.
    out_dir, quality = (APP_ART, 95) if args.app else (ART, 88)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        drawn = draw_app(tmp) if args.app else draw(tmp)
        stale = []
        for name, img in drawn.items():
            path = out_dir / f"{name}.webp"
            fresh = tmp / f"{name}.webp"
            img.save(fresh, quality=quality, method=6)
            if not path.exists() or path.read_bytes() != fresh.read_bytes():
                stale.append(name)
                if not args.check:
                    path.write_bytes(fresh.read_bytes())
    if args.check:
        print("stale: " + ", ".join(stale) if stale else "all images current")
        sys.exit(1 if stale else 0)
    print(f"wrote {len(stale)} of {len(drawn)} images" + (f": {', '.join(stale)}" if stale else ""))


if __name__ == "__main__":
    main()
