#!/usr/bin/env python3
"""Make the home hero's guardian from her transparent original.

tools/guardian/banner-guardian.png is the hooded girl on a transparent background, as drawn
(1768x889). This script writes assets/images/home/banner-guardian.webp, which
_sass/pages/_home.scss shows behind the hero at every width, so the stars and the two glows
run on around her instead of ending at the edge of a black box:

- at 1920x965, the size the hero's CSS places her at, so the phone screenshot covers her
  face as before;
- opaque wherever the original reaches OPAQUE: its body stops at 250-254 of 255, which let
  the stars show faintly through her;
- with her top faded in over TOP_FADE rows, as the hood's tip touches the picture's top, and
  her bottom faded out over BOTTOM_FADE rows, as the cloak runs off the picture's bottom and
  would end in a straight line. Up to 991px she sits halfway down the hero, so both edges
  show there, and CSS cannot fade them: a mask follows the hero's box, not her picture.

The light theme shows banner-bg-light.webp at every width, so she needs no light counterpart.

    python tools/make-guardian.py            # writes the hero image
    python tools/make-guardian.py --check    # reports an image that differs from a fresh run

Never edit the output by hand; change this script or the original and rerun it. Needs Pillow
and NumPy. Run from the repo root.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "guardian" / "banner-guardian.png"
OUT = ROOT / "assets" / "images" / "home" / "banner-guardian.webp"

SIZE = (1920, 965)
OPAQUE = 250        # the original's alpha from here up is her body
TOP_FADE = 50       # rows
BOTTOM_FADE = 170   # rows
QUALITY, ALPHA_QUALITY = 80, 80


def _smoothstep(t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def guardian() -> Image.Image:
    # Resized with premultiplied alpha, so no colour bleeds in from the transparent pixels.
    image = Image.open(SRC).convert("RGBa").resize(SIZE, Image.LANCZOS).convert("RGBA")
    rgba = np.asarray(image).astype(np.float64)
    h = SIZE[1]
    rows = np.arange(h, dtype=np.float64)[:, None]
    alpha = np.clip(rgba[..., 3] / OPAQUE, 0, 1)
    alpha *= _smoothstep(rows / TOP_FADE) * _smoothstep((h - 1 - rows) / BOTTOM_FADE)
    alpha = np.round(alpha * 255)
    alpha[alpha < 2] = 0
    rgba[..., 3] = alpha
    return Image.fromarray(rgba.round().astype(np.uint8), "RGBA")


def encode(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, "WEBP", quality=QUALITY, alpha_quality=ALPHA_QUALITY, method=6, exact=False)
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report a stale image, write nothing")
    args = parser.parse_args()

    data = encode(guardian())
    rel = OUT.relative_to(ROOT).as_posix()
    if args.check:
        if not OUT.exists():
            print(f"missing: {rel}")
            return 1
        if OUT.read_bytes() != data:
            print(f"stale: {rel} (rerun python tools/make-guardian.py)")
            return 1
        print(f"ok: {rel}")
        return 0
    OUT.write_bytes(data)
    print(f"wrote {rel} ({len(data):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
