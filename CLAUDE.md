# VpnHood WWW — Project Instructions

Marketing site for VpnHood (free, secure, open-source VPN). Static **Jekyll** site
ported from the original **Helix Ultimate** template site (the page chrome — `#sp-header`/`#sp-footer`/`.body-wrapper` structure + the vendored theme CSS — is still Helix; see CSS Rules): every page is a standalone
`index.html` with front matter (`layout: none` — no Jekyll layouts) that includes a
shared header/footer. The folder path **is** the URL (e.g. `free-vpn/download/index.html`
→ `/free-vpn/download/`); there are no `.html` URLs and no `permalink:`.

## Build & Deploy
- Jekyll 4.x pinned via `Gemfile`. Local build: `bundle exec jekyll build` (output `_site/`, gitignored). Serve: `bundle exec jekyll serve`.
- **Pushing `main` deploys production.** `.github/workflows/jekyll.yml` builds with the pinned Jekyll and publishes the generated `_site` to GitHub Pages (`actions/deploy-pages`); served at https://www.vpnhood.com. Triggers: `push` (publish), `workflow_dispatch` (manual), and a weekly `schedule` cron (legal sync — see below). Before building, CI runs `vhtranslator` (data-only translation; pinned via `.config/dotnet-tools.json`, `GEMINI_API_KEY` repo secret) so a deploy never ships untranslated strings — incremental via the committed watches, and the generated translations + watches are **committed back to main** by the build job (bot commit, `[skip ci]`; GITHUB_TOKEN pushes don't retrigger workflows), so each change is translated exactly once. Fail-fast like the legal sync. Never switch Pages back to the legacy branch builder (it runs an old Jekyll).
- Custom domain via the `CNAME` file (`www.vpnhood.com`) so `baseurl` stays `""` and the site's absolute `/assets/...` paths resolve. **The `www` host may or may not be proxied through Cloudflare (orange cloud)** — don't assume it is. The apex `vpnhood.com` is kept proxied, which is why geo reads from it (see [.docs/china-bar-geo.md](.docs/china-bar-geo.md)). When `www` *is* proxied, Cloudflare SSL/TLS mode must be **Full** (Flexible causes a redirect loop with GitHub Pages).
- `Gemfile.lock` must keep **both** `x64-mingw-ucrt` and `x86_64-linux` platforms or the Linux CI build fails on `bundler-cache`.
- Plugins (in `_config.yml`): `jekyll-seo-tag`, `jekyll-sitemap`, plus the project plugins `_plugins/i18n-meta.rb` (injects `page.title`/`page.description` from the i18n data — see Page Anatomy) and `_plugins/i18n-pages.rb` (generates the per-language page trees — see Translations). **No `safe: true`** — the site builds in our own Actions workflow, not the legacy shared Pages builder, so `_plugins/` load in CI and locally. `excerpt_separator: ""` disables auto-excerpts; without it, seo-tag could fall back to a page's raw body as its meta description whenever `meta_description` is empty.
- A failed build never takes the site down — `deploy` has `needs: build`, so on failure GitHub Pages keeps serving the previous successful deployment.

