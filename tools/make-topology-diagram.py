#!/usr/bin/env python3
"""Generate the /self-hosted-vpn/ topology diagram as a translatable Liquid include.

Writes `_includes/diagrams/self-hosted-topology.svg`. THAT FILE IS GENERATED — edit this
script and re-run, never the SVG.

Why a script and not a hand-drawn asset: the chalk look is two SVG filters, not artwork.
`feTurbulence` + `feDisplacementMap` warps every stroke off-true so nothing is
machine-straight, and a second noise layer erodes stroke alpha into chalk dust. Roughness
is one number (`scale` on the displacement map), so the whole style is tunable.

Why an inline include and not an <img>:

  * **Translation.** Every label is emitted as `{{ t.diagram_* }}`, so the strings live in
    `_data/i18n/en/self_hosted_vpn.json` and vhtranslator carries them into every language
    like any other copy. Text baked into an image would stay English on the /fa/, /fr/,
    /de/ and /ar/ trees.
  * **Fonts.** The page's own `"Poppins", sans-serif` is used rather than a handwriting
    stack. A chalk font would have to be self-hosted (Google Fonts is blocked in CN — see
    CLAUDE.md), and an unhosted one silently falls back to whatever the visitor has, which
    is different on every OS. The wobbly strokes carry the blackboard feel on their own.

The diagram states two facts and no more: **direction** (every arrow points the way the
connection is opened) and **cardinality** (one optional panel, many servers, many
clients). The MANAGER box and its arrow are dashed because a server runs standalone on
`FileAccessManager` — see `docs/topology.md` in the VpnHood repo.

Run from the repo root:  python tools/make-topology-diagram.py
"""
from __future__ import annotations

import math
import pathlib
import random

OUT = pathlib.Path("_includes/diagrams/self-hosted-topology.svg")

W, H = 940, 830

BOARD = "#22202f"
CHALK = "#ecebe3"
CHALK_DIM = "#a9a7b8"
MINT = "#9fe8d2"
VIOLET = "#c3b0ff"
AMBER = "#f2d9a2"

FONT = "&quot;Poppins&quot;, sans-serif"

# Seeded so the "hand-drawn" jitter is identical on every run - a rebuild must not
# produce a different file.
rnd = random.Random(9)


def t(key: str) -> str:
    """A translatable string, with a per-key fall back to English.

    `t` is the page's localized map. A language whose data folder predates these keys
    would otherwise render the label as an empty string, leaving unlabelled boxes — far
    worse than English text. CI translates before every deploy, so the fallback is a
    safety net rather than the normal path, but the failure it prevents is silent.
    Same per-key fallback rule the chrome strings use.
    """
    return "{{ t.%s | default: vh_topo_en.%s }}" % (key, key)


def j(v: float, amt: float = 2.4) -> float:
    return v + rnd.uniform(-amt, amt)


def box(x, y, w, h, stroke=CHALK, sw=3.0, dash=None):
    d = ("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
         % (j(x), j(y), j(x + w), j(y), j(x + w), j(y + h), j(x), j(y + h)))
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, stroke, sw, da))


def stack(x, y, w, h, stroke, n=2, off=13):
    """Ghost outlines behind a box - "there are many of these" without drawing many."""
    return "".join(
        '<g opacity="%.2f">%s</g>' % (0.30 / i, box(x + off * i, y + off * i, w, h, stroke, 2.4))
        for i in range(n, 0, -1))


def txt(x, y, s, size=22, fill=CHALK, anchor="middle"):
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s">%s</text>' % (x, y, FONT, size, fill, anchor, s))


def arrow(x1, y1, x2, y2, stroke=MINT, sw=3.2, dash=None):
    d = "M %.1f %.1f L %.1f %.1f" % (j(x1, 1.6), j(y1, 1.6), x2, y2)
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    ang = math.atan2(y2 - y1, x2 - x1)
    hl = 19
    h1 = (x2 - hl * math.cos(ang - 0.40), y2 - hl * math.sin(ang - 0.40))
    h2 = (x2 - hl * math.cos(ang + 0.40), y2 - hl * math.sin(ang + 0.40))
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round"%s/>'
            '<path d="M %.1f %.1f L %.1f %.1f M %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>'
            % (d, stroke, sw, da, h1[0], h1[1], x2, y2, h2[0], h2[1], x2, y2, stroke, sw))


def cloud(cx, cy, s=1.0):
    bumps = [(-1.0, 0.15), (-0.78, -0.42), (-0.3, -0.66), (0.2, -0.72),
             (0.66, -0.44), (1.0, -0.02), (0.86, 0.4), (0.2, 0.56), (-0.5, 0.52)]
    pts = [(cx + bx * 84 * s, cy + by * 62 * s) for bx, by in bumps]
    d = "M %.1f %.1f" % pts[0]
    for i in range(1, len(pts) + 1):
        p, prev = pts[i % len(pts)], pts[i - 1]
        d += " Q %.1f %.1f %.1f %.1f" % (j((prev[0] + p[0]) / 2, 11),
                                         j((prev[1] + p[1]) / 2, 11), p[0], p[1])
    return ('<path d="%s Z" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
            % (d, CHALK_DIM))


