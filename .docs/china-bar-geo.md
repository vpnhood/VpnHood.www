# China bar — geo lookup

How `assets/js/china-bar.js` decides a visitor is in China. Read this before
changing the geo source or endpoint.

## Source order (`detect()`)

1. `?geo=CN` query param — manual preview/testing.
2. `localStorage vh_geo` — sticky manual override.
3. Cloudflare `/cdn-cgi/trace` (`loc=CN`) — production. **Always read from the apex
   `https://vpnhood.com/cdn-cgi/trace`** (a cross-origin request).

## Why always the apex (and not same-origin)

The site's host (`www`) is **not necessarily proxied through Cloudflare**. On a
DNS-only host the same-origin `/cdn-cgi/trace` hits GitHub Pages and 404s, so
same-origin geo can't be relied on. The **apex `vpnhood.com` is kept behind
Cloudflare**, so we always read geo there.

It's a cross-origin fetch, which is fine: the apex sends
`Access-Control-Allow-Origin: *`, so the browser allows the read. The cost is one
extra DNS+TLS to the apex — not a concern here.

## Why the apex, not `www.cloudflare.com`

Both would be CORS-readable, but the apex is the **same Cloudflare zone as the
site**, so its China reachability tracks the site itself: if a CN visitor can load
the page, the apex is reachable too. `www.cloudflare.com` is a *separate* zone the
GFW can block independently — using it would risk losing detection for the exact
audience the bar targets. The apex is also our own domain (no third-party
dependency). Both endpoints read the visitor IP at the anycast edge → the same
`loc=`, so there's no accuracy difference.

## SEO

Googlebot renders from non-CN (US), so the endpoint returns a non-CN `loc=` and
the bar is never injected into the DOM Google indexes. Geo-gated, not cloaking.
See [seo-and-semantic-html.md](seo-and-semantic-html.md).
