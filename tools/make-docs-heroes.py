#!/usr/bin/env python3
"""Draw the hero art of the docs pages: one small picture beside each page's title.

Writes `assets/images/<product>/docs/hero-<name>.svg`, for the docs of VpnHood! SERVER and
VpnHood! MANAGER, and `vpnhood-manager/docs/promo-manager.svg`, the art of the MANAGER promo on
the server pages. THOSE FILES ARE GENERATED - edit this script and re-run, never the SVGs.

The art speaks the language of the guides' heroes (`assets/images/guides/*.svg`): a deep
indigo object with a violet-to-mint rim, soft glows and lilac detail, on transparency. That
is what lets it skip the light-art pipeline (`tools/make-light-art.py`): a dark object on a
light page reads as an object, as the guides' gauge does, so both themes show the same file.

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

import pathlib

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


def docker() -> None:
    """Docker: the server packed in a container, stacked with others on its host."""
    a = Art("dhDocker")
    a.ambient(cy=520)
    boxes = ((180, 540, False), (520, 540, False), (350, 320, True))
    for x, y, rim in boxes:
        w, h = 300, 196
        a.solid(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" {{fill}} {{stroke}}/>', rim=rim, width=10)
        if not rim:
            a.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="none" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="5"/>')
        for n in range(5):
            rx = x + 58 + n * 46
            a.add(f'<path d="M {rx} {y + 40} V {y + h - 40}" stroke="{LILAC}" stroke-opacity="{.4 if rim else .25}" stroke-width="12" stroke-linecap="round"/>')
        if rim:
            a.led(x + w - 44, y + 44, r=14)
    a.lane(150, 772, 700, 70)
    for n in range(3):
        a.add(f'<circle cx="{420 + n * 80}" cy="807" r="11" fill="{MINT if n == 2 else LILAC}" opacity="{.95 if n == 2 else .45}"/>')
    a.ambient(cy=820, rx=330, ry=70, opacity=.5)
    a.render("docker")


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
    """The MANAGER docs index: the web panel, with its list of servers, and a page of instructions in front of it."""
    a = Art("dhMgrDocs")
    a.ambient()
    # the panel: a browser window with a sidebar and three servers, the first one lit
    a.solid('<rect x="120" y="190" width="620" height="470" rx="40" {fill} {stroke}/>', width=10)
    a.add(f'<path d="M 120 280 H 740" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="3"/>')
    for n in range(3):
        a.add(f'<circle cx="{178 + n * 40}" cy="235" r="12" fill="{LILAC}" opacity=".45"/>')
    for n in range(4):
        a.bar(170, 330 + n * 52, 120 if n else 90, 16, fill=MINT if n == 0 else LILAC, opacity=.9 if n == 0 else .32)
    for n in range(3):
        y = 320 + n * 100
        a.add(f'<rect x="340" y="{y}" width="350" height="76" rx="22" fill="{INDIGO_DEEP}" fill-opacity=".8" stroke="{VIOLET}" stroke-opacity=".3" stroke-width="2"/>')
        a.led(380, y + 38, r=11, on=(n == 0))
        a.bar(420, y + 30, 150 - n * 20, 16, fill=LILAC, opacity=.4)
    # the page, folded at its top corner
    a.solid('<path d="M 600 500 H 800 L 860 560 V 830 Q 860 860 830 860 H 630 Q 600 860 600 830 Z" {fill} {stroke}/>', width=9)
    a.add(f'<path d="M 800 500 V 560 H 860" fill="none" stroke="{a.url("Rim")}" stroke-width="9" stroke-linejoin="round"/>')
    a.bar(645, 600, 140, 22, fill=MINT, opacity=.9, glow=True)
    for n, w in enumerate((170, 140, 170, 110)):
        a.bar(645, 655 + n * 46, w, 15, fill=LILAC, opacity=.42)
    a.ambient(cy=880, rx=330, ry=60, opacity=.5)
    a.render("docs", product="vpnhood-manager")


def certificates() -> None:
    """Certificates: two certificates of a farm, the front one sealed - the one its keys carry."""
    a = Art("dhCerts")
    a.ambient(cy=470)
    # the one behind, dim
    a.add(f'<rect x="250" y="210" width="540" height="390" rx="34" fill="{INDIGO_DEEP}" fill-opacity=".7" stroke="{VIOLET}" stroke-opacity=".45" stroke-width="5"/>')
    a.bar(310, 270, 200, 18, fill=LILAC, opacity=.3)
    # the one in front: a heading, its lines, and a seal with two ribbons
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
    """The MANAGER promo on the server pages (_includes/docs-managed.html), not a hero: the web
    panel, its servers, and the traffic it shows for them. Shown about 112px wide, so the
    shapes are fewer and heavier than a hero's."""
    a = Art("dhMgrPromo")
    a.ambient(cy=500)
    # the panel: a window with its three dots and a sidebar, the first entry lit
    a.solid('<rect x="110" y="170" width="780" height="640" rx="54" {fill} {stroke}/>', width=14)
    a.add(f'<path d="M 110 285 H 890" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="5"/>')
    for n in range(3):
        a.add(f'<circle cx="{185 + n * 52}" cy="228" r="17" fill="{LILAC}" opacity=".45"/>')
    for n in range(4):
        a.bar(170, 345 + n * 70, 120 if n else 90, 26, fill=MINT if n == 0 else LILAC, opacity=.9 if n == 0 else .32)
    # two servers, the first one up
    for n in range(2):
        y = 335 + n * 125
        a.add(f'<rect x="350" y="{y}" width="480" height="98" rx="28" fill="{INDIGO_DEEP}" fill-opacity=".8" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="4"/>')
        a.led(405, y + 49, r=17, on=(n == 0))
        a.bar(455, y + 37, 230 - n * 60, 24, fill=LILAC, opacity=.42)
    # their traffic: a bar chart, the latest bar lit
    for n, h in enumerate((80, 125, 100, 170)):
        lit = n == 3
        a.bar(370 + n * 115, 760 - h, 70, h, fill=MINT if lit else LILAC, opacity=.95 if lit else .35, glow=lit)
    a.ambient(cy=900, rx=330, ry=60, opacity=.45)
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


if __name__ == "__main__":
    self_hosted_docs()
    how_it_works()
    docs()
    install()
    docker()
    ip_blocking()
    ip_addresses()
    domain()
    reverse_proxy()
    installer_options()
    manager_docs()
    add_server()
    access_points()
    certificates()
    server_profiles()
    farms()
    roles()
    manager_promo()
