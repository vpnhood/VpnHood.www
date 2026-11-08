#!/usr/bin/env python3
"""Draw the app screenshots the site shows, in every language the site has.

A feature page shows the app's own screen, and a reader whose app speaks Persian should see
it in Persian, right to left, as their phone shows it. So every picture here is drawn by the
app's real UI once per language in _data/i18n/: the store screenshot tool in the VpnHood repo
(src/Apps/Tools/StoreScreenshots; its README explains it) starts the Avalonia UI headless
against the CLIENT store fixture, with no app, VPN or device. The languages, the Android
phone's capabilities and the demo apps come from the CLIENT store configuration, and a screen
the Google Play set also shows takes that shot's patch and hidden controls, so the site shows
what the listing shows. The screens are SHOTS below.

    python tools/make-app-shots.py                     # every picture in every language
    python tools/make-app-shots.py --only home --lang en,fa
    python tools/make-app-shots.py --check             # report missing or extra files

Writes assets/images/app/<lang>/<name>.webp, every one 840 wide, and _data/app_shots.yml with
the height of each, which _includes/app-shot.html reads. Never edit either by hand, and never
add these to make-light-art.py: app UI looks the same in both themes. Rerun it after a change
to the app's screens or words; the same inputs draw the same bytes, so git shows only the
pictures that changed.

Needs the .NET SDK, Pillow, and the VpnHood and Vpnhood.App.Client repos beside this one. Run
from the repo root. Each picture's fixture and full-size capture stay in .tmp/app-shots/, so a
wrong pixel can be chased with the tool's own `shot` command.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
VH = ROOT.parent / "VpnHood"
TOOL = VH / "src/Apps/Tools/StoreScreenshots"
ASSETS = VH / "src/AppUi/VpnHood.AppUi.Assets.Classic/assets"
STORE = ROOT.parent / "Vpnhood.App.Client/store"
PLATFORM = "android-phone"  # the store set whose capabilities and screens the site follows

OUT = ROOT / "assets/images/app"
DATA = ROOT / "_data/app_shots.yml"
WORK = ROOT / ".tmp/app-shots"

# The phone: 360 x 692 logical pixels is a phone's screen below its status bar, and 7/3 its
# pixel ratio, so a picture is 840 wide, the size the pages' width/height attributes give.
WIDTH = 360
HEIGHT = 692
SCALE = 7 / 3
# Below the last card of a trimmed page, as much screen as the page's own side margin.
TRIM_MARGIN = 16

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

# Each picture: its file name, the app page by its route (PageRoutes.cs in the tool), and
# what is not the phone's default:
#   height  a taller screen, in logical pixels, for a page the phone would scroll
#   trim    then cut the empty screen below the last card, for a page shorter than that
#   cut     then cut it to this height: the top of a long page, with no scroll bar
#   patch   what the app must be showing, laid over the store shot's own (FixtureComposer)
#   hide    controls to leave out, each a path of x:Names from the page down
SHOTS: list[dict] = [
    # the fixture's chosen profile is none of its profiles, so the row would say No Server;
    # the store's TV sets choose this one too
    {"name": "home", "route": "/",
     "patch": {"userSettings": {"vpnProfileId": "00000000-0000-4000-8000-000000000202"}}},
    {"name": "cloak-mode", "route": "/protocols/cloak-mode"},
    {"name": "protocols", "route": "/protocols"},
    {"name": "proxies", "route": "/settings/proxies", "height": 1200, "cut": 790,
     "patch": {"userSettings": {"proxySettings": {"mode": "Manual"}}, "proxyEndPoints": DEMO_PROXIES}},
    {"name": "private-dns", "route": "/dns"},
    {"name": "kill-switch", "route": "/settings/kill-switch"},
    {"name": "always-on", "route": "/settings/always-on"},
    {"name": "quick-launch", "route": "/settings/quick-launch"},
    {"name": "split-tunneling", "route": "/split-tunneling", "height": 1600, "cut": HEIGHT},
    {"name": "split-apps", "route": "/split-tunneling/split-apps", "height": 1200, "cut": HEIGHT},
    {"name": "split-countries", "route": "/split-tunneling/split-countries", "trim": True},
    {"name": "split-domains", "route": "/split-tunneling/split-domains", "height": 1000, "trim": True,
     "patch": {"userSettings": {"splitTunneling": {"useDomain": True}}}},
    {"name": "split-ips", "route": "/split-tunneling/split-ips-via-device", "height": 1000, "trim": True,
     "patch": {"userSettings": {"splitTunneling": {"useIpViaDevice": True}}}},
    {"name": "split-dns", "route": "/split-tunneling/split-dns", "trim": True},
    # connected to a server that lets a client reach its own network, as the page's switch needs
    {"name": "split-local-network", "route": "/split-tunneling/split-local-network", "trim": True,
     "patch": {"state": {"sessionInfo": {"isLocalNetworkAllowed": True}}}},
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


def file_for(lang: str, name: str) -> Path:
    return OUT / lang / f"{name}.webp"


def trim(image: Image.Image) -> Image.Image:
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
    bottom = min(height, last + 1 + round(TRIM_MARGIN * SCALE))
    return image.crop((0, 0, width, bottom))


def build_tool() -> Path:
    project = next(TOOL.glob("*.csproj"))
    print(f"building  {project.name}", flush=True)
    subprocess.run(["dotnet", "build", str(project), "-c", "Debug", "-nologo", "-v", "q", "-clp:ErrorsOnly"],
                   check=True)
    dlls = sorted(TOOL.glob("bin/Debug/*/VpnHoodStoreScreenshots.dll"), key=lambda p: p.stat().st_mtime)
    if not dlls:
        sys.exit(f"The build left no VpnHoodStoreScreenshots.dll under {TOOL / 'bin/Debug'}.")
    return dlls[-1]


def write_config(shots: list[dict], langs: list[str]) -> Path:
    """A store configuration of the site's own: one 'store' per picture, as each has its own
    screen height, every one with the Android phone's capabilities."""
    store = read_jsonc(STORE / "screenshots.json")
    platform = store["platforms"][PLATFORM]
    store_shots = {x["route"]: x for x in platform["shots"]}

    locales = {x["culture"]: x for x in store["locales"]}
    missing = [x for x in langs if x not in locales]
    if missing:
        sys.exit(f"The app has no {', '.join(missing)}: {STORE / 'screenshots.json'} lists "
                 f"{', '.join(locales)}. Add the language to the app first.")

    platforms = {}
    for shot in shots:
        like = store_shots.get(shot["route"], {})
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
            "devices": {"site": {
                "label": "site", "frame": "none",
                "cssWidth": WIDTH, "cssHeight": shot.get("height", HEIGHT), "scale": SCALE,
            }},
            "shots": [spec],
        }

    WORK.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(STORE / "fixture.json", WORK / "fixture.json")
    if platform.get("patchFile"):
        shutil.copyfile(STORE / platform["patchFile"], WORK / platform["patchFile"])
    config = {
        "installRoot": ".",
        "locales": [locales[x] for x in langs],
        "installedApps": store.get("installedApps", []),
        "platforms": platforms,
    }
    path = WORK / "screenshots.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def write_data(langs: list[str]) -> None:
    lines = [
        "# Written by tools/make-app-shots.py: never edit by hand.",
        "# The height of each app screenshot in assets/images/app/<lang>/, per language; every one is",
        "# 840 wide. _includes/app-shot.html reads it, and a language with no picture of its own gets",
        "# the English one.",
    ]
    for shot in SHOTS:
        heights = [(lang, Image.open(file_for(lang, shot["name"])).height)
                   for lang in langs if file_for(lang, shot["name"]).exists()]
        if heights:
            lines.append(f"{shot['name']}:")
            lines += [f"  {lang}: {height}" for lang, height in heights]
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
    shots = [names[x] for x in args.only.split(",")] if args.only else SHOTS
    langs = args.lang.split(",") if args.lang else all_langs
    unknown = [x for x in langs if x not in all_langs]
    if unknown:
        sys.exit(f"The site has no {', '.join(unknown)}; it has {', '.join(all_langs)}.")

    dll = build_tool()
    config = write_config(shots, langs)
    shutil.rmtree(WORK / "out", ignore_errors=True)
    subprocess.run(["dotnet", str(dll), "generate", "--config", str(config), "--assets", str(ASSETS),
                    "--out", str(WORK / "out"), "--jobs", str(args.jobs)], check=True)

    tags = {x["culture"]: x["tag"] for x in json.loads(config.read_text(encoding="utf-8"))["locales"]}
    for shot in shots:
        for lang in langs:
            image = Image.open(WORK / "out/final" / shot["name"] / f"1_{tags[lang]}.png").convert("RGB")
            if shot.get("trim"):
                image = trim(image)
            if shot.get("cut"):
                image = image.crop((0, 0, image.width, round(shot["cut"] * SCALE)))
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
