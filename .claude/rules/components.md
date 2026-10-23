---
paths:
  - "**/index.html"
  - "_includes/**"
  - "_data/*.yml"
  - "_data/i18n/en/**"
  - "assets/js/vh-general.js"
---

# Components — [.docs/components.md](.docs/components.md)

- **FAQ** `_includes/faq.html`: name-keyed pairs (`q_is_open_source`/`a_is_open_source`) in `faqs.json`; **which questions a page shows, and in what order, lives in `_data/faq_sets.yml`** (`set="go_premium"`); per-key English fallback; only `/faq` emits the FAQPage JSON-LD, every other caller passes `schema=false`. Never hand-write accordion markup or FAQ schema in a page.
- **Compare table** `_includes/compare-table.html`: rendered on `/free-vpn/go-premium/`; strings from `free_vpn_free_vs_premium.json`; feature rows link to their `/features/` pages. Never duplicate the table markup.
- **Typewriter** `_includes/multi-text-writer.html`: `keys="a,b,c"` from the page's JSON; never hardcode phrases in JS.
- **Theme toggle** and **language selector** are each rendered twice (header + mobile offcanvas); the second caller **must** pass its own `id`. The selector renders nothing until a second language exists.
- **Prices** live in `_data/pricing.yml` (one entry per plan, plus the cart URL and product id), read by `/free-vpn/go-premium/`; the sentences around them are translatable templates with `[percent]`/`[amount]`/`[was]`/`[now]`/`[months]`/`[currency]` placeholders. Never put a price in `_data/i18n/` — the translator rewrites those files. Liquid cannot parse `}` inside a quoted string, so placeholders use square brackets.
- **Code** — a command, path, port or setting name in a sentence — lives in `_data/code.yml` the same way: the copy holds `<code>[name]</code>` and the page renders the string with `{% include copy.html s=t.key %}`, which fills in every name and language-prefixes the internal links. Never write code in `_data/i18n/` — the translator would see it. A whole command stays in the page, in a terminal (below). CI swaps any translation that changed a placeholder for its English source (`tools/check-placeholders.py`).
- **Terminal** `_includes/terminal.html`: every command, file and command output on the site — `{% include terminal.html caption=t.key cmd='sudo …' %}`. Each command (one per line) and each `code` file gets a copy button; `output` gets none. Write a command as it is typed; the include escapes it. Never hand-write `.vh-terminal` markup — a command shown any other way has no copy button.
- **Locations** live in `_data/locations.yml` (tier, continent, lat/lng) with names in `_data/i18n/en/locations.json`; `/free-vpn/locations/`, the `/free-vpn/` map, the home flag strip, the home globe dots and both comparison tables all read from it. Land dots for the globe and the map come only from `python tools/make-land-dots.py`. Never hardcode a country, a flag or a count, and never write the **exact total**: pages say "more than 15 countries" / `15+` through `vh_loc_more` (list size minus one), so the claim stays true as the list grows. The **free** count is stated exactly, on purpose. The only literal numbers are the locations page's meta title and description.
- **MANAGER promo** `_includes/docs-managed.html`: MANAGER's steps live only in the MANAGER docs (owner, 2026-10-22). A SERVER docs page with a MANAGER counterpart shows only a standalone server's steps, and puts this card right before its `<h2 id="standalone">` — never at the top of the page — with `href=` the MANAGER page; its copy is the page's `mgr_box_title`, `mgr_box_desc` and `mgr_box_cta`, benefit first ("Easily add, manage and monitor…"). Never write MANAGER steps into a server page.
- **Breadcrumb** `_includes/breadcrumb.html`: the trail from `vh_base_url`, each segment named by its key in `nav_labels.json` (per-key English fallback, then the slug); always emits the BreadcrumbList JSON-LD, and the visible trail only with `visible=true` (docs pages). The docs sidebar names a page by the same key, so the two always agree.
- **CTA tracking**: `data-vh-track="<place>-<action>"` on a link pushes `vh_cta_click` to `dataLayer`; GTM forwards it to GA4 (setup in the doc). Tag a new CTA rather than adding a second listener.
- **Analytics consent**: in the EU/EEA, the UK and Switzerland GTM loads only after the cookie banner's Accept; elsewhere at once, with no banner. Never load GTM or another tracker outside `vhLoadGtm` in `header.html`.
- `header.html` / `footer.html` are shared by every page — make edits there deliberate.
