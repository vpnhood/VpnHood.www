#!/usr/bin/env python3
"""Generate the docs and feature pages' diagrams as translatable Liquid includes.

Writes, under `_includes/diagrams/`:

  server-two-ips.svg, server-two-ips-tall.svg    /vpnhood-server/docs/ip-blocking/
  reverse-proxy.svg, reverse-proxy-tall.svg      /vpnhood-server/docs/reverse-proxy/
  how-it-works.svg, how-it-works-tall.svg,
  how-it-works-device.svg, how-it-works-device-tall.svg,
  how-it-works-tunnel.svg, how-it-works-tunnel-tall.svg,
  how-it-works-tcp.svg, how-it-works-tcp-tall.svg,
  how-it-works-server.svg, how-it-works-server-tall.svg,
  how-it-works-key.svg, how-it-works-key-tall.svg  /self-hosted-vpn/docs/how-it-works/
  relay-route.svg, relay-route-tall.svg,
  relay-proxy.svg, relay-proxy-tall.svg,
  relay-satellite.svg, relay-satellite-tall.svg,
  relay-keys.svg, relay-keys-tall.svg,
  relay-domain.svg, relay-domain-tall.svg,
  relay-custom.svg, relay-custom-tall.svg      /self-hosted-vpn/docs/relay-server/
  cloak-traffic.svg, cloak-traffic-tall.svg,
  block-quic.svg, block-quic-tall.svg            /self-hosted-vpn/docs/vpn-detection/
  dynamic-ip-follow.svg, dynamic-ip-follow-tall.svg,
  dynamic-ip-find.svg, dynamic-ip-find-tall.svg,
  dynamic-ip-urls.svg, dynamic-ip-urls-tall.svg  /vpnhood-manager/docs/dynamic-ip/
  farm-token-key.svg, farm-token-key-tall.svg,  
  farm-token-new.svg, farm-token-new-tall.svg  /vpnhood-manager/docs/farm-token/
  policies-options.svg, policies-options-tall.svg  /vpnhood-manager/docs/policies/
  cloak-mode.svg, cloak-mode-tall.svg            /features/cloak-mode/, and
                                                 /self-hosted-vpn/docs/vpn-detection/, which
                                                 carries the same diagram_* keys

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
proxy, a hood for MANAGER, a key for access keys, a signpost for what shows the way to a
server's address, a phone for your device, and a brick wall for a firewall (DPI). A server's
addresses are ports on its edge, in the colour of the arrow that reaches them. Example
addresses and names are not copy: they come from `_data/code.yml`, the values the pages' own
text uses, so the picture and the text always agree.

Each diagram states one idea and no more:

  server-two-ips  users connect to one address and websites see another, so the address
                  websites can flag is never the one in the access keys.
  reverse-proxy   apps that find the proxy through your domain go around a blocked server
                  address.
  how-it-works    a firewall knows an ordinary VPN protocol by the ridges of its tunnel and
                  stops it; VpnHood's smooth tunnel, built like HTTPS, goes through to your
                  server and on to websites.
  how-it-works-device  one app's traffic goes into the tunnel; another app, left out by split
                  tunneling, goes straight to the internet and never reaches your server.
  how-it-works-tunnel  the tunnel cut open: TLS around WebSocket messages around the traffic.
  how-it-works-tcp  the same TCP twice: as packets your server passes on, and in Cloak Mode as
                  a tunnel per connection, each opened again by your server.
  how-it-works-server  an app connects, and a managed server calls MANAGER to check the key;
                  MANAGER never calls the server.
  how-it-works-key  the three things an access key holds.
  relay-route     straight to your server is blocked at the firewall; the relay, on the users'
                  side of it, has a way through, for whatever reason: a gate the firewall leaves open.
  relay-proxy     relay-route with a proxy in the relay's place: through the same gate, but its
                  request names your server, and anyone on the way can read it.
  relay-satellite as relay-route, straight to your server is blocked; the relay's own link takes
                  the tunnels up to a satellite and down to your server, over the firewall.
  relay-keys      as relay-route, with the key in the users' place: its server address is blocked,
                  its relay address gets through the gate; the app uses whichever answers.
  relay-domain    the key's name leads, through its DNS record, to the relay.
  relay-custom    the user types the relay's address into the app; the key stays as it is.
  cloak-traffic   over time, a server in Cloak Mode has a web server's connections, short
                  ones for browsing and a long one for a download, and not one long tunnel.
                  The first two lanes are alike and never identical, as the page says.
  dynamic-ip-follow  the server's next report shows MANAGER its new address, which goes into
                  the keys.
  dynamic-ip-find an older key's address is gone, and the name or the URL in the key leads
                  apps to the new one.
  dynamic-ip-urls MANAGER keeps a file on the web up to date, and apps that read it reach the
                  server at the new address.
  cloak-mode      nobody outside can see into a tunnel, so a firewall goes by its shape: packets
                  make one long tunnel bumpy, and with Cloak Mode each connection's own tunnel
                  is smooth, like web browsing. Both lanes read left to right on a phone too,
                  one under the other, because setting them side by side is the idea.
  block-quic      one app, in Cloak Mode, which can disguise TCP but not QUIC: its QUIC makes
                  cloak-mode's bumpy tunnel and the firewall can drop it, and with Block QUIC
                  the device stops QUIC, inside the phone, and the app's TCP goes smooth.

  farm-token-key  MANAGER builds one farm token and every key of the farm carries it, beside a
                  part of its own: only the whole key connects.
  farm-token-new  a new token reaches an app by two roads: from your server while it can connect,
                  and from the file at a farm token URL when it cannot.
  policies-options  the user's country, the location and the app decide the choices, and where
                  a trial or a rewarded ad is on offer the app asks on a page of them; a private
                  key skips the question.

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


# VpnHood's hood, the figure of the CLIENT and CONNECT logos, on a 32 grid: one path, its eyes included.
VPNHOOD_HOOD = "M16.060 1.999v0c-7.327 3.442-13.417 13.468-14.967 20.947 4.477 0 7.75 1.426 10.113 3.933l0.654-0.715c-1.751-1.801-4.052-3.271-7.086-4.735 1.631-4.058 4.118-10.201 7.281-10.558 1.238-0.14 2.563 0.607 4.005 2.71 4.513-7.505 8.799 2.406 11.286 7.848-2.976 1.613-5.272 3.087-7.049 4.913l0.576 0.648c2.33-2.481 5.595-4.045 10.154-4.045-1.839-7.386-7.488-17.307-14.967-20.947zM14.129 19.128c0 0.785-1.050 1.218-2.345 0.966s-2.345-1.091-2.345-1.876c0-0.785 1.050-1.218 2.345-0.966s2.345 1.091 2.345 1.876zM17.798 19.128c0 0.785 1.050 1.218 2.345 0.966s2.345-1.091 2.345-1.876c0-0.785-1.050-1.218-2.345-0.966s-2.345 1.091-2.345 1.876z"


def rack(cx, cy, w=104, h=84):
    """Your server: a box with two units, each with two lights and a vent. VpnHood's hood takes
    the top unit's vent, where the unit is tall enough to show it."""
    x, y = cx - w / 2, cy - h / 2
    out = [box(x, y, w, h, CHALK, 3.2)]
    pad = 11
    uh = (h - 3 * pad) / 2
    for i in range(2):
        uy = y + pad + i * (uh + pad)
        my = uy + uh / 2
        out += [box(x + pad, uy, w - 2 * pad, uh, CHALK_DIM, 2.2),
                dot(x + pad + 12, my, 3.4, CHALK_DIM), dot(x + pad + 23, my, 3.4, CHALK_DIM)]
        if i == 0 and uh >= 20:
            size = uh * .9
            out.append('<path transform="translate(%.1f %.1f) scale(%.4f)" d="%s" fill="%s"/>'
                       % (x + w - pad - 19 - size / 2, my - size / 2, size / 32, VPNHOOD_HOOD, CHALK))
        else:
            out.append(line(x + w - pad - 36, my, x + w - pad - 10, my))
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


# VpnHood! MANAGER's figure, the hood of its icon, on a 512 grid where it stands 476 tall: the
# hood, its face and its eyes, the shapes tools/make-docs-heroes.py draws too.
HOOD = "M254.1 18.63c-81.4 0-231.43 155.97-171.63 300.77 8 25.3 27.83 50.4 49.13 77.1 24.4 30.6 51.6 63.2 68.7 96.9h20.5c-18.1-39.8-48.5-75.9-74.6-108.6-27.4-34.3-48.73-65.2-48.73-87.9.1-9.1 2.23-18.1 5.53-26.3 23-61.4 114-119.7 148.5-135l3.6-2 3.9 1.3c60.9 20.9 129.3 66.7 154 135.7 4.1 11.7 5.9 18 5.6 27.3-.5 15.8-24.5 54.7-55 88.7-29.1 32.4-62.4 67.7-80 106.7h20.5c16.8-32.2 46.2-64 73.3-94.2 23.2-25.6 45.3-50 54.9-74.8 52.9-124-99.2-305.67-178.2-305.67z"
HOOD_FACE = "M254.9 154.1c-38.7 21.5-85.1 52.2-113.7 88.2 9.7 83 59 146.1 118.3 146.1 59.2 0 108.3-62.7 118.2-145.3-28.9-42.1-78-72.9-122.8-89z"
HOOD_EYES = ("M196.6 237.1h2.4c13.1.1 26.1 2.7 39.1 7.4-16.8 40.6-59 42-78.1 0 12.2-4.8 24.4-7.2 36.6-7.4z",
             "M321.5 237.1c13-.1 26 2.3 39.1 7.4-19.2 42-61.3 40.6-78.2 0 13.1-4.7 26.1-7.3 39.1-7.4z")
HOOD_W, HOOD_H = 77, 96                 # no taller than the icons beside it: any bigger, and it outweighs them


