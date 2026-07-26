# Injects page <title> and meta description from the i18n data files, so page
# metadata is translated by the same per-key vhtranslator data pipeline as body
# copy (single source of truth in _data/i18n/<lang>/<page_key>.json):
#
#   "meta_title":       becomes page.title       (the <title> tag + og:title/JSON-LD)
#   "meta_description": becomes page.description (meta description + og:description)
#
# The page names its data file explicitly with "i18n: <page_key>" front matter
# (see CLAUDE.md "Page Anatomy"); the body reuses the same declaration via
# "{% assign t = site.data.i18n[vh_lang][page.i18n] %}". Pages without the key
# (legal pages, generated CSS) keep whatever front matter they declare. Missing
# translated keys fall back to English, mirroring the Liquid-side fallbacks.
#
# Runs at :site :pre_render — before any payload is assembled — so jekyll-seo-tag
# sees the injected values exactly as if they were front matter.
module VhI18nMeta
  def self.apply(site, page)
    key = page.data["i18n"]
    return if key.to_s.empty?

    i18n = site.data["i18n"] || {}
    lang = page.data["lang"] || "en"
    localized = (i18n[lang] || {})[key] || {}
    english = (i18n["en"] || {})[key] || {}

    # An empty string (e.g. a skipped translation) falls back like a missing key.
    title = [localized["meta_title"], english["meta_title"]].find { |v| !v.to_s.empty? }
    description = [localized["meta_description"], english["meta_description"]].find { |v| !v.to_s.empty? }
    page.data["title"] = title unless title.to_s.empty?
    page.data["description"] = description unless description.to_s.empty?
  end
end

Jekyll::Hooks.register :site, :pre_render do |site|
  documents = site.pages + site.collections.values.flat_map(&:docs)
  documents.each { |page| VhI18nMeta.apply(site, page) }
end
