#!/usr/bin/env python3
"""Cut the home hero's guardian out of her black backdrop, for phones and tablets.

banner-guardian.webp is the dark theme's hero: the hooded girl on a flat near-black field,
opaque so the stars and the two glows behind her never show through her body. On a desktop
the field fills the hero, so nothing ends inside it. Up to 991px wide the hero stacks, and the
portrait sits halfway down it, so the field's top edge ran across the screen in a straight
line: stars and glows above it, a black box below. That field is also darker than the page,
so its bottom edge showed as well.

This script writes banner-guardian-cutout.webp, the same picture with that field
transparent, which _sass/pages/_home.scss shows up to 991px. She stays opaque. The field is
grown in from the top, left and right edges through pixels that are both dark and flat: the
field is a flat colour, while her shadowed right side, as dark as the field, still carries the
weave of the cloth. Whatever the field cannot reach is her: the dark inside of the hood and
the cloak's folds stay solid, gaps in her outline narrower than SEAL are closed first, and
specks the field did not reach but that are not joined to her body go. The violet haze beside
the hood is flat too, so it is not her; it keeps an alpha by its brightness and becomes soft
light over the glows. Her solid part is pulled in by ERODE, so the same soft alpha draws her
outer edge. Where she is partly transparent, the colour is what it would be without the field
behind it, so no dark fringe shows against the glows. Her top fades in over TOP_FADE rows
(the hood's tip touches the image's top) and her bottom out over BOTTOM_FADE rows, as the
cloak ran into the page there in a line of its own.

Desktop keeps the opaque original, as the field fills the hero there; CSS fades only its
bottom and, on a screen wider than 1920px, its sides. Her size and place are the same at every
width, so the phone screenshot still covers her face. The light theme shows
banner-bg-light.webp at every width, so this file needs no light counterpart.

    python tools/make-guardian-cutout.py            # writes the cutout
    python tools/make-guardian-cutout.py --check    # reports a cutout that differs from a fresh run

Never edit the output by hand; change this script and rerun it. When banner-guardian.webp
changes, rerun it too. Needs Pillow and NumPy. Run from the repo root.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "images" / "home" / "banner-guardian.webp"
OUT = ROOT / "assets" / "images" / "home" / "banner-guardian-cutout.webp"

FIELD = np.array([0.5, 0.0, 14.5])  # the backdrop's colour: (1, 0, 16) on the left, (0, 0, 13) on the right
DARK = 30.0         # a pixel farther than this from FIELD is never backdrop
FLAT = 2.5          # the most a 5x5 window may vary and still count as flat...
FLAT_REL = 0.8      # ...or this share of its distance from FIELD, for the brighter haze's compression steps
SEAL = 9            # gaps in her outline narrower than this are closed before the field grows in
ERODE = 11          # her solid part is pulled in by half this, so the soft alpha draws her edge
SOFT = (6.0, 60.0)  # outside her, alpha rises from 0 to 1 over this distance from FIELD
SMOOTH = 3.0        # where she is faint, the colour is blurred by this much: no one can see its detail
TOP_FADE = 50       # rows
BOTTOM_FADE = 170   # rows
FACE = (slice(440, 460), slice(950, 970))  # a patch of her face: her body is what joins it
QUALITY, ALPHA_QUALITY = 80, 80


def _gray(values: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(values, 0, 255).astype(np.uint8))


def _runs(reached: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Within each horizontal run of mask pixels, one reached pixel reaches the whole run."""
    h, w = mask.shape
    m = np.zeros((h, w + 1), bool)
    m[:, :w] = mask
    r = np.zeros((h, w + 1), bool)
    r[:, :w] = reached & mask
    m, r = m.ravel(), r.ravel()
    run = np.cumsum(m & ~np.r_[False, m[:-1]]) * m
    hit = np.bincount(run[r], minlength=run.max() + 1) > 0
    hit[0] = False
    return hit[run].reshape(h, w + 1)[:, :w]


def _grow(seed: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Every mask pixel joined to the seed through mask pixels (4-connected)."""
    cur = seed & mask
    while True:
        nxt = _runs(_runs(cur, mask).T, mask.T).T
        if (nxt == cur).all():
            return cur
        cur = nxt


def cutout() -> Image.Image:
    src = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64)
    h, w, _ = src.shape
    dist = np.sqrt(((src - FIELD) ** 2).sum(2))

    # Flat: how much the distance varies over a 5x5 window, in quarter steps.
    quarter = _gray(dist * 4)
    spread = (np.asarray(quarter.filter(ImageFilter.MaxFilter(5))).astype(np.float64)
              - np.asarray(quarter.filter(ImageFilter.MinFilter(5)))) / 4
    field_like = (dist <= DARK) & (spread <= np.maximum(FLAT, FLAT_REL * dist))

    # Grow the field in from the top, left and right edges, through gaps wider than SEAL;
    # the cloak runs off the bottom edge, so that edge seeds nothing.
    sealed = np.asarray(_gray(field_like * 255.0).filter(ImageFilter.MinFilter(SEAL))) > 0
    seed = np.zeros((h, w), bool)
    seed[0, :] = seed[:, 0] = seed[:, -1] = True
    field = _grow(seed, sealed)
    near = np.asarray(_gray(field * 255.0).filter(ImageFilter.MaxFilter(SEAL))) > 0
    field |= near & field_like

    # She is what is left and joined to her face.
    face = np.zeros((h, w), bool)
    face[FACE] = True
    body = _grow(face, ~field)

    solid = _gray(body * 255.0).filter(ImageFilter.MinFilter(ERODE)).filter(ImageFilter.GaussianBlur(1.5))
    soft = np.clip((dist - SOFT[0]) / (SOFT[1] - SOFT[0]), 0, 1)
    soft = np.asarray(_gray(soft * 255).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float64) / 255
    alpha = np.maximum(np.asarray(solid).astype(np.float64) / 255, soft)

    # Her colour without the field behind it.
    colour = np.clip(FIELD + (src - FIELD) / np.maximum(alpha, 1 / 255)[..., None], 0, 255)
    blurred = np.dstack([np.asarray(_gray(colour[..., c]).filter(ImageFilter.GaussianBlur(SMOOTH)))
                         for c in range(3)]).astype(np.float64)
    faint = np.clip((0.6 - alpha) / 0.4, 0, 1)[..., None]
    colour = colour * (1 - faint) + blurred * faint

    rows = np.arange(h, dtype=np.float64)[:, None]
    top = np.clip(rows / TOP_FADE, 0, 1)
    bottom = np.clip((h - 1 - rows) / BOTTOM_FADE, 0, 1)
    alpha = alpha * top * top * (3 - 2 * top) * bottom * bottom * (3 - 2 * bottom)
    alpha = np.round(alpha * 255)
    alpha[alpha < 2] = 0

    return Image.fromarray(np.dstack([colour, alpha]).round().astype(np.uint8), "RGBA")


def encode(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, "WEBP", quality=QUALITY, alpha_quality=ALPHA_QUALITY, method=6, exact=False)
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report a stale cutout, write nothing")
    args = parser.parse_args()

    data = encode(cutout())
    rel = OUT.relative_to(ROOT).as_posix()
    if args.check:
        if not OUT.exists():
            print(f"missing: {rel}")
            return 1
        if OUT.read_bytes() != data:
            print(f"stale: {rel} (rerun python tools/make-guardian-cutout.py)")
            return 1
        print(f"ok: {rel}")
        return 0
    OUT.write_bytes(data)
    print(f"wrote {rel} ({len(data):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
