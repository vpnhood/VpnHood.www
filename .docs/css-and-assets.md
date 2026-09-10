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

Head load order: `bootstrap.css` → `helix-theme.css` → Poppins (Google Fonts) → page
`extra_css` → `style.css` → AOS.

- Use palette/utility classes already defined in the theme (`vh-txt-grad-purple-400`,
  `vh-btn vh-btn-primary`, `section-title`, `section-space`, Bootstrap
  `row`/`col-*`/spacing). New CSS is a last resort; add it to the relevant `_sass/pages/`
  partial, not inline.
- **Never write a literal `white` / `#fff` / `rgba(255,255,255,…)` (or any raw colour) in
  our SCSS** — use a `--vh-*` token or the brand ramp, or the light theme has nothing to
  re-point.
- Never edit anything under `_site/`. SCSS style: `//` comments, kebab-case class names.
- In-page anchor targets need `scroll-margin-top`: `#sp-header` is `position: fixed` and
  136px tall on desktop, so a bare `#id` jump lands the section's top behind the nav.
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
  exactly this reason. **Known still-external (move them local when touched):** AOS JS/CSS
  (`unpkg.com/aos@2.3.1`) and the Poppins web font (Google Fonts) — Poppins already uses
  `display=swap` + non-blocking load so it degrades to the system font in CN, but
  self-hosting is better. GTM is analytics and degrades gracefully, so it can stay remote.
