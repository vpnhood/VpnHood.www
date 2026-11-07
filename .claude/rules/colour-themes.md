---
paths:
  - "_sass/**"
  - "assets/css/**"
  - "assets/images/**"
  - "assets/js/theme.js"
  - "tools/make-light-art.py"
  - "_includes/header.html"
  - "_includes/theme-toggle.html"
---

# Colour themes — [.docs/colour-themes.md](.docs/colour-themes.md)

The visitor's mode is Default, Light or Dark, and the theme on screen is `<html data-theme>`. Under Default the docs and `/search/` follow the system setting and every other page stays dark; Light and Dark apply to every page. Never let a page outside the docs follow the system: the whole page then jumps between dark and white as a visitor moves around the top menu. `_sass/theme/_default.scss` holds the brand ramp and the `--vh-*` tokens; `_sass/theme/_light.scss` holds the **entire** light theme and is imported last, so page partials stay single-theme. Text uses `--vh-accent-ink` / `--vh-green-ink` / `--vh-blue-ink` (4.5:1); fills keep the raw ramp. The theme bootstrap at the top of `header.html` must stay inline and blocking. The fade between pages is only for a change of theme: `theme.js` cancels it on `pageswap`, and its URL test must match the rule at the top of `header.html`. Preview with `?vh_theme=default|light|dark`. Never convert anything showing the real app UI to light art.
