---
paths:
  - "**/index.html"
  - "_includes/**"
  - "_sass/**"
  - "assets/js/vh-general.js"
---

# Markup patterns

- Section head: `<div class="section-start-text" data-aos="fade-up">` → `<div class="section-label"><p class="vh-txt-grad-purple-400">eyebrow</p></div>` → `<h2 class="section-title vh-txt-grad-purple-400">` → `<p class="section-desc">`. Keep the outline honest: one H1, no skipped levels.
- Buttons: `vh-btn vh-btn-primary` / `vh-btn-secondary`; text buttons `vh-text-btn vh-txt-purple-300`. Cards: `vh-card-dark vh-feature-panel` with an `_includes/icons/*.svg` in `.vh-feature-icon`.
- Animations are AOS (`data-aos`, `data-aos-delay`), started by the `vhPlayAnimate` event in the footer.
- Desktop mega-menu opens on CSS hover (a 72px hover bridge spans the gap from the nav pill to the panel) or keyboard focus (`vh-general.js` sets `.vh-mega-hold` while anything in the item has `:focus-visible`, holds it 250ms after the pointer leaves, and closes it on Escape). The Free VPN and Self-Hosted labels are links to their hub pages; Resources has no hub, so its label is a `<button>`. The mobile menu is Bootstrap Offcanvas + Collapse; the FAQ accordion is Collapse.
- In-page anchor targets need `scroll-margin-top` — `#sp-header` is fixed and up to 136px tall (91px on one row; the pill uses 10px item padding and the header chip is globe-only so all languages fit from 1400px up, and below 1400px the header reclaims the side margins so most still fit down to 1200px). `#compareTable` and `#faq` already have it in `_default.scss`.
- External `target="_blank"` links announce the new tab (`{{ tc.new_tab }}` in a `.visually-hidden` span).
- Local builds render absolute URLs as `http://localhost:4000`; don't "fix" them.