def manager_hood(cx, cy):
    """VpnHood! MANAGER: its figure in chalk lines, the eyes filled in - HOOD_W x HOOD_H."""
    s = HOOD_H / 476
    at = 'transform="translate(%.1f %.1f) scale(%.4f)"' % (cx - 256 * s, cy - 256 * s, s)
    out = ['<path %s d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (at, HOOD, CHALK, 3.0 / s),
           '<path %s d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (at, HOOD_FACE, CHALK_DIM, 2.2 / s)]
    out += ['<path %s d="%s" fill="%s"/>' % (at, eye, CHALK) for eye in HOOD_EYES]
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

    # ChalkFx is Chalk with a warp about twice as far, for Firefox only (_custom.scss switches
    # to it): Firefox moves pixels in whole steps and loses Chalk's sub-pixel warp. Keep the
    # two filters the same apart from that scale; this template is copied in
    # make-reseller-diagrams.py and make-topology-diagram.py.
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
    <filter id="{UID}ChalkFx" x="-6%" y="-6%" width="112%" height="112%">
      <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3" seed="11" result="warp"/>
      <feDisplacementMap in="SourceGraphic" in2="warp" scale="8"
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

  <g class="vh-chalk" filter="url(#{UID}Chalk)" style="--vh-chalk-fx: url(#{UID}ChalkFx)">
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
# how-it-works - an ordinary VPN protocol stops at a firewall, VpnHood's tunnel goes through
# ===========================================================================
HOW = ("self_hosted_vpn_docs_how_it_works", "vh_how_en")


def other_server(cx, cy, w, h):
    """Somebody else's VPN server: the rack, dim and without VpnHood's hood."""
    x, y = cx - w / 2, cy - h / 2
    out = [box(x, y, w, h, CHALK_DIM, 2.8)]
    pad = 11
    uh = (h - 3 * pad) / 2
    for i in range(2):
        my = y + pad + i * (uh + pad) + uh / 2
        out += [box(x + pad, y + pad + i * (uh + pad), w - 2 * pad, uh, CHALK_DIM, 2.0),
                dot(x + pad + 12, my, 3.2, CHALK_DIM), line(x + w - pad - 34, my, x + w - pad - 10, my)]
    return "".join(out)


def ridged_tunnel(x1, x2, y, colour, half=10, pitch=9, depth=7):
    """An ordinary protocol's tunnel: its walls ridged, a form of its own that a firewall knows."""
    n = 2 * max(2, round((x2 - 6 - x1) / (2 * pitch)))
    step = (x2 - 6 - x1) / n

    def wall(sign):
        d = "M %.1f %.1f" % (x1, y + sign * half)
        for k in range(1, n + 1):
            d += " L %.1f %.1f" % (x1 + k * step, y + sign * (half + (depth if k % 2 else 0)))
        return ('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round" '
                'stroke-linecap="round"/>' % (d, colour))

    return wall(-1) + wall(1) + arrow(x1 + 10, y, x2, y, CHALK)


def wall_gap(xf, wall_w, y, half=15):
    """Where a tunnel goes through the wall: the bricks stop either side of it."""
    return ('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s"/>'
            % (xf - wall_w / 2 - 2, y - half, wall_w + 4, 2 * half, BOARD))


def how_it_works() -> None:
    T, _ = strings(HOW[1])

    # --- left to right: one firewall across both lanes; only VpnHood's tunnel goes on ----------
    seed(17)
    W, H = 920, 484
    XP, XF, XS, XW, WALL = 92, 456, 662, 836, 52
    Y1, Y2 = 146, 314
    a, b = XP + PHONE_W / 2 + 12, XF - WALL / 2 - 3         # the device to the wall
    c = XF + WALL / 2 + 10                                  # the wall's far side
    mid = (a + b) / 2
    top = (XP - PHONE_W / 2 + b) / 2                        # a lane's name, above its phone and tunnel
    parts = [filter_wall(XF, 92, 396, WALL, 26), dragon(XF, 92), magnifier(XF, (Y1 + Y2) / 2 - 4),
             txt(XF + 40, 76, T("diagram_firewall"), 19, CHALK, "start")]
    # an ordinary VPN protocol: the firewall knows its form, and stops it
    parts += [phone(XP, Y1), ridged_tunnel(a, b, Y1, CHALK_DIM),
              cross(XF, Y1, 14, CORAL, 5.0), other_server(XS, Y1, 92, 70),
              arrow(c, Y1, XS - 46 - 14, Y1, CHALK_DIM, 2.6, "9 11"),
              txt(top - 28, Y1 - 62, T("diagram_other"), 22), txt(mid, Y1 + 48, T("diagram_other_sub"), 18, CHALK_DIM),
              txt(c + 2, Y1 + 66, T("diagram_other_result"), 19, CORAL, "start")]
    # VpnHood: a smooth tunnel, built like HTTPS; it goes through, to your server and on
    d = XS - 52 - 14
    parts += [phone(XP, Y2), wall_gap(XF, WALL, Y2), tunnel(a, Y2, d, Y2),
              rack(XS, Y2, 104, 84), arrow(XS + 52 + 14, Y2, XW - 42 - 14, Y2, VIOLET), globe(XW, Y2),
              txt(top - 28, Y2 - 62, T("diagram_vpnhood"), 22), txt(mid, Y2 + 48, T("diagram_tunnel_sub"), 18, CHALK_DIM),
              txt(XS, Y2 + 78, T("diagram_server"), 22), txt(XS, Y2 + 102, T("diagram_server_sub"), 16, CHALK_DIM),
              txt(XW, Y2 + 78, T("diagram_websites"), 20)]
    parts.append(txt(W / 2, H - 28, T("diagram_caption"), 20, AMBER))
    render("how-it-works", *HOW, W, H, "vhHow", parts)

    # --- on a phone: the same lanes, one under the other, each with its own stretch of wall -----
    seed(17)
    W, H = 560, 690
    XP, XF, XS, WALL = 62, 286, 476, 48
    Y1, Y2 = 176, 426
    a, b = XP + PHONE_W / 2 + 12, XF - WALL / 2 - 3
    c = XF + WALL / 2 + 10
    mid = (a + b) / 2
    parts = [filter_wall(XF, y - 60, y + 60, WALL, 20) for y in (Y1, Y2)]
    parts += [dragon(XF, Y2 - 60), txt(XF, 42, T("diagram_firewall"), 17)]
    parts += [phone(XP, Y1), ridged_tunnel(a, b, Y1, CHALK_DIM),
              cross(XF, Y1, 14, CORAL, 5.0), other_server(XS, Y1, 84, 66),
              arrow(c, Y1, XS - 42 - 14, Y1, CHALK_DIM, 2.6, "9 11"),
              txt(W / 2, Y1 - 84, T("diagram_other"), 22), txt(W / 2, Y1 + 88, T("diagram_other_sub"), 17, CHALK_DIM),
              txt(W / 2, Y1 + 116, T("diagram_other_result"), 19, CORAL)]
    d = XS - 46 - 14
    YG = Y2 + 142                                           # websites, below your server
    parts += [phone(XP, Y2), wall_gap(XF, WALL, Y2), tunnel(a, Y2, d, Y2), rack(XS, Y2, 92, 76),
              arrow(XS, Y2 + 38 + 14, XS, YG - 32 - 14, VIOLET), globe(XS, YG, 32),
              txt(28, Y2 - 84, T("diagram_vpnhood"), 22, CHALK, "start"),
              txt(W - 28, Y2 - 70, T("diagram_server"), 19, CHALK, "end"),
              txt(W - 28, Y2 - 50, T("diagram_server_sub"), 14, CHALK_DIM, "end"),
              txt(mid + 24, Y2 + 88, T("diagram_tunnel_sub"), 17, CHALK_DIM),
              txt(XS - 48, YG + 7, T("diagram_websites"), 19, CHALK, "end")]
    parts.append(txt(W / 2, H - 28, T("diagram_caption"), 16, AMBER))
    render("how-it-works-tall", *HOW, W, H, "vhHowTall", parts)


# ===========================================================================
# how-it-works-device - what the app takes into the tunnel, and what split tunneling leaves out
# ===========================================================================
def other_app(cx, cy, s=52):
    """Another app, one the user leaves out: a plain box with a ring."""
    return box(cx - s / 2, cy - s / 2, s, s, CHALK_DIM, 2.8) + ring(cx, cy, 9, CHALK_DIM, 2.4)


def how_device() -> None:
    T, _ = strings(HOW[1])

    # --- left to right: one app's traffic into the tunnel, another's straight out -----------------
    seed(61)
    W, H = 920, 470
    PX0, PX1, PY0, PY1 = 48, 218, 66, 376                   # the device, tall enough for two apps
    XA, Y1, Y2 = 133, 142, 300
    XS, XW = 600, 836
    parts = [box(PX0, PY0, PX1 - PX0, PY1 - PY0, CHALK, 3.2), line(XA - 9, PY0 + 12, XA + 9, PY0 + 12),
             line(XA - 13, PY1 - 12, XA + 13, PY1 - 12), video_app(XA, Y1), other_app(XA, Y2)]
    a, d = PX1 + 10, XS - 52 - 14
    parts += [arrow(XA + 34, Y1, PX1 - 6, Y1, MINT, 3.0), tunnel(a, Y1, d, Y1), rack(XS, Y1, 104, 84),
              arrow(XS + 52 + 14, Y1, XW - 42 - 14, Y1, VIOLET), globe(XW, Y1),
              elbow([(XA + 34, Y2), (XW, Y2), (XW, Y1 + 42 + 14)], VIOLET)]
    m1, m2 = (a + d) / 2, (a + XW) / 2
    parts += [txt(m1, Y1 - 26, T("diagram_split_in"), 20, MINT), txt(m1, Y1 + 40, T("diagram_split_in_sub"), 17, CHALK_DIM),
              txt(m2, Y2 - 18, T("diagram_split_out"), 20), txt(m2, Y2 + 32, T("diagram_split_out_sub"), 17, CHALK_DIM),
              txt(XS, Y1 + 78, T("diagram_server"), 22), txt(XS, Y1 + 102, T("diagram_server_sub"), 16, CHALK_DIM),
              txt(XW, Y1 - 60, T("diagram_websites"), 20), txt(XA, PY1 + 32, T("diagram_device"), 20)]
    parts.append(txt(W / 2, H - 26, T("diagram_split_caption"), 20, AMBER))
    render("how-it-works-device", *HOW, W, H, "vhHowDevice", parts, key="diagram_split")

    # --- top to bottom: the device on its side, an app's lane down from each end --------------------
    seed(61)
    W, H = 560, 806
    X1, X2, YA = 130, 470, 128                              # wide apart: the label between their lanes runs long
    YS, XG, YG = 398, 300, 664
    parts = [box(40, 70, 480, 116, CHALK, 3.2), line(52, YA - 11, 52, YA + 11), video_app(X1, YA), other_app(X2, YA),
             txt(W / 2, 44, T("diagram_device"), 19),
             tunnel(X1, 198, X1, YS - 42 - 14), rack(X1, YS, 104, 84),
             elbow([(X1, YS + 42 + 14), (X1, YG), (XG - 38 - 14, YG)], VIOLET), globe(XG, YG, 38),
             elbow([(X2, 198), (X2, YG), (XG + 38 + 14, YG)], VIOLET)]
    parts += [txt(X1 + 28, 262, T("diagram_split_in"), 19, MINT, "start"),
              txt(X1 + 28, 286, T("diagram_split_in_sub"), 15, CHALK_DIM, "start"),
              txt(X1 + 66, YS - 2, T("diagram_server"), 20, CHALK, "start"),
              txt(X1 + 66, YS + 22, T("diagram_server_sub"), 14, CHALK_DIM, "start"),
              txt((X1 + X2) / 2, 520, T("diagram_split_out"), 16),
              txt((X1 + X2) / 2, 544, T("diagram_split_out_sub"), 15, CHALK_DIM),
              txt(XG, YG + 66, T("diagram_websites"), 20)]
    parts.append(txt(W / 2, H - 28, T("diagram_split_caption"), 16, AMBER))
    render("how-it-works-device-tall", *HOW, W, H, "vhHowDeviceTall", parts, key="diagram_split")


# ===========================================================================
# how-it-works-tunnel - what the tunnel is made of: TLS around WebSocket messages around the traffic
# ===========================================================================
def band(x, y, w, h, colour, opacity="0.10"):
    """One layer of the tunnel: a shaded band with round ends, the next layer inside it."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s" fill-opacity="%s" '
            'stroke="%s" stroke-width="2.6"/>' % (j(x, 0.6), j(y, 0.6), w, h, min(w, h) / 2, colour, opacity, colour))


def leader(x1, y1, x2, y2, colour):
    """From a label to the layer it names, a dot where it lands."""
    return line(x1, y1, x2, y2, colour, 2.0) + dot(x2, y2, 3.6, colour)


def how_tunnel() -> None:
    T, _ = strings(HOW[1])

    # --- left to right: the app, the tunnel cut open, your server ----------------------------------
    seed(67)
    W, H = 920, 346
    XP, XS, Y = 124, 820, 172                               # the phone in from the edge: its label runs long
    x1, x2 = XP + PHONE_W / 2 + 14, XS - 52 - 14
    parts = [phone(XP, Y), rack(XS, Y, 104, 84),
             band(x1, Y - 44, x2 - x1, 88, MINT, "0.07"), band(x1 + 40, Y - 24, x2 - x1 - 80, 48, VIOLET, "0.12"),
             arrow(x1 + 62, Y, x2 - 60, Y, CHALK, 3.0)]
    parts += [txt(300, Y - 72, T("diagram_layers_tls"), 19, MINT), leader(300, Y - 64, 300, Y - 44, MINT),
              txt(612, Y - 72, T("diagram_layers_ws"), 19, VIOLET), leader(612, Y - 64, 612, Y - 24, VIOLET),
              txt((x1 + x2) / 2, Y + 84, T("diagram_layers_traffic"), 19), leader((x1 + x2) / 2, Y + 64, (x1 + x2) / 2, Y + 2, CHALK),
              txt(XP, Y + 84, T("diagram_app"), 20),
              txt(XS, Y + 80, T("diagram_server"), 22), txt(XS, Y + 104, T("diagram_server_sub"), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 24, T("diagram_layers_caption"), 20, AMBER))
    render("how-it-works-tunnel", *HOW, W, H, "vhHowTunnel", parts, key="diagram_layers")

    # --- top to bottom: the tunnel stands between them, its layers named beside it -----------------
    seed(67)
    W, H = 560, 620
    X, YP, YS, TX = 110, 84, 508, 198
    y1, y2 = YP + 46 + 14, YS - 42 - 14
    parts = [phone(X, YP), rack(X, YS, 104, 84),
             band(X - 44, y1, 88, y2 - y1, MINT, "0.07"), band(X - 24, y1 + 34, 48, y2 - y1 - 68, VIOLET, "0.12"),
             arrow(X, y1 + 52, X, y2 - 50, CHALK, 3.0)]
    parts += [txt(TX, 222, T("diagram_layers_tls"), 17, MINT, "start"), leader(TX - 8, 216, X + 44, 216, MINT),
              txt(TX, 302, T("diagram_layers_ws"), 17, VIOLET, "start"), leader(TX - 8, 296, X + 24, 296, VIOLET),
              txt(TX, 382, T("diagram_layers_traffic"), 17, CHALK, "start"), leader(TX - 8, 376, X + 2, 376, CHALK),
              txt(X + 52, YP + 6, T("diagram_app"), 20, CHALK, "start"),
              txt(X + 70, YS - 2, T("diagram_server"), 21, CHALK, "start"),
              txt(X + 70, YS + 22, T("diagram_server_sub"), 14, CHALK_DIM, "start")]
    parts.append(txt(W / 2, H - 26, T("diagram_layers_caption"), 17, AMBER))
    render("how-it-works-tunnel-tall", *HOW, W, H, "vhHowTunnelTall", parts, key="diagram_layers")


# ===========================================================================
# how-it-works-tcp - TCP as packets your server passes on, or one request per connection
# ===========================================================================
def packets_on(x1, x2, y, count):
    """Packets going on from your server: the arrow out, with the same packets on it."""
    out = [arrow(x1, y, x2, y, VIOLET)]
    span = x2 - 30 - x1
    for n in range(count):
        x = x1 + (n + 0.5) * span / count
        out.append('<rect x="%.1f" y="%.1f" width="12" height="12" rx="2" fill="%s"/>' % (j(x - 6, 0.8), j(y - 6, 0.8), CHALK))
    return "".join(out)


def tcp_lanes(xp, xs, xw, y1, y2, rack_w, rack_h, globe_r, packets, on):
    """The same traffic twice: packets in one tunnel, passed on as they are; and a tunnel of its own
    for each connection, with a connection of the server's own on the far side."""
    a, d = xp + PHONE_W / 2 + 12, xs - rack_w / 2 - 14
    e, f = xs + rack_w / 2 + 14, xw - globe_r - 14
    out = [phone(xp, y1), packet_tunnel(a, d, y1, 19, packets), rack(xs, y1, rack_w, rack_h),
           packets_on(e, f, y1, on), globe(xw, y1, globe_r),
           phone(xp, y2), rack(xs, y2, rack_w, rack_h), globe(xw, y2, globe_r)]
    for dy, tip in ((-17, -11), (17, 11)):
        out += [pipe(a, d, y2 + dy, 10), arrow(a + 16, y2 + dy, d - 8, y2 + dy, CHALK, 2.8),
                arrow(e, y2 + dy, f, y2 + tip, VIOLET, 2.8)]
    return out


def how_tcp() -> None:
    T, _ = strings(HOW[1])
    lanes = (("diagram_tcp_packets", "diagram_tcp_packets_sub", "diagram_tcp_packets_out"),
             ("diagram_tcp_requests", "diagram_tcp_requests_sub", "diagram_tcp_requests_out"))

    # --- left to right: a device, your server and websites, twice -----------------------------------
    seed(71)
    W, H = 920, 500
    XP, XS, XW = 84, 540, 830
    Y1, Y2 = 160, 340
    left = (XP + PHONE_W / 2 + 12 + XS - 66) / 2
    right = (XS + XW) / 2 + 14
    parts = tcp_lanes(XP, XS, XW, Y1, Y2, 104, 84, 42, 9, 3)
    parts += [txt(28, 46, T("diagram_device"), 19, CHALK, "start"), txt(XS, 46, T("diagram_server"), 19),
              txt(W - 28, 46, T("diagram_websites"), 19, CHALK, "end")]
    for y, (name, sub, out) in zip((Y1, Y2), lanes):
        parts += [txt(left, y - 48, T(name), 22), txt(left, y + 56, T(sub), 17, CHALK_DIM),
                  txt(right, y + 68, T(out), 17, VIOLET)]
    parts.append(txt(W / 2, H - 28, T("diagram_tcp_caption"), 20, AMBER))
    render("how-it-works-tcp", *HOW, W, H, "vhHowTcp", parts, key="diagram_tcp")

    # --- on a phone: the same lanes, one under the other ---------------------------------------------
    seed(71)
    W, H = 560, 636
    XP, XS, XW = 58, 296, 494
    Y1, Y2 = 176, 430
    parts = tcp_lanes(XP, XS, XW, Y1, Y2, 88, 76, 30, 4, 2)
    parts += [txt(28, 42, T("diagram_device"), 17, CHALK, "start"), txt(XS, 42, T("diagram_server"), 17),
              txt(W - 28, 42, T("diagram_websites"), 17, CHALK, "end")]
    for y, (name, sub, out) in zip((Y1, Y2), lanes):
        parts += [txt(W / 2, y - 78, T(name), 22), txt(W / 2, y + 78, T(sub), 16, CHALK_DIM),
                  txt(W / 2, y + 104, T(out), 17, VIOLET)]
    parts.append(txt(W / 2, H - 26, T("diagram_tcp_caption"), 16, AMBER))
    render("how-it-works-tcp-tall", *HOW, W, H, "vhHowTcpTall", parts, key="diagram_tcp")


# ===========================================================================
# how-it-works-server - a managed server calls MANAGER; nothing calls into your server but the apps
# ===========================================================================
def how_server() -> None:
    T, _ = strings(HOW[1])

    # --- left to right: an app connects, and your server asks MANAGER ------------------------------
    seed(73)
    W, H = 920, 330
    XP, XS, XM, Y = 124, 420, 800, 124                      # the phone in from the edge: its label runs long
    a, b = XP + PHONE_W / 2 + 12, XS - 52 - 14
    c, d = XS + 52 + 14, XM - 38 - 14
    parts = [phone(XP, Y), tunnel(a, Y, b, Y), rack(XS, Y, 104, 84), arrow(c, Y, d, Y, VIOLET), manager_hood(XM, Y),
             txt((a + b) / 2, Y - 26, T("diagram_manager_connect"), 19, MINT),
             txt((c + d) / 2, Y - 18, T("diagram_manager_check"), 19, VIOLET),
             txt((c + d) / 2, Y + 34, T("diagram_manager_check_sub"), 17, CHALK_DIM),
             txt(XP, Y + 84, T("diagram_app"), 20),
             txt(XS, Y + 84, T("diagram_server"), 22), txt(XS, Y + 108, T("diagram_server_sub"), 16, CHALK_DIM),
             txt(XM, Y + 84, T("diagram_manager_node"), 20)]
    parts.append(txt(W / 2, H - 26, T("diagram_manager_caption"), 20, AMBER))
    render("how-it-works-server", *HOW, W, H, "vhHowServer", parts, key="diagram_manager")

    # --- top to bottom ---------------------------------------------------------------------------------
    seed(73)
    W, H = 560, 650
    X, TX, YP, YS, YM = 110, 190, 84, 306, 528
    a, b = YP + 46 + 12, YS - 42 - 14
    c, d = YS + 42 + 14, YM - 48 - 14
    parts = [phone(X, YP), tunnel(X, a, X, b), rack(X, YS, 104, 84), arrow(X, c, X, d, VIOLET), manager_hood(X, YM),
             txt(X + 26, (a + b) / 2 + 6, T("diagram_manager_connect"), 18, MINT, "start"),
             txt(X + 26, (c + d) / 2 - 6, T("diagram_manager_check"), 18, VIOLET, "start"),
             txt(X + 26, (c + d) / 2 + 18, T("diagram_manager_check_sub"), 15, CHALK_DIM, "start"),
             txt(X + 52, YP + 6, T("diagram_app"), 20, CHALK, "start"),
             txt(TX, YS - 2, T("diagram_server"), 21, CHALK, "start"),
             txt(TX, YS + 22, T("diagram_server_sub"), 14, CHALK_DIM, "start"),
             txt(TX - 14, YM + 8, T("diagram_manager_node"), 20, CHALK, "start")]
    parts.append(txt(W / 2, H - 26, T("diagram_manager_caption"), 16, AMBER))
    render("how-it-works-server-tall", *HOW, W, H, "vhHowServerTall", parts, key="diagram_manager")


# ===========================================================================
# how-it-works-key - what an access key holds
# ===========================================================================
KEY_ROWS = (("diagram_key_where", "diagram_key_where_sub"), ("diagram_key_trust", "diagram_key_trust_sub"),
            ("diagram_key_secret", None))


def how_key() -> None:
    T, _ = strings(HOW[1])

    # --- left to right: the key, and a branch to each thing it holds --------------------------------
    seed(79)
    W, H = 920, 364
    XK, YK, XB, XT = 130, 176, 268, 322
    ys = (88, 176, 264)
    parts = [access_key(XK, YK), txt(XK, YK + 72, T("diagram_key_name"), 22),
             elbow([(XK + 76, YK), (XB, YK), (XB, ys[0]), (XT, ys[0])]), arrow(XK + 76, YK, XT, YK),
             elbow([(XB, YK), (XB, ys[2]), (XT, ys[2])])]
    for y, (name, sub) in zip(ys, KEY_ROWS):
        parts.append(txt(XT + 20, y + (-4 if sub else 7), T(name), 21, CHALK, "start"))
        if sub:
            parts.append(txt(XT + 20, y + 22, T(sub), 16, CHALK_DIM, "start"))
    parts.append(txt(W / 2, H - 26, T("diagram_key_caption"), 20, AMBER))
    render("how-it-works-key", *HOW, W, H, "vhHowKey", parts, key="diagram_key")

    # --- top to bottom: the key above, what it holds in a list under it ------------------------------
    seed(79)
    W, H = 560, 500
    XK, YK, XB, XT = 120, 80, 82, 128
    ys = (196, 290, 384)
    parts = [access_key(XK, YK), txt(XK + 86, YK + 8, T("diagram_key_name"), 21, CHALK, "start")]
    for y0, y in zip((YK + 34,) + ys, ys):
        parts.append(elbow([(XB, y0), (XB, y), (XT, y)]))
    for y, (name, sub) in zip(ys, KEY_ROWS):
        parts.append(txt(XT + 16, y + (-4 if sub else 7), T(name), 19, CHALK, "start"))
        if sub:
            parts.append(txt(XT + 16, y + 20, T(sub), 15, CHALK_DIM, "start"))
    parts.append(txt(W / 2, H - 26, T("diagram_key_caption"), 17, AMBER))
    render("how-it-works-key-tall", *HOW, W, H, "vhHowKeyTall", parts, key="diagram_key")


# ===========================================================================
# relay-route, -proxy, -satellite, -keys, -domain, -custom - a relay in front of your server
# ===========================================================================
RELAY = ("self_hosted_vpn_docs_relay_server", "vh_relay_en")
RELAY_W, RELAY_H = 84, 68               # the relay: a smaller rack than your server's


def tunnel(x1, y1, x2, y2, half=11):
    """A tunnel leg: the double mint line of how-it-works around a chalk arrow, either way round."""
    if y1 == y2:
        return (line(x1, y1 - half, x2 - 6, y2 - half, MINT, 2.0) + line(x1, y1 + half, x2 - 6, y2 + half, MINT, 2.0) +
                arrow(x1 + 10, y1, x2, y2, CHALK))
    return (line(x1 - half, y1, x2 - half, y2 - 6, MINT, 2.0) + line(x1 + half, y1, x2 + half, y2 - 6, MINT, 2.0) +
            arrow(x1, y1 + 10, x2, y2, CHALK))


def satellite(cx, cy):
    """A satellite: its body, a solar panel on either side, and its antenna."""
    out = [box(cx - 17, cy - 13, 34, 26, CHALK, 3.0)]
    for side in (-1, 1):
        x0 = cx + side * 21 if side > 0 else cx - 21 - 44
        out += [line(cx + side * 17, cy, cx + side * 21, cy, CHALK, 2.6), box(x0, cy - 10, 44, 20, CHALK_DIM, 2.4),
                line(x0 + 22, cy - 10, x0 + 22, cy + 10, CHALK_DIM, 1.6)]
    out += [line(cx, cy + 13, cx, cy + 24, CHALK, 2.4), dot(cx, cy + 27, 3.5, CHALK)]
    return "".join(out)


def dish(cx, cy):
    """A satellite dish on its stand, its bowl turned up to the right."""
    bowl = ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="3.2" '
            'stroke-linecap="round"/>' % (j(cx - 26), j(cy - 2), j(cx - 12), j(cy + 26), j(cx + 22), j(cy - 16), CHALK))
    return (bowl + line(cx - 6, cy + 6, cx + 6, cy - 6, CHALK_DIM, 2.4) + dot(cx + 8, cy - 8, 3.5, CHALK) +
            line(cx - 4, cy + 10, cx - 4, cy + 30, CHALK, 3.0) + line(cx - 16, cy + 30, cx + 8, cy + 30, CHALK, 3.0))


