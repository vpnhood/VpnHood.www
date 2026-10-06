#!/usr/bin/env python3
"""Fail the build on an internal link, anchor or asset that does not resolve.

A broken link is a dead end for the reader and a small loss of trust with search
engines, and on this site one broken string is rarely broken once: every page is
cloned into each language tree, and a link in the header or footer is on every
page of every tree. So this reads the BUILT site - all thirteen trees, whole
pages, header, footer and sidebars included, not only <main> - and resolves each
internal reference against the files Jekyll wrote, which covers pages, collection
documents and redirect stubs alike.

Four checks, all read-only:

  1. TARGETS. Every internal URL - <a> and <link> href (canonical, hreflang
     alternates, icons, stylesheets), <img>/<source> src and srcset, <script>,
     <video>, <iframe>, the share-image meta tags and a redirect stub's refresh
     target - must name a file in the build: /x/ is x/index.html, a path with an
     extension is that file.
  2. ANCHORS. A fragment (/x/#faq, or #faq on the same page) must match an id, or
     an <a name>, on the target page. #top and a bare # are browser built-ins.
  3. SLASHES. /x for a page that exists as /x/ is reported: GitHub Pages answers
     it with a redirect, and every internal link here is written with the slash.
  4. EMPTY OR RETIRED. href="" (a variable that was never assigned renders as
     nothing), a value still holding Liquid, and an <a> that points at a redirect
     stub, which costs the reader a hop; link to the page the stub sends them to.

Internal means root-relative, or absolute on this site's own host (_config.yml
`url`, its bare domain, or localhost, which `jekyll serve` writes into a local
build). External links are not checked: a deploy must not depend on the uptime and
rate limits of GitHub, the app stores and everyone else we link to.

A problem on a legal page (rendered through _includes/legal-page.html, so inside
.legal-content) is a WARNING and does not fail the build. That text is synced from
the VpnHood repo at build time and fixed there; failing here would let one edit in
another repo stop every deploy of this one.

    python tools/check-links.py [site_dir]     # default: _site

Exit code 1 and the problems when anything is wrong, grouped by target with the
language prefix folded away, so a broken chrome link reads as one problem in
thirteen trees, not 500 lines; 0 and a summary line when the site is clean.
"""
from __future__ import annotations

import io
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The attributes that carry a URL, per tag. srcset holds several, comma-separated.
URL_ATTRS = {
    "a": ("href",),
    "link": ("href",),
    "img": ("src", "srcset"),
    "source": ("src", "srcset"),
    "script": ("src",),
    "video": ("src", "poster"),
    "audio": ("src",),
    "iframe": ("src",),
}
META_URLS = {"og:image", "og:url", "twitter:image"}
REFRESH_URL = re.compile(r"url\s*=\s*['\"]?([^'\";]+)", re.I)
OTHER_SCHEMES = ("mailto:", "tel:", "sms:", "javascript:", "data:")
BUILTIN_FRAGMENTS = {"", "top"}
EXAMPLES = 3


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def config_url():
    try:
        for line in io.open(os.path.join(ROOT, "_config.yml"), encoding="utf-8"):
            m = re.match(r"""^url:\s*["']?(https?://[^"'\s]+)""", line)
            if m:
                return m.group(1)
    except OSError:
        pass
    return ""


def own_hosts():
    """This site's hosts: the configured one, its bare domain, and what a local
    `jekyll serve` writes into absolute URLs."""
    hosts = {"localhost:4000", "127.0.0.1:4000", "localhost", "127.0.0.1"}
    host = urlsplit(config_url()).netloc
    if host:
        hosts |= {host, host[4:] if host.startswith("www.") else host}
    return hosts


def language_dirs():
    """Language codes from _data/languages.yml, read without a YAML parser: they
    are the un-indented keys."""
    codes = set()
    try:
        for line in io.open(os.path.join(ROOT, "_data", "languages.yml"), encoding="utf-8"):
            m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*$", line)
            if m and m.group(1) != "en":
                codes.add(m.group(1))
    except OSError:
        pass
    return codes


