#!/usr/bin/env python3
"""Generate the diagrams of the docs pages as translatable Liquid includes.

Writes, under `_includes/diagrams/`:

  server-two-ips.svg, server-two-ips-tall.svg    /vpnhood-server/docs/ip-blocking/
  reverse-proxy.svg, reverse-proxy-tall.svg      /vpnhood-server/docs/reverse-proxy/
  how-it-works.svg, how-it-works-tall.svg        /self-hosted-vpn/docs/how-it-works/

THOSE FILES ARE GENERATED - edit this script and re-run, never the SVGs.

Same blackboard style, and the same reasons for it, as `tools/make-topology-diagram.py`
(read its header first - it is the original): every label is a `{{ t.diagram_* }}` string
from the page's own JSON, so vhtranslator carries it into every language, and the font is
the page's self-hosted Poppins. The board keeps its dark ground in both themes on purpose,
through the shared `.vh-topology-svg` class.

Three differences from the marketing diagrams, all because a docs page is read on a phone
as often as on a desk:

  * **Drawn twice.** Each diagram reads left to right from a tablet up (`<name>.svg`), and
    top to bottom on a phone (`<name>-tall.svg`), where a left-to-right board would shrink
    its labels to 8px. The page includes both, each in a `<figure>` shown only at its own
    width (Bootstrap's `d-none d-md-block` and `d-md-none`), and the hidden one is out of
    the accessibility tree. The two share their strings; only the geometry differs.
  * **Room for every language.** A label's slot fits the longest of the 13 languages
    (French, Italian, Turkish and Arabic run a third longer than English), so check a new
    label in all of them.
  * **Laid out left to right in every language.** Labels are anchored to the arrows and
    icons, and an inherited `direction: rtl` would flip `start` and `end` and push them
    across. Persian and Arabic text still runs right to left inside each label.

Nodes are icons, not boxes: two people for your users, a rack for your server, a globe for
websites, and a cloud - the docs heroes' cloud, `tools/make-docs-heroes.py` - for a reverse
proxy. A server's addresses are ports on its edge, in the colour of the arrow that reaches
them. Example addresses and names are not copy: they come from `_data/code.yml`, the values
the pages' own text uses, so the picture and the text always agree.

Each diagram states one idea and no more:

  server-two-ips  users connect to one address and websites see another, so the address
                  websites can flag is never the one in the access keys.
  reverse-proxy   apps that find the proxy through your domain go around a blocked server
                  address.
  how-it-works    devices reach your server through an encrypted tunnel, and websites see
                  your server, not your users.

Run from the repo root:  python tools/make-docs-diagrams.py
"""
from __future__ import annotations

import math
import pathlib
import random

BOARD = "#22202f"
CHALK = "#ecebe3"
CHALK_DIM = "#a9a7b8"
MINT = "#9fe8d2"
VIOLET = "#c3b0ff"
AMBER = "#f2d9a2"
CORAL = "#f4a49c"   # a blocked route

FONT = "&quot;Poppins&quot;, sans-serif"

# Seeded so the "hand-drawn" jitter is identical on every run - a rebuild must not produce
# a different file. Re-seeded per drawing so adding one never reshuffles another.
rnd = random.Random(9)


def seed(n: int) -> None:
    global rnd
    rnd = random.Random(n)


def j(v: float, amt: float = 2.4) -> float:
    return v + rnd.uniform(-amt, amt)


def box(x, y, w, h, stroke=CHALK, sw=3.0, dash=None):
    d = ("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
         % (j(x), j(y), j(x + w), j(y), j(x + w), j(y + h), j(x), j(y + h)))
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, stroke, sw, da))


def txt(x, y, s, size=22, fill=CHALK, anchor="middle"):
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s">%s</text>' % (x, y, FONT, size, fill, anchor, s))


def line(x1, y1, x2, y2, stroke=CHALK_DIM, sw=2.2, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round"%s/>' % (j(x1, 1), j(y1, 1), j(x2, 1), j(y2, 1), stroke, sw, da))


def dot(x, y, r, fill):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, fill)


