"""Regenerate assets/images/vpnhood-client/client-app-phones.webp when the app UI
changes: composes two CLIENT store screenshots (../VpnHood/fastlane) into the
double-phone marketing mockup, in the style of vpnhood-connect-app-phone.webp.
Run from the repo root: python tools/make-client-phones.py  (needs Pillow + NumPy).
App-UI art renders identically in both themes - never add it to make-light-art.

Compose two CLIENT store screenshots into a marketing double-phone mockup
in the style of vpnhood-connect-app-phone.webp (transparent background)."""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, os

SRC = "../VpnHood/fastlane/metadata/android/en-US/images/phoneScreenshots/"
OUT = "assets/images/vpnhood-client/client-app-phones.webp"
S = 2  # supersample factor for crisp edges after downscale


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
    shot = Image.open(SRC + shot_name).convert("RGB")
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


def tilt(img, taper, side):
    """Mild perspective: shrink one vertical edge by taper*h (side=+1 right, -1 left)."""
    w, h = img.size
    src = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    t = taper * h
    if side > 0:
        dst = [(0, 0), (w - 1, t), (w - 1, h - 1 - t), (0, h - 1)]
    else:
        dst = [(0, t), (w - 1, 0), (w - 1, h - 1), (0, h - 1 - t)]
    return img.transform((w, h), Image.PERSPECTIVE, find_coeffs(dst, src), Image.BICUBIC)


def shadow_of(img, blur, opacity):
    sil = Image.new("RGBA", img.size, (0, 0, 0, 0))
    black = Image.new("RGBA", img.size, (8, 8, 24, opacity))
    sil.paste(black, (0, 0), img.split()[3])
    return sil.filter(ImageFilter.GaussianBlur(blur))


# build the two phones
a = make_phone("1_en-US.png", 330)             # connected home screen
b = make_phone("2_en-US.png", 330)             # servers screen (public/private profiles)
a = tilt(a, 0.020, +1).rotate(8, Image.BICUBIC, expand=True)
b = tilt(b, 0.020, -1).rotate(-8, Image.BICUBIC, expand=True)

W, H = a.size[0] + b.size[0] - int(150 * S), max(a.size[1], b.size[1]) + 90 * S
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ax, ay = 0, 0
bx, by = a.size[0] - int(150 * S), 90 * S
for img, (x, y) in [(a, (ax, ay)), (b, (bx, by))]:
    canvas.alpha_composite(shadow_of(img, 22 * S, 110), (x + 10 * S, y + 22 * S))
canvas.alpha_composite(a, (ax, ay))
canvas.alpha_composite(b, (bx, by))

# trim and downscale
bbox = canvas.getbbox()
canvas = canvas.crop(bbox)
final_w = 968
final = canvas.resize((final_w, round(canvas.height * final_w / canvas.width)), Image.LANCZOS)
final.save(OUT, "WEBP", quality=86, method=6)
print("saved", final.size, f"{os.path.getsize(OUT)//1024} KB")
