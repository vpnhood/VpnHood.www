#!/usr/bin/env python3
"""Keep every placeholder intact through translation.

The copy (_data/i18n/en/*.json) never holds a value the site fills in. A price
is [amount], a count is [count], and a command or path is a name such as
[vhserver_gen], kept inside its <code> tags, whose value lives in
_data/code.yml; the page swaps each one in at build time, so the translator
never sees the value itself. It does see the placeholder - and a translation
that drops, renames or invents one renders a price, a count or a command wrong,
in a language the author cannot read.

So every translation must hold exactly its English source's placeholders and
<code> spans, tags included, byte for byte. Their order may change, since a
sentence is free to move them. A key a translation does not have yet is
skipped: it has not been translated. Run this after the translator - a
translation that is merely stale, its English edited since, differs too.

    python tools/check-placeholders.py           # report; exit 1 on a mismatch
    python tools/check-placeholders.py --heal    # CI: replace each mismatched
                                                 # translation with its English
                                                 # source, warn, exit 0

--heal fails closed for the reader: the page shows one English sentence instead
of a wrong price or command, and the deploy goes ahead. It rewrites only that
key's value in the generated file, so the translator's formatting is untouched
and the commit-back step records exactly what was deployed. The English stays
until the source string changes and the translator tries again; to retry
sooner, delete the key from the generated file - a missing key is always
translated on the next run.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = os.path.join(ROOT, "_data", "i18n")
PLACEHOLDER = re.compile(r"\[[a-z0-9_]+\]")
CODE = re.compile(r"<code\b[^>]*>.*?</code>", re.S)


def read(path):
    # newline="" keeps the file's own line endings when it is written back.
    return io.open(path, encoding="utf-8", newline="").read()


def tokens(value):
    """Placeholders and <code> spans, sorted: a placeholder inside a span counts
    once on its own and once as part of the span."""
    if not isinstance(value, str):
        return []
    return sorted(PLACEHOLDER.findall(value) + CODE.findall(value))


def languages():
    return sorted(d for d in os.listdir(I18N) if d != "en" and os.path.isdir(os.path.join(I18N, d)))


def check():
    """Return (findings, English strings holding tokens, translations checked);
    a finding is (lang, file, key, English tokens, translated tokens)."""
    findings, guarded_total, checked = [], 0, 0
    langs = languages()
    for name in sorted(os.listdir(os.path.join(I18N, "en"))):
        if not name.endswith(".json"):
            continue
        source = json.loads(read(os.path.join(I18N, "en", name)))
        guarded = {k: tokens(v) for k, v in source.items() if tokens(v)}
        guarded_total += len(guarded)
        if not guarded:
            continue
        for lang in langs:
            path = os.path.join(I18N, lang, name)
            if not os.path.isfile(path):
                continue
            target = json.loads(read(path))
            for key, want in guarded.items():
                got = target.get(key)
                if not isinstance(got, str) or not got.strip():
                    continue
                checked += 1
                if tokens(got) != want:
                    findings.append((lang, name, key, want, tokens(got)))
    return findings, guarded_total, checked


def value_at(key):
    """The key's line in a flat i18n file: group 1 up to the value, group 2 the
    quoted JSON string exactly as written."""
    return re.compile(r'^([ \t]*"%s"[ \t]*:[ \t]*)("(?:[^"\\\r\n]|\\.)*")' % re.escape(key), re.M)


def heal(findings):
    """Swap each mismatched translation for the English source string, copied
    verbatim from the source file, then prove the result parses to it."""
    by_file = {}
    for lang, name, key, _, _ in findings:
        by_file.setdefault((lang, name), []).append(key)
    for (lang, name), keys in sorted(by_file.items()):
        source_text = read(os.path.join(I18N, "en", name))
        path = os.path.join(I18N, lang, name)
        text = read(path)
        for key in keys:
            english, n = value_at(key).search(source_text), 0
            if english:
                text, n = value_at(key).subn(lambda m: m.group(1) + english.group(2), text, count=1)
            if n != 1:
                sys.exit("cannot heal %s/%s %s: the key is not on a line of its own" % (lang, name, key))
        source, healed = json.loads(source_text), json.loads(text)
        if any(healed.get(k) != source.get(k) for k in keys):
            sys.exit("cannot heal %s/%s: the rewritten file does not hold the English strings" % (lang, name))
        io.open(path, "w", encoding="utf-8", newline="").write(text)


def count(n, noun):
    return "%d %s%s" % (n, noun, "" if n == 1 else "s")


def describe(finding):
    lang, name, key, want, got = finding
    return "%s/%s %s\n      en: %s\n      %s: %s" % (
        lang, name, key, "  ".join(want), lang, "  ".join(got) or "(none at all)")


def main():
    # A console that cannot show Persian or Arabic must not turn a report into a crash.
    sys.stdout.reconfigure(errors="backslashreplace")
    healing = "--heal" in sys.argv[1:]
    findings, guarded, checked = check()
    if not findings:
        print("placeholder check passed: %s of %s with placeholders, every one intact"
              % (count(checked, "translation"), count(guarded, "English string")))
        return
    if healing:
        heal(findings)
        print("placeholder check: %s changed a placeholder; each now shows its English source"
              % count(len(findings), "translated string"))
        for f in findings:
            print("  - " + describe(f))
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print("::warning title=Translation discarded::%s/%s %s changed a placeholder; "
                      "the page shows the English sentence instead" % f[:3])
        return
    print("placeholder check FAILED: %s changed a placeholder" % count(len(findings), "translated string"))
    for f in findings:
        print("  - " + describe(f))
    print("\nA placeholder stands for a price, a count or a command the page fills in, so it")
    print("must survive translation byte for byte. CI runs this with --heal, which shows the")
    print("English sentence in its place. To have the translator try again instead, delete")
    print("the key from the generated file. Straight after an English edit, the stale")
    print("translations show up here too, until the translator has run.")
    sys.exit(1)


if __name__ == "__main__":
    main()
