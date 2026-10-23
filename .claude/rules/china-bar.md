---
paths:
  - "assets/js/china-bar.js"
  - "_sass/pages/_china-bar.scss"
---

# China promo bar — [.docs/china-bar-geo.md](.docs/china-bar-geo.md)

`assets/js/china-bar.js` injects the bar only when the Cloudflare apex reports `loc=CN`; nothing CN-specific is in the static HTML. Preview with `?geo=CN`. Works only behind Cloudflare — `/cdn-cgi/trace` 404s on localhost and raw github.io.
