# China promo bar (geo-targeted)

## What it is

On the original server-rendered site a `#chinaBar` was emitted server-side only for CN
visitors. Re-implemented statically by **`assets/js/china-bar.js`**, which **injects** the
bar into `<body>` only when the Cloudflare edge reports `loc=CN` (`/cdn-cgi/trace`). The
markup / Chinese copy / external `c-hood.com` link are **not** in the static HTML — so it's
SEO-safe (geo-gated, not cloaking; Googlebot crawls from non-CN, so it never renders).
Preview locally with `?geo=CN` (or `localStorage vh_geo=CN`). Closing the bar removes it
for the view only (no persisted dismissal — returns on refresh). Layout via
`_sass/pages/_china-bar.scss` (fixed top bar; pushes `#sp-header` down and pads
`.body-wrapper`). **Depends on the site being behind Cloudflare** — `/cdn-cgi/trace` is a
Cloudflare-only endpoint (not Jekyll/GitHub Pages); on localhost and raw github.io it 404s
and the bar never shows, and the same holds for any other geo logic.

Note the product constraint behind the bar: the VpnHood! CONNECT free tier is funded by ads,
so it is not available in China or anywhere ads are not served. The bar exists for exactly
the visitors the free tier cannot serve.

## Geo lookup

How `assets/js/china-bar.js` decides a visitor is in China. Read this before changing the
geo source or endpoint.

### Source order (`detect()`)

1. `?geo=CN` query param — manual preview/testing.
2. `localStorage vh_geo` — sticky manual override.
3. Cloudflare `/cdn-cgi/trace` (`loc=CN`) — production. **Always read from the apex
   `https://vpnhood.com/cdn-cgi/trace`** (a cross-origin request).

### Why always the apex (and not same-origin)

The site's host (`www`) is **not necessarily proxied through Cloudflare**. On a DNS-only
host the same-origin `/cdn-cgi/trace` hits GitHub Pages and 404s, so same-origin geo can't
be relied on. The **apex `vpnhood.com` is kept behind Cloudflare**, so we always read geo
there.

It's a cross-origin fetch, which is fine: the apex sends `Access-Control-Allow-Origin: *`,
so the browser allows the read. The cost is one extra DNS+TLS to the apex — not a concern
here.

### Why the apex, not `www.cloudflare.com`

Both would be CORS-readable, but the apex is the **same Cloudflare zone as the site**, so
its China reachability tracks the site itself: if a CN visitor can load the page, the apex
is reachable too. `www.cloudflare.com` is a *separate* zone the GFW can block
independently — using it would risk losing detection for the exact audience the bar
targets. The apex is also our own domain (no third-party dependency). Both endpoints read
the visitor IP at the anycast edge → the same `loc=`, so there's no accuracy difference.

### SEO

Googlebot renders from non-CN (US), so the endpoint returns a non-CN `loc=` and the bar is
never injected into the DOM Google indexes. Geo-gated, not cloaking. See
[seo-and-semantic-html.md](seo-and-semantic-html.md).
