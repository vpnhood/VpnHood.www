#!/usr/bin/env python3
"""Make the authorized-reseller page's hero art from its transparent originals.

tools/reseller/authorized-guardian.png and authorized-guardian-light.png are the guardian handing a key ring to a
reseller, on a transparent background (2048x2048): in her indigo robe for the dark theme, and for the light one
a snow version drawn as a picture of its own (both in white robes, fluffy white gloves, the merchant's lower
face showing like hers), like the home page's light guardian, never recoloured. They come
from VpnHood.Artworks site/authorized-reseller/set-seal.py, which sets the logo's hood into the seal. This
script writes assets/images/reseller/authorized-guardian.webp and authorized-guardian-light.webp, which the page
(_includes/authorized-reseller.html) and its preview in a browser window (authorized-reseller-preview.html) show,
the light one through data-vh-light-src:

- at 1640x1640: the hero shows them up to 820 CSS px wide, as a faded layer behind its words, so a sharp
  screen gets every pixel. Quality stays high: at 72 the skin, hair and leather broke into blocks (owner,
  2026-11-27: "the quality of image is degraded too much ... the details are rectangular");
- opaque wherever the original reaches OPAQUE: its figures stop at 254 of 255;
- faded out at the edges, each picture by its own FADES (fractions of the width or height, from each side):
  - the dark one only where the cloaks and the hood run off the picture and would end in straight lines; the
    page fades it as a whole and masks its edges in CSS (_sass/pages/_custom.scss, .vh-reseller-hero-art);
  - the light one over long, slow fades, full strength around the faces and the keys and dissolving into the
    page's white towards every side (owner, 2026-11-27: "slowly with gradient go to the completely white", not
    the whole picture faded with a narrow edge). Baked in, as a CSS mask follows the box and not the figures,
    so the light theme shows it with no opacity and no mask.

    python tools/make-reseller-guardian.py            # writes both pictures
    python tools/make-reseller-guardian.py --check    # reports a picture that differs from a fresh run

Never edit the output by hand; change this script or the originals and rerun it. Needs Pillow and NumPy. Run
from the repo root.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "reseller"
OUT = ROOT / "assets" / "images" / "reseller"

# How far each fade reaches in from its side, as a fraction of the picture.
DARK_FADES = {"left": 0.07, "right": 0.07, "top": 0.0, "bottom": 0.15}
# The faces sit at about 20% (his) and 65% (hers) across, 35-40% down; the keys at 45% across, 70% down.
LIGHT_FADES = {"left": 0.34, "right": 0.38, "top": 0.26, "bottom": 0.5}
JOBS = {
    SRC / "authorized-guardian.png": (OUT / "authorized-guardian.webp", DARK_FADES),
    SRC / "authorized-guardian-light.png": (OUT / "authorized-guardian-light.webp", LIGHT_FADES),
}

SIZE = (1640, 1640)
OPAQUE = 250        # the originals' alpha from here up is a figure
QUALITY, ALPHA_QUALITY = 88, 90


def _ease(t: np.ndarray) -> np.ndarray:
    # smootherstep: starts and ends flat, so a long fade shows no edge where it begins or ends
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (6 * t - 15) + 10)


def picture(src: Path, fades: dict[str, float]) -> Image.Image:
    # Resized with premultiplied alpha, so no colour bleeds in from the transparent pixels.
    image = Image.open(src).convert("RGBa").resize(SIZE, Image.LANCZOS).convert("RGBA")
    rgba = np.asarray(image).astype(np.float64)
    w, h = SIZE
    y = np.arange(h, dtype=np.float64)[:, None] / (h - 1)
    x = np.arange(w, dtype=np.float64)[None, :] / (w - 1)
    alpha = np.clip(rgba[..., 3] / OPAQUE, 0, 1)
    for distance, reach in ((x, fades["left"]), (1 - x, fades["right"]), (y, fades["top"]), (1 - y, fades["bottom"])):
        if reach:
            alpha = alpha * _ease(distance / reach)
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
    parser.add_argument("--check", action="store_true", help="report a stale picture, write nothing")
    args = parser.parse_args()

    stale = 0
    for src, (out, fades) in JOBS.items():
        data = encode(picture(src, fades))
        rel = out.relative_to(ROOT).as_posix()
        if args.check:
            if not out.exists():
                print(f"missing: {rel}")
                stale += 1
            elif out.read_bytes() != data:
                print(f"stale: {rel} (rerun python tools/make-reseller-guardian.py)")
                stale += 1
            else:
                print(f"ok: {rel}")
            continue
        out.write_bytes(data)
        print(f"wrote {rel} ({len(data):,} bytes)")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