def filter_wall_h(cy, x0, x1, h, course):
    """A network filter lying across a tall board: a row of bricks, two courses high."""
    y0, y1 = cy - h / 2, cy + h / 2
    out = [box(x0, y0, x1 - x0, h, CHALK_DIM, 2.8), line(x0, cy, x1, cy, CHALK_DIM, 1.8)]
    n = round((x1 - x0) / course)
    step = (x1 - x0) / n
    for k in range(1, n):
        x = x0 + k * step
        out.append(line(x, y0, x, cy, CHALK_DIM, 1.8))
        out.append(line(x - step / 2, cy, x - step / 2, y1, CHALK_DIM, 1.8))
    return "".join(out)


def open_gate(hinges, ends):
    """A gate left open in a filter's gap: each leaf swung from its hinge back toward the relay."""
    return "".join(line(hx, hy, ex, ey, MINT, 3.4) + dot(hx, hy, 3.4, MINT)
                   for (hx, hy), (ex, ey) in zip(hinges, ends))


def dragon(cx, cy, s=0.95):
    """A small dragon keeping the firewall: lying on its top at (cx, cy), facing the users, its wing
    up, spikes down its back, its tail curled down the far side and fire before its open jaws."""
    sw = 2.8 / s
    chalk = 'fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round" stroke-linejoin="round"' % (CHALK, sw)
    solid = 'fill="%s" stroke="%s" stroke-width="%.2f" stroke-linejoin="round"' % (BOARD, CHALK, sw)
    shapes = [
        # fire
        '<path d="M -58 -33 C -70 -35 -80 -29 -86 -17 C -78 -21 -74 -19 -72 -13 C -70 -21 -64 -21 -62 -15 '
        'C -62 -23 -60 -29 -58 -33 Z" fill="%s" fill-opacity=".4" stroke="%s" stroke-width="%.2f" '
        'stroke-linejoin="round"/>' % (CORAL, CORAL, sw),
        # tail, down the far side of the wall, with its spade
        '<path d="M 24 -4 C 40 -2 44 12 38 24 C 34 32 40 42 50 40" %s/>' % chalk,
        '<path d="M 50 40 L 60 32 L 58 46 Z" %s/>' % solid,
        # wing, with its ribs
        '<path d="M 2 -20 L -4 -62 C 4 -56 10 -54 16 -57 C 18 -50 22 -46 30 -44 C 26 -34 20 -26 14 -20 Z" %s/>' % solid,
        '<path d="M -4 -62 L 6 -24 M 16 -57 L 10 -23" %s/>' % chalk,
        # body, lying along the wall's top, and its legs over the edge
        '<path d="M -22 -10 C -12 -26 16 -26 28 -8 C 30 -2 26 0 20 0 L -16 0 C -22 0 -24 -4 -22 -10 Z" %s/>' % solid,
        '<path d="M -13 -1 L -17 9 M 17 -1 L 21 9" %s/>' % chalk,
        # spikes down the back
        '<path d="M -14 -16 L -12 -24 L -7 -20 M 15 -20 L 21 -24 L 22 -15" %s/>' % chalk,
        # neck and head, the jaws open
        '<path d="M -21 -8 C -28 -16 -32 -24 -34 -32 M -14 -18 C -20 -24 -24 -30 -26 -36" %s/>' % chalk,
        '<path d="M -26 -36 C -32 -46 -44 -46 -60 -41 L -58 -36 L -40 -35 L -56 -30 L -54 -27 '
        'C -44 -27 -36 -29 -34 -32 Z" %s/>' % solid,
        '<path d="M -30 -43 L -24 -54 M -35 -45 L -33 -56" %s/>' % chalk,
        '<circle cx="-41" cy="-40" r="2.4" fill="%s"/>' % CORAL]
    return '<g transform="translate(%.1f %.1f) scale(%.2f)">%s</g>' % (cx, cy, s, "".join(shapes))


