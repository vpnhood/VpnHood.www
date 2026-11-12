#!/usr/bin/env python3
"""Draw the hero art of the docs pages: one small picture beside each page's title.

Writes `assets/images/<product>/docs/hero-<name>.svg`, for the docs of VpnHood! SERVER and
VpnHood! MANAGER, `vpnhood-manager/docs/promo-manager.svg`, the art of the MANAGER promo on the
server pages, `vpnhood-manager/docs/trouble-<id>.svg`, the troubleshooting page's problems, and
`vpnhood-client/docs/first-key-<id>.svg`, the ways to get a key on CLIENT's first-key page.
THOSE FILES ARE GENERATED - edit this script and re-run, never the SVGs.

The art speaks the language of the guides' heroes (`assets/images/guides/*.svg`): a deep
indigo object with a violet-to-mint rim, soft glows and lilac detail, on transparency. That
is what lets it skip the light-art pipeline (`tools/make-light-art.py`): a dark object on a
light page reads as an object, as the guides' gauge does, so both themes show the same file.
Two exceptions have light variants: MANAGER's figure, whose eyes are mint on the dark theme and
white on the light one, and the install pictures, whose large marks are not dark objects: their
mint fades into a light card, and their glow and haze turn to smudges there.

The rules come from what a docs page is for:

  * **Decorative.** The art repeats what the title says, so the page shows it with
    `alt=""` (`_includes/docs-hero.html`) and it holds no text: nothing to translate, and
    nothing that reads differently in Persian or Arabic.
  * **Drawn for 200px.** It is shown about 12rem wide, beside the title, from a tablet
    up; on a phone it steps aside so the steps start where they always did. Strokes are
    heavy and details few, so it still reads at a fifth of its size.
  * **One idea each**, named in the function's docstring below.

Run from the repo root:  python tools/make-docs-heroes.py
"""
from __future__ import annotations

import math
import pathlib
import re

IMAGES = pathlib.Path(__file__).resolve().parent.parent / "assets" / "images"

# The guides' palette, unchanged.
VIOLET_DEEP = "#5b2fd6"
VIOLET = "#8257f5"
TEAL = "#3ce8c8"
MINT = "#8ef7e2"
LILAC = "#c0a4ff"
INDIGO = "#2b1470"
INDIGO_DEEP = "#150a3a"
AMBIENT = "#8b5cf6"
CYAN = "#22b6d6"

# The eyes of MANAGER's figure: the palette's mint and teal, a digit off, so that
# tools/make-light-art.py can name them alone and leave the mint of the rim and the bars.
MANAGER_EYE = "#8ef7e3"
MANAGER_EYE_GLOW = "#3ce8c9"

# The install pictures' marks, the glow around them and the haze behind them: the palette a digit
# off for the same reason, so the light variant changes them and leaves the server under them.
MARK_STOPS = ("#5b2fd7", "#8257f4", "#3ce8c7", "#8ef7e1")
MARK_GLOW = "#3ce8c6"
MARK_HAZE = "#8b5cf7"

# VpnHood! MANAGER's figure, the hood of its icon, on a 512 grid: the hood, its face and its eyes.
MANAGER_HOOD = "M254.1 18.63c-81.4 0-231.43 155.97-171.63 300.77 8 25.3 27.83 50.4 49.13 77.1 24.4 30.6 51.6 63.2 68.7 96.9h20.5c-18.1-39.8-48.5-75.9-74.6-108.6-27.4-34.3-48.73-65.2-48.73-87.9.1-9.1 2.23-18.1 5.53-26.3 23-61.4 114-119.7 148.5-135l3.6-2 3.9 1.3c60.9 20.9 129.3 66.7 154 135.7 4.1 11.7 5.9 18 5.6 27.3-.5 15.8-24.5 54.7-55 88.7-29.1 32.4-62.4 67.7-80 106.7h20.5c16.8-32.2 46.2-64 73.3-94.2 23.2-25.6 45.3-50 54.9-74.8 52.9-124-99.2-305.67-178.2-305.67z"
MANAGER_FACE = "M254.9 154.1c-38.7 21.5-85.1 52.2-113.7 88.2 9.7 83 59 146.1 118.3 146.1 59.2 0 108.3-62.7 118.2-145.3-28.9-42.1-78-72.9-122.8-89z"
MANAGER_EYES = ("M196.6 237.1h2.4c13.1.1 26.1 2.7 39.1 7.4-16.8 40.6-59 42-78.1 0 12.2-4.8 24.4-7.2 36.6-7.4z",
                "M321.5 237.1c13-.1 26 2.3 39.1 7.4-19.2 42-61.3 40.6-78.2 0 13.1-4.7 26.1-7.3 39.1-7.4z")


