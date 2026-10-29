# VpnHood WWW — Project Instructions

Marketing site for VpnHood (free, secure, open-source VPN). Static **Jekyll** site ported from a **Helix Ultimate** (Joomla) template: every page is a standalone `index.html` with front matter (`layout: none`) that includes a shared header/footer. The folder path **is** the URL (`free-vpn/download/index.html` → `/free-vpn/download/`); no `.html` URLs, no `permalink:`. The page chrome (`#sp-header`/`#sp-footer`/`.body-wrapper`) and `assets/css/helix-theme.css` are still Helix.

This file is the binding summary of what every task needs. Each area's rules live in `.claude/rules/` and load on their own when a file of that area is read or edited; each links a doc in `.docs/` with the full explanation, history and troubleshooting — read it before changing that area.

## Hard rules

- **Pushing `main` deploys production** (GitHub Pages via `.github/workflows/jekyll.yml`). After a deploy, purge the Cloudflare cache for `www.vpnhood.com`.
- **Copy lives in `_data/i18n/en/<page>.json`, never in page markup.** Edit copy in the JSON, structure in the page.
- **Every internal link is `href="{{ vh_base }}/<path>/"`** — language-prefixed and trailing-slashed. Exceptions: legal pages (never prefixed), `/assets/...` and external URLs (never slashed).
- **Never auto-format `_includes/header.html` or `_includes/footer.html`** — the header intentionally leaves `<html>`, `<body>`, `.body-wrapper`, `.body-innerwrapper` open (div balance net **+2**) and the footer closes them. `.prettierignore` covers both.
- **Translate every new or changed English string yourself, in all 12 languages, before any commit** — by `vh_translator/prompts/<lang>.prompt.txt`, in the translator's file format — then run `dotnet tool run vhtranslator -- --ignore-changes`. CI's vhtranslator is only the fallback for a key you leave out ([translations.md](.claude/rules/translations.md)).
- **Never edit** `_site/` (output) or `_sass/vendor/bootstrap/` (vendored source).
- **Never write a raw colour** (`white`, `#fff`, `rgba(255,255,255,…)`) in our SCSS — use `--vh-*` tokens or the brand ramp, or the light theme has nothing to re-point.
- **Never hot-link a public CDN** — the Great Firewall blocks cdnjs, unpkg and every Google host. Vendor into `assets/js/vendor/` or `assets/css`.
- **Every `meta_title` contains "VpnHood!"**, and [.docs/seo-and-semantic-html.md](.docs/seo-and-semantic-html.md) is binding for any markup change (a shared standard kept byte-identical with `paymenthood-www` — edit both copies together).
- **Light-mode art comes only from `python tools/make-light-art.py`** — never hand-author a `*-light.*` file or a per-image CSS filter.
- **Verify both themes after any markup or CSS change**; the dark theme must stay pixel-identical.
- **`jekyll serve --watch` never reloads `_plugins/`** — restart it after a plugin edit. A `_data` change triggers a full rebuild (~15 s). **Generators must not stamp render-time data onto pages** — that rebuild renders fresh page objects, so the data vanishes in local preview while CI stays green.

## Area rules — `.claude/rules/`

Loaded automatically by file path. When a task touches an area before any of its files has been opened (a question, a plan), read the rule file first.

- [page-anatomy.md](.claude/rules/page-anatomy.md) — front matter, page body, docs pages and their Next steps, chrome copy
- [translations.md](.claude/rules/translations.md) — translating by hand before a commit, vhtranslator as the fallback, LRM, spacing inside strings, per-key fallback
- [css-and-assets.md](.claude/rules/css-and-assets.md) — SCSS layout, vendored framework CSS/JS, fonts, GTM
- [colour-themes.md](.claude/rules/colour-themes.md) — dark/light tokens, `_light.scss`, theme bootstrap
- [components.md](.claude/rules/components.md) — FAQ, compare table, prices, code, terminal, locations, MANAGER promo, site search, breadcrumb, CTA tracking, consent
- [markup-patterns.md](.claude/rules/markup-patterns.md) — section heads, buttons, cards, AOS, mega-menu, anchors
- [legal-pages.md](.claude/rules/legal-pages.md) — synced from the VpnHood repo, `/legal/` addresses are permanent
- [china-bar.md](.claude/rules/china-bar.md) — `loc=CN` promo bar

## Build & deploy — [.docs/build-and-deploy.md](.docs/build-and-deploy.md)

`bundle exec jekyll build` / `bundle exec jekyll serve --livereload`. CI runs `vhtranslator` before every build (the fallback for any key left untranslated), swaps any translation that changed a placeholder for its English source (`tools/check-placeholders.py --heal`) and commits the translations back (`[skip ci]`), syncs the legal pages from the VpnHood repo (fail-fast), fails on a self-link (`tools/check-self-links.py`) or on any internal link, anchor or asset that doesn't resolve in any of the 13 trees (`tools/check-links.py`; legal pages only warn), then publishes `_site`. `Gemfile.lock` must keep both `x64-mingw-ucrt` and `x86_64-linux`. `www` may or may not be Cloudflare-proxied; when it is, SSL mode must be **Full**. A retired URL goes in `_plugins/legacy-redirects.rb` (stubs for every language tree) plus a Cloudflare Single Redirect for a real 301 — enable the rule only once the target exists in production. The site search API is a Cloudflare Worker in `workers/search/`, deployed on its own with `npx wrangler@4 deploy`; a push never deploys it, and its `DAILY_CAP` is the only limit on what Google bills.

## Blog

The blog is a separate project (`vpnhood/VpnHood.Blog`), to be published on its own subdomain; nothing in this repo builds it. Its old `/blog/` URLs here are retired stubs in `_plugins/legacy-redirects.rb`.
