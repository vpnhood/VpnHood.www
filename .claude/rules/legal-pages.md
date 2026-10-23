---
paths:
  - "legal/**"
  - "_includes/legals/**"
  - "_includes/legal-page.html"
  - "_includes/legal-product-index.html"
  - "_sass/pages/_legal.scss"
  - "_plugins/legacy-redirects.rb"
  - ".github/workflows/**"
---

# Legal pages — [.docs/legal-pages.md](.docs/legal-pages.md)

Source of truth is `docs/legal/end-user/` in the `vpnhood/VpnHood` repo (`develop`); CI `curl`s the `.md` into `_includes/legals/` (fail-fast, plus a weekly cron). The wiki keeps only redirect stubs — never fetch from it. Pages render through `legal-page.html`. English only, never `vh_base`-prefixed. Every document lives at `/legal/<scope>/<document>/` (`/legal/vpnhood-connect/privacy-policy/`); those addresses are printed in apps and stores, so a `/legal/` segment is never renamed or reused, and a retired one keeps its plugin stub and Cloudflare 301 forever.
