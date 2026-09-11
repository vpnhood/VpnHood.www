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

**Never put a question in the set of the page its answer links to.** The answer would render
a link to the page the reader is already on, and it is usually a short version of what that
page says at length, so the page repeats itself. The answers that link out are
`is_vpnhood_free` and `supported_platforms` (→ `/free-vpn/go-premium/`), `why_slower`
(→ `/guides/vpn-speed/`) and `many_servers_per_location` (→ `/free-vpn/locations/`); the
same rule applies to any new answer carrying a link.

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

## CTA tracking

Any element with `data-vh-track="<id>"` pushes one event to `dataLayer` when clicked
(`assets/js/vh-general.js`, "CTA click tracking"). The push is
`{ event: "vh_cta_click", vh_cta: "<id>", vh_href: "<href>" }`; nothing in our code talks
to Google directly, and the click is never delayed. Tagged today: the header's
`header-download`, `header-go-premium`, `header-log-in` and the mobile menu's
`menu-download`, `menu-go-premium`, `menu-log-in`. Keep ids kebab-case and
`<place>-<action>`, so the same action in two places stays comparable.

Nothing reaches GA4 until GTM (container `GTM-M39NR6ZS`) forwards it. One-time setup:

1. **Variable** — Data Layer Variable, name `DLV - vh_cta`, variable name `vh_cta`.
   Optionally a second one for `vh_href`.
2. **Trigger** — Custom Event, event name `vh_cta_click`, fires on all custom events.
3. **Tag** — Google Analytics: GA4 Event, event name `cta_click`, event parameter
   `cta_id` = `{{DLV - vh_cta}}`, trigger = the one above.
4. **GA4 Admin → Custom definitions** — register `cta_id` as an event-scoped custom
   dimension, or it will not appear in reports.

Then Reports → Engagement → Events → `cta_click`, broken down by `cta_id`, answers
"what does the header slot earn" with real clicks instead of reasoning.

## Locations

`_data/locations.yml` is the single source of truth for every country the site names:
key, ISO code (names the flag in `assets/images/flags/`, vendored from HatScripts
circle-flags, MIT, licence alongside), tier, continent, and a lat/lng for the globe
and the map.
Names are the only translated part, in `_data/i18n/en/locations.json`
(`country_<key>`, `continent_<key>`, `tier_*`); read them with the same per-key
English fallback as the chrome. Surfaces that read the list:

- `/free-vpn/locations/` - the stat strip, the map (`location-map.html` with
  `pills=false`, since the grid names everything), then the flag grid grouped by
  continent. The three numbers are Liquid `size`s of the list, so a sentence
  never has to carry a count.
- `/free-vpn/` `#locations` - `_includes/location-map.html`: a dotted world map
  with a pulsing pin per country (green free, purple Premium, name in a hover
  tooltip) and, under it, the same linear slider as the home strip with a
  `.vh-flag-pill` per country, the free ones badged. The map is `aria-hidden`;
  the strip is the accessible list (the slider's clones are `aria-hidden`). The land
  is `assets/images/general/world-dots.svg` as a CSS mask coloured by
  `--vh-map-dot`, so it needs no light variant. Pins are placed by Liquid:
  `left = (lng + 180) / 3.6 %`, `top = (84 - lat) / 1.4 %` (viewBox 360 x 140,
  latitude 84 to -56, no Antarctica).
- home `#flagSlider` - one `.vh-flag-pill` per country, same order as the file.
- home globe - `assets/js/globe-points.json` is a Jekyll-rendered page: static
  land dots from `_includes/globe-land-points.json` plus one country dot per
  entry, `x = (lng + 180) * 5.6889`, `y = (90 - lat) * 5.6889` on the 2048 x 1024
  canvas `globe.js` wraps onto the sphere. `globe.js` starts its camera on
  `startingCountry`, which must be a key in the list.

Both dot sets come from `python tools/make-land-dots.py`, which samples
`tools/ne_110m_land.geojson` (Natural Earth 1:110m land, public domain) on a
true equirectangular grid; rerun it to change pitch or crop, never hand-edit the
outputs. The dots it replaced were traced from a decorative map that narrowed the
Pacific, which put every American country's dot in the sea.
- the compare table (`/free-vpn/go-premium/`) and the free-plan cell on
  `/free-vpn/comparison/` count the list instead of carrying a number.

Add a country by adding one line to the yml, one name to the names file, and the
flag SVG. Never hardcode a country, a flag or a count in a page. Two prose strings
still carry a literal number and are the exceptions to grep when the list changes:
the locations page's `meta_title` and go-premium's `banner_desc`.

