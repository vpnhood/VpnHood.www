#!/usr/bin/env python3
"""Draw the hero art of the docs pages: one small picture beside each page's title.

Writes `assets/images/vpnhood-server/docs/hero-<name>.svg`. THOSE FILES ARE GENERATED -
edit this script and re-run, never the SVGs.

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

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "images" / "vpnhood-server" / "docs"

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

    def render(self, name: str) -> None:
        body = "\n".join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">\n'
               f'<!-- Generated by tools/make-docs-heroes.py - edit the script, not this file. -->\n'
               f'{self.defs()}\n{body}\n</svg>\n')
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"hero-{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote hero-{name}.svg ({len(svg.encode())} bytes)")


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


if __name__ == "__main__":
    docs()
    install()
    docker()
    ip_blocking()
    ip_addresses()
    domain()
    reverse_proxy()
