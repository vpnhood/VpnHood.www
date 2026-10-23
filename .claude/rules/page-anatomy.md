---
paths:
  - "**/index.html"
  - "_includes/**"
  - "_data/i18n/en/**"
  - "_data/docs_nav.yml"
  - "_plugins/i18n-meta.rb"
---

# Page anatomy

- Front matter: `layout: none`, `i18n: <page_key>` (names the data file), `nav_active` (`home | free-vpn | reseller | self-hosted | resources`; unset when not in the nav), optional `extra_css` (list; home uses `/assets/css/home.css`, content pages `/assets/css/custom.css`), `globe: true` on home only. **No `title`/`description`** — those are the `meta_title`/`meta_description` JSON keys, injected by `_plugins/i18n-meta.rb`. Legal pages are the exception: they declare both and have no `i18n`. Docs pages are ordinary pages that capture their article and hand it to `{% include docs.html article=vh_article %}`, which adds the breadcrumb and the section's sidebar from `_data/docs_nav.yml` — not a Jekyll layout, because a layout renders after the body, before `header.html` has assigned `vh_base` and `tc`. `_includes/docs-index.html` lists a section's pages with their `meta_description`. A docs page ends with **Next steps**: only what the reader does once its task is done, never the page they came from, an alternative to what they just did, a prerequisite, or a link back to the docs (owner, 2026-10-22).
- Body: `{% include header.html %}` → `{% assign vh_lang = page.lang | default: 'en' %}{% assign t = site.data.i18n[vh_lang][page.i18n] %}` → `<main id="sp-main-body">…</main>` rendering `{{ t.key }}` → `{% include footer.html %}`. Translatable attributes (`alt`, `placeholder`, `aria-label`) use `{{ t.* }}`; `class`/`href`/`data-*` never do. Inline HTML fragments (`<b>…</b>`, a whole `<a>`) may live inside a JSON string.
- Header/footer/offcanvas text is `{{ tc.* }}` from `_data/i18n/<lang>/chrome.json`, assigned once in `header.html`. Edit chrome copy there, never in the includes.