def gated_wall(cx, y0, y1, w, course, gaps, half, leaf):
    """A filter standing up a wide board with a gate open at each height in `gaps`."""
    out, top, face = [], y0, cx - w / 2
    for g in gaps:
        out.append(filter_wall(cx, top, g - half, w, course))
        out.append(open_gate([(face, g - half), (face, g + half)],
                             [(face - 0.85 * leaf, g - half + leaf / 2), (face - 0.85 * leaf, g + half - leaf / 2)]))
        top = g + half
    out.append(filter_wall(cx, top, y1, w, course))
    return "".join(out)


def relay_road(proxy: bool) -> None:
    """The relay-route board, and with `proxy` the same board with a SOCKS or HTTP proxy in the
    relay's place: the same gate lets it through, but its first leg names your server, so a
    magnifier on that leg reads the server's address."""
    T, CODE = strings(RELAY[1])
    node = T("diagram_proxy_node") if proxy else T("diagram_relay")
    caption = T("diagram_proxy_caption") if proxy else T("diagram_caption")
    name, uid, key = ("relay-proxy", "vhRelayProxy", "diagram_proxy") if proxy else ("relay-route", "vhRelay", "diagram")

    # --- left to right: straight to your server is blocked at the firewall; the relay, on the
    #     users' side of it, has a way through: a gate the firewall leaves open, for whatever reason
    seed(41)
    W, H = 920, 540
    XU, YU, XS, YS = 120, 250, 840, 250
    XF, XR = 600, 400
    Y1, Y2 = 120, 380
    rl, rr = XR - RELAY_W / 2, XR + RELAY_W / 2
    parts = [people(XU, YU), rack(XS, YS, RACK_W, RACK_H), rack(XR, Y2, RELAY_W, RELAY_H)]
    # the dragon keeps the wall's top, so the wall starts lower and its name stands beside it
    parts += [gated_wall(XF, 100, 450, 52, 26, [Y2], 20, 20), dragon(XF, 100),
              txt(XF + 40, 84, T("diagram_firewall"), 19, CHALK, "start")]
    # straight to your server: stopped at the firewall
    m1 = (XU + XF - 52) / 2
    parts += [elbow([(XU, YU - 48), (XU, Y1), (XF - 52, Y1)], CORAL), cross(XF - 38, Y1),
              txt(m1, Y1 - 18, T("diagram_direct"), 20), txt(m1, Y1 + 34, T("diagram_blocked"), 18, CORAL)]
    # through the relay or the proxy: to it, then through the gate on to your server
    m2 = (XU + rl - 14) / 2 + 14
    m3 = (XF + 26 + XS) / 2
    parts.append(elbow([(XU, YU + 48), (XU, Y2), (rl - 14, Y2)]))
    if proxy:
        parts += [magnifier(m2 - 16, Y2), txt(m2 - 16, Y2 - 30, T("diagram_proxy_read"), 20, CORAL),
                  txt(m2 - 16, Y2 + 40, CODE("ip_connection_example"), 18, CORAL)]
    else:
        parts += [txt(m2, Y2 - 18, T("diagram_to_relay"), 20, MINT), txt(m2, Y2 + 34, CODE("ip_relay_example"), 18)]
    parts += [elbow([(rr + 14, Y2), (XS, Y2), (XS, YS + RACK_H / 2 + 14)]),
              txt(m3, Y2 - 18, T("diagram_on"), 20, MINT), txt(m3, Y2 + 34, CODE("ip_connection_example"), 18),
              port(rl, Y2, MINT), port(rr, Y2, MINT), port(XS, YS + RACK_H / 2, MINT)]
    parts += [txt(XU + 64, YU - 4, T("diagram_users"), 22, CHALK, "start"),
              txt(XU + 64, YU + 20, T("diagram_users_sub"), 15, CHALK_DIM, "start"),
              txt(XS - 70, YS - 4, T("diagram_server"), 22, CHALK, "end"),
              txt(XS - 70, YS + 20, T("diagram_server_sub"), 15, CHALK_DIM, "end"),
              txt(XR, Y2 + 64, node, 22), txt(XR, Y2 + 88, T("diagram_relay_sub"), 15, CHALK_DIM)]
    parts.append(txt(W / 2, H - 28, caption, 19, AMBER))
    render(name, *RELAY, W, H, uid, parts, key=key)

    # --- top to bottom: the firewall lies across the board, the relay above it --------------------
    seed(41)
    W, H = 560, 820
    XU, YU, XR, YR, XS, YS, YF = 280, 90, 440, 310, 440, 650, 470
    parts = [filter_wall_h(YF, 30, XR - 20, 44, 40), filter_wall_h(YF, XR + 20, 530, 44, 40),
             open_gate([(XR - 20, YF - 22), (XR + 20, YF - 22)], [(XR - 10, YF - 39), (XR + 10, YF - 39)]),
             dragon(362, YF - 22),
             txt(36, YF + 52, T("diagram_firewall"), 17, CHALK, "start"),
             people(XU, YU), rack(XR, YR, RELAY_W, RELAY_H), rack(XS, YS, RACK_W, RACK_H)]
    parts += [elbow([(XU - 58, YU), (90, YU), (90, YF - 48)], CORAL), cross(90, YF - 36),
              txt(110, 392, T("diagram_direct"), 18, CHALK, "start"), txt(110, 418, T("diagram_blocked"), 17, CORAL, "start")]
    parts.append(elbow([(XU + 58, YU), (XR, YU), (XR, YR - RELAY_H / 2 - 14)]))
    if proxy:
        parts += [magnifier(XR, 226, 16), txt(XR - 26, 222, T("diagram_proxy_read"), 18, CORAL, "end"),
                  txt(XR - 26, 246, CODE("ip_connection_example"), 17, CORAL, "end")]
    else:
        parts += [txt(XR - 14, 238, T("diagram_to_relay"), 18, MINT, "end"),
                  txt(XR - 14, 262, CODE("ip_relay_example"), 17, CHALK, "end")]
    parts += [arrow(XR, YR + RELAY_H / 2 + 14, XS, YS - RACK_H / 2 - 14),
              txt(XR - 14, 560, T("diagram_on"), 18, MINT, "end"), txt(XR - 14, 584, CODE("ip_connection_example"), 17, CHALK, "end"),
              port(XR, YR - RELAY_H / 2, MINT), port(XR, YR + RELAY_H / 2, MINT), port(XS, YS - RACK_H / 2, MINT)]
    parts += [txt(XU, YU + 70, T("diagram_users"), 21), txt(XU, YU + 94, T("diagram_users_sub"), 14, CHALK_DIM),
              txt(XR - 60, YR - 2, node, 21, CHALK, "end"),
              txt(XR - 60, YR + 22, T("diagram_relay_sub"), 13, CHALK_DIM, "end"),
              txt(XS, YS + 72, T("diagram_server"), 21), txt(XS, YS + 96, T("diagram_server_sub"), 14, CHALK_DIM)]
    parts.append(txt(W / 2, H - 28, caption, 16, AMBER))
    render(name + "-tall", *RELAY, W, H, uid + "Tall", parts, key=key)