class Page(HTMLParser):
    """One built page: the ids it defines, whether it is a redirect stub or a synced
    legal page, and every URL it references, as (tag, attribute, value)."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.is_stub, self.is_synced = set(), [], False, False
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if a.get("id"):
            self.ids.add(a["id"])
        if "legal-content" in a.get("class", "").split():
            self.is_synced = True
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for attr in URL_ATTRS.get(tag, ()):
            if attr not in a:
                continue
            if attr == "srcset":
                for candidate in a[attr].split(","):
                    url = candidate.strip().split(" ")[0]
                    if url and not url.startswith("data:"):
                        self.refs.append((tag, attr, url))
            else:
                self.refs.append((tag, attr, a[attr]))
        if tag == "meta":
            key = a.get("property") or a.get("name") or ""
            if key in META_URLS and "content" in a:
                self.refs.append((tag, key, a["content"]))
            if a.get("http-equiv", "").lower() == "refresh":
                self.is_stub = True
                m = REFRESH_URL.search(a.get("content", ""))
                if m:
                    self.refs.append((tag, "refresh", m.group(1).strip()))


class Site:
    def __init__(self, site_dir):
        self.dir = site_dir
        self.hosts = own_hosts()
        self.langs = language_dirs()
        self.internal = 0
        self._pages = {}

    def page(self, path):
        if path not in self._pages:
            self._pages[path] = Page(read(path))
        return self._pages[path]

    def url_of(self, path):
        rel = os.path.relpath(path, self.dir).replace("\\", "/")
        if rel == "index.html":
            return "/"
        if rel.endswith("/index.html"):
            return "/" + rel[: -len("index.html")]
        return "/" + rel

    def file_of(self, url_path):
        """The built file a URL path names, or None."""
        path = unquote(url_path)
        if path.endswith("/"):
            path += "index.html"
        full = os.path.join(self.dir, *path.lstrip("/").split("/"))
        return full if os.path.isfile(full) else None

    def fold(self, url):
        """/fa/x/ and /x/ are the same problem in two trees: drop the prefix."""
        parts = url.split("/", 2)
        if len(parts) > 2 and parts[1] in self.langs:
            return "/" + parts[2]
        return url

    def judge(self, page_url, tag, value):
        """Why this reference is broken, and its target - or (None, None)."""
        raw = value.strip()
        if not raw:
            return "empty URL", '""'
        if "{{" in raw or "{%" in raw:
            return "unrendered Liquid", raw
        if raw.lower().startswith(OTHER_SCHEMES):
            return None, None
        parts = urlsplit(urljoin(page_url, raw))
        if parts.scheme not in ("", "http", "https"):
            return None, None
        if parts.netloc and parts.netloc not in self.hosts:
            return None, None
        self.internal += 1
        path = parts.path or page_url
        target = self.file_of(path)
        if target is None:
            has_ext = os.path.splitext(path.rstrip("/"))[1]
            if not path.endswith("/") and not has_ext and self.file_of(path + "/"):
                return "no trailing slash", path
            return "no such page or file", path
        if tag == "a" and target.endswith(".html") and self.page(target).is_stub:
            return "links to a redirect stub", path
        fragment = unquote(parts.fragment)
        if fragment not in BUILTIN_FRAGMENTS and target.endswith(".html"):
            if fragment not in self.page(target).ids:
                return "no such anchor", path + "#" + fragment
        return None, None

    def check(self):
        problems, warnings, scanned = {}, {}, 0
        for root, dirs, files in os.walk(self.dir):
            dirs.sort()
            for name in sorted(files):
                if not name.endswith(".html"):
                    continue
                path = os.path.join(root, name)
                page_url = self.url_of(path)
                page = self.page(path)
                scanned += 1
                for tag, attr, value in page.refs:
                    reason, target = self.judge(page_url, tag, value)
                    if reason:
                        key = (reason, self.fold(target), "<%s %s>" % (tag, attr))
                        bucket = warnings if page.is_synced else problems
                        bucket.setdefault(key, []).append(page_url)
        return problems, warnings, scanned

    def trees(self, pages):
        return len({p.split("/")[1] if p.split("/")[1] in self.langs else "en" for p in pages})


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    site_dir = args[0] if args else os.path.join(ROOT, "_site")
    if not os.path.isdir(site_dir):
        sys.exit("no such directory: %s (run `bundle exec jekyll build` first)" % site_dir)
    site = Site(site_dir)
    problems, warnings, scanned = site.check()
    if warnings:
        print("link check warnings, on legal pages synced from the VpnHood repo (fix them")
        print("in its docs/legal/end-user/; they do not fail this build):")
        report(site, warnings)
    if problems:
        print("link check FAILED: %d problems" % len(problems))
        report(site, problems)
        print("\nTargets are shown with the language prefix folded away (/fa/x/ is /x/).")
        print("Fix the source - the page, its JSON copy or the include - never _site.")
        sys.exit(1)
    print("link check passed: %d pages, %d internal references, all resolve" % (scanned, site.internal))


def report(site, found):
    for (reason, target, where), pages in sorted(found.items()):
        unique = sorted(set(pages))
        print("  - %s: %s  in %s" % (reason, target, where))
        print("      %d trees, %d pages, e.g. %s"
              % (site.trees(unique), len(unique), ", ".join(unique[:EXAMPLES])))


if __name__ == "__main__":
    main()