class Art:
    """One SVG: the shared gradients and filters under a per-file prefix, then the parts."""

    def __init__(self, uid: str):
        self.p = uid
        self.parts: list[str] = []

    def id(self, name: str) -> str:
        return f"{self.p}{name}"

    def url(self, name: str) -> str:
        return f"url(#{self.id(name)})"

    def defs(self) -> str:
        i = self.id
        return f"""<defs>
  <linearGradient id="{i('Rim')}" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0" stop-color="{VIOLET_DEEP}"/><stop offset=".45" stop-color="{VIOLET}"/>
    <stop offset=".78" stop-color="{TEAL}"/><stop offset="1" stop-color="{MINT}"/></linearGradient>
  <linearGradient id="{i('Body')}" x1=".15" y1="0" x2=".85" y2="1">
    <stop offset="0" stop-color="{INDIGO}" stop-opacity=".95"/>
    <stop offset="1" stop-color="{INDIGO_DEEP}" stop-opacity=".95"/></linearGradient>
  <linearGradient id="{i('Lane')}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity=".08"/>
    <stop offset=".5" stop-color="{VIOLET}" stop-opacity=".55"/>
    <stop offset="1" stop-color="{TEAL}" stop-opacity=".08"/></linearGradient>
  <radialGradient id="{i('Ambient')}" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{AMBIENT}" stop-opacity=".3"/>
    <stop offset="1" stop-color="{AMBIENT}" stop-opacity="0"/></radialGradient>
  <radialGradient id="{i('Glow')}" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{MINT}" stop-opacity=".95"/>
    <stop offset=".45" stop-color="{TEAL}" stop-opacity=".6"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <filter id="{i('Soft')}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
  <filter id="{i('Softer')}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="52"/></filter>
</defs>"""

    def add(self, *parts: str) -> None:
        self.parts.extend(parts)

    # --- primitives ---------------------------------------------------------------------

    def ambient(self, cx=500, cy=480, rx=440, ry=410, opacity=1.0) -> None:
        self.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{self.url("Ambient")}" opacity="{opacity}"/>')

    def solid(self, shape: str, rim: bool = True, width: int = 10) -> None:
        """A shape's body; with rim=True, its edge in the violet-to-mint gradient, glowing."""
        self.add(shape.format(fill=f'fill="{self.url("Body")}"', stroke=f'stroke="{VIOLET}" stroke-opacity=".35" stroke-width="2"'))
        if rim:
            self.add(shape.format(fill='fill="none"', stroke=f'stroke="{self.url("Rim")}" stroke-width="{width + 12}" filter="{self.url("Soft")}" opacity=".5"'))
            self.add(shape.format(fill='fill="none"', stroke=f'stroke="{self.url("Rim")}" stroke-width="{width}" stroke-linejoin="round"'))

    def led(self, cx, cy, r=13, on=True) -> None:
        if on:
            self.add(f'<circle cx="{cx}" cy="{cy}" r="{r * 3.2:.0f}" fill="{self.url("Glow")}" filter="{self.url("Soft")}" opacity=".7"/>',
                     f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{MINT}"/>')
        else:
            self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LILAC}" opacity=".45"/>')

    def bar(self, x, y, w, h=20, fill=LILAC, opacity=1.0, glow=False) -> None:
        if glow:
            self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2:g}" fill="{TEAL}" filter="{self.url("Soft")}" opacity=".7"/>')
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2:g}" fill="{fill}" opacity="{opacity}"/>')

    def lane(self, x, y, w, h=86) -> None:
        """The guides' tunnel: a dark rounded lane with a violet-to-mint wash."""
        r = h / 2
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r:g}" fill="{INDIGO_DEEP}" fill-opacity=".85" stroke="{VIOLET}" stroke-opacity=".3" stroke-width="2"/>',
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r:g}" fill="{self.url("Lane")}"/>')

    def address(self, x, y, w, lit: bool) -> None:
        """An IP address with no digits: four groups in a lane, lit when it is in the keys."""
        h = 86
        self.lane(x, y, w, h)
        gw, gap = (w - 120) / 4 - 10, 10
        cx = x + 60
        for n in range(4):
            if lit:
                self.bar(cx, y + 33, gw, 20, fill=MINT, opacity=.85 + .05 * n, glow=(n == 3))
            else:
                self.bar(cx, y + 33, gw, 20, fill=LILAC, opacity=.32)
            if n < 3:
                self.add(f'<circle cx="{cx + gw + gap:.0f}" cy="{y + 43}" r="6" fill="{MINT if lit else LILAC}" opacity="{.8 if lit else .3}"/>')
            cx += gw + 2 * gap

    def server_unit(self, x, y, w, h, rim=False, lit=True) -> None:
        self.solid(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h * .28:.0f}" {{fill}} {{stroke}}/>', rim=rim, width=8)
        cy = y + h / 2
        self.led(x + h * .5, cy, r=h * .11, on=lit)
        self.led(x + h * .5 + h * .42, cy, r=h * .11, on=False)
        for n in range(3):
            self.bar(x + w * .62, cy - 22 + n * 18, 70, 10, fill=LILAC, opacity=.35)

    def manager_hood(self, cx, cy, size, rim=9) -> None:
        """MANAGER's figure: the hood in the art's body and rim, its face in deep indigo, its eyes lit."""
        s = size / 512
        at = f'transform="translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.4f})"'
        self.solid(f'<path {at} d="{MANAGER_HOOD}" {{fill}} {{stroke}}/>', width=round(rim / s, 1))
        self.add(f'<path {at} d="{MANAGER_FACE}" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".5" stroke-width="{3 / s:.1f}"/>')
        for eye in MANAGER_EYES:
            self.add(f'<path {at} d="{eye}" fill="{MANAGER_EYE_GLOW}" filter="{self.url("Soft")}" opacity=".85"/>',
                     f'<path {at} d="{eye}" fill="{MANAGER_EYE}"/>')

    def render(self, name: str, product: str = "vpnhood-server", prefix: str = "hero") -> None:
        body = "\n".join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">\n'
               f'<!-- Generated by tools/make-docs-heroes.py - edit the script, not this file. -->\n'
               f'{self.defs()}\n{body}\n</svg>\n')
        out = IMAGES / product / "docs"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{prefix}-{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote {product}/docs/{prefix}-{name}.svg ({len(svg.encode())} bytes)")


# --- one function per page ------------------------------------------------------------------

def docs() -> None:
    """The docs index: a stack of servers, and a page of instructions in front of it."""
    a = Art("dhDocs")
    a.ambient()
    for n, y in enumerate((230, 380, 530)):
        a.server_unit(170, y, 470, 120, rim=(n == 0), lit=(n == 0))
    # the page, folded at its top corner
    a.solid('<path d="M 560 470 H 790 L 850 530 V 820 Q 850 850 820 850 H 590 Q 560 850 560 820 Z" {fill} {stroke}/>', width=9)
    a.add(f'<path d="M 790 470 V 530 H 850" fill="none" stroke="{a.url("Rim")}" stroke-width="9" stroke-linejoin="round"/>')
    a.bar(610, 570, 150, 22, fill=MINT, opacity=.9, glow=True)
    for n, w in enumerate((190, 160, 190, 120)):
        a.bar(610, 630 + n * 50, w, 16, fill=LILAC, opacity=.42)
    a.ambient(cy=860, rx=330, ry=70, opacity=.5)
    a.render("docs")


def requirements() -> None:
    """System requirements: a server, and in front of it the checklist it passes, every box ticked."""
    a = Art("dhReq")
    a.ambient(cy=470)
    # the server, behind and to the left: the machine the list is about
    a.server_unit(110, 190, 480, 120, rim=False, lit=True)
    a.server_unit(110, 340, 480, 120, rim=False, lit=False)
    # the checklist, in front: three ticked boxes, each with its line
    a.solid('<rect x="370" y="290" width="480" height="540" rx="40" {fill} {stroke}/>', width=10)
    for n in range(3):
        y = 360 + n * 150
        a.add(f'<rect x="420" y="{y}" width="92" height="92" rx="22" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="6"/>')
        tick = f"M 440 {y + 48} L 461 {y + 69} L 494 {y + 26}"
        a.add(f'<path d="{tick}" fill="none" stroke="{TEAL}" stroke-width="32" stroke-linecap="round" stroke-linejoin="round" filter="{a.url("Soft")}" opacity=".55"/>',
              f'<path d="{tick}" fill="none" stroke="{MINT}" stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>')
        a.bar(550, y + 24, 230 - n * 40, 20, fill=LILAC, opacity=.45)
        a.bar(550, y + 58, 150 - n * 20, 14, fill=LILAC, opacity=.25)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("requirements")


def install() -> None:
    """Install: a terminal running the one install command, and the progress it makes."""
    a = Art("dhInstall")
    a.ambient(cy=440)
    a.solid('<rect x="170" y="190" width="660" height="470" rx="44" {fill} {stroke}/>')
    a.add(f'<path d="M 170 288 H 830" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{232 + n * 44}" cy="239" r="13" fill="{LILAC}" opacity=".45"/>')
    # the prompt and a blinking cursor
    a.add(f'<path d="M 250 375 L 318 420 L 250 465" fill="none" stroke="{a.url("Rim")}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<path d="M 250 375 L 318 420 L 250 465" fill="none" stroke="{a.url("Rim")}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>')
    a.bar(362, 440, 118, 26, fill=MINT, glow=True)
    a.bar(250, 530, 400, 20, opacity=.35)
    a.bar(250, 580, 280, 20, opacity=.25)
    # progress, three quarters done
    a.lane(170, 750, 660)
    for n, (x, w) in enumerate(((228, 70), (318, 86), (424, 102))):
        a.bar(x, 783, w, 20, fill=LILAC, opacity=.45 + .15 * n)
    a.bar(546, 783, 120, 20, fill=MINT, opacity=.95, glow=True)
    a.ambient(cy=800, rx=330, ry=70, opacity=.5)
    a.render("install")


def brand_path(name: str) -> str:
    """A system's mark, from the same Simple Icons file the requirements pages show, on a 24 grid."""
    icon = (IMAGES.parent.parent / "_includes" / "icons" / "brands" / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', icon).group(1)


def linux_mark(a: Art, x, y, size, glow=True) -> None:
    """The Linux mark in the rim's gradient."""
    path = brand_path("linux")
    place = f'transform="translate({x} {y}) scale({size / 24:g})"'
    if glow:
        a.add(f'<path d="{path}" {place} fill="{TEAL}" opacity=".5" filter="{a.url("Soft")}"/>')
    a.add(f'<path d="{path}" {place} fill="{a.url("Rim")}"/>')


def linux() -> None:
    """The Linux apps: a terminal with the Linux mark in it, and the one install command's prompt."""
    a = Art("dhLinux")
    a.ambient(cy=470)
    a.solid('<rect x="150" y="170" width="700" height="660" rx="44" {fill} {stroke}/>')
    a.add(f'<path d="M 150 268 H 850" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{212 + n * 44}" cy="219" r="13" fill="{LILAC}" opacity=".45"/>')
    linux_mark(a, 340, 300, 320)
    # the prompt and its cursor, under the mark
    a.add(f'<path d="M 232 672 L 284 706 L 232 740" fill="none" stroke="{a.url("Rim")}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>')
    a.bar(330, 694, 320, 24, opacity=.4)
    a.bar(680, 694, 88, 24, fill=MINT, glow=True)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("linux", product="vpnhood-client")


def linux_requirements() -> None:
    """Linux requirements: the Linux mark, and in front of it the checklist it passes, every box ticked."""
    a = Art("dhLinuxReq")
    a.ambient(cy=470)
    linux_mark(a, 100, 170, 400)
    a.solid('<rect x="370" y="290" width="480" height="540" rx="40" {fill} {stroke}/>', width=10)
    for n in range(3):
        y = 360 + n * 150
        a.add(f'<rect x="420" y="{y}" width="92" height="92" rx="22" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".5" stroke-width="4"/>')
        tick = f"M 440 {y + 48} L 461 {y + 69} L 494 {y + 26}"
        a.add(f'<path d="{tick}" fill="none" stroke="{TEAL}" stroke-width="32" stroke-linecap="round" stroke-linejoin="round" opacity=".5" filter="{a.url("Soft")}"/>',
              f'<path d="{tick}" fill="none" stroke="{MINT}" stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>')
        a.bar(550, y + 24, 230 - n * 40, 20, fill=LILAC, opacity=.45)
        a.bar(550, y + 58, 150 - n * 20, 14, fill=LILAC, opacity=.25)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("linux-requirements", product="vpnhood-client")


# The end of the access key, from the top of its blade round its teeth to the bottom of the blade
KEY_END = ("H 872 Q 892 458 892 478 V 628 Q 892 640 880 640 H 842 Q 830 640 830 628 V 542 H 790 V 600 "
           "Q 790 612 778 612 H 740 Q 728 612 728 600 V 542")


def draw_key(a: Art, cx, cy, scale=1.0, angle=45, width=11) -> None:
    """The access key, drawn flat around the middle of the canvas with its bow on the left, then placed."""
    a.add(f'<g transform="translate({cx} {cy}) rotate({angle}) scale({scale:g}) translate(-500 -500)">')
    a.solid(f'<path d="M 440 458 {KEY_END} H 440 A 175 175 0 1 1 440 458 Z" {{fill}} {{stroke}}/>', width=round(width / scale, 1))
    a.add(f'<circle cx="222" cy="500" r="62" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".6" stroke-width="6"/>')
    a.led(350, 500, r=17)
    a.bar(430, 488, 300, 24, fill=MINT, glow=True)
    a.bar(760, 488, 90, 24, fill=LILAC, opacity=.4)
    a.add('</g>')


def client_diagnose() -> None:
    """Send a diagnosis report: a report with a pulse running across it."""
    a = Art("dhDiagnose")
    a.ambient(cy=470)
    a.solid('<path d="M 250 110 H 620 L 770 260 V 850 Q 770 890 730 890 H 250 Q 210 890 210 850 V 150 Q 210 110 250 110 Z" {fill} {stroke}/>', width=11)
    a.add(f'<path d="M 620 110 V 260 H 770" fill="none" stroke="{a.url("Rim")}" stroke-width="10" stroke-linejoin="round"/>')
    for y, w in ((220, 240), (290, 300), (720, 400), (790, 300)):
        a.bar(280, y, w, 20, opacity=.42)
    pulse = "M 90 520 H 330 L 400 390 L 490 640 L 570 460 L 620 520 H 890"
    a.add(f'<path d="{pulse}" fill="none" stroke="{TEAL}" stroke-width="50" stroke-linecap="round" stroke-linejoin="round" opacity=".5" filter="{a.url("Soft")}"/>',
          f'<path d="{pulse}" fill="none" stroke="{MINT}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>')
    a.ambient(cy=930, rx=300, ry=40, opacity=.45)
    a.render("diagnose", product="vpnhood-client")


def client_tv() -> None:
    """Use it on your TV: a TV showing the app connected, and in front of it the phone that sets it up."""
    a = Art("dhTv")
    a.ambient(cy=450)
    a.solid('<rect x="90" y="170" width="820" height="500" rx="36" {fill} {stroke}/>', width=11)
    a.solid('<path d="M 440 670 H 560 V 760 H 700 Q 720 760 720 780 Q 720 800 700 800 H 300 Q 280 800 280 780 Q 280 760 300 760 H 440 Z" {fill} {stroke}/>', width=10)
    a.add(f'<circle cx="330" cy="420" r="120" fill="none" stroke="{TEAL}" stroke-width="44" opacity=".5" filter="{a.url("Soft")}"/>',
          f'<circle cx="330" cy="420" r="120" fill="none" stroke="{MINT}" stroke-width="22"/>',
          f'<path d="M 275 420 L 318 465 L 392 378" fill="none" stroke="{MINT}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>')
    for y, w in ((300, 300), (380, 240)):
        a.bar(520, y, w, 26, opacity=.42)
    a.solid('<rect x="640" y="430" width="250" height="470" rx="44" {fill} {stroke}/>', width=11)
    for y, w in ((520, 150), (590, 110), (660, 150), (730, 90)):
        a.bar(690, y, w, 22, opacity=.5)
    a.add(f'<circle cx="765" cy="835" r="18" fill="{MINT}"/>')
    a.ambient(cy=930, rx=300, ry=40, opacity=.45)
    a.render("tv", product="vpnhood-client")


def first_key() -> None:
    """Get an access key: one large key, its line of text lit along the blade."""
    a = Art("dhFirstKey")
    a.ambient(cy=470)
    draw_key(a, 500, 500)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("first-key", product="vpnhood-client")


def closed_hand(a: Art) -> None:
    """A hand holding something, coming in from the left: its cuff, the back of it, four fingers and the thumb."""
    a.solid('<rect x="-40" y="420" width="250" height="300" rx="34" {fill} {stroke}/>', rim=False)
    a.bar(170, 440, 22, 260, fill=LILAC, opacity=.4)
    a.solid('<path d="M 210 450 H 400 Q 470 450 470 520 V 650 Q 470 720 400 720 H 210 Z" {fill} {stroke}/>', width=20)
    for n in range(4):
        a.solid(f'<rect x="400" y="{452 + n * 68}" width="190" height="64" rx="32" {{fill}} {{stroke}}/>', width=16)
    a.solid('<path d="M 300 455 Q 300 372 390 372 H 510 Q 560 372 560 420 Q 560 468 510 468 H 400 Q 372 468 360 500 Z" {fill} {stroke}/>', width=18)


def open_hand(a: Art) -> None:
    """An open hand from the side, palm up: its cuff, the palm running on into the fingers, and the thumb."""
    a.solid('<path d="M 62 690 L 186 660 Q 210 654 216 678 L 262 862 Q 268 886 244 892 L 120 922 Q 96 928 90 904 L 44 720 Q 38 696 62 690 Z" {fill} {stroke}/>', rim=False)
    a.solid('<path d="M 214 690 C 300 650 372 668 450 716 C 520 758 600 762 690 746 L 852 716 Q 924 704 938 752 Q 950 800 880 822 '
            'L 650 892 C 520 930 380 928 262 878 Z" {fill} {stroke}/>', width=12)
    for x1, y1, x2, y2 in ((640, 806, 850, 760), (620, 846, 800, 806)):
        a.add(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="10" stroke-linecap="round"/>')
    a.solid('<path d="M 396 700 C 440 640 500 618 548 628 Q 586 638 572 672 Q 560 700 520 712 C 496 720 474 740 462 760 Z" {fill} {stroke}/>', width=10)


def first_key_ask() -> None:
    """Ask whoever runs the server: a hand reaches down and drops a key into your open hand."""
    a = Art("fkAsk")
    a.ambient(cy=470)
    a.add('<g transform="translate(650 345) rotate(-55) scale(-.52 .52) translate(-600 -570)">')
    draw_key(a, 880, 470, scale=.86, angle=0, width=22)
    closed_hand(a)
    a.add('</g>')
    open_hand(a)
    a.ambient(cy=950, rx=330, ry=36, opacity=.45)
    a.render("ask", product="vpnhood-client", prefix="first-key")


def first_key_own() -> None:
    """Run your own server: a hammer forging the key on an anvil, the blade glowing where it lands."""
    a = Art("fkOwn")
    a.ambient(cy=510)
    a.add('<g transform="translate(0 -50)">')
    a.solid('<path d="M 84 628 Q 200 622 300 610 H 862 Q 880 610 880 628 V 690 Q 880 706 862 706 H 712 '
            'Q 642 712 622 790 Q 614 830 692 846 Q 718 852 718 876 V 906 Q 718 920 704 920 H 296 '
            'Q 282 920 282 906 V 876 Q 282 852 308 846 Q 386 830 378 790 Q 358 712 288 706 '
            'Q 168 696 84 628 Z" {fill} {stroke}/>', width=12)
    draw_key(a, 380, 484, scale=.72, angle=0)
    a.add(f'<circle cx="470" cy="454" r="125" fill="{a.url("Glow")}" opacity=".8"/>')
    # the hammer, its face on the blade and its handle up to the right
    a.add('<g transform="translate(470 432) rotate(-18)">')
    a.solid('<rect x="74" y="-128" width="440" height="56" rx="24" {fill} {stroke}/>', width=11)
    a.solid('<rect x="-80" y="-172" width="160" height="172" rx="18" {fill} {stroke}/>', width=12)
    a.add(f'<rect x="-64" y="-42" width="128" height="24" rx="8" fill="{LILAC}" opacity=".8"/>')
    a.add('</g>')
    # the strike: short streaks off the metal, either side of the face, not sparkles
    for x1, y1, x2, y2 in ((372, 446, 322, 424), (360, 398, 318, 358), (562, 438, 632, 418), (580, 396, 646, 356)):
        a.add(f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{MINT}" stroke-width="15" stroke-linecap="round"/>')
    a.add('</g>')
    a.render("own", product="vpnhood-client", prefix="first-key")


def first_key_connect() -> None:
    """Use an app with its own servers: a phone with the servers inside it, connected, and no key to add."""
    a = Art("fkConnect")
    a.ambient(cy=480)
    a.solid('<rect x="260" y="70" width="480" height="860" rx="76" {fill} {stroke}/>', width=12)
    a.bar(435, 122, 130, 18, fill=LILAC, opacity=.42)
    a.server_unit(315, 190, 370, 140, rim=True)
    a.server_unit(315, 360, 370, 140, lit=False)
    a.solid('<circle cx="500" cy="700" r="120" {fill} {stroke}/>', width=11)
    a.add(f'<path d="M 500 628 V 696" fill="none" stroke="{MINT}" stroke-width="28" stroke-linecap="round"/>',
          f'<path d="M 450 656 A 72 72 0 1 0 550 656" fill="none" stroke="{MINT}" stroke-width="28" stroke-linecap="round"/>')
    a.render("connect", product="vpnhood-client", prefix="first-key")


def install_system(name: str, uid: str) -> None:
    """One way to install: the system's mark, large, on the server it runs. The install page's cards show
    these, and each system's page shows its own again beside its title."""
    a = Art(uid)
    s = MARK_STOPS
    a.add(f'<defs><linearGradient id="{a.id("Mark")}" x1="0" y1="1" x2="1" y2="0">'
          f'<stop offset="0" stop-color="{s[0]}"/><stop offset=".45" stop-color="{s[1]}"/>'
          f'<stop offset=".78" stop-color="{s[2]}"/><stop offset="1" stop-color="{s[3]}"/></linearGradient>'
          f'<radialGradient id="{a.id("Haze")}" cx=".5" cy=".5" r=".5">'
          f'<stop offset="0" stop-color="{MARK_HAZE}" stop-opacity=".3"/>'
          f'<stop offset="1" stop-color="{MARK_HAZE}" stop-opacity="0"/></radialGradient></defs>',
          f'<ellipse cx="500" cy="410" rx="440" ry="410" fill="{a.url("Haze")}"/>')
    place = f'transform="translate(250 90) scale({500 / 24:g})"'
    path = brand_path(name)
    # the blur outside the scale, or it grows with the mark past the edge of its filter's region
    a.add(f'<g filter="{a.url("Soft")}" opacity=".5"><path d="{path}" {place} fill="{MARK_GLOW}"/></g>',
          f'<path d="{path}" {place} fill="{a.url("Mark")}"/>')
    a.server_unit(160, 650, 680, 150, rim=True, lit=True)
    a.ambient(cy=880, rx=320, ry=60, opacity=.5)
    a.render(f"install-{name}")


def ip_blocking() -> None:
    """IP blocking: the server behind a shield, with its two addresses leading out of it."""
    a = Art("dhBlock")
    a.ambient(cy=470)
    a.solid('<path d="M 440 150 L 700 236 V 450 C 700 630 590 742 440 812 C 290 742 180 630 180 450 V 236 Z" {fill} {stroke}/>', width=12)
    a.server_unit(285, 330, 310, 96, lit=True)
    a.server_unit(285, 446, 310, 96, lit=False)
    # two routes out: the connection IP (mint) and the outgoing IP (violet)
    for y, colour, glow in ((380, MINT, True), (590, LILAC, False)):
        a.add(f'<path d="M 650 {y} H 850" stroke="{colour}" stroke-width="22" stroke-linecap="round" opacity="{.95 if glow else .6}"/>')
        a.add(f'<circle cx="868" cy="{y}" r="30" fill="{INDIGO_DEEP}" stroke="{colour}" stroke-width="12" opacity="{1 if glow else .7}"/>')
        if glow:
            a.add(f'<path d="M 650 {y} H 850" stroke="{TEAL}" stroke-width="30" stroke-linecap="round" filter="{a.url("Soft")}" opacity=".6"/>')
    a.ambient(cy=860, rx=300, ry=60, opacity=.5)
    a.render("ip-blocking")


def ip_addresses() -> None:
    """IP addresses: an access key, and two addresses - one in it, one kept out."""
    a = Art("dhAddr")
    a.ambient(cy=470)
    # the key: a round bow, a shaft and two teeth, as one outline
    key = ('<path d="M 467.8 345 H 815 A 25 25 0 0 1 815 395 H 810 V 445 H 770 V 395 H 740 V 465 H 700 V 395 '
           'H 467.8 A 140 140 0 1 1 467.8 345 Z" {fill} {stroke}/>')
    a.solid(key, width=10)
    a.add(f'<circle cx="300" cy="370" r="48" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".6" stroke-width="6"/>')
    a.led(300, 370, r=16)
    # the address in the keys is lit and tied to the key; the other stays dim
    a.add(f'<path d="M 330 512 V 598" stroke="{MINT}" stroke-width="10" stroke-dasharray="2 22" stroke-linecap="round" opacity=".9"/>')
    a.address(200, 612, 600, lit=True)
    a.address(200, 736, 600, lit=False)
    a.ambient(cy=870, rx=320, ry=60, opacity=.45)
    a.render("ip-addresses")


def domain() -> None:
    """Domain: a globe, the name the keys carry, locked by a certificate."""
    a = Art("dhDomain")
    a.ambient(cy=470)
    a.solid('<circle cx="450" cy="450" r="270" {fill} {stroke}/>', width=12)
    grid = f'stroke="{LILAC}" stroke-opacity=".3" stroke-width="7" fill="none"'
    a.add(f'<ellipse cx="450" cy="450" rx="115" ry="268" {grid}/>',
          f'<path d="M 450 182 V 718" {grid}/>',
          f'<path d="M 182 450 H 718" {grid}/>',
          f'<path d="M 214 320 Q 450 370 686 320" {grid}/>',
          f'<path d="M 214 580 Q 450 530 686 580" {grid}/>')
    # the padlock: its shackle in the rim gradient, the body dark
    a.add(f'<path d="M 650 625 V 560 A 75 75 0 0 1 800 560 V 625" fill="none" stroke="{a.url("Rim")}" stroke-width="44" filter="{a.url("Soft")}" opacity=".45"/>',
          f'<path d="M 650 625 V 560 A 75 75 0 0 1 800 560 V 625" fill="none" stroke="{a.url("Rim")}" stroke-width="28" stroke-linecap="round"/>')
    a.solid('<rect x="600" y="610" width="250" height="210" rx="38" {fill} {stroke}/>', width=10)
    a.add(f'<circle cx="725" cy="700" r="24" fill="{MINT}"/>',
          f'<rect x="715" y="705" width="20" height="56" rx="10" fill="{MINT}"/>')
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("domain")


def reverse_proxy() -> None:
    """Reverse proxy: a cloud in front takes the apps' connections and passes them to the server behind it."""
    a = Art("dhProxy")
    a.ambient(cy=470)
    # the apps' connections, coming in from the left and ending inside the cloud
    for y, lit in ((300, False), (400, True), (500, False)):
        a.lane(40, y - 30, 260, 60)
        a.add(f'<circle cx="{110}" cy="{y}" r="15" fill="{MINT if lit else LILAC}" opacity="{.95 if lit else .5}"/>')
    # the one way on: from the cloud down to the server
    a.add(f'<path d="M 520 560 V 660" stroke="{TEAL}" stroke-width="30" stroke-linecap="round" filter="{a.url("Soft")}" opacity=".55"/>',
          f'<path d="M 520 560 V 660" stroke="{MINT}" stroke-width="12" stroke-dasharray="2 26" stroke-linecap="round"/>')
    # the server, behind the proxy and out of the apps' sight
    a.server_unit(310, 680, 420, 120, rim=False, lit=True)
    # the proxy: a cloud of three bumps on a flat base
    a.solid('<path d="M 330 560 A 110 110 0 0 1 330 340 A 170 170 0 0 1 640 300 A 135 135 0 0 1 730 560 Z" {fill} {stroke}/>', width=12)
    a.bar(400, 450, 220, 22, fill=MINT, opacity=.9, glow=True)
    a.bar(400, 500, 160, 16, fill=LILAC, opacity=.42)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("reverse-proxy")


def switch(a: Art, x, y, on: bool) -> None:
    """A switch: a pill and its knob, mint with the knob to the right when on, dim with it to the left when off."""
    w, h = 124, 62
    r = h / 2
    if on:
        a.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r:g}" fill="{TEAL}" filter="{a.url("Soft")}" opacity=".55"/>',
              f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r:g}" fill="{MINT}" opacity=".92"/>',
              f'<circle cx="{x + w - r:g}" cy="{y + r:g}" r="{r - 9:g}" fill="{INDIGO_DEEP}"/>')
    else:
        a.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r:g}" fill="{INDIGO_DEEP}" stroke="{LILAC}" stroke-opacity=".45" stroke-width="5"/>',
              f'<circle cx="{x + r:g}" cy="{y + r:g}" r="{r - 13:g}" fill="{LILAC}" opacity=".5"/>')


