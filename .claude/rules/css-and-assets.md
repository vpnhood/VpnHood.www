---
paths:
  - "_sass/**"
  - "assets/**"
  - "tools/fetch-fonts.py"
---

# CSS — [.docs/css-and-assets.md](.docs/css-and-assets.md)

Framework CSS is vendored: Bootstrap 5.3.3 compiled from `_sass/vendor/bootstrap/` via `assets/css/bootstrap.scss` (variables go in `_sass/vendor/_bootstrap-overrides.scss`), Helix stays the static `helix-theme.css`. Our CSS is SCSS in `_sass/`: `style.scss` on every page (`theme/_default` + `pages/_china-bar` + `pages/_legal` + `theme/_light` **last**), `home.scss` (home), `custom.scss` (content pages), `comparison.scss` (`/free-vpn/comparison/`). Reach for existing classes (`vh-txt-grad-purple-400`, `vh-btn vh-btn-primary`, `section-title`, `section-space`, Bootstrap utilities) before writing CSS; the same visual pattern uses the same class on every page; new rules go in the relevant `_sass/pages/` partial, never inline. `//` comments, kebab-case names.

# Assets — [.docs/css-and-assets.md](.docs/css-and-assets.md)

Everything is under `/assets`. The only vendored framework JS is the stock Bootstrap 5 bundle; **no jQuery**; our scripts are vanilla (`main.js`, `globe.js`, `vh-general.js`, `china-bar.js`, `lang.js`, `theme.js`). Nothing is hot-linked any more: AOS is `assets/css/aos.css` + `assets/js/vendor/aos.js`, and Poppins is self-hosted from `assets/fonts/poppins/` through `assets/css/fonts.css` (regenerate with `python tools/fetch-fonts.py`). GTM renders **only in production** (`jekyll.environment`), so a local serve never reports to the live GA4 property.
