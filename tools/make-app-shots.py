#!/usr/bin/env python3
"""Draw the app screenshots the site shows, in every language the site has.

A page shows the app's own screen, and a reader whose app speaks Persian should see it in
Persian, right to left, as their phone shows it. So every picture here is drawn by the app's
real UI once per language in _data/i18n/: the store screenshot tool in the VpnHood repo
(src/Apps/Tools/StoreScreenshots; its README explains it) starts the Avalonia UI headless
against a product's store fixture, with no app, VPN or device. The languages, the Android
phone's capabilities and the demo apps come from that product's store configuration (CLIENT's
or CONNECT's), and a screen its Google Play set also shows takes that shot's patch and hidden
controls, so the site shows what the listing shows. /free-vpn/'s strip shows CONNECT's screens
whole, in that set's own phone: the status bar and the home indicator come with them. The
screens are SHOTS below.

    python tools/make-app-shots.py                     # every picture in every language
    python tools/make-app-shots.py --only home --lang en,fa
    python tools/make-app-shots.py --check             # report missing or extra files

Writes assets/images/app/<lang>/<name>.webp and _data/app_shots.yml with the pixel size of
each, which _includes/app-shot.html reads: a picture is drawn at twice the size it is shown.
Never edit either by hand, and never add these to make-light-art.py: app UI looks the same in
both themes. Rerun it after a change to the app's screens or words; the same inputs draw the
same bytes, so git shows only the pictures that changed.

Needs the .NET SDK, Pillow, and the VpnHood, Vpnhood.App.Client and Vpnhood.App.Connect repos
beside this one. Run from the repo root. Each picture's fixture and full-size capture stay in
.tmp/app-shots/<product>/, so a wrong pixel can be chased with the tool's own `shot` command.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
VH = ROOT.parent / "VpnHood"
TOOL = VH / "src/Apps/Tools/StoreScreenshots"
ASSETS = VH / "src/AppUi/VpnHood.AppUi.Assets.Classic/assets"
STORES = {"client": ROOT.parent / "Vpnhood.App.Client/store", "connect": ROOT.parent / "Vpnhood.App.Connect/store"}
PLATFORM = "android-phone"  # the store set whose capabilities and screens the site follows
PHONE = "android-phone"  # ...and its phone, for a picture that shows the phone's whole screen
TV = "apple-tv"  # the store set of a TV's screens: the TV layout, whole, on that set's own device

OUT = ROOT / "assets/images/app"
DATA = ROOT / "_data/app_shots.yml"
WORK = ROOT / ".tmp/app-shots"

# The phone: 360 x 692 logical pixels is a phone's screen below its status bar. A feature page's
# picture is drawn at 7/3 of that, 840 wide, as it is shown up to 420 wide.
WIDTH = 360
HEIGHT = 692
SCALE = 7 / 3
# Below the last card of a trimmed page, as much screen as the page's own side margin.
TRIM_MARGIN = 16
# /free-vpn/'s strip shows each screen 220 wide in a phone of the site's own (.vh-phone in
# _custom.scss), drawn at 440.
STRIP = {"phone": 440}
# A TV's screen is 960 x 540 logical pixels, drawn at 1.5 as the docs show it 720 wide.
TV_SCALE = 1.5
# The docs' details are drawn at 2x, the size their pages show halved.
DOCS = 2
# The ring that marks what a docs step is about: the site's green, as on the feature pages.
RING = (99, 230, 190)


# The Smart Proxies page shows a list the app has rated. Addresses are from the ranges reserved
# for documentation (RFC 5737) and example.net, never a real proxy.
def _proxy(host: str, port: int, protocol: str, country: str, ok: int, failed: int, ms: int, quality: str) -> dict:
    return {
        "endPoint": {"id": f"{host}:{port}", "isEnabled": True, "protocol": protocol, "host": host, "port": port,
                     "url": f"{protocol.lower()}://{host}:{port}"},
        "status": {"succeededCount": ok, "failedCount": failed, "latency": f"00:00:00.{ms:03d}", "quality": quality},
        "countryCode": country,
    }


DEMO_PROXIES = [
    _proxy("203.0.113.9", 1080, "Socks5", "DE", 14, 0, 86, "Excellent"),
    _proxy("proxy.example.net", 443, "Https", "NL", 11, 0, 112, "Excellent"),
    _proxy("198.51.100.33", 1080, "Socks5", "FR", 9, 1, 164, "Good"),
    _proxy("192.0.2.100", 3128, "Http", "US", 6, 1, 238, "Good"),
    _proxy("203.0.113.71", 1080, "Socks5", "SG", 3, 2, 412, "Fair"),
]

# The split lists as someone has filled them, with names reserved for examples (RFC 2606) and
# the documentation address ranges (RFC 5737).
DEMO_DOMAINS = {"excludes": "bank.example\n*.example.org", "includes": "", "blocks": "ads.example.net"}
DEMO_IPS = {"excludes": "198.51.100.0/24\n203.0.113.10", "includes": "", "blocks": ""}
DOMAINS_ON = {"userSettings": {"splitTunneling": {"useDomain": True}}, "splitDomains": DEMO_DOMAINS}
PROXIES_ON = {"userSettings": {"proxySettings": {"mode": "Manual"}}, "proxyEndPoints": DEMO_PROXIES}

# Each picture: its file name, the app page by its route (PageRoutes.cs in the tool), the
# product whose store fixture draws it (CONNECT unless said: the feature pages, guides and
# /free-vpn/ speak to CONNECT's readers and offer its download, so only CLIENT's docs show
# CLIENT), and what is not the default. All lengths are the app's logical pixels:
#   height  a taller screen, for a page the phone would scroll
#   scale   pixels per logical pixel, SCALE unless said
#   trim    then cut the empty screen below the last card, for a page shorter than that
#   cut     then cut it to this height: the top of a long page, with no scroll bar
#   crop    then cut out this box, [left, top, width, height]
#   box     then cut to the light box on the page (a message), with this much around it
#   ring    then draw a ring around this box, [left, top, width, height], in the cut picture
#   phone   instead, the whole screen in the Google Play set's phone, its status bar and home
#           indicator included, this many pixels wide and its corners round as the phone's
#   tv      instead, a TV's whole screen, with the capabilities and patch of the TV store set
#   patch   what the app must be showing, laid over the store shot's own (FixtureComposer)
#   hide    controls to leave out, each a path of x:Names from the page down
SHOTS: list[dict] = [
    # the feature pages
    {"name": "home", "route": "/"},
    {"name": "cloak-mode", "route": "/protocols/cloak-mode"},
    {"name": "protocols", "route": "/protocols"},
    {"name": "proxies", "route": "/settings/proxies", "height": 1200, "cut": 790, "patch": PROXIES_ON},
    {"name": "private-dns", "route": "/dns"},
    {"name": "kill-switch", "route": "/settings/kill-switch"},
    {"name": "always-on", "route": "/settings/always-on"},
    {"name": "quick-launch", "route": "/settings/quick-launch"},
    {"name": "split-tunneling", "route": "/split-tunneling", "height": 1600, "cut": HEIGHT},
    {"name": "split-apps", "route": "/split-tunneling/split-apps", "height": 1200, "cut": HEIGHT},
    {"name": "split-countries", "route": "/split-tunneling/split-countries", "trim": True},
    {"name": "split-domains", "route": "/split-tunneling/split-domains", "height": 1000, "trim": True,
     "patch": DOMAINS_ON},
    {"name": "split-ips", "route": "/split-tunneling/split-ips-via-device", "height": 1000, "trim": True,
     "patch": {"userSettings": {"splitTunneling": {"useIpViaDevice": True}}, "splitIpsViaDevice":
               {k: v for k, v in DEMO_IPS.items() if k != "blocks"}}},
    {"name": "split-dns", "route": "/split-tunneling/split-dns", "trim": True},
    # connected to a server that lets a client reach its own network, as the page's switch needs
    {"name": "split-local-network", "route": "/split-tunneling/split-local-network", "trim": True,
     "patch": {"state": {"sessionInfo": {"isLocalNetworkAllowed": True}}}},

    # /vpnhood-client/docs/diagnose/: the menu with Diagnose ringed, the home screen while
    # diagnosing, and the message when it is stopped
    {"name": "diagnose-menu", "product": "client", "route": "/menu", "scale": DOCS, "crop": [0, 81, 300, 136],
     "ring": [6, 47, 288, 42]},
    {"name": "diagnose-stop", "product": "client", "route": "/", "scale": DOCS, "crop": [60, 182, 240, 246],
     "patch": {"state": {"connectionState": "Connected", "hasDiagnoseRequested": True, "isDiagnosing": True,
                         "canDiagnose": False, "sessionStatus": {"speed": {"received": 1164000, "sent": 893900}}}}},
    {"name": "diagnose-report", "product": "client", "route": "/diagnose-finished", "scale": DOCS, "box": 8},

    # /vpnhood-client/docs/tv/: a TV's home screen, connected, and its Remote Access screen
    {"name": "tv-home", "product": "client", "route": "/", "tv": True},
    {"name": "tv-remote-access", "product": "client", "route": "/remote-access", "tv": True},
    # /features/tv/: the same two in CONNECT
    {"name": "connect-tv-home", "route": "/", "tv": True},
    {"name": "connect-tv-remote-access", "route": "/remote-access", "tv": True},

    # /free-vpn/'s strip: CONNECT's own Google Play screens, each with that shot's patch, the home
    # screen connected among them
    {"name": "connect-home", "route": "/", **STRIP},
    {"name": "connect-locations", "route": "/servers", **STRIP},
    {"name": "connect-cloak-mode", "route": "/protocols/cloak-mode", **STRIP},
    {"name": "connect-split-tunneling", "route": "/split-tunneling", **STRIP},
    {"name": "connect-quick-launch", "route": "/settings/quick-launch", **STRIP},
]


def read_jsonc(path: Path):
    """JSON with // and /* */ comments and trailing commas, as the store configuration is."""
    text = path.read_text(encoding="utf-8-sig")
    out, i, n, in_string = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\":
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
            out.append(c)
        elif text.startswith("//", i):
            end = text.find("\n", i)
            i = n if end < 0 else end
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i)
            i = n if end < 0 else end + 2
            continue
        else:
            out.append(c)
        i += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))