def relay_route() -> None:
    relay_road(proxy=False)


def relay_proxy() -> None:
    relay_road(proxy=True)


def relay_satellite() -> None:
    T, _ = strings(RELAY[1])

    # --- left to right: as relay-route, straight to your server is blocked at the firewall; the
    #     relay's dish beams up to the satellite, over the wall, and down to your server ------------
    seed(47)
    W, H = 920, 620
    XU, YU, XR, Y1, Y2 = 120, 330, 430, 240, 450
    XF, XA, YA, XS, YS = 600, 600, 84, 840, 330
    rl = XR - RELAY_W / 2
    parts = [filter_wall(XF, 190, 500, 52, 26), dragon(XF, 190), txt(XF, 534, T("diagram_firewall"), 19),
             people(XU, YU), rack(XR, Y1, RELAY_W, RELAY_H), dish(XR + 20, Y1 - 70), satellite(XA, YA),
             rack(XS, YS, RACK_W, RACK_H)]
    # the users reach the relay over the local network
    parts += [elbow([(XU, YU - 48), (XU, Y1), (rl - 14, Y1)]), port(rl, Y1, MINT),
              txt((XU + rl - 14) / 2 + 14, Y1 - 18, T("diagram_sat_local"), 20, MINT)]
    # straight to your server: stopped at the firewall
    m1 = (XU + XF - 52) / 2
    parts += [elbow([(XU, YU + 48), (XU, Y2), (XF - 52, Y2)], CORAL), cross(XF - 38, Y2),
              txt(m1, Y2 - 18, T("diagram_direct"), 20), txt(m1, Y2 + 34, T("diagram_blocked"), 18, CORAL)]
    # the satellite link, over the wall
    parts += [arrow(XR + 48, Y1 - 94, XA - 74, YA + 14, MINT, 3.0, "10 9"),
              arrow(XA + 70, YA + 18, XS - 14, YS - RACK_H / 2 - 16, MINT, 3.0, "10 9"),
              txt(XA + 92, YA + 6, T("diagram_sat_link"), 20, MINT, "start")]
    parts += [txt(XU + 64, YU - 4, T("diagram_users"), 22, CHALK, "start"),
              txt(XU + 64, YU + 20, T("diagram_users_sub"), 15, CHALK_DIM, "start"),
              txt(XR, Y1 + 64, T("diagram_relay"), 22), txt(XR, Y1 + 88, T("diagram_sat_relay_sub"), 15, CHALK_DIM),
              txt(XS - 70, YS - 4, T("diagram_server"), 22, CHALK, "end"),
              txt(XS - 70, YS + 20, T("diagram_server_sub"), 15, CHALK_DIM, "end")]
    parts.append(txt(W / 2, H - 28, T("diagram_sat_caption"), 19, AMBER))
    render("relay-satellite", *RELAY, W, H, "vhRelaySat", parts, key="diagram_sat")

    # --- top to bottom: the firewall lies across the left, under the users and the relay; the
    #     straight road stops at it, and the satellite link goes past its end ---------------------
    seed(47)
    W, H = 560, 820
    X, YU, YR, YF = 170, 84, 250, 480
    XA, YA, XS, YS = 460, 300, 460, 660
    rt = YR - RELAY_H / 2
    parts = [filter_wall_h(YF, 24, 360, 44, 40), dragon(320, YF - 22),
             txt(30, YF + 52, T("diagram_firewall"), 17, CHALK, "start"),
             people(X, YU), rack(X, YR, RELAY_W, RELAY_H), dish(X + 88, YR - 10), satellite(XA, YA),
             rack(XS, YS, RACK_W, RACK_H)]
    parts += [arrow(X, YU + 44, X, rt - 14), port(X, rt, MINT),
              txt(X + 24, (YU + 44 + rt - 14) / 2 + 6, T("diagram_sat_local"), 18, MINT, "start")]
    parts += [elbow([(X - 58, YU), (50, YU), (50, YF - 48)], CORAL), cross(50, YF - 36),
              txt(70, 404, T("diagram_direct"), 18, CHALK, "start"), txt(70, 428, T("diagram_blocked"), 17, CORAL, "start")]
    parts += [arrow(X + 114, YR - 30, XA - 72, YA, MINT, 3.0, "10 9"),
              arrow(XA, YA + 44, XS, YS - RACK_H / 2 - 16, MINT, 3.0, "10 9"),
              txt(XA, YA - 40, T("diagram_sat_link"), 18, MINT)]
    parts += [txt(X + 64, YU - 4, T("diagram_users"), 21, CHALK, "start"),
              txt(X, YR + 66, T("diagram_relay"), 21), txt(X, YR + 90, T("diagram_sat_relay_sub"), 14, CHALK_DIM),
              txt(XS, YS + 72, T("diagram_server"), 21)]
    parts.append(txt(W / 2, H - 28, T("diagram_sat_caption"), 16, AMBER))
    render("relay-satellite-tall", *RELAY, W, H, "vhRelaySatTall", parts, key="diagram_sat")


def relay_keys() -> None:
    T, CODE = strings(RELAY[1])

    # --- left to right: as relay-route, with the key in the users' place: of its two addresses,
    #     your server's is blocked at the firewall, and the relay's gets through the gate ----------
    seed(51)
    W, H = 920, 520
    XK, YK, XB = 110, 250, 204
    XR, XF, XS, YS = 460, 600, 840, 250
    Y1, Y2 = 120, 380
    rl, rr = XR - RELAY_W / 2, XR + RELAY_W / 2
    parts = [gated_wall(XF, 100, 450, 52, 26, [Y2], 20, 20), dragon(XF, 100),
             txt(XF + 40, 84, T("diagram_firewall"), 19, CHALK, "start"),
             access_key(XK, YK), txt(XK, YK + 70, T("diagram_keys_key"), 22),
             rack(XR, Y2, RELAY_W, RELAY_H), rack(XS, YS, RACK_W, RACK_H)]
    m1 = (XB + XF - 52) / 2
    parts += [line(XK + 62, YK, XB - 18, YK, MINT, 3.2),
              elbow([(XB - 18, YK), (XB, YK), (XB, Y1), (XF - 52, Y1)], CORAL), cross(XF - 38, Y1),
              txt(m1, Y1 - 18, T("diagram_keys_server"), 20), txt(m1, Y1 + 34, CODE("ip_connection_example"), 18)]
    m2 = (XB + rl - 14) / 2
    parts += [elbow([(XB - 18, YK), (XB, YK), (XB, Y2), (rl - 14, Y2)]),
              txt(m2, Y2 - 18, T("diagram_keys_relay"), 18, MINT), txt(m2, Y2 + 34, CODE("ip_relay_example"), 18),
              elbow([(rr + 14, Y2), (XS, Y2), (XS, YS + RACK_H / 2 + 14)]),
              port(rl, Y2, MINT), port(rr, Y2, MINT), port(XS, YS + RACK_H / 2, MINT),
              txt(XR, Y2 + 64, T("diagram_relay"), 22), txt(XS - 70, YS + 8, T("diagram_server"), 22, CHALK, "end")]
    parts.append(txt(W / 2, H - 28, T("diagram_keys_caption"), 19, AMBER))
    render("relay-keys", *RELAY, W, H, "vhRelayKeys", parts, key="diagram_keys")

    # --- top to bottom: the key on top, its two addresses branching down, as relay-route-tall -----
    seed(51)
    W, H = 560, 820
    XK, YK, XT, XR, YR, XS, YS, YF = 250, 80, 212, 440, 310, 440, 650, 470
    parts = [filter_wall_h(YF, 30, XR - 20, 44, 40), filter_wall_h(YF, XR + 20, 530, 44, 40),
             open_gate([(XR - 20, YF - 22), (XR + 20, YF - 22)], [(XR - 10, YF - 39), (XR + 10, YF - 39)]),
             dragon(362, YF - 22),
             txt(36, YF + 52, T("diagram_firewall"), 17, CHALK, "start"),
             access_key(XK, YK), txt(XK + 82, YK + 8, T("diagram_keys_key"), 21, CHALK, "start"),
             rack(XR, YR, RELAY_W, RELAY_H), rack(XS, YS, RACK_W, RACK_H)]
    parts += [line(XT, YK + 26, XT, 132, MINT, 3.2),
              elbow([(XT, 132), (XT, 150), (90, 150), (90, YF - 48)], CORAL), cross(90, YF - 36),
              txt(110, 392, T("diagram_keys_server"), 18, CHALK, "start"),
              txt(110, 418, CODE("ip_connection_example"), 17, CHALK, "start")]
    parts += [elbow([(XT, 132), (XT, 150), (XR, 150), (XR, YR - RELAY_H / 2 - 14)]),
              txt(XR - 14, 238, T("diagram_keys_relay"), 18, MINT, "end"),
              txt(XR - 14, 262, CODE("ip_relay_example"), 17, CHALK, "end"),
              arrow(XR, YR + RELAY_H / 2 + 14, XS, YS - RACK_H / 2 - 14),
              port(XR, YR - RELAY_H / 2, MINT), port(XR, YR + RELAY_H / 2, MINT), port(XS, YS - RACK_H / 2, MINT)]
    parts += [txt(XR - 60, YR + 8, T("diagram_relay"), 21, CHALK, "end"), txt(XS, YS + 72, T("diagram_server"), 21)]
    parts.append(txt(W / 2, H - 28, T("diagram_keys_caption"), 16, AMBER))
    render("relay-keys-tall", *RELAY, W, H, "vhRelayKeysTall", parts, key="diagram_keys")


