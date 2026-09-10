# Build & deploy

The full picture behind the "Build & deploy" summary in [CLAUDE.md](../CLAUDE.md).

## Local

- Jekyll 4.x pinned via `Gemfile`. Build: `bundle exec jekyll build` (output `_site/`,
  gitignored). Serve: `bundle exec jekyll serve --livereload` — without `--livereload` the
  watcher only rebuilds and the browser never refreshes.
- `jekyll serve --watch` **never reloads `_plugins/`** — restart the server after a plugin
  edit. A change under `_data/` forces a full rebuild (15–25 s on this site), so there is a
  real lag before the page changes.
- `Gemfile.lock` must keep **both** `x64-mingw-ucrt` and `x86_64-linux` platforms or the
  Linux CI build fails on `bundler-cache`.
- Local builds render absolute URLs as `http://localhost:4000`; production uses `site.url`.
  Don't "fix" localhost URLs seen in a local `_site`.

## CI (`.github/workflows/jekyll.yml`)

- **Pushing `main` deploys production.** The workflow builds with the pinned Jekyll and
  publishes the generated `_site` to GitHub Pages (`actions/deploy-pages`); served at
  https://www.vpnhood.com. Triggers: `push` (publish), `workflow_dispatch` (manual, also used
  by the blog repo), and a weekly `schedule` cron (legal sync).
- Before building, CI runs `vhtranslator` (data-only translation; pinned via
  `.config/dotnet-tools.json`, `GEMINI_API_KEY` repo secret) so a deploy never ships
  untranslated strings — incremental via the committed watches, and the generated
  translations + watches are **committed back to main** by the build job (bot commit,
  `[skip ci]`; GITHUB_TOKEN pushes don't retrigger workflows), so each change is translated
  exactly once. Fail-fast like the legal sync.
- Never switch Pages back to the legacy branch builder (it runs an old Jekyll).
- A failed build never takes the site down — `deploy` has `needs: build`, so on failure
  GitHub Pages keeps serving the previous successful deployment.
- After a deploy, **purge the Cloudflare cache** for `www.vpnhood.com` (zone
  `1483dd881d6089285a99ee141f48d432`, `POST /purge_cache {"purge_everything": true}`).
  GitHub Pages sends `Cache-Control: max-age=600` and our assets are not fingerprinted, so
  a deploy otherwise serves stale CSS/JS for up to ten minutes.

## Domain and Cloudflare

- Custom domain via the `CNAME` file (`www.vpnhood.com`) so `baseurl` stays `""` and the
  site's absolute `/assets/...` paths resolve.
- **The `www` host may or may not be proxied through Cloudflare (orange cloud)** — don't
  assume it is. The apex `vpnhood.com` is kept proxied, which is why geo reads from it (see
  [china-bar-geo.md](china-bar-geo.md)). When `www` *is* proxied, Cloudflare SSL/TLS mode
  must be **Full** (Flexible causes a redirect loop with GitHub Pages).

## Retiring a URL

GitHub Pages cannot 301, so a retired page needs two things:

1. An entry in `_plugins/legacy-redirects.rb`. Every page with `i18n:` front matter is
   cloned into each `/<lang>/` tree, so retiring one page retires thirteen URLs; the plugin
   emits a canonical + `noindex` + meta-refresh stub for each, pointing at that language's
   copy of the destination, and keeps them out of the sitemap. These cover the site whenever
   `www` is not proxied.
2. A Cloudflare Single Redirect (zone ruleset, phase `http_request_dynamic_redirect`) for a
   real 301 at the edge. Use a `*/old-path*` wildcard so one rule covers every language tree
   and the slashless variant, and `concat("https://www.vpnhood.com", wildcard_replace(...))`
   as the target so `http://` requests redirect in one hop. **Enable the rule only once the
   target exists in production** — a rule created ahead of the deploy 301s a live URL to a
   404. The Free plan allows 10 Single Redirects per zone (Bulk Redirects: 15 rules, 5
   lists, 10,000 URLs at account level, exact-URL only).

Retired so far: `/free-vpn/features/` → `/features/` (features are shared by CLIENT and
CONNECT now); `/free-vpn/free-vs-premium/` → `/free-vpn/go-premium/` (it was only the
compare table go-premium also renders, and Search Console showed it ranking on brand terms
at 0.7% CTR and on no "free vs premium" query at all).

## Plugins (`_config.yml`)

`jekyll-seo-tag`, `jekyll-sitemap`, plus the project plugins: `_plugins/i18n-meta.rb`
(injects `page.title`/`page.description` from the i18n data), `_plugins/i18n-pages.rb`
(generates the per-language page trees), `_plugins/legacy-redirects.rb`,
`_plugins/blog-pages.rb`, `_plugins/blog-paginate.rb`, `_plugins/blog-redirects.rb`.
**No `safe: true`** — the site builds in our own Actions workflow, not the legacy shared
Pages builder, so `_plugins/` load in CI and locally. `excerpt_separator: ""` disables
auto-excerpts; without it, seo-tag could fall back to a page's raw body as its meta
description whenever `meta_description` is empty.

## History

The pre-migration Joomla/Helix old-site source is no longer in the working tree; it remains
recoverable from early git commits if a reference is ever needed. The i18n extraction that
moved all copy into `_data/i18n/en/` was verified by whitespace-normalised diffs of the
built `_site` pages — keep that technique for future refactors of the same kind.
