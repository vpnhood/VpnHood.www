# Generates the per-language page tree at build time, so no translated page
# copies live in the repo (vhtranslator translates ONLY _data/i18n/en/ into
# sibling folders; pages are pure clones — all their text renders from the data
# via {{ t.* }}, and title/description come from _plugins/i18n-meta.rb).
#
# Languages are discovered from _data/i18n/<code>/ folders (same rule as the
# language selector): committing a translated data folder is all it takes for
# its whole page tree to exist. Every page that declares `i18n:` front matter
# (and not `translate: false`) is cloned once per language and served at
# /<lang>/<source path>/ via an explicit permalink; legal pages and asset pages
# have no `i18n:` key and are never cloned. The clones join site.pages, so
# hreflang, the language selector, jekyll-seo-tag, and jekyll-sitemap all see
# them like ordinary pages.
module VhI18nPages
  class Generator < Jekyll::Generator
    safe false

    def generate(site)
      languages = (site.data["i18n"] || {}).keys - ["en"]
      return if languages.empty?

      sources = site.pages.select { |p| p.data["i18n"] && p.data["translate"] != false }
      languages.each do |lang|
        sources.each { |page| site.pages << clone(site, page, lang) }
      end
    end

    private

    # A REAL Jekyll::Page re-read from the source file — never `page.dup`: a dup
    # shares renderer state with its source and silently renders the source
    # page's Liquid context (English) into the clone's destination.
    def clone(site, page, lang)
      copy = Jekyll::Page.new(site, site.source, File.dirname(page.relative_path), page.name)
      copy.data["lang"] = lang
      copy.data["permalink"] = "/#{lang}#{page.url}"
      # Territory-qualified OG locale (fa_IR, zh_CN, ...) from _data/languages.yml.
      # jekyll-seo-tag resolves og:locale as page.locale || site.locale || page.lang,
      # so stamping it here makes seo-tag emit the qualified form natively. Meta-tag
      # only — URLs, <html lang>, and hreflang all keep the bare `lang` code. Must be
      # set on EVERY clone (site.locale exists, so an unstamped clone would claim the
      # English en_US); an unmapped language falls back to its bare code.
      lang_meta = site.data["languages"][lang] if site.data["languages"]
      copy.data["locale"] = (lang_meta && lang_meta["og_locale"]) || lang
      copy
    end
  end
end