def installer_options() -> None:
    """Installer options: the install command's terminal, and in front of it its options as switches, one of them off."""
    a = Art("dhOpts")
    a.ambient(cy=470)
    # the terminal, as on the install page, behind: its prompt, the command and a line of output
    a.add(f'<rect x="110" y="150" width="600" height="430" rx="42" fill="{INDIGO_DEEP}" fill-opacity=".7" stroke="{VIOLET}" stroke-opacity=".45" stroke-width="5"/>',
          f'<path d="M 110 245 H 710" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{170 + n * 44}" cy="197" r="13" fill="{LILAC}" opacity=".45"/>')
    a.add(f'<path d="M 180 315 L 238 352 L 180 389" fill="none" stroke="{a.url("Rim")}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>')
    a.bar(280, 341, 300, 22, fill=LILAC, opacity=.4)
    a.bar(180, 440, 160, 20, fill=LILAC, opacity=.25)
    # the options: a card of three switches in front, the middle one off
    a.solid('<rect x="390" y="420" width="480" height="410" rx="40" {fill} {stroke}/>', width=10)
    for n, on in enumerate((True, False, True)):
        y = 478 + n * 112
        switch(a, 440, y, on)
        a.bar(600, y + 22, 210 - n * 35, 18, fill=LILAC, opacity=.4)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("installer-options")