## Page Anatomy
- Every page: front matter (`layout: none`, `i18n: <page_key>` naming the page's data file, `nav_active`, optional `extra_css` — **no `title`/`description`**: page metadata lives in the i18n data, see next bullet; legal pages are the exception, declaring both and no `i18n`) → `{% include header.html %}` → the page's `<section id="sp-main-body">…</section>` content → `{% include footer.html %}`.
- **All page text lives in `_data/i18n/en/<page>.json`, not in the page markup.** Every page body starts with the same two lines — `{% assign vh_lang = page.lang | default: 'en' %}{% assign t = site.data.i18n[vh_lang][page.i18n] %}` (the key comes from the page's `i18n:` front matter) — and renders text via `{{ t.key }}` (inline HTML fragments like `<b>…</b>` or a whole `<a>` live inside the JSON string). **Edit copy in the JSON file; edit structure in the page.** Translatable attributes (`alt`, `placeholder`, `aria-label`) use `{{ t.* }}` too; `class`/`href`/`data-*` never do. **The page `<title>` and meta description live there too**, as `meta_title`/`meta_description` keys: `_plugins/i18n-meta.rb` injects them into `page.title`/`page.description` at build time (keyed by the page's `i18n:` front matter, empty/missing keys fall back to English), so the hand-written `<title>` tag and jekyll-seo-tag see them exactly as if they were front matter — a new page needs both keys in its JSON, and `meta_title` must contain "VpnHood!". The i18n files are flat string maps (the vhtranslator classic format — they are listed under `site.data` in `vh_translator/vhtranslator.json` and machine-translated per key). Page bodies are no longer `{% raw %}`-wrapped (they contain no stray braces; the old Joomla-era wrappers were removed during the i18n extraction).
- `nav_active` drives the active state of the top-level nav in `header.html`: one of `home | free-vpn | reseller | self-hosted | resources` (legal pages use `resources`). Leave unset for pages not in the main nav.
- `extra_css` is a list of page-specific stylesheets, linked **after** the framework CSS/Poppins and **before** `style.css`. Home uses `/assets/css/home.css`; secondary/content pages use `/assets/css/custom.css`.
- The home page sets `globe: true` (loads the three.js server globe — home only) — see footer.

### Shared header/footer (important)
`header.html` renders the `<head>`, the framework JS, and the sticky nav, and **intentionally leaves `.body-wrapper` + `.body-innerwrapper` (and `<body>`/`<html>`) OPEN**; `footer.html` closes them (plus the off-canvas menu and page scripts). **Do NOT auto-format/"balance" these two includes** — an HTML formatter that closes the wrappers early breaks the page wrapper (the home globe stops being clipped by `.body-innerwrapper{overflow-x:hidden}` and the mobile layout overflows). `.prettierignore` guards them. `header.html` div balance must be net **+2** opens. It also opens `<html>` with `data-theme="dark"` and runs the pre-paint theme bootstrap — see Colour themes.

## SEO & semantic HTML
**All SEO + semantic-HTML conventions live in [.docs/seo-and-semantic-html.md](.docs/seo-and-semantic-html.md) — read it before editing pages or the shared `header.html`/`footer.html`/`faq.html`.** It is a **shared standard kept byte-identical with the `paymenthood-www` repo** (edit both copies together). It covers seo-tag/JSON-LD/sitemap/robots & site metadata, generated structured data (FAQPage/SoftwareApplication/BreadcrumbList from includes), favicons/app-icons/manifest, the heading outline (one H1, no skipped levels), title-tag branding (every page title must contain "VpnHood!" — titles live in the `meta_title` i18n keys, legal pages in `title:` front matter; this site uses `{% seo title=false %}`; see the doc's §3 table), image & inline-SVG a11y (decorative `alt=""`/`aria-hidden` vs descriptive; no redundant alt), `<ul><li>` link groups, and announcing `target="_blank"` new-tab links. These are binding for any markup change.

## CSS Rules
**Core principle: framework CSS is vendored, our CSS is authored as SCSS.** Reach for Bootstrap utilities and existing Helix/VpnHood classes before writing any CSS; the same visual pattern must use the same class on every page.

- **Framework CSS — two paths, never hand-convert a framework's CSS to Sass yourself:**
  - **Bootstrap → compiled from vendored Sass source** (mirrors the `paymenthood-www` build). The official **Bootstrap 5.3.3** Sass source lives **unmodified** in `_sass/vendor/bootstrap/` — *never edit files there*. The Jekyll entry `assets/css/bootstrap.scss` imports `_sass/vendor/_bootstrap-overrides.scss` (project-owned Bootstrap variables — customize **here**, currently empty since we ship stock Bootstrap) then `vendor/bootstrap/bootstrap`, compiling to `assets/css/bootstrap.css`. To change Bootstrap tokens (`$primary`, breakpoints…) edit the overrides partial, not the source. To upgrade Bootstrap, re-vendor `_sass/vendor/bootstrap/` from `npm pack bootstrap@<ver>` (the `scss/` folder).
  - **Helix theme → still a static vendored CSS file:** `assets/css/helix-theme.css` (the Helix Ultimate theme — `system-j4` + the Helix-generated `template.css` + the active color preset; `url()` paths repointed to `/assets/images/`). Kept as static CSS (not folded into the Sass bundle) because it contains stray non-CSS tokens (e.g. `--header_height: $header_height`) that would break Sass parsing. Vendor such prebuilt theme CSS as-is.
  - Loaded in that order — Bootstrap first, Helix on top.
- **VpnHood's own CSS → SCSS in `_sass/`, compiled by Jekyll** (entry files in `assets/css/*.scss`, two `---` lines required):
  - `style.scss` → `_sass/theme/_default.scss` + `_sass/pages/_china-bar.scss` + `_sass/pages/_legal.scss` + `_sass/theme/_light.scss` (**last** — see Colour themes). Loaded on every page, last in the cascade.
  - `home.scss` → `_sass/pages/_home.scss`. Home only.
  - `custom.scss` → `_sass/pages/_custom.scss`. Secondary/content pages.
  - `comparison.scss` → `_sass/pages/_comparison.scss`. `/free-vpn/comparison/` only.
- Head load order: `bootstrap.css` (compiled from Sass) → `helix-theme.css` → Poppins (Google Fonts) → page `extra_css` → `style.css` → AOS.
- Use palette/utility classes already defined in the theme (`vh-txt-grad-purple-400`, `vh-btn vh-btn-primary`, `section-title`, `section-space`, Bootstrap `row`/`col-*`/spacing). New CSS is a last resort; add it to the relevant `_sass/pages/` partial, not inline.
- **Never write a literal `white` / `#fff` / `rgba(255,255,255,…)` (or any raw colour) in our SCSS** — use a `--vh-*` token or the brand ramp, or the light theme has nothing to re-point. See Colour themes.
- Never edit anything under `_site/` (build output). SCSS style: `//` comments, kebab-case class names.

## Colour themes (dark is the default; light is opt-in)
Both themes ship on every page; the active one is `<html data-theme="dark|light">`.

- **How it's applied.** `header.html` renders `data-theme="dark"` and a small **inline, blocking** script at the very top of `<head>` upgrades it to `light` when `localStorage vh_theme` says so — before first paint, so a light visitor never flashes dark. `assets/js/theme.js` (deferred) only wires the toggles, persists the choice, swaps `<meta name="theme-color">` and the decorative image sources, and dispatches a `vhThemeChange` event. Preview either theme with **`?vh_theme=light|dark`** (does not overwrite the stored choice) — same idea as `?vh_lang=fa` and the China bar's `?geo=CN`.
- **Toggle — `_includes/theme-toggle.html`.** A `<button>` rendered twice, exactly like the language selector: `header.html` drops the bare `<li>` into `#topRightMenu`, `footer.html` puts a second one in the mobile off-canvas — the second caller **must** pass its own `id`. Its accessible name states the action ("Switch to light theme") and `theme.js` swaps it with the theme. Strings live in `chrome.json` (`theme_switch_to_light` / `theme_switch_to_dark`) but fall back to English **per key**, so a not-yet-translated `chrome.json` can't leave the button unnamed.
- **Two layers, and only two.** `_sass/theme/_default.scss` holds the raw brand ramp (the **dark** values) plus the semantic `--vh-*` tokens every rule consumes. `_sass/theme/_light.scss` holds the **entire** light theme: it re-points the surface end of the ramp (`--purple-600/700/710/800`, inverted) and the ink end (`--purple-90/100/120/130/200`, darkened) so most rules work unedited, then overrides what inversion can't express. **All light-mode rules live in that one file** — page partials stay single-theme, so there is one place to look when something reads wrong in light. It is imported last, so it beats the page stylesheets without needing extra specificity.
- **Fills vs. text.** The brand purple/mint/sky are tuned for fills on a dark page and land near 3:1 on white. Fills keep the raw ramp; text uses `--vh-accent-ink` / `--vh-green-ink` / `--vh-blue-ink`, which clear 4.5:1. `--vh-on-accent` is ink on a brand-purple fill (always white); `--vh-on-bright` is ink on a mint/white fill (flips).
- **The globe** (`assets/js/globe.js`) picks its dot colours from `data-theme` and re-tints on `vhThemeChange` — white dots and cyan trails vanish on a light page.
- **Verify both themes after any markup/CSS change.** The dark theme must stay pixel-identical: build, then screenshot each page in both themes and diff dark against the previous build (the only expected delta is the header band that holds the toggle).

### Light-mode art — always via `tools/make-light-art.py`
The backdrops are light-on-dark glows authored for the dark theme, so each one has a
generated `<name>-light.<ext>` sibling. **That script is the only way light art is
produced. Do not hand-author a light variant, hand-edit a generated `*-light.*` file, or
invent a per-image CSS filter — those are all output, and the next run overwrites them.**

To give a dark image a light counterpart:

1. **Register the source** in `tools/make-light-art.py` — `RASTERS` for bitmaps (value = a
   blur radius applied to the *source*, which kills the compression mottling that only
   becomes visible once lightness is flipped), or `SVGS` for vectors (value = an explicit
   `{dark colour: light colour}` map; vector art is hand-authored, so guessing is worse
   than naming the swaps).
2. **Run `python tools/make-light-art.py`** (needs Pillow + NumPy). `--check` reports
   missing or stale output without writing anything — use it to confirm the tree is in
   sync after changing a dark original.
3. **Reference the generated file**: art referenced from CSS gets a `background-image`
   override in `_sass/theme/_light.scss`; an `<img>` gets `data-vh-light-src="…-light.…"`
   and `theme.js` swaps `src` on theme change.

Why a script and not a CSS filter: the art is dark indigo, and `invert()` turns that pale
yellow. The transform inverts *lightness* in HSL while keeping hue and saturation, then
cross-fades the flat field into the light page background (`PAGE_BG`, which must stay in
sync with `--purple-800` in `_sass/theme/_light.scss`) so a full-bleed backdrop has no
seam. CSS can't express that.

**Never convert anything depicting the real app UI.** The CONNECT screenshots, the phone
mockup, and `vpnhood-connect/download-pending-bg.webp` (which looks like a backdrop but is
a phone running the app) must render identically in both themes — `#appWrapper` becomes a
dark showcase panel on a light page instead. Also skipped, deliberately: brand logos, the
flag/brand marks, and art that already reads on white (the hero glows, the resilient
underline, the guarantee ring, the rocket, the `light-bg-*` blurs, the open-source swirl).
The script's docstring carries the same list — keep the two in agreement.

## Assets
Everything lives under `/assets` (`assets/css`, `assets/js`, `assets/images`). There are no legacy CMS `/templates`, `/media`, `/plugins` folders.
- JS: the only vendored framework JS is the stock Bootstrap 5 bundle (`vendor/bootstrap.bundle.min.js`, Popper included), loaded `defer` in the `<head>`. **No jQuery.** VpnHood's own scripts in `assets/js/` are plain vanilla JS: `main.js` (preloader→`vhPlayAnimate`, sticky header, scroll-to-top, drawer↔burger sync), `globe.js`, `ThreeOrbitControls.js`, `vh-general.js`, `china-bar.js`, `lang.js` (language preference + auto-switch — see Translations), `theme.js` (colour theme — see Colour themes).
- Images: every dark backdrop has a generated `<name>-light.<ext>` sibling for the light theme — produced by `tools/make-light-art.py`, never hand-edited. See Colour themes.
- **Self-host third-party assets — do NOT hot-link public CDNs.** We target China (see the China promo bar), and the **Great Firewall blocks/throttles `cdnjs.cloudflare.com`, `unpkg.com`, and all Google hosts (`fonts.googleapis.com`/`fonts.gstatic.com`, `googletagmanager.com`)** — a CDN asset that silently fails there breaks the page for those users. So vendor external libs into `assets/js/vendor/` (or `assets/css`) and reference them locally. three.js (r87) is vendored at `assets/js/vendor/three.min.js` for exactly this reason. **Known still-external (move them local when touched):** AOS JS/CSS (`unpkg.com/aos@2.3.1`) and the Poppins web font (Google Fonts) — Poppins already uses `display=swap` + non-blocking load so it degrades to the system font in CN, but self-hosting is better. GTM is analytics and degrades gracefully, so it can stay remote.

## Components & Includes
- **FAQ — `_includes/faq.html` + `_data/i18n/<lang>/faqs.json`.** Data-driven and translatable: renders the Bootstrap accordion **and** the `FAQPage` JSON-LD from numbered keys (`q1`/`a1`, `q2`/`a2`, …) plus the section chrome (`eyebrow`/`heading`/`desc`/`view_all`), selected by `page.lang` with English fallback. Used on 8 pages. Params: `heading` (default true — `/faq` passes `heading=false` to emit just the accordion under its own `<h1>`), `explore` (default true; `/faq` passes `explore=false`), `wrapper_class`, `eyebrow`, `schema`. Internal links inside answers are rewritten via `vh_base`. **Edit FAQ copy in `_data/i18n/en/faqs.json`, not in the pages.** Never hand-write FAQ accordion markup or FAQPage schema per page.
- **Compare table — `_includes/compare-table.html`.** The Free-vs-Premium feature table, shared by `/free-vpn/free-vs-premium/` and `/free-vpn/go-premium/` (params `heading`, `heading_class`); strings from `_data/i18n/<lang>/free_vpn_free_vs_premium.json`. Never duplicate the table markup in pages.
- **Typewriter text — `_includes/multi-text-writer.html`.** The self-typing text loop (currently the Premium card on `/free-vpn/`). Pass `keys="a,b,c"` — comma-separated key names from the page's i18n data file, typed in that order; optional `class`. Renders the animated span plus a hidden phrase list that `vh-general.js` reads, so the copy is translatable and empty/missing keys are skipped. **Never hardcode typed phrases in JS.**
- **Legal pages — `_includes/legal-page.html` + `_includes/legals/*.md`.** See below.
- **Theme toggle — `_includes/theme-toggle.html` + `assets/js/theme.js`.** See Colour themes.
- **Language selector — `_includes/lang-selector.html` + `_data/languages.yml` + `assets/js/lang.js`.** Renders **nothing until a second language exists**: languages are discovered from `site.data.i18n` folder keys (no registry — a language appears when vhtranslator drops its `_data/i18n/<code>/` folder); `_data/languages.yml` only maps codes to native display names. Used twice, and it is the **same Bootstrap dropdown** both times — `header.html` drops the bare `<li>` into the desktop `#topRightMenu` (already a `<ul>`), `footer.html` renders it in the mobile offcanvas by passing `wrapper_class` (which wraps it in its own `<ul>`) plus `align="start"`. The second caller **must** pass its own `id`: both instances are in the DOM of every page, so a shared toggle id would duplicate and break `aria-labelledby`. Each entry links to the current page's counterpart when it exists (checked against `site.pages`), else that language's home. `lang.js` persists clicks in `localStorage vh_lang` and, **on English pages only** (crawler-safe), redirects a stored/browser-preferred language to its translation using the page's own hreflang alternates (never 404s). Preview with `?vh_lang=fa`.
- **China promo bar — `assets/js/china-bar.js`.** See below.
- `header.html` / `footer.html` are shared by every page — edits there are global; make them deliberate.

## Translations (build-time language trees)
Only **strings** are ever translated; pages are generated. Two halves:

1. **Strings — `vhtranslator`** (VpnHood.Tools.ResourceTranslator, classic folder mode; config at `vh_translator/vhtranslator.json`: `base: _data/i18n/en`, `languages: [fa, fr, de, ar]`): translates the English data folder file-by-file, key-by-key (incremental via committed watches) into sibling folders (`_data/i18n/fa/…`). This includes each page's `meta_title`/`meta_description`. For RTL targets the tool appends an invisible LRM after Latin-word `!`/`?` so "VpnHood!" renders correctly — but **only when the next word is actually translated** (RTL) or the string ends; "VpnHood! CLIENT" and `VpnHood!<span>ENGINE</span>` stay inside one Latin run and get no mark. **Never put an LRM (`&lrm;`/U+200E) in the English source** — page markup that needs a brand literal in an RTL page uses `dir="ltr"` on the element instead (see the logo/preloader in `header.html`). CI runs this before every deploy and commits results back (see Build & Deploy).
2. **Pages — `_plugins/i18n-pages.rb`** clones every page that declares `i18n:` front matter, once per language, **at Jekyll build time** — no translated page copies exist in the repo. Languages are discovered from `_data/i18n/<code>/` folders (same rule as the selector): committing a translated data folder is all it takes for its whole `/xx/` tree, hreflang set, sitemap entries, and selector entry to appear. Each clone gets `lang` + an explicit `permalink: /<lang>/<path>/` and joins `site.pages`. Opt a page out with `translate: false` front matter; legal pages have no `i18n:` key and are never cloned. Adding a language = add it to `languages` in the config, let the translator (or CI) fill the data folder.

**Never hand-edit generated data folders** (`_data/i18n/<lang>/` — overwritten by the tool; fixes go in `vh_translator/custom_prompt.txt`; per-key edits in the generated JSON survive until the source key changes). `header.html` derives **reciprocal hreflang + `x-default`** from the generated pages' `lang` and sets `<html lang>`/`dir` from `page.lang` + `_data/languages.yml` — see [.docs/seo-and-semantic-html.md](.docs/seo-and-semantic-html.md) §8 before touching any of it. Never add body-level `inLanguage` microdata. Translator bookkeeping lives in `vh_translator/watches/i18n/<file>_watch.json` — commit it.

**Language-aware links (`vh_base`)**: `header.html` assigns `vh_base` once per page (`''` on English, `/fa` on Persian, …; Jekyll includes share Liquid scope). **Every internal link must be written `href="{{ vh_base }}/free-vpn/download"`** so translated pages link within their own tree — a bare `href="/free-vpn"` on a fa page would jump back to English. Exceptions (never prefixed): legal pages (`/privacy-policy`, `/terms-of-use`, `/vpnhood-*-privacy-policy` — English only by policy), `/assets/...`, and external URLs.

**Chrome strings (`chrome.json`)**: all header/footer/offcanvas/language-selector text (nav labels, mega-menu blurbs, footer columns, copyright, aria-labels) lives in `_data/i18n/<lang>/chrome.json`; `header.html` assigns `tc` once per page (English fallback) and the includes render `{{ tc.* }}`. **Edit chrome copy there, never in the includes.**

## Legal pages (privacy / terms) — synced from the GitHub wiki
Source of truth is the **`vpnhood/VpnHood` GitHub wiki** (`Legal` is an index → `VpnHood-CLIENT-Privacy-Policy`, `VpnHood-CONNECT-Privacy-Policy`, `VpnHood-MANAGER-Privacy-Policy`, `VpnHood-MANAGER-Terms-of-Use`).
- The workflow step **"Sync legal pages from wiki"** `curl`s those `.md` (raw URL `https://raw.githubusercontent.com/wiki/vpnhood/VpnHood/<Page>.md`) into `_includes/legals/` **at build time** — no runtime fetch; the rendered HTML is static and SEO-friendly. The committed `_includes/legals/*.md` are the working copy. A **weekly** cron rebuild keeps it synced even without a code push. It's intentionally fail-fast: if a fetch fails the build is skipped and Pages keeps the last deployment.
- Pages render the md via `{% capture md %}{% include legals/<Page>.md %}{% endcapture %}{% include legal-page.html md=md %}`; `legal-page.html` runs it through `markdownify`. Styled by `_sass/pages/_legal.scss`.
- URL map: `/privacy-policy/` = static index linking to the 3 product pages; `/vpnhood-connect-privacy-policy/`, `/vpnhood-client-privacy-policy/`, `/vpnhood-manager-privacy-policy/` render the product privacy md; `/terms-of-use/` renders the MANAGER terms md directly.

## China promo bar (geo-targeted)
On the original server-rendered site a `#chinaBar` was emitted server-side only for CN visitors. Re-implemented statically by **`assets/js/china-bar.js`**, which **injects** the bar into `<body>` only when the Cloudflare edge reports `loc=CN` (`/cdn-cgi/trace`). The markup / Chinese copy / external `c-hood.com` link are **not** in the static HTML — so it's SEO-safe (geo-gated, not cloaking; Googlebot crawls from non-CN, so it never renders). Preview locally with `?geo=CN` (or `localStorage vh_geo=CN`). Closing the bar removes it for the view only (no persisted dismissal — returns on refresh). Layout via `_sass/pages/_china-bar.scss` (fixed top bar; pushes `#sp-header` down and pads `.body-wrapper`). **Depends on the site being behind Cloudflare** — on localhost / raw github.io `/cdn-cgi/trace` 404s and the bar never shows.
- **Geo lookup** — see [.docs/china-bar-geo.md](.docs/china-bar-geo.md) before changing the geo source or endpoint order.

## Markup Patterns
- Section head: `<div class="section-start-text" data-aos="fade-up">` → `<div class="section-label"><h3 class="vh-txt-grad-purple-400">eyebrow</h3></div>` → `<h4 class="section-title vh-txt-grad-purple-400">` → `<p class="section-desc">`.
- Buttons: `<a class="vh-btn vh-btn-primary …">` / `vh-btn-secondary`; text buttons `vh-text-btn vh-txt-purple-300`.
- Internal links: `href="{{ vh_base }}/<path>"` (no trailing slash, matching the existing markup) — see Translations. Legal/asset/external URLs stay bare.
- Animations are **AOS** (`data-aos="fadeInUp|fade-left|…"`, `data-aos-delay`), initialized on a custom `vhPlayAnimate` event in the footer.
- External `target="_blank"` links must announce the new tab — see SEO doc §6.

## Gotchas
- **Never auto-format `_includes/header.html` or `_includes/footer.html`** — they share intentionally-unbalanced tags (see Page Anatomy). Covered by `.prettierignore`.
- New page copy goes into `_data/i18n/en/<page>.json` — hardcoding text in a page body reintroduces untranslatable strings; the i18n extraction was verified by whitespace-normalized diffs of the built `_site` pages (keep that technique for future refactors).
- **Menus** — the top nav lives in `header.html`/`footer.html` and is styled by the `vh-*` rules in `_sass/theme/_default.scss`. The **desktop mega-menu** opens on **hover via CSS** (`.vh-mega-menu:hover`), with the `#vhOverlay` blur driven by `body:has(.vh-mega-menu:hover)` — no JS. The **mobile menu** is a Bootstrap **Offcanvas** (`#mobileMenu`) with **Collapse** submenus (`data-bs-*`); `main.js` mirrors its open state onto the header burger (hamburger↔X) and lifts the header above the backdrop. The **FAQ accordion** is the other Bootstrap-JS feature (Collapse).
- The theme bootstrap at the top of `header.html` **must stay inline and blocking** — moving it into `theme.js` (deferred) would make every light-theme page flash dark before first paint.
- Inline SVGs drawn with a literal white fill/stroke are re-pointed in light mode by attribute selector in `_sass/theme/_light.scss`. Two carve-outs are load-bearing there: the circle-flag icons use `fill="#fff"` for `<mask>` geometry (white = "show this pixel", not a colour), and icons inside a fill that stays dark/brand-coloured must remain white. Adding a white icon on a new kind of background means checking both lists.
- `/cdn-cgi/trace` is a Cloudflare-only endpoint (not Jekyll/GitHub Pages) — the China bar and any geo logic only work in production behind Cloudflare.
- Local builds render absolute URLs as `http://localhost:4000`; production uses `site.url`. Don't "fix" localhost URLs seen in a local `_site`.
- The pre-migration Joomla/Helix old-site source is no longer in the working tree; it remains recoverable from early git commits (see memory) if a reference is ever needed.
