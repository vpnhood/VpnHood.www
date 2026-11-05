#!/usr/bin/env python3
"""Generate the docs pages' diagrams, and Cloak Mode's, as translatable Liquid includes.

Writes, under `_includes/diagrams/`:

  server-two-ips.svg, server-two-ips-tall.svg    /vpnhood-server/docs/ip-blocking/
  reverse-proxy.svg, reverse-proxy-tall.svg      /vpnhood-server/docs/reverse-proxy/
  how-it-works.svg, how-it-works-tall.svg        /self-hosted-vpn/docs/how-it-works/
  dynamic-ip-follow.svg, dynamic-ip-follow-tall.svg,
  dynamic-ip-find.svg, dynamic-ip-find-tall.svg  /vpnhood-manager/docs/dynamic-ip/
  cloak-mode.svg, cloak-mode-tall.svg            /features/cloak-mode/

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
    across. Persian and Arabic text still runs right to left inside each label: on those
    pages each translated label sits in a right-to-left isolate (`vh_bidi_in`, `vh_bidi_out`),
    or a Latin word in it would swap the parts of the sentence on either side of it.

Nodes are icons, not boxes: two people for your users, a rack for your server, a globe for
websites, a cloud - the docs heroes' cloud, `tools/make-docs-heroes.py` - for a reverse
proxy, a window for MANAGER, a key for access keys, a signpost for what shows the way to a
server's address, a phone for your device, and a brick wall for a network filter. A server's
addresses are ports on its edge, in the colour of the arrow that reaches them. Example
addresses and names are not copy: they come from `_data/code.yml`, the values the pages' own
text uses, so the picture and the text always agree.

Each diagram states one idea and no more:

  server-two-ips  users connect to one address and websites see another, so the address
                  websites can flag is never the one in the access keys.
  reverse-proxy   apps that find the proxy through your domain go around a blocked server
                  address.
  how-it-works    devices reach your server through an encrypted tunnel, and websites see
                  your server, not your users.
  dynamic-ip-follow  the server's next report shows MANAGER its new address, which goes into
                  the keys.
  dynamic-ip-find an older key's address is gone, and the name or the URL in the key leads
                  apps to the new one.
  cloak-mode      nobody outside can see into a tunnel, so a filter goes by its shape: packets
                  make one long tunnel bumpy, and with Cloak Mode each connection's own tunnel
                  is smooth, like web browsing. Both lanes read left to right on a phone too,
                  one under the other, because setting them side by side is the idea.

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


def window(cx, cy, w=128, h=92):
    """VpnHood! MANAGER: a web panel's window, with a title bar and a small chart."""
    x, y = cx - w / 2, cy - h / 2
    base = y + h - 13
    out = [box(x, y, w, h, CHALK, 3.2), line(x, y + 22, x + w, y + 22, CHALK_DIM, 2.2)]
    out += [dot(x + 14 + n * 12, y + 11, 2.8, CHALK_DIM) for n in range(3)]
    for n, height in enumerate((13, 24, 18, 34)):
        bx = x + 28 + n * 24
        out.append(line(bx, base, bx, base - height, MINT if n == 3 else CHALK_DIM, 6.0))
    return "".join(out)


def access_key(cx, cy, stroke=CHALK):
    """An access key on its side: a round bow, a shaft and two teeth - about 124 x 60."""
    bx, end = cx - 38, cx + 62
    return (ring(bx, cy, 24, stroke, 3.2) + ring(bx, cy, 7, CHALK_DIM, 2.2) +
            line(bx + 24, cy, end, cy, stroke, 3.4) +
            line(end, cy, end, cy + 21, stroke, 3.4) + line(end - 22, cy, end - 22, cy + 16, stroke, 3.4))


def signpost(cx, cy, stroke=CHALK):
    """What shows the way: a post with two boards, one pointing on - about 124 x 108."""
    def board(x0, x1, tip, y):
        return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" stroke="%s" '
                'stroke-width="3.0" stroke-linejoin="round"/>'
                % (j(x0, 1.2), j(y, 1.2), j(x1, 1.2), j(y, 1.2), tip, y + 15, j(x1, 1.2), j(y + 30, 1.2),
                   j(x0, 1.2), j(y + 30, 1.2), stroke))
    return (line(cx, cy - 54, cx, cy - 42, stroke, 3.4) + line(cx, cy - 12, cx, cy + 2, stroke, 3.4) +
            line(cx, cy + 32, cx, cy + 54, stroke, 3.4) + line(cx - 20, cy + 54, cx + 20, cy + 54, stroke, 3.0) +
            board(cx - 44, cx + 44, cx + 62, cy - 42) + board(cx + 36, cx - 36, cx - 52, cy + 2))