def relay_domain() -> None:
    T, CODE = strings(RELAY[1])

    # --- left to right: the key's name, its DNS record, the relay ------------------------------------
    seed(53)
    W, H = 920, 330
    Y = 130
    XK, XD, XT = 130, 450, 780
    parts = [access_key(XK, Y), signpost(XD, Y + 8), rack(XT, Y, RELAY_W, RELAY_H), port(XT - RELAY_W / 2, Y, MINT),
             arrow(XK + 64, Y, XD - 50, Y), arrow(XD + 50, Y, XT - RELAY_W / 2 - 14, Y),
             txt((XK + 64 + XD - 50) / 2, Y - 18, CODE("domain_example"), 17, MINT),
             txt((XD + 50 + XT - 56) / 2, Y - 18, CODE("ip_relay_example"), 18, MINT)]
    for x, name, sub in ((XK, "diagram_domain_key", "diagram_domain_key_sub"),
                         (XD, "diagram_domain_dns", "diagram_domain_dns_sub"),
                         (XT, "diagram_relay", None)):
        parts.append(txt(x, Y + 86, T(name), 21))
        if sub:
            parts.append(txt(x, Y + 110, T(sub), 15, CHALK_DIM))
    parts.append(txt(W / 2, H - 28, T("diagram_domain_caption"), 19, AMBER))
    render("relay-domain", *RELAY, W, H, "vhRelayDomain", parts, key="diagram_domain")

    # --- top to bottom ------------------------------------------------------------------------------
    seed(53)
    W, H = 560, 660
    X, TX, YK, YD, YT = 110, 190, 84, 300, 516
    parts = [access_key(X, YK), signpost(X, YD + 8), rack(X, YT, RELAY_W, RELAY_H), port(X, YT - RELAY_H / 2, MINT),
             arrow(X, YK + 40, X, YD - 62), arrow(X, YD + 46, X, YT - RELAY_H / 2 - 14),
             txt(X + 24, (YK + YD) / 2 + 8, CODE("domain_example"), 16, MINT, "start"),
             txt(X + 24, (YD + YT) / 2 + 12, CODE("ip_relay_example"), 17, MINT, "start")]
    for y, name, sub in ((YK, "diagram_domain_key", "diagram_domain_key_sub"),
                         (YD, "diagram_domain_dns", "diagram_domain_dns_sub"),
                         (YT, "diagram_relay", None)):
        parts.append(txt(TX + 20, y - 2, T(name), 21, CHALK, "start"))
        if sub:
            parts.append(txt(TX + 20, y + 22, T(sub), 14, CHALK_DIM, "start"))
    parts.append(txt(W / 2, H - 28, T("diagram_domain_caption"), 16, AMBER))
    render("relay-domain-tall", *RELAY, W, H, "vhRelayDomainTall", parts, key="diagram_domain")


def address_field(x, y, w, h, T, CODE, size):
    """The app's Custom server address box: its title, and the relay's address and port typed in."""
    value = "%s:%s" % (CODE("ip_relay_example"), CODE("server_port"))
    return (box(x, y, w, h, CHALK, 2.8) + txt(x + 16, y + 30, T("diagram_custom_field"), size, CHALK, "start") +
            box(x + 16, y + 44, w - 32, h - 58, MINT, 2.2) + txt(x + 30, y + 44 + (h - 58) / 2 + 6, value, size, MINT, "start"))


def relay_custom() -> None:
    T, CODE = strings(RELAY[1])

    # --- left to right: the user types the relay's address into the app, which goes to the relay -----
    seed(57)
    W, H = 920, 330
    Y = 140
    XP, XT = 110, 790
    parts = [phone(XP, Y), line(XP + PHONE_W / 2 + 8, Y, 182, Y, CHALK_DIM, 2.2, "6 8"),
             address_field(190, Y - 58, 380, 116, T, CODE, 18),
             arrow(590, Y, XT - RELAY_W / 2 - 14, Y), rack(XT, Y, RELAY_W, RELAY_H), port(XT - RELAY_W / 2, Y, MINT),
             txt(XP, Y + 86, T("diagram_custom_app"), 21), txt(XT, Y + 86, T("diagram_relay"), 21)]
    parts.append(txt(W / 2, H - 28, T("diagram_custom_caption"), 19, AMBER))
    render("relay-custom", *RELAY, W, H, "vhRelayCustom", parts, key="diagram_custom")

    # --- top to bottom --------------------------------------------------------------------------------
    seed(57)
    W, H = 560, 600
    parts = [phone(110, 96), txt(170, 102, T("diagram_custom_app"), 21, CHALK, "start"),
             line(110, 96 + PHONE_H / 2 + 8, 110, 162, CHALK_DIM, 2.2, "6 8"),
             address_field(60, 170, 440, 112, T, CODE, 17),
             arrow(280, 296, 280, 430), rack(280, 476, RELAY_W, RELAY_H), port(280, 476 - RELAY_H / 2, MINT),
             txt(280, 540, T("diagram_relay"), 21)]
    parts.append(txt(W / 2, H - 22, T("diagram_custom_caption"), 16, AMBER))
    render("relay-custom-tall", *RELAY, W, H, "vhRelayCustomTall", parts, key="diagram_custom")


# ===========================================================================
# cloak-traffic - in Cloak Mode a server's connections take a web server's shape
# ===========================================================================
DETECT = ("self_hosted_vpn_docs_vpn_detection", "vh_detect_en")


def browsing(x0, x1, y, colour, step=17):
    """Three page loads on the wire: each a few short connections that start close together."""
    part = (x1 - x0) / 3
    out = []
    for n in range(3):
        for row in (-1, 0, 1):
            a = x0 + n * part + rnd.uniform(0, part * 0.22)
            b = a + rnd.uniform(part * 0.30, part * 0.62)
            out.append(line(a, y + row * step, b, y + row * step, colour, 6.0))
    return "".join(out)


def cloak_traffic() -> None:
    T, _ = strings(DETECT[1])
    heads = (("diagram_cloak_browsing", "diagram_cloak_browsing_sub"),
             ("diagram_cloak_download", "diagram_cloak_download_sub"))
    lanes = (("diagram_cloak_web_server", "diagram_cloak_web_server_sub", VIOLET),
             ("diagram_server", "diagram_cloak_on", MINT),
             ("diagram_server", "diagram_cloak_off", None))

    def lane(parts, x0, xm, x1, y, colour, step=17):
        """A lane's connections: browsing up to xm and a download after it, or one tunnel."""
        if colour:
            parts += [browsing(x0, xm, y, colour, step), line(xm + 34, y, x1, y, colour, 11.0)]
        else:
            parts += [line(x0, y - 12, x1, y - 12, CHALK, 3.0), line(x0, y + 12, x1, y + 12, CHALK, 3.0),
                      txt((x0 + x1) / 2, y - 26, T("diagram_cloak_tunnel"), 18, CHALK)]

    # --- left to right: each lane's name, then its connections over time -----------------
    seed(29)
    W, H = 920, 520
    X, TX = 80, 138                     # the icons' column, and the names' left edge
    X0, XM, X1 = 396, 622, 884          # the timeline, and where browsing gives way to the download
    parts = []
    for (name, sub), m in zip(heads, ((X0 + XM) / 2, (XM + 34 + X1) / 2)):
        parts += [txt(m, 50, T(name), 22), txt(m, 76, T(sub), 16, CHALK_DIM)]
    for y, (name, sub, colour) in zip((150, 256, 362), lanes):
        parts.append(globe(X, y, 34) if colour == VIOLET else rack(X, y, 84, 68))
        parts += [txt(TX, y - 2, T(name), 23, CHALK, "start"), txt(TX, y + 24, T(sub), 16, CHALK_DIM, "start")]
        lane(parts, X0, XM, X1, y, colour)
    parts += [arrow(X0, 424, X1, 424, CHALK_DIM, 2.2), txt(X1, 450, T("diagram_cloak_time"), 16, CHALK_DIM, "end"),
              txt(W / 2, H - 28, T("diagram_cloak_caption"), 20, AMBER)]
    render("cloak-traffic", *DETECT, W, H, "vhCloak", parts, "diagram_cloak")

    # --- top to bottom: each lane's name, with its connections under it ------------------
    seed(29)
    W, H = 560, 820
    X, TX = 78, 136
    X0, XM, X1 = 44, 250, 516
    parts = []
    for (name, sub), m in zip(heads, ((X0 + XM) / 2, (XM + 34 + X1) / 2)):
        parts += [txt(m, 48, T(name), 20), txt(m, 72, T(sub), 15, CHALK_DIM)]
    for y, (name, sub, colour) in zip((136, 342, 548), lanes):
        parts.append(globe(X, y, 30) if colour == VIOLET else rack(X, y, 72, 58))
        parts += [txt(TX, y - 2, T(name), 23, CHALK, "start"), txt(TX, y + 24, T(sub), 16, CHALK_DIM, "start")]
        lane(parts, X0, XM, X1, y + 92, colour, 15)
    parts += [arrow(X0, 716, X1, 716, CHALK_DIM, 2.2), txt(X1, 742, T("diagram_cloak_time"), 15, CHALK_DIM, "end"),
              txt(W / 2, H - 28, T("diagram_cloak_caption"), 18, AMBER)]
    render("cloak-traffic-tall", *DETECT, W, H, "vhCloakTall", parts, "diagram_cloak")


# ===========================================================================
# dynamic-ip-follow - the server's next report shows MANAGER its new address
# ===========================================================================
DYNAMIC_IP = ("vpnhood_manager_docs_dynamic_ip", "vh_dynip_en")


def dynamic_ip_follow() -> None:
    T, CODE = strings(DYNAMIC_IP[1])
    steps = (("diagram_report", "diagram_report_sub", MINT), ("diagram_update", "diagram_update_sub", VIOLET))

    # --- left to right: the server, MANAGER, the keys ------------------------------------
    seed(21)
    W, H = 920, 330
    Y = 92
    XS, XM, XK = 120, 460, 800
    parts = [rack(XS, Y, RACK_W, RACK_H), manager_hood(XM, Y), access_key(XK, Y)]
    spans = ((XS + RACK_W / 2 + 14, XM - HOOD_W / 2 - 14), (XM + HOOD_W / 2 + 14, XK - 78))
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
    parts = [rack(X, YS, RACK_W, RACK_H), manager_hood(X, YM), access_key(X, YK)]
    spans = ((YS + RACK_H / 2 + 14, YM - HOOD_H / 2 - 14), (YM + HOOD_H / 2 + 14, YK - 44))
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
# dynamic-ip-urls - the file MANAGER keeps up to date leads apps to the new address
# ===========================================================================
FILE_HALF_W, FILE_HALF_H = 44, 48


def web_file(cx, cy):
    """A file on the web: a sheet with a folded corner, a small globe on its other corner. The
    sheet's outline stops short of the globe, as a mask would show through the chalk's grain."""
    w, h, fold, bite = 64, 76, 19, 24
    x, y = cx - FILE_HALF_W, cy - FILE_HALF_H
    d = ("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f"
         % (j(x + w - bite), j(y + h), j(x), j(y + h), j(x), j(y), j(x + w - fold), j(y),
            j(x + w), j(y + fold), j(x + w), j(y + h - bite)))
    out = ['<path d="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-linejoin="round" '
           'stroke-linecap="round"/>' % (d, CHALK),
           line(x + w - fold, y, x + w - fold, y + fold, CHALK_DIM, 2.2),
           line(x + w - fold, y + fold, x + w, y + fold, CHALK_DIM, 2.2)]
    for n, (end, colour) in enumerate(((w - 30, CHALK_DIM), (w - 12, MINT), (w - 32, MINT))):
        ly = y + 26 + n * 14
        out.append(line(x + 11, ly, x + end, ly, colour, 3.0))
    out.append(globe(x + w + 2, y + h - 2, 21))
    return "".join(out)


