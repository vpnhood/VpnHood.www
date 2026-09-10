# Colour themes (dark is the default; light is opt-in)

The full picture behind the "Colour themes" summary in [CLAUDE.md](../CLAUDE.md). Both
themes ship on every page; the active one is `<html data-theme="dark|light">`.

## How it's applied

`header.html` renders `data-theme="dark"` and a small **inline, blocking** script at the
very top of `<head>` upgrades it to `light` when `localStorage vh_theme` says so — before
first paint, so a light visitor never flashes dark. **That bootstrap must stay inline and
blocking** — moving it into `theme.js` (deferred) would make every light-theme page flash
dark before first paint. `assets/js/theme.js` (deferred) only wires the toggles, persists
the choice, swaps `<meta name="theme-color">` and the decorative image sources, and
dispatches a `vhThemeChange` event. Preview either theme with **`?vh_theme=light|dark`**
(does not overwrite the stored choice) — same idea as `?vh_lang=fa` and the China bar's
`?geo=CN`.

## Toggle — `_includes/theme-toggle.html`

A `<button>` rendered twice, exactly like the language selector: `header.html` drops the
bare `<li>` into `#topRightMenu`, `footer.html` puts a second one in the mobile off-canvas —
the second caller **must** pass its own `id`. Its accessible name states the action
("Switch to light theme") and `theme.js` swaps it with the theme. Strings live in
`chrome.json` (`theme_switch_to_light` / `theme_switch_to_dark`) but fall back to English
**per key**, so a not-yet-translated `chrome.json` can't leave the button unnamed.

## Two layers, and only two

`_sass/theme/_default.scss` holds the raw brand ramp (the **dark** values) plus the semantic
`--vh-*` tokens every rule consumes. `_sass/theme/_light.scss` holds the **entire** light
theme: it re-points the surface end of the ramp (`--purple-600/700/710/800`, inverted) and
the ink end (`--purple-90/100/120/130/200`, darkened) so most rules work unedited, then
overrides what inversion can't express. **All light-mode rules live in that one file** —
page partials stay single-theme, so there is one place to look when something reads wrong
in light. It is imported last, so it beats the page stylesheets without needing extra
specificity.

## Fills vs. text

The brand purple/mint/sky are tuned for fills on a dark page and land near 3:1 on white.
Fills keep the raw ramp; text uses `--vh-accent-ink` / `--vh-green-ink` / `--vh-blue-ink`,
which clear 4.5:1. `--vh-on-accent` is ink on a brand-purple fill (always white);
`--vh-on-bright` is ink on a mint/white fill (flips).

## White inline SVGs

Inline SVGs drawn with a literal white fill/stroke are re-pointed in light mode by attribute
selector in `_sass/theme/_light.scss`. Two carve-outs are load-bearing there: the
circle-flag icons use `fill="#fff"` for `<mask>` geometry (white = "show this pixel", not a
colour), and icons inside a fill that stays dark/brand-coloured must remain white. Adding a
white icon on a new kind of background means checking both lists.

## The globe

`assets/js/globe.js` picks its dot colours from `data-theme` and re-tints on
`vhThemeChange` — white dots and cyan trails vanish on a light page.

## Verify both themes after any markup/CSS change

The dark theme must stay pixel-identical: build, then screenshot each page in both themes
and diff dark against the previous build (the only expected delta is the header band that
holds the toggle). Playwright can be borrowed from `VpnHood.Client.WebUI/node_modules`;
force AOS elements visible (`[data-aos]` → `aos-animate`, opacity 1, transform none) and
remove `.sp-pre-loader` before capturing, or the shots come out ghosted.

## Light-mode art — always via `tools/make-light-art.py`

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
