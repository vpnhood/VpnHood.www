#!/usr/bin/env python3
"""Fail the build on a link that points at the page it is on.

A link to the page you are already on is a dead end: it reloads the same page
and spends a click for nothing. They are easy to introduce without noticing,
because the text carrying the link usually lives somewhere shared - a FAQ answer
in _data/i18n/en/faqs.json is written once and rendered on up to eight pages,
and it is only a self-link on the one page it happens to name.

Three checks, all read-only:

  1. SOURCE. For every page that includes faq.html, the answers it selects are
     checked for a link to that page's own URL. This is the one that matters:
     _includes/faq-answer.html unwraps such a link at render time, so the built
     HTML looks fine while the page still carries a short version of itself,
     ending in "see <this page>". Keep the question out of that page's set in
     _data/faq_sets.yml.

  2. OUTPUT. Every rendered page body (<main id="sp-main-body">) is scanned for
     an <a> whose href resolves to that page's URL, which catches a self-link
     hand-written into page markup, where nothing unwraps it. Fragments (#faq)
     and query strings are NOT self-links - jumping to a section of the current
     page is real navigation - so they are skipped.

  3. INVARIANT. No FAQ answer carries more than one <a>. faq-answer.html finds
     the matching </a> by taking the first one after the opening tag, which is
     only correct while each answer holds a single link.

Check 2 reads the English tree only: the other twelve are clones of the same
source, so a finding there is the same finding repeated.

    python tools/check-self-links.py [site_dir]      # default: _site
    python tools/check-self-links.py --source-only   # no build needed

Exit code 1 and a list of findings when anything is wrong, 0 and a summary line
when the site is clean.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY_START = '<main id="sp-main-body"'
BODY_END = "</main>"
ANCHOR = re.compile(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', re.S)
FAQ_INCLUDE = re.compile(r"\{%-?\s*include\s+faq\.html(.*?)%\}", re.S)
TAGS = re.compile(r"<[^>]+>")
SKIP_DIRS = {"_site", "_sass", "node_modules", "vendor", "vh_translator", ".git", ".github", "tools"}


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def text_of(html):
    return re.sub(r"\s+", " ", TAGS.sub("", html)).strip()


def faqs():
    path = os.path.join(ROOT, "_data", "i18n", "en", "faqs.json")
    return json.load(io.open(path, encoding="utf-8"))


def faq_sets():
    """Parse _data/faq_sets.yml without a YAML dependency: `all:` and, under
    `sets:`, one two-space key per set with four-space `- name` items."""
    path = os.path.join(ROOT, "_data", "faq_sets.yml")
    out, current, in_sets = {}, None, False
    for raw in io.open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^sets:\s*$", line):
            in_sets, current = True, None
            continue
        top = re.match(r"^([A-Za-z_][\w-]*):\s*$", line)
        if top:
            in_sets = False
            current = top.group(1)
            out[current] = []
            continue
        if in_sets:
            name = re.match(r"^  ([A-Za-z_][\w-]*):\s*$", line)
            if name:
                current = name.group(1)
                out[current] = []
                continue
        item = re.match(r"^\s+-\s*(\S+)\s*$", line)
        if item and current:
            out[current].append(item.group(1))
    return out


def source_pages():
    """Every repo index.html that includes faq.html, as (url, [question names])."""
    sets = faq_sets()
    pages = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        if "index.html" not in files:
            continue
        m = FAQ_INCLUDE.search(read(os.path.join(root, "index.html")))
        if not m:
            continue
        args = m.group(1)
        keys = re.search(r'keys="([^"]*)"', args)
        name = re.search(r'set="([^"]*)"', args)
        if keys:
            selected = [k.strip() for k in keys.group(1).split(",")]
        else:
            selected = sets.get(name.group(1) if name else "", sets.get("all", []))
        rel = os.path.relpath(root, ROOT).replace("\\", "/")
        pages.append(("/" if rel == "." else "/" + rel + "/", selected))
    return pages


def check_source():
    answers, findings = faqs(), []
    for url, selected in source_pages():
        for q in selected:
            answer = answers.get("a_" + q)
            if answer and ('href="%s"' % url) in answer:
                findings.append(
                    '%s shows "%s", whose answer links to %s - the page names itself'
                    % (url, answers.get("q_" + q, q), url)
                )
    return findings


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


def check_output(site_dir):
    skip = language_dirs() | {"assets"}
    findings, scanned = [], 0
    for root, dirs, files in os.walk(site_dir):
        rel = os.path.relpath(root, site_dir).replace("\\", "/")
        if rel.split("/")[0] in skip:
            dirs[:] = []
            continue
        if "index.html" not in files:
            continue
        html = read(os.path.join(root, "index.html"))
        if BODY_START not in html or BODY_END not in html:
            continue  # legal pages and the blog use their own wrappers
        scanned += 1
        url = "/" if rel == "." else "/" + rel + "/"
        body = html[html.index(BODY_START):html.index(BODY_END)]
        for m in ANCHOR.finditer(body):
            href = m.group(1).split("#")[0].split("?")[0]
            if not href or href.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            if not href.endswith("/"):
                href += "/"
            if href == url:
                findings.append("%s links to itself in its markup, as %r" % (url, text_of(m.group(2))))
    return findings, scanned


def check_invariant():
    return [
        "faqs.json %s holds %d links; _includes/faq-answer.html assumes one"
        % (k, v.count("<a "))
        for k, v in faqs().items()
        if k.startswith("a_") and isinstance(v, str) and v.count("<a ") > 1
    ]


def main():
    args = [a for a in sys.argv[1:]]
    source_only = "--source-only" in args
    args = [a for a in args if not a.startswith("-")]
    findings = check_source() + check_invariant()
    scanned = 0
    if not source_only:
        site_dir = args[0] if args else os.path.join(ROOT, "_site")
        if not os.path.isdir(site_dir):
            sys.exit("no such directory: %s (run `bundle exec jekyll build` first)" % site_dir)
        out, scanned = check_output(site_dir)
        findings += out
    if findings:
        print("self-link check FAILED")
        for f in findings:
            print("  - " + f)
        print("\nA page must not carry a link to itself, and must not list a FAQ question")
        print("whose answer links to it. Fix it in _data/faq_sets.yml, not by editing the")
        print("answer: the same answer is useful on every other page that shows it.")
        sys.exit(1)
    print("self-link check passed: %d FAQ pages in source, %d page bodies built" % (len(source_pages()), scanned))


if __name__ == "__main__":
    main()
