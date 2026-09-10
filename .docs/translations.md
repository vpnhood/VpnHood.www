# Translations (build-time language trees)

The full picture behind the "Translations" summary in [CLAUDE.md](../CLAUDE.md). Only
**strings** are ever translated; pages are generated. Two halves:

## 1. Strings — `vhtranslator`

VpnHood.Tools.ResourceTranslator, classic folder mode; config at
`vh_translator/vhtranslator.json` (`base: _data/i18n/en`, currently 12 target languages).
It translates the English data folder file-by-file, key-by-key (incremental via committed
watches) into sibling folders (`_data/i18n/fa/…`). This includes each page's
`meta_title`/`meta_description`. The i18n files are flat string maps; anything under
`_data/` outside `i18n/en` (for example `_data/faq_sets.yml`) is never translated, which is
where page *structure* belongs.

For RTL targets the tool appends an invisible LRM after Latin-word `!`/`?` so "VpnHood!"
renders correctly — but **only when the next word is actually translated** (RTL) or the
string ends; "VpnHood! CLIENT" and `VpnHood!<span>ENGINE</span>` stay inside one Latin run
and get no mark. **Never put an LRM (`&lrm;`/U+200E) in the English source** — page markup
that needs a brand literal in an RTL page uses `dir="ltr"` on the element instead (see the
logo/preloader in `header.html`).

CI runs the translator before every deploy and commits results back (see
[build-and-deploy.md](build-and-deploy.md)). Translator bookkeeping lives in
`vh_translator/watches/i18n/<file>.watch.json` — commit it.

**Never hand-edit generated data folders** (`_data/i18n/<lang>/` — overwritten by the tool).
Fixes go in `vh_translator/prompt.txt`, or `vh_translator/prompts/<lang>.prompt.txt` for one
language; per-key edits in the generated JSON survive until the source key changes.

**New keys lag translation.** Between an English edit and the next CI run, a new key does
not exist in the other languages, and a bare `{{ t.new_key }}` renders empty there. Any
include that reads data therefore falls back per key — `{{ t.x | default: t_en.x }}` — as
`faq.html`, `compare-table.html` and the chrome strings do. Renaming a key is the same as
adding one; the old translations are simply orphaned, so there is no need to delete the
generated files.

## 2. Pages — `_plugins/i18n-pages.rb`

Clones every page that declares `i18n:` front matter, once per language, **at Jekyll build
time** — no translated page copies exist in the repo. Languages are discovered from
`_data/i18n/<code>/` folders (same rule as the selector): committing a translated data
folder is all it takes for its whole `/xx/` tree, hreflang set, sitemap entries, and
selector entry to appear. Each clone gets `lang` + an explicit `permalink: /<lang>/<path>/`
and joins `site.pages`. Opt a page out with `translate: false` front matter; legal pages
have no `i18n:` key and are never cloned. Adding a language = add it to `languages` in the
config, let the translator (or CI) fill the data folder.

`_plugins/i18n-meta.rb` injects `meta_title`/`meta_description` into
`page.title`/`page.description` at build time (keyed by the page's `i18n:` front matter,
empty/missing keys fall back to English), so the hand-written `<title>` tag and
jekyll-seo-tag see them exactly as if they were front matter — a new page needs both keys
in its JSON, and `meta_title` must contain "VpnHood!".

`header.html` derives **reciprocal hreflang + `x-default`** from the generated pages'
`lang` and sets `<html lang>`/`dir` from `page.lang` + `_data/languages.yml` — see
[seo-and-semantic-html.md](seo-and-semantic-html.md) §8 before touching any of it. Never
add body-level `inLanguage` microdata.

## Language-aware links (`vh_base`)

`header.html` assigns `vh_base` once per page (`''` on English, `/fa` on Persian, …; Jekyll
includes share Liquid scope). **Every internal link must be written
`href="{{ vh_base }}/free-vpn/download/"`** so translated pages link within their own tree
— a bare `href="/free-vpn"` on a fa page would jump back to English. Exceptions (never
prefixed, but still trailing-slashed): legal pages (`/privacy-policy/`,
`/legal/terms-of-use/`, `/vpnhood-*-privacy-policy/`, `/legal/vpnhood-*-terms-of-use/` —
English only by policy). Never slashed: `/assets/...` and external URLs.

**Always the trailing slash.** Jekyll serves every page as `<path>/index.html`, so
`/free-vpn/` is the canonical URL and GitHub Pages 301s `/free-vpn` to it. Google does
honour that redirect (URL Inspection reports the slashless form as "Page with redirect",
canonical = the slashed one), so this is a crawl-efficiency and UX rule, not a
duplicate-content fix: linking without the slash costs a redirect hop on every internal
navigation. Search Console reports the slashless variants as separate URLs, which is why
they show up in performance data.

## Chrome strings (`chrome.json`)

All header/footer/offcanvas/language-selector text (nav labels, mega-menu blurbs, footer
columns, copyright, aria-labels) lives in `_data/i18n/<lang>/chrome.json`; `header.html`
assigns `tc` once per page (English fallback) and the includes render `{{ tc.* }}`. **Edit
chrome copy there, never in the includes.**

## Verifying a copy refactor

The original i18n extraction (moving every string out of page markup into
`_data/i18n/en/`) was verified by whitespace-normalised diffs of the built `_site` pages
before and after. Keep that technique for any future refactor that must not change rendered
output.