def manager_docs() -> None:
    """The MANAGER docs index: MANAGER's figure, with a page of instructions in front of it."""
    a = Art("dhMgrDocs")
    a.ambient()
    a.manager_hood(400, 440, 760)
    # the page, folded at its top corner
    a.solid('<path d="M 600 500 H 800 L 860 560 V 830 Q 860 860 830 860 H 630 Q 600 860 600 830 Z" {fill} {stroke}/>', width=9)
    a.add(f'<path d="M 800 500 V 560 H 860" fill="none" stroke="{a.url("Rim")}" stroke-width="9" stroke-linejoin="round"/>')
    a.bar(645, 600, 140, 22, fill=MINT, opacity=.9, glow=True)
    for n, w in enumerate((170, 140, 170, 110)):
        a.bar(645, 655 + n * 46, w, 15, fill=LILAC, opacity=.42)
    a.ambient(cy=880, rx=330, ry=60, opacity=.5)
    a.render("docs", product="vpnhood-manager")


def sealed_certificate(a: Art) -> None:
    """A certificate in front: a heading, its lines, and a seal with two ribbons."""
    a.solid('<rect x="160" y="320" width="560" height="400" rx="36" {fill} {stroke}/>', width=11)
    a.bar(220, 390, 230, 24, fill=MINT, opacity=.9, glow=True)
    for n, w in enumerate((380, 320, 360)):
        a.bar(220, 460 + n * 52, w, 16, fill=LILAC, opacity=.4)
    a.add(f'<path d="M 640 690 L 610 820 L 650 795 L 682 830 L 690 700" fill="{INDIGO}" stroke="{a.url("Rim")}" stroke-width="10" stroke-linejoin="round"/>',
          f'<path d="M 700 700 L 712 830 L 742 795 L 785 815 L 750 690" fill="{INDIGO}" stroke="{a.url("Rim")}" stroke-width="10" stroke-linejoin="round"/>')
    a.solid('<circle cx="695" cy="650" r="95" {fill} {stroke}/>', width=12)
    a.add(f'<circle cx="695" cy="650" r="62" fill="none" stroke="{LILAC}" stroke-opacity=".35" stroke-width="6" stroke-dasharray="4 14" stroke-linecap="round"/>')
    a.add(f'<path d="M 662 652 L 686 676 L 730 628" fill="none" stroke="{MINT}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round" filter="{a.url("Soft")}" opacity=".55"/>',
          f'<path d="M 662 652 L 686 676 L 730 628" fill="none" stroke="{MINT}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>')