def render(out: str, data_file: str, en_var: str, w: int, h: int, uid: str, parts: list[str],
           key: str = "diagram") -> None:
    """Wrap the drawn parts in the board, the chalk filters and the Liquid preamble. `key` names
    the title and description strings, for a page with more than one diagram."""
    def t(key):
        return "{{ t.%s | default: %s.%s }}" % (key, en_var, key)

    svg = """<!-- GENERATED by tools/make-docs-diagrams.py - do not edit; edit the script.
     Strings come from _data/i18n/<lang>/{DATA}.json via the page's `t` assign, each
     falling back to English so a not-yet-translated language never renders blank. -->
{{%- assign {EN} = site.data.i18n.en.{DATA} -%}}
{{%- assign vh_bidi_in = "" -%}}{{%- assign vh_bidi_out = "" -%}}
{{%- if vh_dir == "rtl" -%}}{{%- assign vh_bidi_in = "&#x2067;" -%}}{{%- assign vh_bidi_out = "&#x2069;" -%}}{{%- endif -%}}
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
           TITLE=t(key + "_title"), DESC=t(key + "_desc"),
           PARTS="\n".join("    " + p for p in parts))

    path = pathlib.Path("_includes/diagrams/%s.svg" % out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print("wrote %s (%d bytes)" % (path, len(svg)))


def strings(en_var: str):
    """The page's string `k`, falling back to English, and the code value `k`."""
    def t(k):
        return "{{ vh_bidi_in }}{{ t.%s | default: %s.%s }}{{ vh_bidi_out }}" % (k, en_var, k)

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


# ===========================================================================
# dynamic-ip-follow - the server's next report shows MANAGER its new address
# ===========================================================================
DYNAMIC_IP = ("vpnhood_manager_docs_dynamic_ip", "vh_dynip_en")
WINDOW_W, WINDOW_H = 128, 92


def dynamic_ip_follow() -> None:
    T, CODE = strings(DYNAMIC_IP[1])
    steps = (("diagram_report", "diagram_report_sub", MINT), ("diagram_update", "diagram_update_sub", VIOLET))

    # --- left to right: the server, MANAGER, the keys ------------------------------------
    seed(21)
    W, H = 920, 330
    Y = 92
    XS, XM, XK = 120, 460, 800
    parts = [rack(XS, Y, RACK_W, RACK_H), window(XM, Y), access_key(XK, Y)]
    spans = ((XS + RACK_W / 2 + 14, XM - WINDOW_W / 2 - 14), (XM + WINDOW_W / 2 + 14, XK - 78))
    for (x1, x2), (role, sub, colour) in zip(spans, steps):
        m = (x1 + x2) / 2
        parts += [arrow(x1, Y, x2, Y, colour),
                  txt(m, Y - 18, T(role), 22, colour),
                  txt(m, Y + 36, CODE("ip_connection_example"), 20),
                  txt(m, Y + 66, T(sub), 17, CHALK_DIM)]
    for x, name, sub in ((XS, "diagram_server", "diagram_server_sub"),
                         (XM, "diagram_manager", "diagram_manager_sub"),
                         (XK, "diagram_keys", "diagram_keys_sub")):
        parts += [txt(x, Y + 104, T(name), 24), txt(x, Y + 130, T(sub), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 34, T("diagram_follow_caption"), 20, AMBER))
    render("dynamic-ip-follow", *DYNAMIC_IP, W, H, "vhDynFollow", parts, "diagram_follow")

    # --- top to bottom: icons down the left, their labels beside them ----------------
    seed(21)
    W, H = 560, 660
    X, TX = 104, 186
    YS, YM, YK = 84, 316, 530
    parts = [rack(X, YS, RACK_W, RACK_H), window(X, YM), access_key(X, YK)]
    spans = ((YS + RACK_H / 2 + 14, YM - WINDOW_H / 2 - 14), (YM + WINDOW_H / 2 + 14, YK - 44))
    for (y1, y2), (role, sub, colour) in zip(spans, steps):
        m = (y1 + y2) / 2
        parts += [arrow(X, y1, X, y2, colour),
                  txt(TX, m - 12, T(role), 22, colour, "start"),
                  txt(TX, m + 16, CODE("ip_connection_example"), 20, CHALK, "start"),
                  txt(TX, m + 40, T(sub), 17, CHALK_DIM, "start")]
    for y, name, sub in ((YS, "diagram_server", "diagram_server_sub"),
                         (YM, "diagram_manager", "diagram_manager_sub"),
                         (YK, "diagram_keys", "diagram_keys_sub")):
        parts += [txt(TX, y - 2, T(name), 24, CHALK, "start"),
                  txt(TX, y + 24, T(sub), 16, CHALK_DIM, "start")]
    parts.append(txt(W / 2, H - 34, T("diagram_follow_caption"), 18, AMBER))
    render("dynamic-ip-follow-tall", *DYNAMIC_IP, W, H, "vhDynFollowTall", parts, "diagram_follow")