def ring(x, y, r, stroke=CHALK, sw=3.0):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (j(x, 0.8), j(y, 0.8), r, stroke, sw))


def head(x1, y1, x2, y2, stroke, sw):
    """An arrowhead at (x2, y2), pointing away from (x1, y1)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    hl = 19
    h1 = (x2 - hl * math.cos(ang - 0.40), y2 - hl * math.sin(ang - 0.40))
    h2 = (x2 - hl * math.cos(ang + 0.40), y2 - hl * math.sin(ang + 0.40))
    return ('<path d="M %.1f %.1f L %.1f %.1f M %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>'
            % (h1[0], h1[1], x2, y2, h2[0], h2[1], x2, y2, stroke, sw))


def arrow(x1, y1, x2, y2, stroke=MINT, sw=3.2, dash=None):
    d = "M %.1f %.1f L %.1f %.1f" % (j(x1, 1.6), j(y1, 1.6), x2, y2)
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round"%s/>'
            % (d, stroke, sw, da) + head(x1, y1, x2, y2, stroke, sw))


def elbow(pts, stroke=MINT, sw=3.2, r=18):
    """An arrow along square turns, each corner rounded, with its head at the last point."""
    d = "M %.1f %.1f" % (j(pts[0][0], 1.2), j(pts[0][1], 1.2))
    for (ax, ay), (px, py), (bx, by) in zip(pts, pts[1:], pts[2:]):
        la, lb = math.hypot(px - ax, py - ay), math.hypot(bx - px, by - py)
        d += " L %.1f %.1f Q %.1f %.1f %.1f %.1f" % (
            px - (px - ax) / la * r, py - (py - ay) / la * r, px, py,
            px + (bx - px) / lb * r, py + (by - py) / lb * r)
    d += " L %.1f %.1f" % pts[-1]
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>'
            % (d, stroke, sw) + head(*pts[-2], *pts[-1], stroke, sw))


def person(x, y, s, stroke):
    """A head and shoulders, the head centred on (x, y)."""
    w, top, base = 24 * s, y + 14 * s, y + 47 * s
    return (ring(x, y, 12.5 * s, stroke) +
            '<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="3.0" stroke-linecap="round"/>'
            % (x - w, base, x - w, top, x + w, top, x + w, base, stroke))


def people(cx, cy):
    """Your users: two people side by side, centred on (cx, cy) - about 92 x 60."""
    return person(cx + 24, cy - 21, 0.88, CHALK_DIM) + person(cx - 22, cy - 17, 1.0, CHALK)


def rack(cx, cy, w=104, h=84):
    """Your server: a box with two units, each with two lights and a vent."""
    x, y = cx - w / 2, cy - h / 2
    out = [box(x, y, w, h, CHALK, 3.2)]
    pad = 11
    uh = (h - 3 * pad) / 2
    for i in range(2):
        uy = y + pad + i * (uh + pad)
        my = uy + uh / 2
        out += [box(x + pad, uy, w - 2 * pad, uh, CHALK_DIM, 2.2),
                dot(x + pad + 12, my, 3.4, CHALK_DIM), dot(x + pad + 23, my, 3.4, CHALK_DIM),
                line(x + w - pad - 36, my, x + w - pad - 10, my)]
    return "".join(out)


def port(x, y, colour):
    """One of the server's addresses, on its edge."""
    return dot(x, y, 7, colour)


def globe(cx, cy, r=42, stroke=CHALK_DIM):
    """Websites: a globe."""
    c = 0.866 * r
    return (ring(cx, cy, r, stroke, 2.8) +
            '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
            % (cx, cy, r * 0.42, r, stroke) +
            line(cx - r, cy, cx + r, cy, stroke) +
            line(cx - c, cy - r / 2, cx + c, cy - r / 2, stroke, 2.0) +
            line(cx - c, cy + r / 2, cx + c, cy + r / 2, stroke, 2.0))


# The docs heroes' cloud (tools/make-docs-heroes.py, reverse_proxy): three bumps on a flat
# base, drawn there in a 1000-wide frame, where it spans x 220..815 and y 217..560.
CLOUD_X0, CLOUD_W, CLOUD_Y0, CLOUD_H = 220, 595, 217, 343


