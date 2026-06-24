# VpnHood WWW — Project Instructions

Marketing site for VpnHood (free, secure, open-source VPN). Static **Jekyll** site
ported from the original **Helix Ultimate** template site (the page chrome — `#sp-header`/`#sp-footer`/`.body-wrapper` structure + the vendored theme CSS — is still Helix; see CSS Rules): every page is a standalone
`index.html` with front matter (`layout: none` — no Jekyll layouts) that includes a
shared header/footer. The folder path **is** the URL (e.g. `free-vpn/download/index.html`
→ `/free-vpn/download/`); there are no `.html` URLs and no `permalink:`.

## Build & Deploy
- Jekyll 4.x pinned via `Gemfile`. Local build: `bundle exec jekyll build` (output `_site/`, gitignored). Serve: `bundle exec jekyll serve`.
- **Pushing `main` deploys production.** `.github/workflows/jekyll.yml` builds with the pinned Jekyll and publishes the generated `_site` to GitHub Pages (`actions/deploy-pages`); served at https://www.vpnhood.com. Triggers: `push` (publish), `workflow_dispatch` (manual), and a weekly `schedule` cron (legal sync — see below). Never switch Pages back to the legacy branch builder (it runs an old Jekyll).
- Custom domain via the `CNAME` file (`www.vpnhood.com`) so `baseurl` stays `""` and the site's absolute `/assets/...` paths resolve. **The `www` host may or may not be proxied through Cloudflare (orange cloud)** — don't assume it is. The apex `vpnhood.com` is kept proxied, which is why geo reads from it (see [.docs/china-bar-geo.md](.docs/china-bar-geo.md)). When `www` *is* proxied, Cloudflare SSL/TLS mode must be **Full** (Flexible causes a redirect loop with GitHub Pages).
- `Gemfile.lock` must keep **both** `x64-mingw-ucrt` and `x86_64-linux` platforms or the Linux CI build fails on `bundler-cache`.
- Plugins (in `_config.yml`): `jekyll-seo-tag`, `jekyll-sitemap`. `safe: true`.
- A failed build never takes the site down — `deploy` has `needs: build`, so on failure GitHub Pages keeps serving the previous successful deployment.

## Page Anatomy
- Every page: front matter (`layout: none`, `title`, `description`, `nav_active`, optional `extra_css`) → `{% include header.html %}` → the page's `<section id="sp-main-body">…</section>` content → `{% include footer.html %}`.
- **The page body (Helix template markup) is wrapped in `{% raw %}…{% endraw %}`** because it can contain stray `{`/`}` that would otherwise trip Liquid. **To use a Liquid tag inside that body (e.g. a component include), break out of raw:** `{% endraw %}{% include faq.html … %}{% raw %}`.
- `nav_active` drives the active state of the top-level nav in `header.html`: one of `home | free-vpn | reseller | self-hosted | resources` (legal pages use `resources`). Leave unset for pages not in the main nav.
- `extra_css` is a list of page-specific stylesheets, linked **after** `vendor.bundle.css`/Poppins and **before** `style.css`. Home uses `/assets/css/home.css`; secondary/content pages use `/assets/css/custom.css`.
- The home page sets `globe: true` (loads the three.js server globe — home only) — see footer.

### Shared header/footer (important)
`header.html` renders the `<head>`, the framework JS, and the sticky nav, and **intentionally leaves `.body-wrapper` + `.body-innerwrapper` (and `<body>`/`<html>`) OPEN**; `footer.html` closes them (plus the off-canvas menu and page scripts). **Do NOT auto-format/"balance" these two includes** — an HTML formatter that closes the wrappers early breaks the page wrapper (the home globe stops being clipped by `.body-innerwrapper{overflow-x:hidden}` and the mobile layout overflows). `.prettierignore` guards them. `header.html` div balance must be net **+2** opens.