def dynamic_ip_urls() -> None:
    T, _ = strings(DYNAMIC_IP[1])
    labels = (("diagram_manager", "diagram_publish"), ("diagram_file", "diagram_file_sub"),
              ("diagram_users", "diagram_read"), ("diagram_server", "diagram_reached"))
    colours = (VIOLET, MINT, MINT)

    # --- left to right: MANAGER, the file, your users, your server ------------------------
    seed(25)
    W, H = 920, 300
    Y = 88
    XM, XF, XU, XS = 122, 347, 573, 798
    parts = [manager_hood(XM, Y), web_file(XF, Y), people(XU, Y), rack(XS, Y, RACK_W, RACK_H)]
    spans = ((XM + HOOD_W / 2 + 14, XF - FILE_HALF_W - 14), (XF + FILE_HALF_W + 16, XU - 62),
             (XU + 58, XS - RACK_W / 2 - 14))
    for (x1, x2), colour in zip(spans, colours):
        parts.append(arrow(x1, Y, x2, Y, colour))
    for x, (name, sub) in zip((XM, XF, XU, XS), labels):
        parts += [txt(x, Y + 94, T(name), 22), txt(x, Y + 120, T(sub), 16, CHALK_DIM)]
    parts.append(txt(W / 2, H - 30, T("diagram_urls_caption"), 20, AMBER))
    render("dynamic-ip-urls", *DYNAMIC_IP, W, H, "vhDynUrls", parts, "diagram_urls")

    # --- top to bottom: icons down the left, their labels beside them ---------------------
    seed(25)
    W, H = 560, 780
    X, TX = 104, 186
    YS = (84, 272, 460, 642)
    parts = [manager_hood(X, YS[0]), web_file(X, YS[1]), people(X, YS[2]), rack(X, YS[3], RACK_W, RACK_H)]
    tops = (FILE_HALF_H, 40, RACK_H / 2)            # how far each icon reaches above its middle
    bottoms = (HOOD_H / 2, FILE_HALF_H + 8, 36)     # and below it
    for y, y_next, top, bottom, colour in zip(YS, YS[1:], tops, bottoms, colours):
        parts.append(arrow(X, y + bottom + 14, X, y_next - top - 14, colour))
    for y, (name, sub) in zip(YS, labels):
        parts += [txt(TX, y - 2, T(name), 24, CHALK, "start"), txt(TX, y + 24, T(sub), 16, CHALK_DIM, "start")]
    parts.append(txt(W / 2, H - 34, T("diagram_urls_caption"), 18, AMBER))
    render("dynamic-ip-urls-tall", *DYNAMIC_IP, W, H, "vhDynUrlsTall", parts, "diagram_urls")


# ===========================================================================
# cloak-mode - a firewall can recognize one long tunnel, and not a browser's requests
# ===========================================================================
CLOAK = ("features_cloak_mode", "vh_cloak_en")
PHONE_W, PHONE_H = 54, 92


def phone(cx, cy):
    """Your device: a phone, with its speaker and its home bar."""
    x, y = cx - PHONE_W / 2, cy - PHONE_H / 2
    return (box(x, y, PHONE_W, PHONE_H, CHALK, 3.2) + line(cx - 7, y + 10, cx + 7, y + 10) +
            line(cx - 11, y + PHONE_H - 10, cx + 11, y + PHONE_H - 10))


def filter_wall(cx, y0, y1, w, course):
    """A firewall (DPI): a column of bricks, each course offset from the last."""
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
    parts = [filter_wall(XF, 110, 450, WALL, 26), dragon(XF, 110), magnifier(XF, (Y1 + Y2) / 2 - 6)]
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
    W, H = 560, 684
    XP, XF, XS, WALL = 62, 300, 492, 48
    Y1, Y2 = 204, 470
    parts = [filter_wall(XF, y - 60, y + 60, WALL, 20) for y in (Y1, Y2)]
    parts += [dragon(XF, Y1 - 60)]
    parts += cloak_lanes(XP, XF, XS, Y1, Y2, 84, 66, WALL, 19, 5)
    parts += [txt(28, 42, T("diagram_device"), 17, CHALK, "start"), txt(XF, 42, T("diagram_filter"), 17),
              txt(W - 28, 42, T("diagram_server"), 17, CHALK, "end")]
    for y, (key, sub, result, colour) in zip((Y1, Y2), lanes):
        parts += [txt(28, y - 96, T(key), 21, CHALK, "start"), txt(W / 2, y + 88, T(sub), 17, CHALK_DIM),
                  txt(W / 2, y + 116, T(result), 19, colour)]
    parts.append(txt(W / 2, H - 28, T("diagram_caption"), 18, AMBER))
    render("cloak-mode-tall", *CLOAK, W, H, "vhCloakModeTall", parts)


# ===========================================================================
# block-quic - Cloak Mode can disguise TCP and not QUIC, so the device stops QUIC and the app moves
# ===========================================================================
def phone_on_side(x0, x1, cy, h):
    """Your device, turned for a video, wide enough to show what happens inside it."""
    return box(x0, cy - h / 2, x1 - x0, h, CHALK, 3.2) + line(x0 + 10, cy - 11, x0 + 10, cy + 11)


def video_app(cx, cy, s=52):
    """An app: a video's play button in a box."""
    r = s * 0.2
    return (box(cx - s / 2, cy - s / 2, s, s, VIOLET, 2.8) +
            '<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
            % (cx - r * 0.8, cy - r, cx + r * 1.1, cy, cx - r * 0.8, cy + r, VIOLET))


def switch(x, cy, on):
    """The app's toggle: the knob at the right, in mint, when it is on."""
    w, h = 44, 24
    colour = MINT if on else CHALK_DIM
    return ('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="%d" fill="%s" fill-opacity="%s" '
            'stroke="%s" stroke-width="2.4"/>' % (x, cy - h / 2, w, h, h / 2, colour, "0.2" if on else "0", colour) +
            dot(x + (w - h / 2 if on else h / 2), cy, 7.5, colour))


def quic_lanes(x0, x1, xf, xs, y1, y2, phone_h, app_x, rack_w, rack_h, wall_w, half, packets, size):
    """One app, twice. Its QUIC leaves the phone as packets and stops at the wall; with QUIC stopped
    inside the phone, its TCP goes through the wall in a tunnel of its own, up to the server."""
    a = app_x + 34                                          # the app's edge
    t0, b = x1 + 8, xf - wall_w / 2 - 3                     # the phone to the wall
    c, d = xf + wall_w / 2 + 10, xs - rack_w / 2 - 14       # the wall to the server
    gap = 24
    mid = (a + x1) / 2
    stop = x1 - 36
    return [phone_on_side(x0, x1, y1, phone_h), video_app(app_x, y1), rack(xs, y1, rack_w, rack_h),
            arrow(a, y1, x1 - 8, y1, CORAL, 3.0), txt(mid, y1 - 12, "QUIC", size, CORAL),
            packet_tunnel(t0, b, y1, half, packets),
            arrow(c, y1, d, y1, CHALK_DIM, 2.6, "9 11"), cross(xf, y1, 14, CORAL, 5.0),
            phone_on_side(x0, x1, y2, phone_h), video_app(app_x, y2), rack(xs, y2 + gap, rack_w, rack_h),
            arrow(a, y2 - gap, stop - 20, y2 - gap, CORAL, 3.0), cross(stop, y2 - gap, 12, CORAL, 4.6),
            txt((a + stop - 20) / 2, y2 - gap - 16, "QUIC", size, CORAL),
            arrow(a, y2 + gap, x1 - 8, y2 + gap, MINT, 3.0), txt(mid, y2 + gap - 10, "TCP", size, MINT),
            stream_tunnel(t0, d, y2 + gap, xf, wall_w)]


def block_quic() -> None:
    T, _ = strings(DETECT[1])
    lanes = (("diagram_quic_off", False, "diagram_quic_off_app", "diagram_quic_off_sub",
              "diagram_quic_off_result", CORAL),
             ("diagram_quic_on", True, "diagram_quic_on_stop", "diagram_quic_on_sub",
              "diagram_quic_on_result", MINT))

    # --- left to right, on cloak-mode's grid: one wall across both lanes ------------------------
    seed(37)
    W, H = 920, 618
    X0, X1, XF, XS, WALL = 36, 272, 548, 836, 52
    Y1, Y2 = 176, 408
    left, right = (X0 + XF - WALL / 2) / 2, 742     # the middle of what lies on either side of the wall
    parts = [filter_wall(XF, 110, 552, WALL, 26), dragon(XF, 110), magnifier(XF, (Y1 + Y2) / 2 + 2)]
    parts += quic_lanes(X0, X1, XF, XS, Y1, Y2, 124, X0 + 48, 92, 72, WALL, 19, 8, 18)
    for x, key in ((X0 + (X1 - X0) / 2, "diagram_quic_device"), (XF, "diagram_filter"), (XS, "diagram_server")):
        parts.append(txt(x, 46, T(key), 19))
    for y, (key, on, line1, line2, result, colour) in zip((Y1, Y2), lanes):
        parts += [switch(X0, y - 85, on), txt(X0 + 56, y - 77, T(key), 21, CHALK, "start"),
                  txt(left, y + 90, T(line1), 18), txt(left, y + 116, T(line2), 18),
                  txt(right, y + 104, T(result), 18, colour)]
    parts.append(txt(W / 2, H - 28, T("diagram_quic_caption"), 20, AMBER))
    render("block-quic", *DETECT, W, H, "vhBlockQuic", parts, "diagram_quic")

    # --- on a phone: the same lanes, one under the other, each with its own stretch of wall -----
    seed(37)
    W, H = 560, 760
    X0, X1, XF, XS, WALL = 22, 208, 336, 494, 44
    Y1, Y2 = 170, 492
    parts = [filter_wall(XF, y - 62, y + 62, WALL, 20) for y in (Y1, Y2)] + [dragon(XF, Y1 - 62)]
    parts += quic_lanes(X0, X1, XF, XS, Y1, Y2, 124, X0 + 44, 80, 64, WALL, 19, 4, 17)
    parts += [txt(X0 + 6, 42, T("diagram_quic_device"), 17, CHALK, "start"), txt(XF, 42, T("diagram_filter"), 17),
              txt(W - 22, 42, T("diagram_server"), 17, CHALK, "end")]
    for y, (key, on, line1, line2, result, colour) in zip((Y1, Y2), lanes):
        parts += [switch(X0, y - 84, on), txt(X0 + 56, y - 77, T(key), 21, CHALK, "start"),
                  txt(W / 2, y + 92, T(line1), 17), txt(W / 2, y + 118, T(line2), 17),
                  txt(W / 2, y + 146, T(result), 19, colour)]
    parts.append(txt(W / 2, H - 24, T("diagram_quic_caption"), 17, AMBER))
    render("block-quic-tall", *DETECT, W, H, "vhBlockQuicTall", parts, "diagram_quic")


# ===========================================================================
# farm-token-key - one farm token, in every key of the farm, beside each key's own part
# ===========================================================================
FARM_TOKEN = ("vpnhood_manager_docs_farm_token", "vh_farmtoken_en")


def key_cells(x, y, w_token, w_own, h, T, size):
    """One access key as two cells: the farm token, the same in every key, and its own ID and secret."""
    gap = 8
    base = y + h / 2 + size * .36
    return [box(x, y, w_token, h, MINT, 3.0), box(x + w_token + gap, y, w_own, h, VIOLET, 3.0),
            txt(x + w_token / 2, base, T("diagram_token"), size, MINT),
            txt(x + w_token + gap + w_own / 2, base, T("diagram_own"), size, VIOLET)]