BW, BH, BX = 250, 118, 330          # shared box geometry
CXX = BX + BW / 2                   # the centre line everything hangs off
MY, SY, CY = 108, 356, 604          # manager / server / client row tops

parts = []

parts.append(txt(470, 62, t("diagram_title"), size=32))

# --- MANAGER: one, and optional -------------------------------------------
parts.append(box(BX, MY, BW, BH, VIOLET, 3.2, dash="15 11"))
parts.append(txt(CXX, MY + 54, t("diagram_manager"), size=26))
parts.append(txt(CXX, MY + 84, t("diagram_manager_sub"), size=16, fill=CHALK_DIM))
parts.append(txt(BX - 30, MY + 68, t("diagram_count_one"), size=20, fill=VIOLET, anchor="end"))
parts.append(txt(BX + BW + 28, MY + 56, t("diagram_optional"), size=19, fill=AMBER, anchor="start"))
parts.append(txt(BX + BW + 28, MY + 84, t("diagram_optional_note"), size=15,
                 fill=CHALK_DIM, anchor="start"))

# --- SERVER: many ----------------------------------------------------------
parts.append(stack(BX, SY, BW, BH, MINT))
parts.append(box(BX, SY, BW, BH, MINT, 3.2))
parts.append(txt(CXX, SY + 54, t("diagram_server"), size=26))
parts.append(txt(CXX, SY + 84, t("diagram_server_sub"), size=16, fill=CHALK_DIM))
parts.append(txt(BX - 30, SY + 68, t("diagram_count_many"), size=20, fill=MINT, anchor="end"))

# --- CLIENT: many ----------------------------------------------------------
parts.append(stack(BX, CY, BW, BH, CHALK))
parts.append(box(BX, CY, BW, BH, CHALK, 3.2))
parts.append(txt(CXX, CY + 54, t("diagram_client"), size=26))
parts.append(txt(CXX, CY + 84, t("diagram_client_sub"), size=16, fill=CHALK_DIM))
parts.append(txt(BX - 30, CY + 68, t("diagram_count_many"), size=20, fill=CHALK_DIM, anchor="end"))

# --- the three connections -------------------------------------------------
parts.append(arrow(CXX, CY - 12, CXX, SY + BH + 14, stroke=MINT))
parts.append(txt(CXX + 26, CY - 46, t("diagram_tunnel"), size=17, fill=MINT, anchor="start"))

# dashed to match the panel: this link goes away with it
parts.append(arrow(CXX, SY - 12, CXX, MY + BH + 14, stroke=VIOLET, dash="13 10"))
parts.append(txt(CXX + 26, SY - 46, t("diagram_status"), size=17, fill=VIOLET, anchor="start"))

parts.append(cloud(778, SY + 59))
parts.append(txt(778, SY + 66, t("diagram_internet"), size=17, fill=CHALK_DIM))
parts.append(arrow(BX + BW + 22, SY + 59, 686, SY + 59, stroke=MINT, sw=2.8))

# --- the one idea the whole picture carries -------------------------------
parts.append(txt(470, 792, t("diagram_caption"), size=18, fill=AMBER))

SVG = """<!-- GENERATED by tools/make-topology-diagram.py - do not edit; edit the script.
     Strings come from _data/i18n/<lang>/self_hosted_vpn.json via the page's `t` assign,
     each falling back to English so a not-yet-translated language never renders blank. -->
{{%- assign vh_topo_en = site.data.i18n.en.self_hosted_vpn -%}}
<svg class="vh-topology-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     role="img" aria-labelledby="vhTopoTitle vhTopoDesc" preserveAspectRatio="xMidYMid meet">
  <title id="vhTopoTitle">{TITLE}</title>
  <desc id="vhTopoDesc">{DESC}</desc>
  <defs>
    <filter id="vhTopoChalk" x="-6%" y="-6%" width="112%" height="112%">
      <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3" seed="11" result="warp"/>
      <feDisplacementMap in="SourceGraphic" in2="warp" scale="4.2"
                         xChannelSelector="R" yChannelSelector="G" result="wobbly"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.62" numOctaves="4" seed="5" result="grain"/>
      <feColorMatrix in="grain" type="matrix" result="grainA"
                     values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  .7 .4 .2 0 .05"/>
      <feComposite in="wobbly" in2="grainA" operator="in" result="eroded"/>
      <feMerge><feMergeNode in="eroded"/><feMergeNode in="eroded"/></feMerge>
    </filter>
    <filter id="vhTopoBoard" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="4" seed="19" result="n"/>
      <feColorMatrix in="n" type="matrix"
                     values="0 0 0 0 .55  0 0 0 0 .54  0 0 0 0 .62  0 0 0 .05 0"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" rx="18" fill="{BOARD}"/>
  <rect width="{W}" height="{H}" rx="18" filter="url(#vhTopoBoard)"/>

  <g filter="url(#vhTopoChalk)">
{PARTS}
  </g>
</svg>
""".format(W=W, H=H, BOARD=BOARD, TITLE=t("diagram_title"), DESC=t("diagram_desc"),
           PARTS="\n".join("    " + p for p in parts))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(SVG, encoding="utf-8")
print("wrote %s (%d bytes)" % (OUT, len(SVG)))