# ===========================================================================
# dynamic-ip-find - the name or the URL in a key leads apps to the new address
# ===========================================================================
def gone_route(parts, a, b, horizontal, T, CODE, label_at, cut=0.5):
    """The way to the old address: dashed and cut `cut` of the way along, as blocked_route,
    with the old address and its name at `label_at` (x, y, anchor, step)."""
    (ax, ay), (bx, by) = a, b
    cx, cy = ax + (bx - ax) * cut, ay + (by - ay) * cut
    gap = 24
    if horizontal:
        parts += [line(ax, ay, cx - gap, cy, CHALK_DIM, 2.6, "9 11"),
                  arrow(cx + gap, cy, bx, by, CHALK_DIM, 2.6, "9 11")]
    else:
        parts += [line(ax, ay, cx, cy - gap, CHALK_DIM, 2.6, "9 11"),
                  arrow(cx, cy + gap, bx, by, CHALK_DIM, 2.6, "9 11")]
    parts.append(cross(cx, cy))
    lx, ly, anchor, step = label_at
    parts += [txt(lx, ly, CODE("ip_outgoing_example"), 19, CHALK_DIM, anchor),
              txt(lx, ly + step, T("diagram_old"), 19, CORAL, anchor)]


def dynamic_ip_find() -> None:
    T, CODE = strings(DYNAMIC_IP[1])

    # --- left to right: the signpost above, the way to the old address below -------------
    seed(23)
    W, H = 920, 548
    XU, XS, YB = 120, 800, 350          # users and server, on the old route
    XP, YP = 460, 118                   # the signpost
    parts = [people(XU, YB), rack(XS, YB, RACK_W, RACK_H), signpost(XP, YP),
             txt(XP, YP + 92, T("diagram_finder"), 22),
             txt(XP, YP + 118, T("diagram_finder_sub"), 17, CHALK_DIM)]
    x_in, x_out = XP - 74, XP + 76      # where the route meets the signpost
    lx = (x_out + XS) / 2 - 8           # the new address's slot: between the signpost and the corner
    parts += [elbow([(XU, YB - 42), (XU, YP), (x_in, YP)]),
              elbow([(x_out, YP), (XS, YP), (XS, YB - RACK_H / 2 - 14)]),
              txt(lx, YP - 18, T("diagram_new"), 21, MINT),
              txt(lx, YP + 32, CODE("ip_connection_example"), 19)]
    gone_route(parts, (XU + 58, YB), (XS - RACK_W / 2 - 14, YB), True, T, CODE,
               ((XU + XS) / 2, YB - 26, "middle", 64))
    for x, name, sub in ((XU, "diagram_users", "diagram_users_sub"),
                         (XS, "diagram_server", "diagram_server_sub")):
        parts += [txt(x, YB + 82, T(name), 24), txt(x, YB + 108, T(sub), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 34, T("diagram_find_caption"), 20, AMBER))
    render("dynamic-ip-find", *DYNAMIC_IP, W, H, "vhDynFind", parts, "diagram_find")

    # --- top to bottom: the old route down the left, the signpost on the right -----------
    seed(23)
    W, H = 560, 766
    X, YU, YS = 110, 84, 586            # users and server, on the old route
    XP, YP = 402, 262                   # the signpost
    parts = [people(X, YU), rack(X, YS, RACK_W, RACK_H), signpost(XP, YP),
             txt(XP, YP + 92, T("diagram_finder"), 21),
             txt(XP, YP + 118, T("diagram_finder_sub"), 16, CHALK_DIM)]
    top, bottom = YP - 66, YP + 136     # where the route meets the signpost and leaves its label
    parts += [elbow([(X + 58, YU), (XP, YU), (XP, top)]),
              elbow([(XP, bottom), (XP, YS), (X + RACK_W / 2 + 14, YS)]),
              txt((X + RACK_W / 2 + XP) / 2 + 8, YS - 18, T("diagram_new"), 21, MINT),
              txt((X + RACK_W / 2 + XP) / 2 + 8, YS + 32, CODE("ip_connection_example"), 19)]
    y1, y2 = YU + 112, YS - RACK_H / 2 - 14
    gone_route(parts, (X, y1), (X, y2), False, T, CODE,
               (X + 24, y1 + (y2 - y1) * 0.64 - 4, "start", 24), 0.64)
    for y, name, sub in ((YU, "diagram_users", "diagram_users_sub"),
                         (YS, "diagram_server", "diagram_server_sub")):
        parts += [txt(X, y + 72, T(name), 23), txt(X, y + 96, T(sub), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 32, T("diagram_find_caption"), 18, AMBER))
    render("dynamic-ip-find-tall", *DYNAMIC_IP, W, H, "vhDynFindTall", parts, "diagram_find")