def small_key(cx, cy, scale):
    """The access key at a size that leaves room beside it."""
    return '<g transform="translate(%.1f %.1f) scale(%.2f)">%s</g>' % (cx, cy, scale, access_key(0, 0))


def farm_token_key() -> None:
    T, _ = strings(FARM_TOKEN[1])

    # --- left to right: MANAGER, then two keys, each its two cells and the key they make --------
    seed(41)
    W, H = 920, 372
    XM, Y = 116, 138
    XC, WT, WO, CH = 274, 236, 208, 62
    TOPS = (84, 176)
    XK = 824
    parts = [manager_hood(XM, Y), txt(XM, Y + 90, T("diagram_manager"), 20), txt(XM, Y + 116, T("diagram_builds"), 15, CHALK_DIM)]
    parts += [txt(XC + WT / 2, 60, T("diagram_same"), 15, MINT), txt(XC + WT + 8 + WO / 2, 60, T("diagram_different"), 15, VIOLET),
              txt(XK, 60, T("diagram_keys"), 15, CHALK)]
    x0, xm = XM + HOOD_W / 2 + 12, (XM + HOOD_W / 2 + XC) / 2 + 4
    for top in TOPS:
        mid = top + CH / 2
        parts += key_cells(XC, top, WT, WO, CH, T, 19)
        parts.append(elbow([(x0, Y), (xm, Y), (xm, mid), (XC - 12, mid)], MINT))
        parts.append(small_key(XK, mid - 8, .8))
    parts += [txt(W / 2, H - 56, T("diagram_key_caption_1"), 19, AMBER), txt(W / 2, H - 28, T("diagram_key_caption_2"), 19, AMBER)]
    render("farm-token-key", *FARM_TOKEN, W, H, "vhFarmTokenKey", parts, "diagram_key")

    # --- top to bottom: MANAGER above the two keys, each key's picture beside its cells ---------
    seed(41)
    W, H = 560, 590
    X, YM = 280, 76
    XC, WT, WO, CH = 108, 216, 196, 58
    TOPS = (284, 368)
    parts = [manager_hood(X, YM), txt(X, YM + 88, T("diagram_manager"), 22), txt(X, YM + 114, T("diagram_builds"), 16, CHALK_DIM)]
    parts += [txt(XC + WT / 2, TOPS[0] - 16, T("diagram_same"), 14, MINT), txt(XC + WT + 8 + WO / 2, TOPS[0] - 16, T("diagram_different"), 14, VIOLET)]
    parts.append(arrow(XC + WT / 2, YM + 134, XC + WT / 2, TOPS[0] - 38, MINT))
    for top in TOPS:
        parts += key_cells(XC, top, WT, WO, CH, T, 18)
        parts.append(small_key(58, top + CH / 2 - 5, .55))
    parts += [txt(W / 2, H - 76, T("diagram_key_caption_1"), 18, AMBER), txt(W / 2, H - 46, T("diagram_key_caption_2"), 18, AMBER)]
    render("farm-token-key-tall", *FARM_TOKEN, W, H, "vhFarmTokenKeyTall", parts, "diagram_key")


# ===========================================================================
# farm-token-new - the two roads a new farm token takes to an app
# ===========================================================================
def farm_token_new() -> None:
    T, CODE = strings(FARM_TOKEN[1])

    # --- left to right: MANAGER, then your server over the file, then the app -------------------
    seed(43)
    W, H = 920, 452
    XM, Y = 116, 196
    XN, Y1, Y2 = 452, 84, 288
    XA = 806
    parts = [manager_hood(XM, Y), rack(XN, Y1, RACK_W, RACK_H), web_file(XN, Y2), phone(XA, Y)]
    parts += [txt(XM, Y + 90, T("diagram_manager"), 20), txt(XM, Y + 116, T("diagram_new_token"), 15, CHALK_DIM),
              txt(XN, Y1 + 72, T("diagram_server"), 21), txt(XN, Y1 + 96, CODE("manager_push_token"), 15, CHALK_DIM),
              txt(XN, Y2 + 78, T("diagram_url"), 21), txt(XN, Y2 + 102, T("diagram_url_sub"), 15, CHALK_DIM),
              txt(XA - PHONE_W / 2 - 18, Y + 8, T("diagram_app"), 21, CHALK, "end")]
    x0, xm = XM + HOOD_W / 2 + 12, XM + HOOD_W / 2 + 96
    parts += [elbow([(x0, Y), (xm, Y), (xm, Y1), (XN - RACK_W / 2 - 14, Y1)], MINT),
              elbow([(x0, Y), (xm, Y), (xm, Y2), (XN - FILE_HALF_W - 14, Y2)], MINT)]
    xr, xa = XN + RACK_W / 2 + 14, XA
    parts += [elbow([(xr, Y1), (xa, Y1), (xa, Y - PHONE_H / 2 - 14)], MINT),
              elbow([(XN + FILE_HALF_W + 26, Y2), (xa, Y2), (xa, Y + PHONE_H / 2 + 14)], MINT),
              txt((xr + xa) / 2, Y1 - 14, T("diagram_can"), 16), txt((XN + FILE_HALF_W + 26 + xa) / 2, Y2 + 26, T("diagram_cannot"), 16)]
    parts.append(txt(W / 2, H - 26, T("diagram_new_caption"), 19, AMBER))
    render("farm-token-new", *FARM_TOKEN, W, H, "vhFarmTokenNew", parts, "diagram_new")

    # --- top to bottom: MANAGER, your server beside the file, then the app ----------------------
    seed(43)
    W, H = 560, 800
    X, YM, YN, YA = 280, 76, 322, 620
    XL, XR = 140, 420
    parts = [manager_hood(X, YM), rack(XL, YN, RACK_W, RACK_H), web_file(XR, YN), phone(X, YA)]
    parts += [txt(X, YM + 88, T("diagram_manager"), 22), txt(X, YM + 114, T("diagram_new_token"), 16, CHALK_DIM),
              txt(XL, YN + 74, T("diagram_server"), 20), txt(XL, YN + 98, CODE("manager_push_token"), 14, CHALK_DIM),
              txt(XR, YN + 80, T("diagram_url"), 20), txt(XR, YN + 104, T("diagram_url_sub"), 14, CHALK_DIM),
              txt(X, YA + 76, T("diagram_app"), 21)]
    yb = YM + 134
    parts += [elbow([(X, yb), (X, yb + 28), (XL, yb + 28), (XL, YN - RACK_H / 2 - 14)], MINT),
              elbow([(X, yb), (X, yb + 28), (XR, yb + 28), (XR, YN - FILE_HALF_H - 14)], MINT)]
    yl = YN + 118
    parts += [elbow([(XL, yl), (XL, YA), (X - PHONE_W / 2 - 14, YA)], MINT),
              elbow([(XR, yl), (XR, YA), (X + PHONE_W / 2 + 14, YA)], MINT),
              txt(XL - 112, YA + 28, T("diagram_can"), 15, CHALK, "start"), txt(XR + 112, YA + 28, T("diagram_cannot"), 15, CHALK, "end")]
    parts.append(txt(W / 2, H - 30, T("diagram_new_caption"), 17, AMBER))
    render("farm-token-new-tall", *FARM_TOKEN, W, H, "vhFarmTokenNewTall", parts, "diagram_new")


# ===========================================================================
# policies-options - what decides a user's choices at a location, and the page where the app asks
# ===========================================================================
POLICIES = ("vpnhood_manager_docs_policies", "vh_policies_en")

# the app's page of choices: each row's label, its line under it, and its chalk
POLICY_ROWS = (("diagram_free", "diagram_free_sub", CHALK), ("diagram_free_ad", "diagram_free_ad_sub", CHALK),
               None,
               ("diagram_watch", "diagram_watch_sub", VIOLET), ("diagram_try", "diagram_try_sub", VIOLET),
               ("diagram_go", "diagram_go_sub", MINT))


def policy_inputs(T, x, ys, size, sub):
    """The three things that decide, an icon each with its label and line beside it, then the private key."""
    parts = [globe(x, ys[0], 30), rack(x, ys[1], 74, 60), phone(x, ys[2])]
    for y, label in zip(ys, ("diagram_country", "diagram_location", "diagram_app")):
        parts += [txt(x + 58, y - 3, T(label), size, CHALK, "start"), txt(x + 58, y + 21, T(label + "_sub"), sub, CHALK_DIM, "start")]
    parts += [small_key(x + 6, ys[3] - 4, .55), txt(x + 58, ys[3] - 3, T("diagram_private"), size, AMBER, "start"),
              txt(x + 58, ys[3] + 21, T("diagram_private_sub"), sub, CHALK_DIM, "start")]
    return parts


def policy_page(T, x, y, w, h, row_w):
    """The app's page of choices for a location that is free with premium: two free rows, then three premium ones."""
    cx = x + w / 2
    parts = [box(x, y, w, h, CHALK, 3.2), line(cx - 12, y + 14, cx + 12, y + 14), line(cx - 18, y + h - 14, cx + 18, y + h - 14),
             txt(cx, y + 48, T("diagram_screen_1"), 15, CHALK_DIM), txt(cx, y + 72, T("diagram_screen_2"), 19, CHALK)]
    ry = y + 92
    for row in POLICY_ROWS:
        if row is None:
            parts.append(txt(cx, ry + 18, T("diagram_or"), 15, CHALK_DIM))
            ry += 30
            continue
        label, sub, chalk = row
        parts += [box(cx - row_w / 2, ry, row_w, 48, chalk, 2.6), txt(cx, ry + 21, T(label), 17, chalk),
                  txt(cx, ry + 40, T(sub), 13, CHALK_DIM)]
        ry += 58
    return parts


def policies_options() -> None:
    T, _ = strings(POLICIES[1])

    # --- left to right: what decides, beside the app's page of choices ---------------------------
    seed(47)
    W, H = 920, 520
    X, YS = 78, (96, 198, 304, 418)
    XP, YP, WP, HP = 560, 26, 300, 446
    parts = [txt(X - 30, 44, T("diagram_decides"), 18, CHALK_DIM, "start")]
    parts += policy_inputs(T, X, YS, 20, 15)
    parts += policy_page(T, XP, YP, WP, HP, 244)
    for y in YS[:3]:
        parts.append(elbow([(452, y), (500, y), (500, 248), (XP - 14, 248)], MINT))
    parts.append(txt(W / 2, H - 20, T("diagram_caption"), 19, AMBER))
    render("policies-options", *POLICIES, W, H, "vhPoliciesOptions", parts)

    # --- top to bottom: what decides, the page below it, and under the page the private key, which skips it
    seed(47)
    W, H = 560, 1000
    X, YS = 64, (96, 198, 304, 912)
    XP, YP, WP, HP = 120, 410, 320, 446
    parts = [txt(X - 30, 44, T("diagram_decides"), 18, CHALK_DIM, "start")]
    parts += policy_inputs(T, X, YS, 20, 15)
    parts += policy_page(T, XP, YP, WP, HP, 256)
    parts.append(arrow(W / 2, 362, W / 2, YP - 14, MINT))
    parts.append(txt(W / 2, H - 22, T("diagram_caption"), 18, AMBER))
    render("policies-options-tall", *POLICIES, W, H, "vhPoliciesOptionsTall", parts)


if __name__ == "__main__":
    server_two_ips()
    reverse_proxy()
    how_it_works()
    how_device()
    how_tunnel()
    how_tcp()
    how_server()
    how_key()
    cloak_traffic()
    dynamic_ip_follow()
    dynamic_ip_find()
    dynamic_ip_urls()
    cloak_mode()
    block_quic()
    farm_token_key()
    farm_token_new()
    policies_options()
    relay_route()
    relay_proxy()
    relay_satellite()
    relay_keys()
    relay_domain()
    relay_custom()
