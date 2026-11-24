# Legal pages (privacy / terms) — synced from the VpnHood repo

The full picture behind the "Legal pages" summary in [CLAUDE.md](../CLAUDE.md).

Source of truth is **`docs/legal/end-user/` in the `vpnhood/VpnHood` repo**, branch `develop`:
the CLIENT, CONNECT, MANAGER, VpnHood ID and SELLER privacy policies and terms of use, plus the website's
privacy policy, one `.md` each, named `<scope>-<document>.md`. What reaches `develop` is published. That folder's README is
written for forkers; how we publish is here:

- **Effective date:** a substantive change moves the document's `Effective:` line in the same commit.
  An edit that only changes a URL is not substantive. The MANAGER terms of use came over from
  the wiki unchanged and carry none yet; add one with their next substantive change.
- **Never rename a source file:** the sync step fetches it by name, and two policies print the
  GitHub history URL of their own file as their archive.
- **The wiki** keeps only redirect stubs at the old page names, plus its `Legal` index (linked
  from the MANAGER web UI), which points at the URLs below. Never fetch from the wiki, and never
  edit policy text there; the stubs stay so old links keep working.

## Addresses — permanent

Every document lives at `/legal/<scope>/<document>/`, and every `/legal/<scope>/` is an index:

| Address | Page |
|---|---|
| `/legal/` | index of everything; the footer links its `#privacy-policy` and `#terms-of-use` |
| `/legal/vpnhood-<product>/` | the product's two documents (`_includes/legal-product-index.html`) |
| `/legal/vpnhood-<product>/privacy-policy/` | `vpnhood-<product>-privacy-policy.md` |
| `/legal/vpnhood-<product>/terms-of-use/` | `vpnhood-<product>-terms-of-use.md` |
| `/legal/website/` | the website's one document (same include, `terms="false"`) |
| `/legal/website/privacy-policy/` | `website-privacy-policy.md` |

`<product>` is `connect`, `client`, `manager`, `id` (the VpnHood ID, whose sign-in pages link
its two documents: they are set as its pool's `PrivacyPolicyUri` and `TermsOfUseUri`) or `seller`
(VpnHood! SELLER, whose sign-up page links its two documents and records which version of them a seller
account's owner accepted: its settings name their addresses and that version, the later of the two
`Effective:` dates). Until 2026-11-24 VpnHood! SELLER was VpnHood! STORE, at `store`, now retired (below). A new source file is pushed to the VpnHood repo
before its `sync_repo` line lands here, or the fail-fast sync stops every build. These addresses are printed in installed apps,
store listings, Google's OAuth consent screen and emails, so:

- **A segment under `/legal/` is never renamed or reused** for something else. A new product or
  program gets a new scope folder (`/legal/reseller-program/terms-of-use/`); nothing moves.
- **One printed form:** `https://www.vpnhood.com/legal/vpnhood-connect/privacy-policy/` —
  lowercase, `www`, trailing slash. Stores, apps and consoles get exactly that string, never an
  old address (GitHub Pages is case-sensitive, and a redirect is a hop a reviewer sees).
- **Retired addresses redirect forever,** through both mechanisms: an entry in
  `_plugins/legacy-redirects.rb` (in `ENGLISH_ONLY`; its stub carries the `#fragment`, which a meta
  refresh alone drops) and a Cloudflare Single Redirect (a real 301). Never remove either.

Retired so far (2026-10-19 move; before it the privacy pages sat at the root and the terms at
`/legal/vpnhood-<product>-terms-of-use/`):

| From | To |
|---|---|
| `/privacy-policy/`, `/terms-of-use/`, `/legal/privacy-policy/`, `/legal/terms-of-use/` | `/legal/` |
| `/vpnhood-<product>-privacy-policy/` | `/legal/vpnhood-<product>/privacy-policy/` |
| `/legal/vpnhood-<product>-terms-of-use/` | `/legal/vpnhood-<product>/terms-of-use/` |

`/terms-of-use/` was every product's terms page before the per-product split (and may still be
linked from checkouts), so it goes to the index, not to one product's terms.

Retired 2026-11-24, when VpnHood! STORE became VpnHood! SELLER (named RESELLER for a day before, never
published): `/legal/vpnhood-store/` and its two documents go to `/legal/vpnhood-seller/` and the same document. Their source files went with them:
`vpnhood-store-*.md` were deleted in the VpnHood repo, and the SELLER documents link their last
version as the archive. Their Cloudflare Single Redirect is made once the SELLER pages are live, as
before that it would send the old addresses to a 404; the plugin's stubs cover them meanwhile.

The old Joomla site's `/products/vpnhood-store/privacy-policy/` goes to
`/legal/vpnhood-seller/privacy-policy/`: the unpublished STORE listing on the old Play account
still links it. That address has the plugin's stub only, no Cloudflare rule (the Free plan's last
rules are kept for this site's own pages).

The Cloudflare side (zone `vpnhood.com`, phase `http_request_dynamic_redirect`; Free plan, 10
rules, 7 used): three Single Redirects, 301, query string kept. Each matches only the exact old
paths, with or without the trailing slash, compared with `lower(http.request.uri.path) in {...}`;
the two per-product rules build the target with
`wildcard_replace(lower(http.request.uri.path), "<old pattern>", "<new pattern>")`.

| Rule id | Matches | Target |
|---|---|---|
| `aaa2859784b940be842c6005c7cd8188` | the four retired indexes | `https://www.vpnhood.com/legal/` |
| `195de098903b4a2c825a2a38f98b29a0` | `/vpnhood-{connect,client,manager}-privacy-policy` | `/legal/vpnhood-${1}/privacy-policy/` |
| `eb53fb465ef44c158bd921e3c92546ec` | `/legal/vpnhood-{connect,client,manager}-terms-of-use` | `/legal/vpnhood-${1}/terms-of-use/` |

## Build

- The workflow step **"Sync legal pages"** `curl`s those `.md` (raw URL
  `https://raw.githubusercontent.com/vpnhood/VpnHood/develop/docs/legal/end-user/<name>.md`)
  into `_includes/legals/` under their wiki-era names (`VpnHood-MANAGER-Privacy-Policy.md`, …)
  **at build time** — no runtime fetch; the rendered HTML is static and
  SEO-friendly. The committed `_includes/legals/*.md` are the working copy. A **weekly**
  cron rebuild keeps it synced even without a code push. It's intentionally fail-fast: if a
  fetch fails the build is skipped and Pages keeps the last deployment. So a change of addresses
  lands here first, and the text's links change in the VpnHood repo after it is live.
- Pages render the md via
  `{% capture md %}{% include legals/<Page>.md %}{% endcapture %}{% include legal-page.html md=md %}`;
  `legal-page.html` runs it through `markdownify`. Styled by `_sass/pages/_legal.scss`.
- Legal pages declare `title:` and `description:` front matter and have no `i18n:` key, so
  they are never cloned into the language trees and their URLs are never `vh_base`-prefixed
  (English only by policy). They use `nav_active: resources`. The indexes are navigation only:
  every legal statement lives in the synced documents.