def server_certificates() -> None:
    """Which certificate: a false one crossed out, a plain one, and in front the sealed one."""
    a = Art("dhServerCerts")
    a.ambient(cy=470)
    # the false one at the back, crossed out
    a.add(f'<rect x="340" y="105" width="500" height="360" rx="32" fill="{INDIGO_DEEP}" fill-opacity=".55" stroke="{VIOLET}" stroke-opacity=".3" stroke-width="5"/>')
    a.bar(395, 160, 170, 16, fill=LILAC, opacity=.22)
    a.add(f'<path d="M 742 150 L 792 200 M 792 150 L 742 200" fill="none" stroke="{RED}" stroke-width="18" stroke-linecap="round"/>')
    # the plain one, dim
    a.add(f'<rect x="250" y="210" width="540" height="390" rx="34" fill="{INDIGO_DEEP}" fill-opacity=".7" stroke="{VIOLET}" stroke-opacity=".45" stroke-width="5"/>')
    a.bar(310, 270, 200, 18, fill=LILAC, opacity=.3)
    sealed_certificate(a)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("certificates", product="vpnhood-server")


def certificates() -> None:
    """Certificates: two certificates of a farm, the front one sealed - the one its keys carry."""
    a = Art("dhCerts")
    a.ambient(cy=470)
    # the one behind, dim
    a.add(f'<rect x="250" y="210" width="540" height="390" rx="34" fill="{INDIGO_DEEP}" fill-opacity=".7" stroke="{VIOLET}" stroke-opacity=".45" stroke-width="5"/>')
    a.bar(310, 270, 200, 18, fill=LILAC, opacity=.3)
    sealed_certificate(a)
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("certificates", product="vpnhood-manager")


def add_server() -> None:
    """Add a server: the panel's list of servers, and a new one joining it under a plus."""
    a = Art("dhMgrAdd")
    a.ambient(cy=470)
    # the panel, as on the MANAGER docs index: a window with its three dots
    a.solid('<rect x="130" y="170" width="640" height="560" rx="40" {fill} {stroke}/>', width=10)
    a.add(f'<path d="M 130 260 H 770" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{188 + n * 40}" cy="215" r="12" fill="{LILAC}" opacity=".45"/>')
    # two servers already in the list, dim
    for n in range(2):
        y = 310 + n * 110
        a.add(f'<rect x="190" y="{y}" width="520" height="84" rx="24" fill="{INDIGO_DEEP}" fill-opacity=".8" stroke="{VIOLET}" stroke-opacity=".3" stroke-width="2"/>')
        a.led(235, y + 42, r=12, on=False)
        a.bar(280, y + 34, 220 - n * 40, 16, fill=LILAC, opacity=.4)
    # the new one, outlined in dashes while it joins, already lit
    y = 530
    a.add(f'<rect x="190" y="{y}" width="520" height="84" rx="24" fill="{INDIGO_DEEP}" fill-opacity=".6" stroke="{MINT}" stroke-opacity=".85" stroke-width="5" stroke-dasharray="18 14"/>')
    a.led(235, y + 42, r=12)
    a.bar(280, y + 34, 190, 16, fill=MINT, opacity=.9, glow=True)
    # the plus, on a badge over the panel's corner
    a.solid('<circle cx="760" cy="700" r="100" {fill} {stroke}/>', width=12)
    a.add(f'<path d="M 760 652 V 748 M 712 700 H 808" stroke="{MINT}" stroke-width="44" stroke-linecap="round" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<path d="M 760 652 V 748 M 712 700 H 808" stroke="{MINT}" stroke-width="26" stroke-linecap="round"/>')
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("add-server", product="vpnhood-manager")


def manager_promo() -> None:
    """The MANAGER promo on the server pages (_includes/docs-managed.html), not a hero:
    MANAGER's figure alone, where a reader meets the name. Shown about 112px wide, so it
    fills the picture."""
    a = Art("dhMgrPromo")
    a.ambient(cy=500)
    a.manager_hood(500, 490, 800)
    a.ambient(cy=930, rx=300, ry=50, opacity=.45)
    a.render("manager", product="vpnhood-manager", prefix="promo")


def access_points() -> None:
    """Access points: a server and its addresses, the one in the keys lit, the other kept out."""
    a = Art("dhMgrAp")
    a.ambient(cy=470)
    a.server_unit(200, 200, 600, 150, rim=True, lit=True)
    # the address in the keys hangs from the server, lit; the other stays dim
    a.add(f'<path d="M 300 365 V 452" stroke="{MINT}" stroke-width="10" stroke-dasharray="2 22" stroke-linecap="round" opacity=".9"/>')
    a.address(200, 466, 600, lit=True)
    a.address(200, 596, 600, lit=False)
    a.ambient(cy=860, rx=320, ry=60, opacity=.45)
    a.render("access-points", product="vpnhood-manager")