def merge(target: dict, patch: dict | None) -> dict:
    """A patch merges into objects and replaces anything else, lists included, as the tool's."""
    for key, value in (patch or {}).items():
        if isinstance(target.get(key), dict) and isinstance(value, dict):
            merge(target[key], value)
        else:
            target[key] = json.loads(json.dumps(value))
    return target


def site_languages() -> list[str]:
    langs = sorted(p.name for p in (ROOT / "_data/i18n").iterdir() if p.is_dir())
    return ["en"] + [x for x in langs if x != "en"]


def rtl_languages() -> set[str]:
    """The languages _data/languages.yml writes right to left, where the app mirrors its layout."""
    text = (ROOT / "_data/languages.yml").read_text(encoding="utf-8")
    return set(re.findall(r"^([\w-]+):\n(?:[ \t]+.*\n)*?[ \t]+dir:[ \t]*rtl\b", text, re.M))


def file_for(lang: str, name: str) -> Path:
    return OUT / lang / f"{name}.webp"


def trim(image: Image.Image, scale: float) -> Image.Image:
    """Cut the screen's empty bottom: rows that are all the page's own background."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    ground = rgb.getpixel((width // 2, height - 1))
    pixels = rgb.load()
    last = height - 1
    while last > 0 and all(
        max(abs(a - b) for a, b in zip(pixels[x, last], ground)) <= 3 for x in range(0, width, 2)
    ):
        last -= 1
    return image.crop((0, 0, width, min(height, last + 1 + round(TRIM_MARGIN * scale))))


def light_box(image: Image.Image, pad: float, scale: float) -> Image.Image:
    """Cut to the light box on a dark page, a message, with `pad` of the page around it."""
    mask = image.convert("L").point(lambda v: 255 if v > 200 else 0)
    left, top, right, bottom = mask.getbbox()
    p = round(pad * scale)
    return image.crop((max(0, left - p), max(0, top - p), min(image.width, right + p), min(image.height, bottom + p)))


def ring(image: Image.Image, box: list[float], scale: float) -> Image.Image:
    """A rounded ring around a box, drawn four times over and brought down, so its edge is smooth."""
    big = 4
    layer = Image.new("RGBA", (image.width * big, image.height * big), (0, 0, 0, 0))
    x, y, w, h = (round(v * scale * big) for v in box)
    ImageDraw.Draw(layer).rounded_rectangle([x, y, x + w, y + h], radius=round(10 * scale * big),
                                            outline=RING + (255,), width=round(2 * scale * big))
    out = image.convert("RGBA")
    out.alpha_composite(layer.resize(image.size, Image.LANCZOS))
    return out


def phone_screen(image: Image.Image, device: dict, width: int) -> Image.Image:
    """The screen of the store's phone, cut out of the picture of it: the phone sits in the middle
    of the device's canvas, its screen all of it but the bezel (PhoneFrame.cs in the tool). Brought
    down to `width`, then its corners rounded as the phone's own, the rim beyond them left clear;
    the mask is drawn four times over and brought down, so its edge is smooth."""
    scale = image.width / device["cssWidth"]
    screen_w = device["screenW"]
    screen_h = round(screen_w * device["cssHeight"] / device["cssWidth"])
    left, top = (device["cssWidth"] - screen_w) / 2, (device["cssHeight"] - screen_h) / 2
    image = image.crop(tuple(round(v * scale) for v in (left, top, left + screen_w, top + screen_h)))
    w, h = width, round(image.height * width / image.width)
    image = image.resize((w, h), Image.LANCZOS).convert("RGBA")
    big = 4
    mask = Image.new("L", (w * big, h * big), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * big - 1, h * big - 1],
                                           radius=round(device["screenRadius"] * w / screen_w * big), fill=255)
    image.putalpha(mask.resize((w, h), Image.LANCZOS))
    return image


def mirrored(box: list[float], width: float) -> list[float]:
    x, y, w, h = box
    return [width - x - w, y, w, h]


def finish(image: Image.Image, shot: dict, rtl: bool, device: dict) -> Image.Image:
    """Cut and mark a drawn screen, drawn on `device`; a box is measured on the English screen,
    and mirrored where the app lays the screen out right to left."""
    if shot.get("phone"):
        return phone_screen(image, device, shot["phone"])
    if shot.get("tv"):
        return image
    scale = shot.get("scale", SCALE)
    if shot.get("trim"):
        image = trim(image, scale)
    if shot.get("cut"):
        image = image.crop((0, 0, image.width, round(shot["cut"] * scale)))
    if shot.get("crop"):
        x, y, w, h = mirrored(shot["crop"], WIDTH) if rtl else shot["crop"]
        image = image.crop((round(x * scale), round(y * scale), round((x + w) * scale), round((y + h) * scale)))
    if shot.get("box"):
        image = light_box(image, shot["box"], scale)
    if shot.get("ring"):
        image = ring(image, mirrored(shot["ring"], image.width / scale) if rtl else shot["ring"], scale)
    return image


def build_tool() -> Path:
    project = next(TOOL.glob("*.csproj"))
    print(f"building  {project.name}", flush=True)
    subprocess.run(["dotnet", "build", str(project), "-c", "Debug", "-nologo", "-v", "q", "-clp:ErrorsOnly"],
                   check=True)
    dlls = sorted(TOOL.glob("bin/Debug/*/VpnHoodStoreScreenshots.dll"), key=lambda p: p.stat().st_mtime)
    if not dlls:
        sys.exit(f"The build left no VpnHoodStoreScreenshots.dll under {TOOL / 'bin/Debug'}.")
    return dlls[-1]


def write_config(product: str, shots: list[dict], langs: list[str]) -> Path:
    """A store configuration of the site's own: one 'store' per picture, as each has its own
    screen, every one with the Android phone's capabilities, drawn on a bare device or, for a
    picture of the whole screen, in the store's own phone; a TV's screen has the TV set's
    capabilities and its device."""
    store_dir = STORES[product]
    store = read_jsonc(store_dir / "screenshots.json")

    locales = {x["culture"]: x for x in store["locales"]}
    missing = [x for x in langs if x not in locales]
    if missing:
        sys.exit(f"The app has no {', '.join(missing)}: {store_dir / 'screenshots.json'} lists "
                 f"{', '.join(locales)}. Add the language to the app first.")

    platforms = {}
    patch_files = set()
    for shot in shots:
        platform = store["platforms"][TV if shot.get("tv") else PLATFORM]
        like = {x["route"]: x for x in platform["shots"]}.get(shot["route"], {})
        if platform.get("patchFile"):
            patch_files.add(platform["patchFile"])
        if shot.get("tv"):
            device = dict(next(iter(platform["devices"].values())), label="site", scale=TV_SCALE)
        elif shot.get("phone"):
            device = dict(platform["devices"][PHONE], label="site")
        else:
            device = {"label": "site", "frame": "none", "cssWidth": WIDTH,
                      "cssHeight": shot.get("height", HEIGHT), "scale": shot.get("scale", SCALE)}
        spec = {
            "route": shot["route"],
            "label": shot["name"],
            "patch": merge(json.loads(json.dumps(like.get("patch") or {})), shot.get("patch")),
            "hide": like.get("hide", []) + shot.get("hide", []),
        }
        platforms[shot["name"]] = {
            "label": shot["name"],
            "store": "site",
            "installDir": "-",
            "patch": platform.get("patch"),
            "patchFile": platform.get("patchFile"),
            "devices": {"site": device},
            "shots": [spec],
        }

    work = WORK / product
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(store_dir / "fixture.json", work / "fixture.json")
    for name in patch_files:
        shutil.copyfile(store_dir / name, work / name)
    config = {
        "installRoot": ".",
        "locales": [locales[x] for x in langs],
        "installedApps": store.get("installedApps", []),
        "platforms": platforms,
    }
    path = work / "screenshots.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def write_data(langs: list[str]) -> None:
    lines = [
        "# Written by tools/make-app-shots.py: never edit by hand.",
        "# The size in pixels of each app screenshot in assets/images/app/<lang>/, per language: each is",
        "# drawn at twice the size it is shown. _includes/app-shot.html reads it, and a language with",
        "# no picture of its own gets the English one.",
    ]
    for shot in SHOTS:
        sizes = [(lang, Image.open(file_for(lang, shot["name"])).size)
                 for lang in langs if file_for(lang, shot["name"]).exists()]
        if sizes:
            lines.append(f"{shot['name']}:")
            lines += [f"  {lang}: [{w}, {h}]" for lang, (w, h) in sizes]
    DATA.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def extras(langs: list[str]) -> list[Path]:
    wanted = {file_for(lang, shot["name"]) for lang in langs for shot in SHOTS}
    return [p for p in OUT.rglob("*") if p.is_file() and p not in wanted]


def check(langs: list[str]) -> int:
    missing = [file_for(lang, shot["name"]) for lang in langs for shot in SHOTS
               if not file_for(lang, shot["name"]).exists()]
    for p in missing:
        print(f"missing   {p.relative_to(ROOT).as_posix()}")
    for p in extras(langs):
        print(f"extra     {p.relative_to(ROOT).as_posix()}")
    return 1 if missing or extras(langs) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--only", help="picture names, comma-separated (default: all)")
    parser.add_argument("--lang", help="site languages, comma-separated (default: all)")
    parser.add_argument("--jobs", type=int, default=8, help="pictures drawn at once")
    parser.add_argument("--check", action="store_true", help="report missing or extra files, write nothing")
    args = parser.parse_args()

    all_langs = site_languages()
    if args.check:
        return check(all_langs)

    names = {x["name"]: x for x in SHOTS}
    unknown = [x for x in (args.only.split(",") if args.only else []) if x not in names]
    if unknown:
        sys.exit(f"There is no picture called {', '.join(unknown)}; there is {', '.join(names)}.")
    shots = [names[x] for x in args.only.split(",")] if args.only else SHOTS
    langs = args.lang.split(",") if args.lang else all_langs
    unknown = [x for x in langs if x not in all_langs]
    if unknown:
        sys.exit(f"The site has no {', '.join(unknown)}; it has {', '.join(all_langs)}.")

    dll = build_tool()
    for product in STORES:
        mine = [x for x in shots if x.get("product", "connect") == product]
        if not mine:
            continue
        config = write_config(product, mine, langs)
        out = WORK / product / "out"
        shutil.rmtree(out, ignore_errors=True)
        subprocess.run(["dotnet", str(dll), "generate", "--config", str(config), "--assets", str(ASSETS),
                        "--out", str(out), "--jobs", str(args.jobs)], check=True)

        written = json.loads(config.read_text(encoding="utf-8"))
        tags = {x["culture"]: x["tag"] for x in written["locales"]}
        rtl = rtl_languages()
        for shot in mine:
            device = written["platforms"][shot["name"]]["devices"]["site"]
            for lang in langs:
                image = Image.open(out / "final" / shot["name"] / f"1_{tags[lang]}.png").convert("RGB")
                image = finish(image, shot, lang in rtl, device)
                target = file_for(lang, shot["name"])
                target.parent.mkdir(parents=True, exist_ok=True)
                image.save(target, "WEBP", quality=88, method=6)
            print(f"wrote     {shot['name']} in {len(langs)} languages")

    for p in extras(all_langs):
        p.unlink()
        print(f"removed   {p.relative_to(ROOT).as_posix()}")
    write_data(all_langs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
