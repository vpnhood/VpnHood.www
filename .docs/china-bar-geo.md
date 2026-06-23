# China bar — geo lookup

How `assets/js/china-bar.js` decides a visitor is in China. Read this before
changing the geo source, the endpoint order, or the `www` Cloudflare config.

## Source order (`detect()`)

1. `?geo=CN` query param — manual preview/testing.
2. `localStorage vh_geo` — sticky manual override.
3. Cloudflare `/cdn-cgi/trace` (`loc=CN`) — production. **Same-origin first, then
   the apex `https://vpnhood.com/cdn-cgi/trace` as a fallback.**

## Why same-origin first

`detect()` fetches same-origin `/cdn-cgi/trace` first. The visitor already loaded
this (Cloudflare-proxied) page, so it's the one host we *know* they can reach, and
the request reuses the already-warm connection — no extra DNS/TLS.

If it returns no `loc=` (e.g. the `www` record is DNS-only / grey-cloud, so the
request hits GitHub Pages and 404s), it falls back to the apex.

## Why apex is the fallback (not `www.cloudflare.com`, not the primary)

- **Not the primary.** Making apex first would force a cross-origin DNS+TLS
  handshake on *every* page view worldwide, even when `www` is healthy — paying
  the fallback cost always, for no gain. A persistent `www` 404 is a config bug to
  fix (see below), not something to route around on every visit.
- **Apex, not `cloudflare.com`.** Apex is the *same Cloudflare zone* as the site,
  so its China reachability matches the site itself: if a CN visitor can load the
  page, apex is reachable too. `www.cloudflare.com` is a separate zone the GFW can
  block independently — flipping to it would risk losing detection for the exact
  audience the bar targets. Apex is also our own domain (no third-party
  dependency) and we keep it reliably proxied.
- Apex sends `Access-Control-Allow-Origin: *`, so the cross-origin read is allowed
  by the browser. Both endpoints read the visitor IP at the anycast edge → the
  same `loc=`, so there's **no accuracy difference**.

## The real fix for a `www` 404

The fallback only stops the bar from being collateral damage. If
`www.vpnhood.com/cdn-cgi/trace` 404s, the underlying problem is that the `www`
DNS record isn't proxied — **orange-cloud it** (the site also needs the proxy for
the http→https redirect). The fallback is not a substitute for that.

## SEO

Googlebot renders from non-CN (US), so both endpoints return a non-CN `loc=` and
the bar is never injected into the DOM Google indexes. Geo-gated, not cloaking.
See [seo-and-semantic-html.md](seo-and-semantic-html.md).