def cloud(cx, cy, w, stroke=CHALK, sw=3.0):
    """A reverse proxy: the heroes' cloud, its box centred on (cx, cy), `w` wide."""
    s = w / CLOUD_W
    ox, oy = cx - (CLOUD_X0 + CLOUD_W / 2) * s, cy - (CLOUD_Y0 + CLOUD_H / 2) * s

    def p(x, y):
        return "%.1f %.1f" % (ox + x * s, oy + y * s)

    d = ("M %s A %.1f %.1f 0 0 1 %s A %.1f %.1f 0 0 1 %s A %.1f %.1f 0 0 1 %s Z"
         % (p(330, 560), 110 * s, 110 * s, p(330, 340), 170 * s, 170 * s, p(640, 300),
            135 * s, 135 * s, p(730, 560)))
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>'
            % (d, stroke, sw))


def cross(cx, cy, s=12, colour=CORAL, sw=4.2):
    """A blocked route."""
    return line(cx - s, cy - s, cx + s, cy + s, colour, sw) + line(cx - s, cy + s, cx + s, cy - s, colour, sw)


def render(out: str, data_file: str, en_var: str, w: int, h: int, uid: str, parts: list[str]) -> None:
    """Wrap the drawn parts in the board, the chalk filters and the Liquid preamble."""
    def t(key):
        return "{{ t.%s | default: %s.%s }}" % (key, en_var, key)

    svg = """<!-- GENERATED by tools/make-docs-diagrams.py - do not edit; edit the script.
     Strings come from _data/i18n/<lang>/{DATA}.json via the page's `t` assign, each
     falling back to English so a not-yet-translated language never renders blank. -->
{{%- assign {EN} = site.data.i18n.en.{DATA} -%}}
<svg class="vh-topology-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" direction="ltr"
     role="img" aria-labelledby="{UID}Title {UID}Desc" preserveAspectRatio="xMidYMid meet">
  <title id="{UID}Title">{TITLE}</title>
  <desc id="{UID}Desc">{DESC}</desc>
  <defs>
    <filter id="{UID}Chalk" x="-6%" y="-6%" width="112%" height="112%">
      <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3" seed="11" result="warp"/>
      <feDisplacementMap in="SourceGraphic" in2="warp" scale="4.2"
                         xChannelSelector="R" yChannelSelector="G" result="wobbly"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.62" numOctaves="4" seed="5" result="grain"/>
      <feColorMatrix in="grain" type="matrix" result="grainA"
                     values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  .7 .4 .2 0 .05"/>
      <feComposite in="wobbly" in2="grainA" operator="in" result="eroded"/>
      <feMerge><feMergeNode in="eroded"/><feMergeNode in="eroded"/></feMerge>
    </filter>
    <filter id="{UID}Board" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="4" seed="19" result="n"/>
      <feColorMatrix in="n" type="matrix"
                     values="0 0 0 0 .55  0 0 0 0 .54  0 0 0 0 .62  0 0 0 .05 0"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" rx="18" fill="{BOARD}"/>
  <rect width="{W}" height="{H}" rx="18" filter="url(#{UID}Board)"/>

  <g filter="url(#{UID}Chalk)">
{PARTS}
  </g>
</svg>
""".format(W=w, H=h, BOARD=BOARD, UID=uid, DATA=data_file, EN=en_var,
           TITLE=t("diagram_title"), DESC=t("diagram_desc"),
           PARTS="\n".join("    " + p for p in parts))

    path = pathlib.Path("_includes/diagrams/%s.svg" % out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print("wrote %s (%d bytes)" % (path, len(svg)))


def strings(en_var: str):
    """The page's string `k`, falling back to English, and the code value `k`."""
    def t(k):
        return "{{ t.%s | default: %s.%s }}" % (k, en_var, k)

    def code(k):
        return "{{ site.data.code.%s }}" % k
    return t, code


# ===========================================================================
# server-two-ips - users come in on one address, the server goes out on another
# ===========================================================================
TWO_IPS = ("vpnhood_server_docs_ip_blocking", "vh_twoips_en")
RACK_W, RACK_H = 104, 84


def server_two_ips() -> None:
    T, CODE = strings(TWO_IPS[1])

    # --- left to right: users, the server with a port on each side, websites --------
    seed(9)
    W, H = 920, 318
    Y = 92                              # the line the icons and arrows sit on
    XU, XS, XW = 120, 460, 800
    pl, pr = XS - RACK_W / 2, XS + RACK_W / 2
    parts = [people(XU, Y), rack(XS, Y, RACK_W, RACK_H), globe(XW, Y)]
    # each arrow: what the address is above it, the address and who knows it below
    for x1, x2, colour, role, ip, who in (
            (XU + 58, pl - 14, MINT, "diagram_connection_ip", "ip_connection_example", "diagram_in_keys"),
            (pr + 14, XW - 56, VIOLET, "diagram_outgoing_ip", "ip_outgoing_example", "diagram_websites_see")):
        m = (x1 + x2) / 2
        parts += [arrow(x1, Y, x2, Y, colour),
                  txt(m, Y - 18, T(role), 22, colour),
                  txt(m, Y + 36, CODE(ip), 20),
                  txt(m, Y + 60, T(who), 17, CHALK_DIM)]
    parts += [port(pl, Y, MINT), port(pr, Y, VIOLET)]
    for x, name, sub in ((XU, "diagram_users", "diagram_users_sub"),
                         (XS, "diagram_server", "diagram_server_sub"),
                         (XW, "diagram_websites", None)):
        parts.append(txt(x, Y + 98, T(name), 24))
        if sub:
            parts.append(txt(x, Y + 124, T(sub), 16, CHALK_DIM))
    parts.append(txt(W / 2, H - 38, T("diagram_caption"), 20, AMBER))
    render("server-two-ips", *TWO_IPS, W, H, "vhTwoIps", parts)

    # --- top to bottom: icons down the left, their labels beside them ----------------
    seed(9)
    W, H = 560, 660
    X, TX = 104, 186                    # the icons' column, and the labels' left edge
    YU, YS, YW = 84, 316, 544
    pt, pb = YS - RACK_H / 2, YS + RACK_H / 2
    parts = [people(X, YU), rack(X, YS, RACK_W, RACK_H), globe(X, YW)]
    for y1, y2, colour, role, ip, who in (
            (YU + 44, pt - 14, MINT, "diagram_connection_ip", "ip_connection_example", "diagram_in_keys"),
            (pb + 14, YW - 56, VIOLET, "diagram_outgoing_ip", "ip_outgoing_example", "diagram_websites_see")):
        m = (y1 + y2) / 2
        parts += [arrow(X, y1, X, y2, colour),
                  txt(TX, m - 12, T(role), 22, colour, "start"),
                  txt(TX, m + 16, CODE(ip), 20, CHALK, "start"),
                  txt(TX, m + 40, T(who), 17, CHALK_DIM, "start")]
    parts += [port(X, pt, MINT), port(X, pb, VIOLET)]
    for y, name, sub in ((YU, "diagram_users", "diagram_users_sub"),
                         (YS, "diagram_server", "diagram_server_sub")):
        parts += [txt(TX, y - 2, T(name), 24, CHALK, "start"),
                  txt(TX, y + 24, T(sub), 16, CHALK_DIM, "start")]
    parts.append(txt(TX, YW + 8, T("diagram_websites"), 24, CHALK, "start"))
    parts.append(txt(W / 2, H - 34, T("diagram_caption"), 19, AMBER))
    render("server-two-ips-tall", *TWO_IPS, W, H, "vhTwoIpsTall", parts)


# ===========================================================================
# reverse-proxy - apps go around a blocked server address, through the proxy
# ===========================================================================
REVERSE_PROXY = ("vpnhood_server_docs_reverse_proxy", "vh_rproxy_en")
CLOUD_SIZE = 250


def blocked_route(parts, a, b, horizontal, T, CODE, label_at):
    """A dashed route from a to b, cut by a cross half way, with the server's address
    and "blocked" at `label_at` (x, y, anchor) - the first line above the second."""
    (ax, ay), (bx, by) = a, b
    cx, cy = (ax + bx) / 2, (ay + by) / 2
    gap = 24
    if horizontal:
        parts += [line(ax, ay, cx - gap, cy, CHALK_DIM, 2.6, "9 11"),
                  arrow(cx + gap, cy, bx, by, CHALK_DIM, 2.6, "9 11")]
    else:
        parts += [line(ax, ay, cx, cy - gap, CHALK_DIM, 2.6, "9 11"),
                  arrow(cx, cy + gap, bx, by, CHALK_DIM, 2.6, "9 11")]
    parts.append(cross(cx, cy))
    lx, ly, anchor, step = label_at
    parts += [txt(lx, ly, CODE("ip_connection_example"), 19, CHALK_DIM, anchor),
              txt(lx, ly + step, T("diagram_blocked"), 19, CORAL, anchor)]


def reverse_proxy() -> None:
    T, CODE = strings(REVERSE_PROXY[1])

    # --- left to right: the proxy above, the blocked direct route below ---------------
    seed(13)
    W, H = 920, 500
    XU, XS, YB = 120, 800, 300          # users and server, on the direct route
    XP, YP = 460, 126                   # the proxy's cloud
    YA = 140                            # the route through the proxy
    parts = [people(XU, YB), rack(XS, YB, RACK_W, RACK_H), cloud(XP, YP, CLOUD_SIZE),
             txt(XP, YP + 12, T("diagram_proxy"), 23),
             txt(XP, YP + 36, T("diagram_proxy_sub"), 16, CHALK_DIM)]
    # in through your domain, then on to the server
    x_in = XP - CLOUD_SIZE / 2 - 12
    lx = (XU + x_in) / 2 + 6            # the domain's slot: between the elbow's corner and the cloud
    parts += [elbow([(XU, YB - 42), (XU, YA), (x_in, YA)]),
              txt(lx, YA - 18, T("diagram_domain"), 21, MINT),
              txt(lx, YA + 32, CODE("domain_example"), 18),
              elbow([(XP + CLOUD_SIZE / 2 + 14, YA), (XS, YA), (XS, YB - RACK_H / 2 - 14)])]
    blocked_route(parts, (XU + 58, YB), (XS - RACK_W / 2 - 14, YB), True, T, CODE,
                  ((XU + XS) / 2, YB - 26, "middle", 64))
    for x, name, sub in ((XU, "diagram_users", "diagram_users_sub"),
                         (XS, "diagram_server", "diagram_server_sub")):
        parts += [txt(x, YB + 82, T(name), 24), txt(x, YB + 108, T(sub), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 34, T("diagram_caption"), 20, AMBER))
    render("reverse-proxy", *REVERSE_PROXY, W, H, "vhRevProxy", parts)

    # --- top to bottom: the direct route down the left, the proxy on the right --------
    seed(13)
    W, H = 560, 760
    X, YU, YS = 110, 84, 556            # users and server, on the direct route
    XP, YP = 410, 300                   # the proxy's cloud, clear of the longest "blocked"
    parts = [people(X, YU), rack(X, YS, RACK_W, RACK_H), cloud(XP, YP, CLOUD_SIZE),
             txt(XP, YP + 12, T("diagram_proxy"), 23),
             txt(XP, YP + 36, T("diagram_proxy_sub"), 16, CHALK_DIM)]
    top, bottom = YP - 70, YP + 72      # where the arrows meet the cloud
    parts += [elbow([(X + 58, YU), (XP, YU), (XP, top - 12)]),
              txt((X + 58 + XP) / 2, YU - 18, T("diagram_domain"), 21, MINT),
              txt((X + 58 + XP) / 2, YU + 32, CODE("domain_example"), 19),
              elbow([(XP, bottom + 12), (XP, YS), (X + RACK_W / 2 + 14, YS)])]
    blocked_route(parts, (X, YU + 112), (X, YS - RACK_H / 2 - 14), False, T, CODE,
                  (X + 24, (YU + 112 + YS - RACK_H / 2 - 14) / 2 - 4, "start", 24))
    for y, name, sub in ((YU, "diagram_users", "diagram_users_sub"),
                         (YS, "diagram_server", "diagram_server_sub")):
        parts += [txt(X, y + 66, T(name), 23), txt(X, y + 90, T(sub), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 32, T("diagram_caption"), 18, AMBER))
    render("reverse-proxy-tall", *REVERSE_PROXY, W, H, "vhRevProxyTall", parts)


# ===========================================================================
# how-it-works - the tunnel to your server, and on from there
# ===========================================================================
HOW = ("self_hosted_vpn_docs_how_it_works", "vh_how_en")


def how_it_works() -> None:
    T, _ = strings(HOW[1])

    # --- left to right: users, the tunnel, the server, websites -------------------------
    seed(17)
    W, H = 920, 300
    Y = 92
    XU, XS, XW = 120, 460, 800
    pl, pr = XS - RACK_W / 2, XS + RACK_W / 2
    parts = [people(XU, Y), rack(XS, Y, RACK_W, RACK_H), globe(XW, Y)]
    # the tunnel: a double line around the arrow, as on the guides' pictures
    x1, x2 = XU + 58, pl - 14
    parts += [line(x1, Y - 11, x2 - 6, Y - 11, MINT, 2.0), line(x1, Y + 11, x2 - 6, Y + 11, MINT, 2.0),
              arrow(x1 + 10, Y, x2, Y, MINT)]
    m = (x1 + x2) / 2
    parts += [txt(m, Y - 26, T("diagram_tunnel"), 20, MINT),
              txt(m, Y + 40, T("diagram_tunnel_sub"), 17, CHALK_DIM)]
    x1, x2 = pr + 14, XW - 56
    m = (x1 + x2) / 2
    parts += [arrow(x1, Y, x2, Y, VIOLET), txt(m, Y - 18, T("diagram_out"), 20, VIOLET)]
    for x, name, sub in ((XU, "diagram_users", "diagram_users_sub"),
                         (XS, "diagram_server", "diagram_server_sub"),
                         (XW, "diagram_websites", None)):
        parts.append(txt(x, Y + 98, T(name), 24))
        if sub:
            parts.append(txt(x, Y + 124, T(sub), 16, CHALK_DIM))
    parts.append(txt(W / 2, H - 30, T("diagram_caption"), 20, AMBER))
    render("how-it-works", *HOW, W, H, "vhHow", parts)

    # --- top to bottom: icons down the left, their labels beside them ----------------
    seed(17)
    W, H = 560, 640
    X, TX = 104, 186
    YU, YS, YW = 84, 316, 530
    pt, pb = YS - RACK_H / 2, YS + RACK_H / 2
    parts = [people(X, YU), rack(X, YS, RACK_W, RACK_H), globe(X, YW)]
    y1, y2 = YU + 44, pt - 14
    parts += [line(X - 11, y1, X - 11, y2 - 6, MINT, 2.0), line(X + 11, y1, X + 11, y2 - 6, MINT, 2.0),
              arrow(X, y1 + 10, X, y2, MINT)]
    m = (y1 + y2) / 2
    parts += [txt(TX, m - 2, T("diagram_tunnel"), 21, MINT, "start"),
              txt(TX, m + 24, T("diagram_tunnel_sub"), 17, CHALK_DIM, "start")]
    y1, y2 = pb + 14, YW - 56
    parts += [arrow(X, y1, X, y2, VIOLET), txt(TX, (y1 + y2) / 2 + 7, T("diagram_out"), 21, VIOLET, "start")]
    for y, name, sub in ((YU, "diagram_users", "diagram_users_sub"),
                         (YS, "diagram_server", "diagram_server_sub")):
        parts += [txt(TX, y - 2, T(name), 24, CHALK, "start"),
                  txt(TX, y + 24, T(sub), 16, CHALK_DIM, "start")]
    parts.append(txt(TX, YW + 8, T("diagram_websites"), 24, CHALK, "start"))
    parts.append(txt(W / 2, H - 32, T("diagram_caption"), 19, AMBER))
    render("how-it-works-tall", *HOW, W, H, "vhHowTall", parts)


if __name__ == "__main__":
    server_two_ips()
    reverse_proxy()
    how_it_works()
