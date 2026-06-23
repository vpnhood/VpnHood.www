# China bar — geo lookup

How `assets/js/china-bar.js` decides a visitor is in China. Read this before
changing the geo source, the endpoint order, or the `www` Cloudflare config.

## Source order (`detect()`)

1. `?geo=CN` query param — manual preview/testing.
2. `localStorage vh_geo` — sticky manual override.
3. Cloudflare `/cdn-cgi/trace` (`loc=CN`) — production. **Same-origin first, then
   `www.cloudflare.com` as a fallback.**

## Why same-origin first, `www.cloudflare.com` as fallback

`detect()` fetches same-origin `/cdn-cgi/trace` first. If that returns no `loc=`
(e.g. the `www` record is DNS-only / grey-cloud, so the request hits GitHub Pages
and 404s), it falls back to `https://www.cloudflare.com/cdn-cgi/trace` — always
Cloudflare-proxied and CORS-enabled (`Access-Control-Allow-Origin: *`), so the
cross-origin read is allowed by the browser.

**Do not flip the order.** `www.cloudflare.com` is frequently throttled/blocked
inside mainland China, so a CN visitor who *can* reach our proxied site might
*not* reach `cloudflare.com`. Making it primary would lose detection for the exact
audience the bar targets. The fallback exists only to cover `www` not being
proxied, and it costs an extra DNS+TLS to a third-party origin — so it's the
backstop, not the default.

Both endpoints read the visitor IP at the anycast edge, so they return the same
`loc=`. There is **no accuracy difference** between them.

## The real fix for a `www` 404

The fallback only stops the bar from being collateral damage. If
`www.vpnhood.com/cdn-cgi/trace` 404s, the underlying problem is that the `www`
DNS record isn't proxied — **orange-cloud it** (the site also needs the proxy for
the http→https redirect). The fallback is not a substitute for that.

## SEO

Googlebot renders from non-CN (US), so both endpoints return a non-CN `loc=` and
the bar is never injected into the DOM Google indexes. Geo-gated, not cloaking.
See [seo-and-semantic-html.md](seo-and-semantic-html.md).
