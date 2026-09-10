# Components and includes

The full picture behind the "Components" summary in [CLAUDE.md](../CLAUDE.md).

## FAQ — `_includes/faq.html` + `_data/i18n/<lang>/faqs.json` + `_data/faq_sets.yml`

Data-driven and translatable: renders the Bootstrap accordion **and** the `FAQPage` JSON-LD
from **name-keyed** pairs (`q_is_open_source`/`a_is_open_source`, …) plus the section chrome
(`eyebrow`/`heading`/`desc`/`view_all`), selected by `page.lang` with **per-key** English
fallback (so a question added in English shows everywhere at once instead of rendering
blank until vhtranslator catches up).

**Which questions a page shows, and in what order, lives in `_data/faq_sets.yml`** —
structure, not copy, so the translator (which only walks `_data/i18n/en`) never touches it.
Entries are base names (`is_open_source` → `q_`/`a_`); `all` is the full ordered list used
by `/faq`; `sets:` holds the per-page selections. Pick 3–4 questions a visitor to that page
is actually wondering — the same six answers repeated on every URL is near-duplicate body
text. Used on 7 pages.

Params: `set` (a name under `sets:`; unknown falls back to `all`), `keys` (comma-separated
base names, a one-off that beats `set`), `heading` (default true — `/faq` passes
`heading=false` to emit just the accordion under its own `<h1>`), `explore` (default true;
`/faq` passes `explore=false`), `wrapper_class` (default `section-space`; footer-adjacent
pages pass `section-space-top`), `eyebrow`, `schema`.

**Only `/faq` emits the FAQPage JSON-LD**; every other page passes `schema=false`, since
several pages each declaring a different FAQPage entity duplicates the entity for no gain —
Google restricted FAQ rich results to government and health sites in 2023, so the markup is
inert either way. Internal links inside answers are rewritten via `vh_base`. DOM ids are
`#faq-<name>`, so they stay stable when a question is inserted. **Edit FAQ copy in
`_data/i18n/en/faqs.json`, not in the pages.** Never hand-write FAQ accordion markup or
FAQPage schema per page.

## Compare table — `_includes/compare-table.html`

The Free-vs-Premium feature table, rendered on `/free-vpn/go-premium/`
(`/free-vpn/free-vs-premium/` was retired in September 2026 and redirects there; the
"Free vs Premium" nav entry points at `/free-vpn/go-premium/#compareTable`). Params
`heading` (tag for the column titles, default `h2`; go-premium passes `h3`) and
`heading_class` (go-premium passes `h2`). Strings from
`_data/i18n/<lang>/free_vpn_free_vs_premium.json`, with per-key English fallback. Feature
rows link to their `/features/` pages and the data/speed rows to `/free-vpn/#unlimited`
(`.vh-cmp-link`, global in `_default.scss`); the remaining plan rows (locations, ads,
support, platforms) don't link. The table stays decision-focused — rows where both plans
tick add little, and the "See every feature explained" link under it carries the long tail.
Never duplicate the table markup in pages. The mobile heading rule must match every heading
tag the include can render (`#compareTable #header :is(h2, h3, h4)`), or the `h3.h2` variant
overflows its 27%-wide column.

## Typewriter text — `_includes/multi-text-writer.html`

The self-typing text loop (currently the Premium card on `/free-vpn/`). Pass `keys="a,b,c"`
— comma-separated key names from the page's i18n data file, typed in that order; optional
`class`. Renders the animated span plus a hidden phrase list that `vh-general.js` reads, so
the copy is translatable and empty/missing keys are skipped. **Never hardcode typed phrases
in JS.**

## Theme toggle — `_includes/theme-toggle.html` + `assets/js/theme.js`

See [colour-themes.md](colour-themes.md).

## Language selector — `_includes/lang-selector.html` + `_data/languages.yml` + `assets/js/lang.js`

Renders **nothing until a second language exists**: languages are discovered from
`site.data.i18n` folder keys (no registry — a language appears when vhtranslator drops its
`_data/i18n/<code>/` folder); `_data/languages.yml` only maps codes to native display
names. Used twice, and it is the **same Bootstrap dropdown** both times — `header.html`
drops the bare `<li>` into the desktop `#topRightMenu` (already a `<ul>`), `footer.html`
renders it in the mobile offcanvas by passing `wrapper_class` (which wraps it in its own
`<ul>`) plus `align="start"`. The second caller **must** pass its own `id`: both instances
are in the DOM of every page, so a shared toggle id would duplicate and break
`aria-labelledby`. Each entry links to the current page's counterpart when it exists
(checked against `site.pages`), else that language's home. `lang.js` persists clicks in
`localStorage vh_lang` and, **on English pages only** (crawler-safe), redirects a
stored/browser-preferred language to its translation using the page's own hreflang
alternates (never 404s). Preview with `?vh_lang=fa`.

## Legal pages — `_includes/legal-page.html` + `_includes/legals/*.md`

See [legal-pages.md](legal-pages.md).

## China promo bar — `assets/js/china-bar.js`

See [china-bar-geo.md](china-bar-geo.md).

## Shared header/footer

`header.html` renders the `<head>`, the framework JS, and the sticky nav, and
**intentionally leaves `.body-wrapper` + `.body-innerwrapper` (and `<body>`/`<html>`)
OPEN**; `footer.html` closes them (plus the off-canvas menu and page scripts). **Do NOT
auto-format/"balance" these two includes** — an HTML formatter that closes the wrappers
early breaks the page wrapper (the home globe stops being clipped by
`.body-innerwrapper{overflow-x:hidden}` and the mobile layout overflows). `.prettierignore`
guards them. `header.html` div balance must be net **+2** opens. It also opens `<html>` with
`data-theme="dark"` and runs the pre-paint theme bootstrap. Both are shared by every page —
edits there are global; make them deliberate.