# ===========================================================================
# cloak-mode - a filter can recognize one long tunnel, and not a browser's requests
# ===========================================================================
CLOAK = ("features_cloak_mode", "vh_cloak_en")
PHONE_W, PHONE_H = 54, 92


def phone(cx, cy):
    """Your device: a phone, with its speaker and its home bar."""
    x, y = cx - PHONE_W / 2, cy - PHONE_H / 2
    return (box(x, y, PHONE_W, PHONE_H, CHALK, 3.2) + line(cx - 7, y + 10, cx + 7, y + 10) +
            line(cx - 11, y + PHONE_H - 10, cx + 11, y + PHONE_H - 10))


def filter_wall(cx, y0, y1, w, course):
    """A network filter: a column of bricks, each course offset from the last."""
    x0, x1 = cx - w / 2, cx + w / 2
    rows = round((y1 - y0) / course)
    step = (y1 - y0) / rows
    out = [box(x0, y0, w, y1 - y0, CHALK_DIM, 2.8)]
    for n in range(rows):
        y = y0 + n * step
        if n:
            out.append(line(x0, y, x1, y, CHALK_DIM, 1.8))
        for x in (cx,) if n % 2 else (x0 + w / 4, x1 - w / 4):
            out.append(line(x, y, x, y + step, CHALK_DIM, 1.8))
    return "".join(out)


def magnifier(cx, cy, r=19):
    """Inspection: a lens, with the board's ground inside it so the bricks stop at its rim."""
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, BOARD) +
            ring(cx, cy, r, CHALK, 3.2) +
            line(cx + r * 0.72, cy + r * 0.72, cx + r * 1.62, cy + r * 1.62, CHALK, 4.6))


TUBE = 'fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="2.4"' % (MINT, MINT)


def pipe(x1, x2, y, half):
    """A smooth tunnel: a shaded band with round ends, however many lie side by side."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="%d" %s/>'
            % (x1, j(y - half, 0.6), x2 - x1, 2 * half, half, TUBE))


def packet_tunnel(x1, x2, y, half, count):
    """One long tunnel, with packets in single file. Nobody outside can see them, but each one
    bulges the wall, by its own amount, and that outline is what gives the tunnel away."""
    size, pad, nose = 13, 20, 10
    xs = [x1 + pad + n * (x2 - x1 - 2 * pad) / (count - 1) for n in range(count)]
    rise = [j(half, 2.8) for _ in xs]
    waist = half - 8

    def side(sign):
        """The bulges along one wall, left to right: level at each top and at each dip."""
        pts = [(xs[0], y + sign * rise[0])]
        for n in range(1, count):
            pts += [((xs[n - 1] + xs[n]) / 2, y + sign * waist), (xs[n], y + sign * rise[n])]
        return pts

    def curve(pts):
        return "".join(" C %.1f %.1f %.1f %.1f %.1f %.1f" % ((ax + bx) / 2, ay, (ax + bx) / 2, by, bx, by)
                       for (ax, ay), (bx, by) in zip(pts, pts[1:]))

    top, bottom = side(-1), side(1)[::-1]
    d = ("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (x1, y, x1, top[0][1], x1 + nose, top[0][1], *top[0]) +
         curve(top) + " C %.1f %.1f %.1f %.1f %.1f %.1f" % (x2 - nose, top[-1][1], x2, top[-1][1], x2, y) +
         " C %.1f %.1f %.1f %.1f %.1f %.1f" % (x2, bottom[0][1], x2 - nose, bottom[0][1], *bottom[0]) +
         curve(bottom) + " C %.1f %.1f %.1f %.1f %.1f %.1f Z" % (x1 + nose, bottom[-1][1], x1, bottom[-1][1], x1, y))
    out = ['<path d="%s" stroke-linejoin="round" %s/>' % (d, TUBE)]
    for x in xs:
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2" fill="%s"/>'
                   % (j(x - size / 2, 0.8), j(y - size / 2, 0.8), size, size, CHALK))
    return "".join(out)


def stream_tunnel(x1, x2, y, wall_x, wall_w, half=10):
    """A connection's own tunnel, through a gap in the wall, with its stream in one piece inside it."""
    return ('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s"/>'
            % (wall_x - wall_w / 2 - 2, y - half, wall_w + 4, 2 * half, BOARD) +
            pipe(x1, x2, y, half) + arrow(x1 + 16, y, x2 - 8, y, CHALK, 2.8))


