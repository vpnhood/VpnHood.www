# CSS and assets

The full picture behind the "CSS" and "Assets" summaries in [CLAUDE.md](../CLAUDE.md).

## Core principle

Framework CSS is vendored; our CSS is authored as SCSS. Reach for Bootstrap utilities and
existing Helix/VpnHood classes before writing any CSS; the same visual pattern must use the
same class on every page.

## Framework CSS — two paths

Never hand-convert a framework's CSS to Sass yourself.

- **Bootstrap → compiled from vendored Sass source** (mirrors the `paymenthood-www` build).
  The official **Bootstrap 5.3.3** Sass source lives **unmodified** in
  `_sass/vendor/bootstrap/` — *never edit files there*. The Jekyll entry
  `assets/css/bootstrap.scss` imports `_sass/vendor/_bootstrap-overrides.scss` (project-owned
  Bootstrap variables — customise **here**; currently empty since we ship stock Bootstrap)
  then `vendor/bootstrap/bootstrap`, compiling to `assets/css/bootstrap.css`. To change
  Bootstrap tokens (`$primary`, breakpoints…) edit the overrides partial, not the source. To
  upgrade Bootstrap, re-vendor `_sass/vendor/bootstrap/` from `npm pack bootstrap@<ver>`
  (the `scss/` folder).
- **Helix theme → still a static vendored CSS file:** `assets/css/helix-theme.css` (the
  Helix Ultimate theme — `system-j4` + the Helix-generated `template.css` + the active
  colour preset; `url()` paths repointed to `/assets/images/`). Kept as static CSS (not
  folded into the Sass bundle) because it contains stray non-CSS tokens (e.g.
  `--header_height: $header_height`) that would break Sass parsing. Vendor such prebuilt
  theme CSS as-is.
- Loaded in that order — Bootstrap first, Helix on top.

## Our CSS — SCSS in `_sass/`, compiled by Jekyll

Entry files live in `assets/css/*.scss` and need the two `---` front-matter lines:

| entry | partials | where |
|---|---|---|
| `style.scss` | `theme/_default` + `pages/_china-bar` + `pages/_legal` + `theme/_light` (**last** — see [colour-themes.md](colour-themes.md)) | every page, last in the cascade |
| `home.scss` | `pages/_home` | home only |
| `custom.scss` | `pages/_custom` | secondary/content pages |
| `comparison.scss` | `pages/_comparison` | `/free-vpn/comparison/` only |

Head load order: `bootstrap.css` → `helix-theme.css` → `fonts.css` (self-hosted Poppins)
→ page `extra_css` → `style.css` → `aos.css`.

- Use palette/utility classes already defined in the theme (`vh-txt-grad-purple-400`,
  `vh-btn vh-btn-primary`, `section-title`, `section-space`, Bootstrap
  `row`/`col-*`/spacing). New CSS is a last resort; add it to the relevant `_sass/pages/`
  partial, not inline.
- **Never write a literal `white` / `#fff` / `rgba(255,255,255,…)` (or any raw colour) in
  our SCSS** — use a `--vh-*` token or the brand ramp, or the light theme has nothing to
  re-point.
- Never edit anything under `_site/`. SCSS style: `//` comments, kebab-case class names.
- In-page anchor targets need `scroll-margin-top`: `#sp-header` is `position: fixed` and
  up to 136px tall on desktop (91px on one row; it wraps to two below 1200px, and in the
  longer languages up to 1399px), so a bare `#id` jump lands the section's top behind the nav.
  `#compareTable` and `#faq` carry the rule in `_default.scss`; add any new anchor target to
  that selector list.

## Menus

The top nav lives in `header.html`/`footer.html` and is styled by the `vh-*` rules in
`_sass/theme/_default.scss`. The **desktop mega-menu** opens on **hover via CSS**
(`.vh-mega-menu:hover`), with the `#vhOverlay` blur driven by `body:has(.vh-mega-menu:hover)`
— no JS. The **mobile menu** is a Bootstrap **Offcanvas** (`#mobileMenu`) with **Collapse**
submenus (`data-bs-*`); `main.js` mirrors its open state onto the header burger
(hamburger↔X) and lifts the header above the backdrop. The **FAQ accordion** is the other
Bootstrap-JS feature (Collapse).

## Assets

Everything lives under `/assets` (`assets/css`, `assets/js`, `assets/images`). There are no
legacy CMS `/templates`, `/media`, `/plugins` folders.

- **JS:** the only vendored framework JS is the stock Bootstrap 5 bundle
  (`vendor/bootstrap.bundle.min.js`, Popper included), loaded `defer` in the `<head>`. **No
  jQuery.** VpnHood's own scripts in `assets/js/` are plain vanilla JS: `main.js`
  (preloader→`vhPlayAnimate`, sticky header, scroll-to-top, drawer↔burger sync),
  `globe.js`, `ThreeOrbitControls.js`, `vh-general.js`, `china-bar.js`, `lang.js` (language
  preference + auto-switch — see [translations.md](translations.md)), `theme.js` (colour
  theme — see [colour-themes.md](colour-themes.md)).
- **Images:** every dark backdrop has a generated `<name>-light.<ext>` sibling for the light
  theme — produced by `tools/make-light-art.py`, never hand-edited.
- **Self-host third-party assets — do NOT hot-link public CDNs.** We target China (see the
  China promo bar), and the **Great Firewall blocks/throttles `cdnjs.cloudflare.com`,
  `unpkg.com`, and all Google hosts (`fonts.googleapis.com`/`fonts.gstatic.com`,
  `googletagmanager.com`)** — a CDN asset that silently fails there breaks the page for
  those users. So vendor external libs into `assets/js/vendor/` (or `assets/css`) and
  reference them locally. three.js (r87) is vendored at `assets/js/vendor/three.min.js` for
  exactly this reason. **Nothing is hot-linked any more.** AOS 2.3.1 is vendored as
  `assets/css/aos.css` + `assets/js/vendor/aos.js`. Poppins is served from
  `assets/fonts/poppins/` (15 woff2: weights 300-700 x latin, latin-ext, devanagari) through
  the generated `assets/css/fonts.css` — rerun `python tools/fetch-fonts.py` to change the
  weights or subsets, and never hand-edit either output. Each face keeps `font-display:swap`
  and a `unicode-range`, so a visitor downloads only the subsets their text needs and the
  system font shows until then. GTM is the one remote script left, and it now renders only
  when `jekyll.environment == "production"`: a local `jekyll serve` used to send page views
  and CTA clicks to the live GA4 property, which put our own testing in the reports.