def dynamic_ip() -> None:
    """A dynamic IP: a home, the address it had, and the new one taking its place."""
    a = Art("dhDynIp")
    a.ambient(cy=440)
    # the home: a roof and its walls, as one outline
    a.solid('<path d="M 500 110 L 850 400 Q 872 420 842 420 H 780 V 610 Q 780 640 750 640 H 250 Q 220 640 220 610 '
            'V 420 H 158 Q 128 420 150 400 Z" {fill} {stroke}/>', width=12)
    # the server inside it, running
    a.server_unit(300, 430, 400, 130, rim=False, lit=True)
    # the old address, dim, and the new one, lit, with the way from one to the other
    a.address(120, 690, 560, lit=False)
    a.address(120, 810, 560, lit=True)
    turn = "M 690 733 H 790 Q 850 733 850 793 Q 850 853 790 853 H 720"
    a.add(f'<path d="{turn}" fill="none" stroke="{a.url("Rim")}" stroke-width="36" stroke-linecap="round" '
          f'filter="{a.url("Soft")}" opacity=".6"/>',
          f'<path d="{turn}" fill="none" stroke="{a.url("Rim")}" stroke-width="20" stroke-linecap="round"/>',
          f'<path d="M 762 806 L 712 853 L 762 900" fill="none" stroke="{MINT}" stroke-width="20" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    a.render("dynamic-ip", "vpnhood-manager")


def server_profiles() -> None:
    """Server profiles: one card of settings, and the servers of a farm it reaches, each lit."""
    a = Art("dhMgrProf")
    a.ambient(cy=470)
    # the profile: a heading and its settings as switches, one of them off
    a.solid('<rect x="110" y="250" width="420" height="440" rx="40" {fill} {stroke}/>', width=10)
    a.bar(160, 305, 200, 24, fill=MINT, opacity=.9, glow=True)
    for n, on in enumerate((True, False, True)):
        y = 372 + n * 100
        switch(a, 160, y, on)
        a.bar(310, y + 22, 170 - n * 30, 18, fill=LILAC, opacity=.4)
    # its settings reach every server of the farm
    for y in (300, 470, 640):
        a.add(f'<path d="M 548 470 C 585 470 575 {y} 612 {y}" fill="none" stroke="{MINT}" stroke-width="10" stroke-dasharray="2 22" stroke-linecap="round" opacity=".9"/>')
    for y in (235, 405, 575):
        a.server_unit(625, y, 265, 130, rim=False, lit=True)
    a.ambient(cy=870, rx=320, ry=60, opacity=.45)
    a.render("server-profiles", product="vpnhood-manager")


def farms() -> None:
    """Server farms: a farm's servers, framed as one group, and the one key that reaches them all."""
    a = Art("dhMgrFarms")
    a.ambient(cy=480)
    # the farm: a dashed frame around its servers, every one of them up
    a.add(f'<rect x="595" y="185" width="325" height="590" rx="48" fill="{INDIGO_DEEP}" fill-opacity=".12" stroke="{LILAC}" stroke-opacity=".6" stroke-width="7" stroke-dasharray="26 18" stroke-linecap="round"/>')
    for y in (230, 400, 570):
        a.server_unit(625, y, 265, 120, rim=False, lit=True)
    # the key, as on the IP addresses page at half its size, its bow on the left
    key = ('<path d="M 258.9 487.5 H 432.5 A 12.5 12.5 0 0 1 432.5 512.5 H 430 V 537.5 H 410 V 512.5 H 395 V 547.5 H 375 V 512.5 '
           'H 258.9 A 70 70 0 1 1 258.9 487.5 Z" {fill} {stroke}/>')
    a.solid(key, width=9)
    a.add(f'<circle cx="190" cy="500" r="24" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".6" stroke-width="5"/>')
    a.led(190, 500, r=8)
    # one key, every server of the farm
    for y in (290, 460, 630):
        a.add(f'<path d="M 465 500 C 540 500 540 {y} 612 {y}" fill="none" stroke="{MINT}" stroke-width="10" stroke-dasharray="2 22" stroke-linecap="round" opacity=".9"/>')
    a.ambient(cy=870, rx=320, ry=60, opacity=.45)
    a.render("farms", product="vpnhood-manager")


def farm_token() -> None:
    """Farm token: a token that holds a farm's addresses, on its way into a key."""
    a = Art("dhMgrFarmToken")
    a.ambient(cy=470)
    # the token: a disc, its addresses inside, one of them lit
    a.solid('<circle cx="640" cy="400" r="245" {fill} {stroke}/>', width=10)
    a.add(f'<circle cx="640" cy="400" r="196" fill="none" stroke="{LILAC}" stroke-opacity=".3" stroke-width="5" stroke-dasharray="4 16" stroke-linecap="round"/>')
    a.bar(520, 318, 240, 26, fill=LILAC, opacity=.35)
    a.bar(520, 387, 240, 26, fill=MINT, glow=True)
    a.bar(520, 456, 170, 26, fill=LILAC, opacity=.35)
    # the key that carries it, as on the farms page, its bow on the left
    key = ('<path d="M 258.9 687.5 H 432.5 A 12.5 12.5 0 0 1 432.5 712.5 H 430 V 737.5 H 410 V 712.5 H 395 V 747.5 H 375 V 712.5 '
           'H 258.9 A 70 70 0 1 1 258.9 687.5 Z" {fill} {stroke}/>')
    a.solid(key, width=9)
    a.add(f'<circle cx="190" cy="700" r="24" fill="{INDIGO_DEEP}" stroke="{VIOLET}" stroke-opacity=".6" stroke-width="5"/>')
    a.led(190, 700, r=8)
    a.add(f'<path d="M 470 690 C 520 650 540 640 556 622" fill="none" stroke="{MINT}" stroke-width="10" stroke-dasharray="4 22" stroke-linecap="round"/>')
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("farm-token", product="vpnhood-manager")


def roles() -> None:
    """Roles: a project's team, one person a row with their role, the owner's lit, and the shield of what a role allows."""
    a = Art("dhMgrRoles")
    a.ambient(cy=470)
    # the panel, as on Add a server: a window with its three dots
    a.solid('<rect x="130" y="170" width="640" height="560" rx="40" {fill} {stroke}/>', width=10)
    a.add(f'<path d="M 130 260 H 770" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{188 + n * 40}" cy="215" r="12" fill="{LILAC}" opacity=".45"/>')
    # the team: a person, a name and a role chip on each row
    for n in range(3):
        y = 310 + n * 110
        owner = n == 0
        tone, op = (MINT, .9) if owner else (LILAC, .45)
        a.add(f'<rect x="190" y="{y}" width="520" height="84" rx="24" fill="{INDIGO_DEEP}" fill-opacity=".8" stroke="{VIOLET}" stroke-opacity=".3" stroke-width="2"/>',
              f'<circle cx="240" cy="{y + 30}" r="13" fill="{tone}" opacity="{op}"/>',
              f'<path d="M 214 {y + 68} Q 240 {y + 40} 266 {y + 68}" fill="none" stroke="{tone}" stroke-width="12" stroke-linecap="round" opacity="{op}"/>')
        a.bar(290, y + 34, 170 - n * 30, 16, fill=LILAC, opacity=.4)
        a.bar(540, y + 28, 120, 28, fill=tone, opacity=.9 if owner else .3, glow=owner)
    # the shield over the panel's corner: what a role allows
    a.solid('<path d="M 760 575 L 860 615 V 700 Q 860 790 760 835 Q 660 790 660 700 V 615 Z" {fill} {stroke}/>', width=12)
    check = 'M 715 705 L 748 738 L 808 676'
    a.add(f'<path d="{check}" fill="none" stroke="{MINT}" stroke-width="44" stroke-linecap="round" stroke-linejoin="round" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<path d="{check}" fill="none" stroke="{MINT}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>')
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("roles", product="vpnhood-manager")


def troubleshooting() -> None:
    """Troubleshooting: the panel of servers, one whose status is out (a dashed, unlit chip), and a wrench over the corner."""
    a = Art("dhMgrTroubleshooting")
    a.ambient(cy=470)
    # the panel, as on Roles: a window with its three dots
    a.solid('<rect x="130" y="170" width="640" height="560" rx="40" {fill} {stroke}/>', width=10)
    a.add(f'<path d="M 130 260 H 770" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{188 + n * 40}" cy="215" r="12" fill="{LILAC}" opacity=".45"/>')
    # a server a row, two units with their lights, a name and a status chip; the middle one is out
    for n in range(3):
        y = 310 + n * 110
        a.add(f'<rect x="190" y="{y}" width="520" height="84" rx="24" fill="{INDIGO_DEEP}" fill-opacity=".8" stroke="{VIOLET}" stroke-opacity=".3" stroke-width="2"/>')
        for u in range(2):
            a.add(f'<rect x="220" y="{y + 18 + u * 26}" width="52" height="20" rx="6" fill="none" stroke="{LILAC}" stroke-opacity=".5" stroke-width="4"/>',
                  f'<circle cx="260" cy="{y + 28 + u * 26}" r="3.5" fill="{LILAC}" opacity=".6"/>')
        a.bar(300, y + 34, 170 - n * 30, 16, fill=LILAC, opacity=.4)
        if n == 1:
            a.add(f'<rect x="540" y="{y + 28}" width="120" height="28" rx="14" fill="none" stroke="{LILAC}" stroke-opacity=".55" stroke-width="4" stroke-dasharray="10 9"/>')
        else:
            a.bar(540, y + 28, 120, 28, fill=MINT, opacity=.9, glow=True)
    # the badge over the panel's corner: a wrench, its open jaw away from the handle
    a.solid('<circle cx="760" cy="700" r="110" {fill} {stroke}/>', width=12)
    wrench = 'M 784.6 649.5 A 32 32 0 1 0 810.5 675.4 M 756.4 703.6 L 709 751'
    a.add(f'<path d="{wrench}" fill="none" stroke="{MINT}" stroke-width="40" stroke-linecap="round" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<path d="{wrench}" fill="none" stroke="{MINT}" stroke-width="24" stroke-linecap="round"/>')
    a.ambient(cy=880, rx=300, ry=55, opacity=.45)
    a.render("troubleshooting", product="vpnhood-manager")


# --- the troubleshooting page's problems ----------------------------------------------------------
#
# Not heroes: one small character a problem, shown about 64px wide in the page's list of problems
# and beside each one's heading (trouble-<id>.svg, the id the heading's anchor). Each is a thing
# from MANAGER with a face that says what went wrong. At a fifteenth of the canvas a stroke must be
# 30 wide to show at all, so there are few of them, heavy, in the lit mint; red marks only the
# error itself, as in the console.

RED = "#ff4752"   # the site's --red-200


def stroke(a: Art, d: str, color: str = MINT, width: int = 34, glow: bool = True) -> None:
    """A heavy line in a lit colour, its glow under it."""
    if glow:
        a.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width + 24}" stroke-linecap="round" stroke-linejoin="round" filter="{a.url("Soft")}" opacity=".45"/>')
    a.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


def eyes(a: Art, cx, cy, gap=180, r=44, rs=(1, 1)) -> None:
    """Two lit eyes, a server's lights looking back at the reader; rs sizes each, for a puzzled look."""
    for x, s in zip((cx - gap / 2, cx + gap / 2), rs):
        a.add(f'<circle cx="{x:g}" cy="{cy}" r="{r * s * 1.9:.0f}" fill="{a.url("Glow")}" filter="{a.url("Soft")}" opacity=".5"/>',
              f'<circle cx="{x:g}" cy="{cy}" r="{r * s:.0f}" fill="{MINT}"/>')


def tube(a: Art, d: str, width: int = 70) -> None:
    """A thick stroke drawn as a solid: the body's ink inside the violet-to-mint rim."""
    a.add(f'<path d="{d}" fill="none" stroke="{a.url("Rim")}" stroke-width="{width + 60}" stroke-linecap="round" filter="{a.url("Soft")}" opacity=".45"/>',
          f'<path d="{d}" fill="none" stroke="{a.url("Rim")}" stroke-width="{width + 36}" stroke-linecap="round"/>',
          f'<path d="{d}" fill="none" stroke="{INDIGO}" stroke-width="{width}" stroke-linecap="round"/>')