def cloak_lanes(xp, xf, xs, y1, y2, rack_w, rack_h, wall_w, half, packets):
    """Both lanes: one tunnel stopped at the wall, and a tunnel of its own for each connection."""
    a, b = xp + PHONE_W / 2 + 12, xf - wall_w / 2 - 3       # the device to the wall
    c, d = xf + wall_w / 2 + 10, xs - rack_w / 2 - 14       # the wall to the server
    return ([phone(xp, y1), rack(xs, y1, rack_w, rack_h), packet_tunnel(a, b, y1, half, packets),
             arrow(c, y1, d, y1, CHALK_DIM, 2.6, "9 11"), cross(xf, y1, 14, CORAL, 5.0),
             phone(xp, y2), rack(xs, y2, rack_w, rack_h)] +
            [stream_tunnel(a, d, y2 + n * 35, xf, wall_w) for n in (-1, 0, 1)])


def cloak_mode() -> None:
    T, _ = strings(CLOAK[1])
    lanes = (("diagram_off", "diagram_off_sub", "diagram_off_result", CORAL),
             ("diagram_on", "diagram_on_sub", "diagram_on_result", MINT))

    # --- left to right: one wall across both lanes, the device and the server on either side ---
    seed(31)
    W, H = 920, 516
    XP, XF, XS, WALL = 104, 530, 836, 52
    Y1, Y2 = 164, 358
    left, right = 320, 726              # the middle of what lies on either side of the wall
    parts = [filter_wall(XF, 68, 450, WALL, 26), magnifier(XF, (Y1 + Y2) / 2 - 6)]
    parts += cloak_lanes(XP, XF, XS, Y1, Y2, 92, 72, WALL, 19, 10)
    for x, key in ((XP, "diagram_device"), (XF, "diagram_filter"), (XS, "diagram_server")):
        parts.append(txt(x, 46, T(key), 19))
    for y, above, below, (key, sub, result, colour) in zip((Y1, Y2), (38, 60), (62, 72), lanes):
        parts += [txt(left, y - above, T(key), 22), txt(left, y + below, T(sub), 18, CHALK_DIM),
                  txt(right, y + below, T(result), 19, colour)]
    parts.append(txt(W / 2, H - 30, T("diagram_caption"), 20, AMBER))
    render("cloak-mode", *CLOAK, W, H, "vhCloakMode", parts)

    # --- on a phone: the same lanes, one under the other, each with its own stretch of wall -----
    seed(31)
    W, H = 560, 660
    XP, XF, XS, WALL = 62, 300, 492, 48
    Y1, Y2 = 180, 446
    parts = [filter_wall(XF, y - 60, y + 60, WALL, 20) for y in (Y1, Y2)]
    parts += cloak_lanes(XP, XF, XS, Y1, Y2, 84, 66, WALL, 19, 5)
    parts += [txt(28, 42, T("diagram_device"), 17, CHALK, "start"), txt(XF, 42, T("diagram_filter"), 17),
              txt(W - 28, 42, T("diagram_server"), 17, CHALK, "end")]
    for y, (key, sub, result, colour) in zip((Y1, Y2), lanes):
        parts += [txt(W / 2, y - 84, T(key), 22), txt(W / 2, y + 88, T(sub), 17, CHALK_DIM),
                  txt(W / 2, y + 116, T(result), 19, colour)]
    parts.append(txt(W / 2, H - 28, T("diagram_caption"), 18, AMBER))
    render("cloak-mode-tall", *CLOAK, W, H, "vhCloakModeTall", parts)


if __name__ == "__main__":
    server_two_ips()
    reverse_proxy()
    how_it_works()
    dynamic_ip_follow()
    dynamic_ip_find()
    cloak_mode()