## SEO & semantic HTML
**All SEO + semantic-HTML conventions live in [.docs/seo-and-semantic-html.md](.docs/seo-and-semantic-html.md) — read it before editing pages or the shared `header.html`/`footer.html`/`faq.html`.** It is a **shared standard kept byte-identical with the `paymenthood-www` repo** (edit both copies together). It covers seo-tag/JSON-LD/sitemap/robots & site metadata, generated structured data (FAQPage/SoftwareApplication/BreadcrumbList from includes), favicons/app-icons/manifest, the heading outline (one H1, no skipped levels), title-tag branding (every `title:` must contain "VpnHood!" — this site uses `{% seo title=false %}`; see the doc's §3 table), image & inline-SVG a11y (decorative `alt=""`/`aria-hidden` vs descriptive; no redundant alt), `<ul><li>` link groups, and announcing `target="_blank"` new-tab links. These are binding for any markup change.

## CSS Rules
**Core principle: framework CSS is vendored, our CSS is authored as SCSS.** Reach for Bootstrap utilities and existing Helix/VpnHood classes before writing any CSS; the same visual pattern must use the same class on every page.

- **Framework / generated CSS → static `assets/css/vendor.bundle.css`, never hand-converted to Sass.** That bundle is Bootstrap 5.3 + Helix `system-j4` + the Helix-generated `template.css` + the active color preset (plus a small alert web-component), concatenated unmodified (only `url()` paths repointed to `/assets/images/`). Rule of thumb: if a framework ships a Sass source, compile that; otherwise vendor its CSS as-is. Never convert a framework's CSS to Sass yourself.
- **VpnHood's own CSS → SCSS in `_sass/`, compiled by Jekyll** (entry files in `assets/css/*.scss`, two `---` lines required):
  - `style.scss` → `_sass/theme/_default.scss` + `_sass/pages/_china-bar.scss` + `_sass/pages/_legal.scss`. Loaded on every page, last in the cascade.
  - `home.scss` → `_sass/pages/_home.scss`. Home only.
  - `custom.scss` → `_sass/pages/_custom.scss`. Secondary/content pages.
- Head load order: `vendor.bundle.css` → Poppins (Google Fonts) → page `extra_css` → `style.css` → AOS.
- Use palette/utility classes already defined in the theme (`vh-txt-grad-purple-400`, `vh-btn vh-btn-primary`, `section-title`, `section-space`, Bootstrap `row`/`col-*`/spacing). New CSS is a last resort; add it to the relevant `_sass/pages/` partial, not inline.
- Never edit anything under `_site/` (build output). SCSS style: `//` comments, kebab-case class names.

## Assets
Everything lives under `/assets` (`assets/css`, `assets/js`, `assets/images`). There are no legacy CMS `/templates`, `/media`, `/plugins` folders.
- JS: the only vendored framework JS is the stock Bootstrap 5 bundle (`vendor/bootstrap.bundle.min.js`, Popper included), loaded `defer` in the `<head>`. **No jQuery.** VpnHood's own scripts in `assets/js/` are plain vanilla JS: `main.js` (preloader→`vhPlayAnimate`, sticky header, scroll-to-top, drawer↔burger sync), `globe.js`, `ThreeOrbitControls.js`, `vh-general.js`, `china-bar.js`.

## Components & Includes
- **FAQ — `_includes/faq.html` + `_data/faqs.yml`.** Data-driven: renders the Bootstrap accordion **and** the `FAQPage` JSON-LD from a list of `{q, a}` items. Used on 7 pages. Params: `items` (required; usually `site.data.faqs`), `heading` (default true — `/faq` passes `heading=false` to emit just the accordion under its own `<h1>`), `explore` (default true — the "Explore full FAQs" → /faq button; `/faq` passes `explore=false`), `eyebrow`, `schema`. **Edit FAQ copy in `_data/faqs.yml`, not in the pages.** Never hand-write FAQ accordion markup or FAQPage schema per page.
- **Legal pages — `_includes/legal-page.html` + `_includes/legals/*.md`.** See below.
- **China promo bar — `assets/js/china-bar.js`.** See below.
- `header.html` / `footer.html` are shared by every page — edits there are global; make them deliberate.

## Legal pages (privacy / terms) — synced from the GitHub wiki
Source of truth is the **`vpnhood/VpnHood` GitHub wiki** (`Legal` is an index → `VpnHood-CLIENT-Privacy-Policy`, `VpnHood-CONNECT-Privacy-Policy`, `VpnHood-MANAGER-Privacy-Policy`, `VpnHood-MANAGER-Terms-of-Use`).
- The workflow step **"Sync legal pages from wiki"** `curl`s those `.md` (raw URL `https://raw.githubusercontent.com/wiki/vpnhood/VpnHood/<Page>.md`) into `_includes/legals/` **at build time** — no runtime fetch; the rendered HTML is static and SEO-friendly. The committed `_includes/legals/*.md` are the working copy. A **weekly** cron rebuild keeps it synced even without a code push. It's intentionally fail-fast: if a fetch fails the build is skipped and Pages keeps the last deployment.
- Pages render the md via `{% capture md %}{% include legals/<Page>.md %}{% endcapture %}{% include legal-page.html md=md %}`; `legal-page.html` runs it through `markdownify`. Styled by `_sass/pages/_legal.scss`.
- URL map: `/privacy-policy/` = static index linking to the 3 product pages; `/vpnhood-connect-privacy-policy/`, `/vpnhood-client-privacy-policy/`, `/vpnhood-manager-privacy-policy/` render the product privacy md; `/terms-of-use/` renders the MANAGER terms md directly.

## China promo bar (geo-targeted)
On the original server-rendered site a `#chinaBar` was emitted server-side only for CN visitors. Re-implemented statically by **`assets/js/china-bar.js`**, which **injects** the bar into `<body>` only when the Cloudflare edge reports `loc=CN` (`/cdn-cgi/trace`). The markup / Chinese copy / external `c-hood.com` link are **not** in the static HTML — so it's SEO-safe (geo-gated, not cloaking; Googlebot crawls from non-CN, so it never renders). Preview locally with `?geo=CN` (or `localStorage vh_geo=CN`). Closing the bar removes it for the view only (no persisted dismissal — returns on refresh). Layout via `_sass/pages/_china-bar.scss` (fixed top bar; pushes `#sp-header` down and pads `.body-wrapper`). **Depends on the site being behind Cloudflare** — on localhost / raw github.io `/cdn-cgi/trace` 404s and the bar never shows.
- **Geo lookup** — see [.docs/china-bar-geo.md](.docs/china-bar-geo.md) before changing the geo source or endpoint order.

## Markup Patterns
- Section head: `<div class="section-start-text" data-aos="fade-up">` → `<div class="section-label"><h3 class="vh-txt-grad-purple-400">eyebrow</h3></div>` → `<h4 class="section-title vh-txt-grad-purple-400">` → `<p class="section-desc">`.
- Buttons: `<a class="vh-btn vh-btn-primary …">` / `vh-btn-secondary`; text buttons `vh-text-btn vh-txt-purple-300`.
- Animations are **AOS** (`data-aos="fadeInUp|fade-left|…"`, `data-aos-delay`), initialized on a custom `vhPlayAnimate` event in the footer.
- External `target="_blank"` links must announce the new tab — see SEO doc §6.

## Gotchas
- **Never auto-format `_includes/header.html` or `_includes/footer.html`** — they share intentionally-unbalanced tags (see Page Anatomy). Covered by `.prettierignore`.
- A Liquid tag placed inside a page's `{% raw %}` body is treated as literal text — wrap it `{% endraw %}…{% raw %}`.
- **Menus** — the top nav lives in `header.html`/`footer.html` and is styled by the `vh-*` rules in `_sass/theme/_default.scss`. The **desktop mega-menu** opens on **hover via CSS** (`.vh-mega-menu:hover`), with the `#vhOverlay` blur driven by `body:has(.vh-mega-menu:hover)` — no JS. The **mobile menu** is a Bootstrap **Offcanvas** (`#mobileMenu`) with **Collapse** submenus (`data-bs-*`); `main.js` mirrors its open state onto the header burger (hamburger↔X) and lifts the header above the backdrop. The **FAQ accordion** is the other Bootstrap-JS feature (Collapse).
- `/cdn-cgi/trace` is a Cloudflare-only endpoint (not Jekyll/GitHub Pages) — the China bar and any geo logic only work in production behind Cloudflare.
- Local builds render absolute URLs as `http://localhost:4000`; production uses `site.url`. Don't "fix" localhost URLs seen in a local `_site`.
- `_reference/` holds the downloaded source pages used to build this site — excluded from the build and gitignored; safe to delete.
