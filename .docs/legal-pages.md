# Legal pages (privacy / terms) — synced from the GitHub wiki

The full picture behind the "Legal pages" summary in [CLAUDE.md](../CLAUDE.md).

Source of truth is the **`vpnhood/VpnHood` GitHub wiki** (`Legal` is an index →
`VpnHood-CLIENT-Privacy-Policy`, `VpnHood-CONNECT-Privacy-Policy`,
`VpnHood-MANAGER-Privacy-Policy`, `VpnHood-MANAGER-Terms-of-Use`).

- The workflow step **"Sync legal pages from wiki"** `curl`s those `.md` (raw URL
  `https://raw.githubusercontent.com/wiki/vpnhood/VpnHood/<Page>.md`) into
  `_includes/legals/` **at build time** — no runtime fetch; the rendered HTML is static and
  SEO-friendly. The committed `_includes/legals/*.md` are the working copy. A **weekly**
  cron rebuild keeps it synced even without a code push. It's intentionally fail-fast: if a
  fetch fails the build is skipped and Pages keeps the last deployment.
- Pages render the md via
  `{% capture md %}{% include legals/<Page>.md %}{% endcapture %}{% include legal-page.html md=md %}`;
  `legal-page.html` runs it through `markdownify`. Styled by `_sass/pages/_legal.scss`.
- Legal pages declare `title:` and `description:` front matter and have no `i18n:` key, so
  they are never cloned into the language trees and their URLs are never `vh_base`-prefixed
  (English only by policy). They use `nav_active: resources`.
- URL map — each family has a static index linking to its 3 product pages:
  `/privacy-policy/` → `/vpnhood-connect-privacy-policy/`,
  `/vpnhood-client-privacy-policy/`, `/vpnhood-manager-privacy-policy/` (the product
  privacy md); `/legal/terms-of-use/` → `/legal/vpnhood-connect-terms-of-use/`,
  `/legal/vpnhood-client-terms-of-use/`, `/legal/vpnhood-manager-terms-of-use/` (the
  product terms md). The terms pages live under `/legal/`; the privacy pages are still at
  the root. The MANAGER terms used to be at `/terms-of-use/`, which is now a canonical +
  noindex + meta-refresh redirect stub (`sitemap: false`) to its new address — GitHub Pages
  can't 301; same form as `_plugins/blog-redirects.rb`.
