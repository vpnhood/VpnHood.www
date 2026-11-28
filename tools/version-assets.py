"""Stamp every local stylesheet and script URL in the built pages with a content hash.

    python3 tools/version-assets.py _site

    /assets/css/style.css  ->  /assets/css/style.css?v=3f9a1c2e

Why: a changed file that keeps its URL is not picked up by anyone who already has it
cached, so a new page can run against an old stylesheet, and Google's renderer, which may
ignore caching headers, can render a new page with old CSS. A hash in the URL makes a
changed file a new URL and leaves an unchanged one alone, so CSS and JS can be cached for
long. paymenthood-www does the same with scripts/version-assets.mjs.

CI runs it right after `jekyll build`, so the hash is taken from the final bytes in _site.
It rewrites _site only: `jekyll serve` and a local build keep plain URLs. It stamps the
double-quoted href="/assets/css/..." and src="/assets/js/..." attributes every template
writes. A file a script loads by URL (globe.js reads /assets/js/globe-points.json) keeps
its URL, so only stamped URLs may be given a long cache.
"""
import hashlib
import re
import sys
from pathlib import Path

REF = re.compile(r'((?:href|src)=")(/assets/(?:css|js)/[^"?#]+\.(?:css|js))(\?[^"#]*)?(")')


def main(site: Path) -> int:
    if not site.is_dir():
        print(f"version-assets: {site} is not a folder; build the site first")
        return 1
    hashes: dict[str, str | None] = {}
    missing: set[str] = set()
    refs = 0

    def hash_of(url_path: str) -> str | None:
        if url_path not in hashes:
            file = site / url_path.lstrip("/")
            hashes[url_path] = hashlib.sha1(file.read_bytes()).hexdigest()[:8] if file.is_file() else None
        return hashes[url_path]

    def stamp(match: re.Match) -> str:
        nonlocal refs
        open_attr, url_path, _query, close = match.groups()
        digest = hash_of(url_path)
        if digest is None:
            missing.add(url_path)
            return match.group(0)
        refs += 1
        return f"{open_attr}{url_path}?v={digest}{close}"

    files = changed = 0
    for page in sorted(site.rglob("*.html")):
        # bytes in and out, so the page's line endings stay exactly as Jekyll wrote them
        before = page.read_bytes().decode("utf-8")
        after = REF.sub(stamp, before)
        files += 1
        if after != before:
            page.write_bytes(after.encode("utf-8"))
            changed += 1

    print(f"version-assets: {refs} references stamped in {changed} of {files} html files")
    # A page linking a file the build does not have, or no stamped link at all, would deploy a site whose
    # long cache no longer works as meant: fail instead.
    if missing:
        print("version-assets: no such file in _site, so left unstamped: " + ", ".join(sorted(missing)))
    if refs == 0:
        print("version-assets: no CSS or JS link was stamped")
    return 1 if missing or refs == 0 else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "_site")))
