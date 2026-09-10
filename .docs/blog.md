# Blog (`/blog/`) — content fetched from VpnHood.Blog

The full picture behind the "Blog" summary in [CLAUDE.md](../CLAUDE.md).

Posts live in the **private `vpnhood/VpnHood.Blog`** repo (markdown + images, no build of
its own) so its writers publish without any access to this repo. This build fetches and
renders them, so posts get the site's real chrome, one sitemap, and the language machinery.

- **Never commit blog content here.** The workflow checks VpnHood.Blog out to `.blog-src/`
  (dot-folder → Jekyll ignores it) via the **read-only** `BLOG_DEPLOY_KEY` deploy key, then
  stages `posts/` → `_blog/`, `images/` → `assets/images/blog/`, `redirects.yml` →
  `_data/blog_redirects.yml`. All are gitignored. Staging **replaces** rather than merges,
  so a post deleted in the content repo disappears from the site.
- **The blog must never block a deploy** — unlike the legal sync, which is fail-fast. The
  fetch is `continue-on-error`; if it fails, the build falls back to the last good copy from
  `actions/cache` (`.blog-good/`, rotating key + prefix restore), and if there's no cache it
  publishes the site *without* `/blog/` rather than not publishing at all. Keeping the cache
  matters: every `/blog/` URL 404ing is far worse than slightly stale posts.
- **Validation is re-run here** (`.blog-src/tools/validate-posts.py --prune`), because this
  build is what publishes — a writer who merges past a red check still can't put a broken
  post on the site. `--prune` drops **only** the posts that fail. Posts are rejected
  outright for `<script>`/`<iframe>`/`<form>`/inline handlers/`javascript:` URLs (code
  blocks exempt): posts ship unsanitised, so executable markup would run on our own origin.
- **Retired posts redirect, they don't 404.** `redirects.yml` in the content repo maps an
  old slug to where it went; `_plugins/blog-redirects.rb` emits a canonical + `noindex` +
  instant meta-refresh stub at the old URL (GitHub Pages can't 301), excluded from the
  sitemap via `sitemap: false`. Its `RedirectPage` class is reused by
  `_plugins/legacy-redirects.rb` for retired site pages.
- **Publishing is push-triggered**: VpnHood.Blog's CI mints a token from the
  `vpnhood-blog-publisher` GitHub App — scoped to **Actions: write on this repo only**, so
  it can start a build and nothing else — and calls `workflow_dispatch`. Never widen that
  App to Contents; that would let blog writers push here.
- Source layout `_blog/<lang>/<slug>.md` mirrors `posts/<lang>/` (the sibling-folder
  convention `vhtranslator` expects). `_plugins/blog-pages.rb` stamps the URLs —
  `/blog/<slug>/` for English, `/<lang>/blog/<slug>/` for translations, matching
  `i18n-pages.rb` — and appends "VpnHood!" to `page.title` for the `<title>` while
  `page.headline` keeps the clean text for the `<h1>`.
- Rendered by `_layouts/post.html` (**the only Jekyll layout on the site**) +
  `blog/index.html`, styled by `_sass/pages/_blog.scss`. **No `BlogPosting` JSON-LD in the
  layout** — jekyll-seo-tag already emits a complete one for any dated document; a second
  block would duplicate the entity.
- **Paginated by `_plugins/blog-paginate.rb`** (25/page): `/blog/` is page 1, then
  `/blog/page/2/`, generated from `blog/index.html` itself (marked `blog_index: true`) so
  there's one template. Runs at `:low` priority, after `blog-pages.rb` has stamped the URLs.
  Pages are self-canonical with distinct titles — never canonicalise page 2 to page 1, it
  hides those posts. `page` is a reserved post slug (the content repo's validator enforces
  it) because `/blog/page/` would collide.
- **Never test `page.image` for truthiness** — `_config.yml` defaults give *every* document
  the site-wide OG share image, so it is never empty; doing so put that generic banner on
  every post hero and every index card. Both templates instead test
  `image contains '/assets/images/blog/'`, the path a post's own image must use (the content
  repo's validator enforces it). Alt text comes from the post's `image_alt`, falling back to
  the title; the templates test `image_alt == nil` rather than using `default:`, because
  `default:` cannot distinguish "no key" from the deliberate `image_alt: ""` that marks a
  decorative image.
- **Generators must not stamp render-time data onto pages or documents.**
  `blog-paginate.rb` sets exactly one integer (`paginator_page`) and `blog-pages.rb` sets
  only URL/language/title; everything else is derived in Liquid. Richer generator-set data
  (a paginator object, a `card_image` key) silently vanished under `jekyll serve`: a rebuild
  triggered by a `_data` change renders an object that is not the one the generator
  mutated, so the index came out empty and images disappeared. A one-shot `jekyll build`
  never hits it, so CI stayed green and only local preview broke. Related trap while
  debugging: **`jekyll serve --watch` never reloads `_plugins/`** — restart the server after
  a plugin edit.
- **`future: true` is set for the blog's sake.** Jekyll's default silently drops a document
  dated ahead of the build clock — a one-day typo and the post just never appears, with no
  error. Static sites can't really schedule anyway (nothing rebuilds on the date), so posts
  publish immediately and the content repo's validator warns about a future date.
- **Known gap:** `header.html`'s hreflang loop and `lang-selector.html` scan `site.pages`,
  which excludes collection docs — translated posts won't pair until both also scan
  `site.blog`. Inert while the blog is English-only. Those loops are also O(n²): measured
  240 pages = 9 s, 740 = 19 s, but 6,740 = **24 min**, so precompute each page's alternates
  in `i18n-pages.rb` before going wide across languages.
