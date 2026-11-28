"""After a deploy: clear Cloudflare's cache for the site's host, then check every stamped CSS and JS URL.

    python3 verify-deploy.py <deployed site folder> --host www.example.com --zone <Cloudflare zone id>

The deploy stamps each CSS and JS URL with its content hash (?v=<first 8 hex digits of its SHA-1>), and
Cloudflare keeps such URLs for a year in browsers. A stamped URL that serves other bytes, from a stale copy
anywhere between Cloudflare and GitHub Pages, would be wrong for that long. So each one the deployed pages
use is fetched through Cloudflare and its bytes hashed; one that differs, or answers with an error, is
purged and fetched again for about ten minutes, longer than GitHub Pages lets any cache keep a copy, and
the run fails if it is still wrong (its edge copy purged once more). The live home page must also be
this deploy's: the same build marker and the same stamped links. The check runs from one place, the
runner's Cloudflare location: a sample, not a guarantee for every visitor. The same script runs in
paymenthood-www and VpnHood.www.

CLOUDFLARE_PURGE_TOKEN is a token that may only purge the zone's cache. Without it the run fails, as a
deploy whose cache was not cleared must not look green.
"""
import argparse
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

STAMPED = re.compile(r'(?:href|src)="(/assets/(?:css|js)/[^"?#]+\.(?:css|js))\?v=([0-9a-f]{8})"')
BUILD = re.compile(r"<!-- build (\d+) -->")  # the marker each site's footer ends its pages with
PURGE = "https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache"
AGENT = "Mozilla/5.0 (compatible; deploy-check)"


def call(url: str, body: bytes, headers: dict) -> bytes:
    """A Cloudflare API call: retried on network errors, fatal on any other failure."""
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(url, data=body, method="POST",
                                             headers={"User-Agent": AGENT, **headers})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            sys.exit(f"::error::{url}: HTTP {error.code} {error.read()[:300]!r}")
        except (OSError, http.client.HTTPException) as error:  # network errors, also a connection cut mid-read
            if attempt == 3:
                sys.exit(f"::error::{url}: {error}")
            time.sleep(5 * attempt)
    raise AssertionError("unreachable")


def get(url: str) -> bytes | None:
    """A page or file as a visitor gets it, or None when it answers with an error or cannot be reached."""
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError:
            return None
        except (OSError, http.client.HTTPException):  # network errors, also a connection cut mid-read
            if attempt < 3:
                time.sleep(5 * attempt)
    return None


def purge(zone: str, token: str, body: dict) -> None:
    answer = json.loads(call(PURGE.format(zone=zone), json.dumps(body).encode(),
                             {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}))
    if not answer.get("success"):
        sys.exit(f"::error::Cloudflare refused the purge: {answer.get('errors')}")


def stamped_in(html: str) -> dict[str, str]:
    return {f"{path}?v={digest}": digest for path, digest in STAMPED.findall(html)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    parser.add_argument("--host", required=True)
    parser.add_argument("--zone", required=True)
    args = parser.parse_args()

    token = os.environ.get("CLOUDFLARE_PURGE_TOKEN", "")
    if not token:
        sys.exit("::error::CLOUDFLARE_PURGE_TOKEN is not set, so Cloudflare's cache was not cleared")

    stamped: dict[str, str] = {}
    for page in Path(args.site).rglob("*.html"):
        stamped.update(stamped_in(page.read_text(encoding="utf-8", errors="replace")))
    if not stamped:
        sys.exit("::error::the deployed pages have no stamped CSS or JS URL")
    # The live home page must link what the deployed one links: if it still linked old hashes, visitors would
    # fetch an old ?v= URL that now serves new bytes, and keep them for a year.
    home = Path(args.site, "index.html")
    if not home.is_file():
        sys.exit("::error::the deployed site has no index.html")
    home_html = home.read_text(encoding="utf-8", errors="replace")
    home_links, home_build = set(stamped_in(home_html)), BUILD.search(home_html)

    def files(urls: list[str]) -> None:
        for start in range(0, len(urls), 30):
            purge(args.zone, token, {"files": [f"https://{args.host}{url}" for url in urls[start:start + 30]]})

    time.sleep(30)  # GitHub Pages' own CDN serves the new deployment first
    purge(args.zone, token, {"hosts": [args.host]})
    print(f"cleared Cloudflare's cache for {args.host}")

    # About ten minutes in all: longer than the 600 seconds GitHub Pages lets any cache keep a copy.
    waits = (10, 20, 40, 80, 160, 320)
    wrong, home_ok, recheck_all = sorted(stamped), False, False
    for attempt, wait in enumerate(waits, start=1):
        time.sleep(wait)
        if recheck_all:  # the last round's host purge dropped every copy, so every URL is checked again
            wrong, recheck_all = sorted(stamped), False
        if not home_ok:
            live = get(f"https://{args.host}/")
            text = live.decode("utf-8", errors="replace") if live is not None else None
            live_build = BUILD.search(text) if text is not None else None
            home_ok = text is not None and set(stamped_in(text)) == home_links and (
                home_build is None or (live_build is not None and live_build.group(1) == home_build.group(1)))
        wrong = [url for url in wrong if (body := get(f"https://{args.host}{url}")) is None
                 or hashlib.sha1(body).hexdigest()[:8] != stamped[url]]
        if home_ok and not wrong:
            break
        print(f"check {attempt}: live home page is this deploy's: {home_ok}; {len(wrong)} stamped URLs wrong or failing"
              + (f": {', '.join(wrong[:5])}" if wrong else ""))
        if attempt == len(waits):
            break
        if not home_ok:
            purge(args.zone, token, {"hosts": [args.host]})
            recheck_all = True
        elif wrong:
            files(wrong)
    if not home_ok or wrong:
        if not home_ok:
            purge(args.zone, token, {"hosts": [args.host]})  # leave no stale copy at the edge
        else:
            files(wrong)  # leave no wrong copy at the edge
        reasons = []
        if not home_ok:
            reasons.append("the live home page is not this deploy's (another build marker, or other CSS or JS links)")
        if wrong:
            reasons.append(f"{len(wrong)} stamped URLs still serve other bytes or fail: {', '.join(wrong[:10])}")
        sys.exit("::error::" + "; ".join(reasons))
    print(f"the live home page is current, and all {len(stamped)} stamped CSS and JS URLs serve the bytes "
          f"their hash names (checked from this runner's Cloudflare location)")


if __name__ == "__main__":
    main()
