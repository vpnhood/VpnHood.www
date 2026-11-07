---
paths:
  - "_sass/**"
  - "assets/css/**"
  - "assets/images/**"
  - "assets/js/theme.js"
  - "tools/make-light-art.py"
  - "_includes/header.html"
  - "_includes/theme-toggle.html"
  - "_config.yml"
---

# Colour themes — [.docs/colour-themes.md](.docs/colour-themes.md)

The visitor's mode is Auto (the default), Light or Dark, and the theme on screen is `<html data-theme>`. Under Auto the showcase pages (`auto_theme: dark` in `_config.yml`, listed by section) stay dark and every other page follows the system setting; Light and Dark apply to every page. `_sass/theme/_default.scss` holds the brand ramp and the `--vh-*` tokens; `_sass/theme/_light.scss` holds the **entire** light theme and is imported last, so page partials stay single-theme. Text uses `--vh-accent-ink` / `--vh-green-ink` / `--vh-blue-ink` (4.5:1); fills keep the raw ramp. The theme bootstrap at the top of `header.html` must stay inline and blocking. Preview with `?vh_theme=auto|light|dark`. Never convert anything showing the real app UI to light art.