def trouble_status() -> None:
    """A server's status: a cheerful server, telling its heartbeat in a speech bubble."""
    a = Art("tsStatus")
    a.ambient(cy=560, rx=420, ry=380, opacity=.8)
    a.solid('<path d="M 520 90 H 820 Q 900 90 900 170 V 330 Q 900 410 820 410 H 650 L 560 490 L 570 410 H 520 '
            'Q 440 410 440 330 V 170 Q 440 90 520 90 Z" {fill} {stroke}/>', width=30)
    stroke(a, "M 505 250 H 575 L 625 160 L 695 340 L 745 250 H 835", width=30)
    a.solid('<rect x="100" y="450" width="560" height="440" rx="100" {fill} {stroke}/>', width=36)
    eyes(a, 380, 610, gap=200, r=46)
    stroke(a, "M 285 730 Q 380 810 475 730", width=34)
    a.render("status", product="vpnhood-manager", prefix="trouble")


def trouble_ssh() -> None:
    """An SSH install that fails: a terminal window, dazed, its eyes crossed out and its mouth wobbling."""
    a = Art("tsSsh")
    a.ambient(cy=520, opacity=.8)
    a.solid('<rect x="90" y="140" width="820" height="700" rx="90" {fill} {stroke}/>', width=36)
    a.add(f'<path d="M 90 285 H 910" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="12"/>')
    for n in range(3):
        a.add(f'<circle cx="{185 + n * 72}" cy="213" r="25" fill="{LILAC}" opacity=".55"/>')
    for cx in (365, 635):
        stroke(a, f"M {cx - 60} 420 L {cx + 60} 540 M {cx + 60} 420 L {cx - 60} 540", width=36)
    stroke(a, "M 320 690 Q 365 640 410 690 T 500 690 T 590 690 T 680 690", width=32)
    a.render("ssh", product="vpnhood-manager", prefix="trouble")


def trouble_never_connects() -> None:
    """A server that never connects: it holds out its plug to nothing, puzzled, a question mark over it."""
    a = Art("tsNever")
    a.ambient(cy=560, opacity=.8)
    # the cable, from the server's side up to the plug
    a.add(f'<path d="M 540 740 C 690 780 720 640 745 560" fill="none" stroke="{LILAC}" stroke-opacity=".75" stroke-width="30" stroke-linecap="round"/>')
    a.add(f'<g transform="rotate(18 760 470)">'
          f'<path d="M 722 395 V 315 M 798 395 V 315" stroke="{LILAC}" stroke-width="32" stroke-linecap="round"/>'
          f'</g>')
    a.solid('<rect x="685" y="385" width="150" height="170" rx="36" transform="rotate(18 760 470)" {fill} {stroke}/>', width=26)
    # the question
    stroke(a, "M 690 175 Q 690 85 775 85 Q 860 85 860 165 Q 860 225 790 245 V 270", width=34)
    a.add(f'<circle cx="790" cy="335" r="23" fill="{MINT}"/>')
    # the server, eyebrow up
    a.solid('<rect x="90" y="380" width="480" height="500" rx="100" {fill} {stroke}/>', width=36)
    eyes(a, 330, 600, gap=180, r=44, rs=(.85, 1.15))
    stroke(a, "M 205 495 L 275 505 M 375 470 L 455 445", color=LILAC, width=26, glow=False)
    a.add(f'<circle cx="330" cy="755" r="34" fill="none" stroke="{MINT}" stroke-width="28"/>')
    a.render("never-connects", product="vpnhood-manager", prefix="trouble")


def trouble_error() -> None:
    """A server that shows an error: a sick server, a plaster on its head and a thermometer in its mouth."""
    a = Art("tsError")
    a.ambient(cy=540, opacity=.8)
    a.solid('<rect x="130" y="200" width="640" height="660" rx="110" {fill} {stroke}/>', width=36)
    # the plaster, across its top corner
    a.add('<g transform="rotate(-35 320 290)">'
          f'<rect x="170" y="238" width="300" height="104" rx="52" fill="{LILAC}" opacity=".92"/>'
          f'<rect x="285" y="238" width="70" height="104" fill="{INDIGO}" opacity=".22"/>'
          '</g>')
    # its eyes squeezed shut
    stroke(a, "M 290 470 L 370 515 L 290 560", width=34)
    stroke(a, "M 610 470 L 530 515 L 610 560", width=34)
    # the thermometer, its bulb in the mouth and its stem out past its side, red to the line
    a.add(f'<path d="M 450 690 L 880 500" stroke="{LILAC}" stroke-width="66" stroke-linecap="round"/>',
          f'<path d="M 450 690 L 690 584" stroke="{RED}" stroke-width="26" stroke-linecap="round"/>',
          f'<circle cx="450" cy="690" r="78" fill="{RED}" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<circle cx="450" cy="690" r="54" fill="{RED}"/>')
    a.render("error", product="vpnhood-manager", prefix="trouble")


def trouble_lost() -> None:
    """A server that stops reporting: the server's ghost, an O of surprise on its face."""
    a = Art("tsLost")
    a.ambient(cy=520, opacity=.8)
    for y, w in ((430, 90), (560, 60)):
        stroke(a, f"M {110 - w} {y} H 110", color=LILAC, width=26, glow=False)
    ghost = ("M 200 850 V 470 A 300 300 0 0 1 800 470 V 850 Q 750 790 700 850 Q 650 910 600 850 "
             "Q 550 790 500 850 Q 450 910 400 850 Q 350 790 300 850 Q 250 910 200 850 Z")
    a.solid(f'<path d="{ghost}" {{fill}} {{stroke}}/>', width=36)
    for x in (405, 595):
        a.add(f'<ellipse cx="{x}" cy="470" rx="78" ry="105" fill="{a.url("Glow")}" filter="{a.url("Soft")}" opacity=".5"/>',
              f'<ellipse cx="{x}" cy="470" rx="42" ry="62" fill="{MINT}"/>')
    a.add(f'<ellipse cx="500" cy="660" rx="48" ry="62" fill="{INDIGO_DEEP}" stroke="{MINT}" stroke-width="28"/>')
    a.render("lost", product="vpnhood-manager", prefix="trouble")


def trouble_tv_phone() -> None:
    """A phone that can't open the TV's page: the phone, puzzled, one eyebrow up, a question mark beside it."""
    a = Art("tsTvPhone")
    a.ambient(cy=540, opacity=.8)
    stroke(a, "M 700 215 Q 700 125 785 125 Q 870 125 870 205 Q 870 265 800 285 V 310", width=34)
    a.add(f'<circle cx="800" cy="375" r="23" fill="{MINT}"/>')
    a.solid('<rect x="170" y="130" width="450" height="760" rx="100" {fill} {stroke}/>', width=36)
    eyes(a, 395, 430, gap=180, r=44, rs=(.85, 1.15))
    stroke(a, "M 270 325 L 340 335 M 440 300 L 520 275", color=LILAC, width=26, glow=False)
    a.add(f'<circle cx="395" cy="610" r="34" fill="none" stroke="{MINT}" stroke-width="28"/>')
    a.bar(335, 790, 120, 22, opacity=.5)
    a.render("tv-phone", product="vpnhood-client", prefix="trouble")


def trouble_tv_lost() -> None:
    """A page that stops answering: the TV has left the screen and dozed off, eyes shut, a Z rising from it."""
    a = Art("tsTvLost")
    a.ambient(cy=540, opacity=.8)
    stroke(a, "M 690 95 H 790 L 690 205 H 790", width=28)
    stroke(a, "M 840 40 H 900 L 840 105 H 900", color=LILAC, width=20, glow=False)
    a.solid('<path d="M 430 760 H 570 V 850 H 700 Q 730 850 730 880 Q 730 910 700 910 H 300 Q 270 910 270 880 Q 270 850 300 850 H 430 Z" {fill} {stroke}/>', width=26)
    a.solid('<rect x="80" y="260" width="840" height="510" rx="90" {fill} {stroke}/>', width=36)
    for cx in (350, 650):
        stroke(a, f"M {cx - 75} 470 Q {cx} 540 {cx + 75} 470", width=34)
    stroke(a, "M 440 640 H 560", color=LILAC, width=28, glow=False)
    a.render("tv-lost", product="vpnhood-client", prefix="trouble")


def trouble_farm() -> None:
    """A farm with a red message: a barn, worried, a red flag on its roof."""
    a = Art("tsFarm")
    a.ambient(cy=580, opacity=.8)
    a.add(f'<path d="M 500 270 V 70" stroke="{LILAC}" stroke-width="24" stroke-linecap="round"/>',
          f'<path d="M 512 62 L 700 115 L 512 172 Z" fill="{RED}" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<path d="M 512 62 L 700 115 L 512 172 Z" fill="{RED}" stroke="{RED}" stroke-width="16" stroke-linejoin="round"/>')
    a.solid('<path d="M 130 880 V 530 L 500 255 L 870 530 V 880 Z" {fill} {stroke}/>', width=36)
    # its barn door
    a.add(f'<rect x="385" y="680" width="230" height="200" fill="none" stroke="{LILAC}" stroke-opacity=".7" stroke-width="20"/>',
          f'<path d="M 385 680 L 615 880 M 615 680 L 385 880" stroke="{LILAC}" stroke-opacity=".7" stroke-width="20"/>')
    eyes(a, 500, 515, gap=220, r=42)
    stroke(a, "M 335 430 L 415 410 M 585 410 L 665 430", color=LILAC, width=24, glow=False)
    stroke(a, "M 445 625 Q 500 590 555 625", width=30)
    a.render("farm", product="vpnhood-manager", prefix="trouble")


