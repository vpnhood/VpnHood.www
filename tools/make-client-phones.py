"""Regenerate assets/images/vpnhood-client/client-app-phones.webp: composes two
CLIENT store screenshots into the double-phone marketing mockup, in the style of
vpnhood-connect-app-phone.webp.
Run from the repo root: python tools/make-client-phones.py  (needs Pillow, NumPy,
and the VpnHood repo beside this one).
App-UI art renders identically in both themes - never add it to make-light-art.

Both phones are built at the SAME size: depth comes from the z-order (right
phone in front), the lower placement, and a symmetric vertical keystone (top
edge slightly narrower, as if the phones lean away at the top). Never scale one
phone down or taper a single side edge - a smaller-but-in-front phone reads as
squashed, and a one-sided taper reads as a widened bottom.

Each shadow is blurred with room on every side, so it fades out inside the
picture: blurred inside its phone's own box, it stopped at that box's edges,
which a light page showed as a pale box around each phone (owner, 2026-11-11).
The picture is as wide as the phones plus SIDE, so they fill the page's column
as before; at the left and right the shadow fades out instead."""
from PIL import Image, ImageDraw, ImageFilter
import io, numpy as np, os, subprocess

# The store screenshots left the VpnHood repo's fastlane folder on 2026-08-01
# (0ca50653a), so the two the picture shows come from the last commit with them.
SRC_REPO, SRC_REV = "../VpnHood", "ce5eb8cec1371ae7b9c428a7d99bb0d9c3659975"
SRC = "fastlane/metadata/android/en-US/images/phoneScreenshots/"
OUT = "assets/images/vpnhood-client/client-app-phones.webp"
S = 2  # supersample factor for crisp edges after downscale


def screenshot(name):
    data = subprocess.run(["git", "-C", SRC_REPO, "show", f"{SRC_REV}:{SRC}{name}"],
                          capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data)).convert("RGB")


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=float)
    B = np.array(pb, dtype=float).reshape(8)
    res = np.linalg.lstsq(A, B, rcond=None)[0]
    return res.tolist()


def make_phone(shot_name, screen_w):
    screen_w *= S
    shot = screenshot(shot_name)
    screen_h = round(shot.height * screen_w / shot.width)
    shot = shot.resize((screen_w, screen_h), Image.LANCZOS)
    frame, bezel = 5 * S, 14 * S
    pw = screen_w + 2 * (frame + bezel)
    ph = screen_h + 2 * (frame + bezel)
    margin = 6 * S  # room for side buttons
    canvas = Image.new("RGBA", (pw + 2 * margin, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    # side buttons (drawn first, sticking out of the frame)
    bx = margin + pw
    d.rounded_rectangle([margin - 4 * S, ph * 0.24, margin + 2 * S, ph * 0.24 + 46 * S], radius=3 * S, fill=(120, 132, 156, 255))
    d.rounded_rectangle([margin - 4 * S, ph * 0.24 + 60 * S, margin + 2 * S, ph * 0.24 + 106 * S], radius=3 * S, fill=(120, 132, 156, 255))
    d.rounded_rectangle([bx - 2 * S, ph * 0.30, bx + 4 * S, ph * 0.30 + 90 * S], radius=3 * S, fill=(120, 132, 156, 255))
    # metallic outer frame
    d.rounded_rectangle([margin, 0, margin + pw - 1, ph - 1], radius=62 * S, fill=(171, 181, 201, 255))
    # inner bezel
    d.rounded_rectangle([margin + frame, frame, margin + pw - 1 - frame, ph - 1 - frame], radius=57 * S, fill=(10, 13, 38, 255))
    # screen
    canvas.paste(shot, (margin + frame + bezel, frame + bezel), rounded_mask(shot.size, 40 * S))
    return canvas


def keystone(img, k):
    """Symmetric vertical perspective: top edge narrower by k*w per corner, as
    if the phone leans away at the top. Same transform for both phones, so
    neither silhouette reads wider than the other."""
    w, h = img.size
    src = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    t = k * w
    dst = [(t, 0), (w - 1 - t, 0), (w - 1, h - 1), (0, h - 1)]
    return img.transform((w, h), Image.PERSPECTIVE, find_coeffs(dst, src), Image.BICUBIC)


def shadow_of(img, blur, opacity, pad):
    """the silhouette, blurred with pad of room on every side"""
    sil = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (8, 8, 24, 0))
    sil.paste(Image.new("RGBA", img.size, (8, 8, 24, opacity)), (pad, pad), img.split()[3])
    return sil.filter(ImageFilter.GaussianBlur(blur))


# build the two phones - identical geometry, mirrored rotation
a = make_phone("1_en-US.png", 330)             # connected home screen (back left)
b = make_phone("2_en-US.png", 330)             # servers screen (front right)
a = keystone(a, 0.030).rotate(8, Image.BICUBIC, expand=True)
b = keystone(b, 0.030).rotate(-8, Image.BICUBIC, expand=True)

OVERLAP, DROP = int(175 * S), 110 * S
BLUR, OFFSET, OPACITY = 22 * S, (10 * S, 22 * S), 110
PAD = 3 * BLUR + 4 * S  # Pillow's Gaussian is three box blurs, which end at 3 x BLUR
SIDE, FADE = 18 * S, 40 * S
W = a.size[0] + b.size[0] - OVERLAP + 2 * PAD
H = max(a.size[1], b.size[1]) + DROP + 2 * PAD
places = [(a, (PAD, PAD)), (b, (PAD + a.size[0] - OVERLAP, PAD + DROP))]
shade = Image.new("RGBA", (W, H), (8, 8, 24, 0))
phones = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for img, (x, y) in places:
    shade.alpha_composite(shadow_of(img, BLUR, OPACITY, PAD), (x + OFFSET[0] - PAD, y + OFFSET[1] - PAD))
    phones.alpha_composite(img, (x, y))

# the phones' width plus SIDE, the shadow faded out towards those sides, and its whole height
left, _, right, _ = phones.getbbox()
left, right = left - SIDE, right + SIDE
xs = np.arange(W)
ramp = np.clip(np.minimum(xs - left, right - xs) / FADE, 0, 1)
ramp = ramp * ramp * (3 - 2 * ramp)
alpha = np.asarray(shade.getchannel("A"), dtype=float) * ramp[None, :]
shade.putalpha(Image.fromarray(np.round(alpha).astype(np.uint8)))
shade.alpha_composite(phones)
_, top, _, bottom = shade.getbbox()
canvas = shade.crop((left, top, right, bottom))

# downscale
final_w = 968
final = canvas.resize((final_w, round(canvas.height * final_w / canvas.width)), Image.LANCZOS)
final.save(OUT, "WEBP", quality=86, method=6)
print("saved", final.size, f"{os.path.getsize(OUT)//1024} KB")