def trouble_key() -> None:
    """A key that will not open: a key, puzzled, its shaft tied in a loop."""
    a = Art("tsKey")
    a.ambient(cy=520, opacity=.8)
    # the shaft, in the key's own frame: u along it from the bow's centre, v across it, up. On the
    # way it loops up and back over itself (a trochoid, x = t - 3 sin t, y = 3 cos t), drawn in two
    # halves so the second crosses over the first
    th, ox, oy, u0, k = math.radians(40), 270, 330, 470, 56

    def at(u: float, v: float) -> str:
        return f"{ox + u * math.cos(th) + v * math.sin(th):.0f} {oy + u * math.sin(th) - v * math.cos(th):.0f}"

    def loop(t0: float, t1: float) -> str:
        ts = [t0 + (t1 - t0) * n / 32 for n in range(33)]
        return " L ".join(at(u0 + k * (t - 3 * math.sin(t)), k * (3 * math.cos(t) + 3)) for t in ts)

    tube(a, f"M {at(180, 0)} L {loop(-math.pi, 0)}", width=52)
    tube(a, f"M {loop(0, math.pi)} L {at(840, 0)}", width=52)
    for u in (735, 805):
        a.add(f'<path d="M {at(u, -20)} L {at(u, -95)}" stroke="{a.url("Rim")}" stroke-width="40" stroke-linecap="round"/>')
    a.solid(f'<circle cx="{ox}" cy="{oy}" r="200" {{fill}} {{stroke}}/>', width=36)
    eyes(a, ox, 310, gap=150, r=36, rs=(.9, 1.35))
    stroke(a, "M 158 222 L 218 237 M 310 197 L 380 172", color=LILAC, width=24, glow=False)
    stroke(a, "M 195 425 Q 225 400 255 425 T 315 425 T 375 425", width=28)
    a.render("key", product="vpnhood-manager", prefix="trouble")


def trouble_apps() -> None:
    """Apps that cannot connect: a phone in tears, its Wi-Fi struck through."""
    a = Art("tsApps")
    a.ambient(cy=540, opacity=.8)
    a.solid('<rect x="265" y="95" width="470" height="820" rx="95" {fill} {stroke}/>', width=36)
    a.bar(435, 160, 130, 26, fill=LILAC, opacity=.5)
    # the Wi-Fi, dimmed, and the stroke through it
    wifi = f'fill="none" stroke="{LILAC}" stroke-opacity=".6" stroke-width="30" stroke-linecap="round"'
    a.add(f'<path d="M 385 345 A 165 165 0 0 1 615 345" {wifi}/>',
          f'<path d="M 435 395 A 95 95 0 0 1 565 395" {wifi}/>',
          f'<circle cx="500" cy="440" r="22" fill="{LILAC}" opacity=".6"/>')
    a.add(f'<path d="M 395 255 L 605 460" stroke="{RED}" stroke-width="34" stroke-linecap="round"/>')
    eyes(a, 500, 590, gap=180, r=38)
    a.add(f'<path d="M 410 640 Q 380 700 410 725 Q 440 700 410 640 Z" fill="{CYAN}" stroke="{CYAN}" stroke-width="10" stroke-linejoin="round"/>')
    stroke(a, "M 430 790 Q 500 735 570 790", width=30)
    a.render("apps", product="vpnhood-manager", prefix="trouble")


def phone(a: Art, x, y, w, h, lit_rows: int = 1) -> None:
    """A phone: its body, a speaker slot and app rows on the screen, the first ones lit."""
    a.solid(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w * .2:.0f}" {{fill}} {{stroke}}/>', width=10)
    a.bar(x + w * .38, y + 32, w * .24, 12, fill=LILAC, opacity=.4)
    for n in range(4):
        lit = n < lit_rows
        a.bar(x + w * .2, y + 96 + n * 62, w * (.6 if n % 2 == 0 else .45), 22,
              fill=MINT if lit else LILAC, opacity=.9 if lit else .32, glow=lit)


def self_hosted_docs() -> None:
    """The self-hosted VPN docs: a phone and a server joined by the tunnel, and a page of instructions in front of them."""
    a = Art("dhSelfDocs")
    a.ambient()
    phone(a, 130, 230, 210, 390)
    a.lane(330, 352, 260, 76)
    a.add(f'<circle cx="460" cy="390" r="13" fill="{MINT}"/>')
    a.server_unit(560, 250, 310, 110, rim=True, lit=True)
    a.server_unit(560, 380, 310, 110, rim=False, lit=False)
    # the page, folded at its top corner
    a.solid('<path d="M 500 530 H 720 L 780 590 V 860 Q 780 890 750 890 H 530 Q 500 890 500 860 Z" {fill} {stroke}/>', width=9)
    a.add(f'<path d="M 720 530 V 590 H 780" fill="none" stroke="{a.url("Rim")}" stroke-width="9" stroke-linejoin="round"/>')
    a.bar(548, 630, 140, 22, fill=MINT, opacity=.9, glow=True)
    for n, w in enumerate((180, 150, 180, 110)):
        a.bar(548, 685 + n * 46, w, 15, fill=LILAC, opacity=.42)
    a.ambient(cy=890, rx=330, ry=60, opacity=.5)
    a.render("docs", product="self-hosted-vpn")


def how_it_works() -> None:
    """How it works: a phone's traffic goes through the tunnel to the server, and out to the internet from there."""
    a = Art("dhHow")
    a.ambient(cy=500)
    # the internet, which only the server reaches
    a.solid('<circle cx="770" cy="250" r="125" {fill} {stroke}/>', width=10)
    grid = f'stroke="{LILAC}" stroke-opacity=".3" stroke-width="6" fill="none"'
    a.add(f'<ellipse cx="770" cy="250" rx="52" ry="123" {grid}/>',
          f'<path d="M 645 250 H 895" {grid}/>')
    a.add(f'<path d="M 770 390 V 470" stroke="{MINT}" stroke-width="10" stroke-dasharray="2 22" stroke-linecap="round" opacity=".9"/>')
    phone(a, 100, 330, 200, 380, lit_rows=2)
    # the tunnel, with packets on their way
    a.lane(290, 562, 330, 96)
    for n, (x, w) in enumerate(((340, 46), (418, 58), (510, 70))):
        a.bar(x, 600, w, 20, fill=MINT, opacity=.55 + .2 * n, glow=(n == 2))
    a.server_unit(600, 490, 300, 120, rim=True, lit=True)
    a.server_unit(600, 630, 300, 120, rim=False, lit=False)
    a.ambient(cy=880, rx=330, ry=60, opacity=.5)
    a.render("how-it-works", product="self-hosted-vpn")


def vpn_detection() -> None:
    """VPN detection: a filter's lens over a tunnel finds one smooth stream and nothing to recognize."""
    a = Art("dhDetect")
    a.ambient(cy=470)
    # the tunnel, and the one smooth stream in it
    a.lane(60, 372, 880, 170)
    a.bar(120, 440, 760, 34, fill=MINT, opacity=.9, glow=True)
    # the lens over it: a glass that leaves the tunnel in view, and its handle
    ring = 'cx="430" cy="457" r="250" fill="none"'
    a.add(f'<circle cx="430" cy="457" r="250" fill="{LILAC}" fill-opacity=".07"/>',
          f'<circle {ring} stroke="{a.url("Rim")}" stroke-width="44" filter="{a.url("Soft")}" opacity=".5"/>',
          f'<circle {ring} stroke="{a.url("Rim")}" stroke-width="30"/>',
          f'<path d="M 625 652 L 815 842" stroke="{a.url("Rim")}" stroke-width="66" stroke-linecap="round"/>')
    a.ambient(cy=890, rx=330, ry=60, opacity=.5)
    a.render("vpn-detection", product="self-hosted-vpn")


if __name__ == "__main__":
    self_hosted_docs()
    how_it_works()
    vpn_detection()
    docs()
    requirements()
    install()
    linux()
    linux_requirements()
    client_diagnose()
    first_key()
    client_tv()
    trouble_tv_phone()
    trouble_tv_lost()
    first_key_ask()
    first_key_own()
    first_key_connect()
    install_system("linux", "dhInstallLinux")
    install_system("docker", "dhInstallDocker")
    install_system("windows", "dhInstallWindows")
    ip_blocking()
    ip_addresses()
    server_certificates()
    domain()
    reverse_proxy()
    installer_options()
    manager_docs()
    add_server()
    access_points()
    dynamic_ip()
    certificates()
    server_profiles()
    farms()
    farm_token()
    roles()
    troubleshooting()
    manager_promo()
    for problem in (trouble_status, trouble_ssh, trouble_never_connects, trouble_error,
                    trouble_lost, trouble_farm, trouble_key, trouble_apps):
        problem()
