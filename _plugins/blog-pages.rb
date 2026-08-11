# Blog posts: URLs, language, and the branded <title>.
#
# Source files come from the VpnHood.Blog repo (fetched at build time) and are
# laid out as _blog/<lang>/<slug>.md — the same shape as posts/<lang>/<slug>.md
# there, so the fetch step is a plain copy. Jekyll would derive the URL from
# that path (/blog/en/<slug>/), which is wrong in two ways: English must not
# carry a language segment, and a translation belongs in its own language tree
# (/fa/blog/<slug>/, matching _plugins/i18n-pages.rb) rather than under /blog/.
# So permalinks are stamped here instead.
#
# The site's SEO rule is that every <title> contains "VpnHood!" (see
# .docs/seo-and-semantic-html.md §3). A blogger writes a headline, not a title
# tag, so the brand is appended here: `headline` keeps the clean text for the
# <h1>, `title` becomes the branded form that header.html and jekyll-seo-tag
# read. A post that already says "VpnHood!" is left alone rather than repeating
# it.
module VhBlogPages
  class Generator < Jekyll::Generator
    safe false

    BRAND = "VpnHood!".freeze

    def generate(site)
      collection = site.collections["blog"]
      return if collection.nil?

      collection.docs.each do |doc|
        lang = language_of(doc)
        slug = File.basename(doc.basename, ".*")

        # English is the default tree and carries no `lang` — the same
        # convention as source pages, which header.html reads as
        # `page.lang | default: 'en'`.
        doc.data["lang"] = lang unless lang == "en"
        doc.data["permalink"] = lang == "en" ? "/blog/#{slug}/" : "/#{lang}/blog/#{slug}/"
        doc.data["slug"] = slug

        headline = doc.data["title"].to_s
        doc.data["headline"] = headline
        doc.data["title"] = brand(headline)

        # `image` is never empty: _config.yml gives every document the site-wide
        # OG share image by default. So the index card can't test it directly —
        # every post would show the same generic thumbnail. A post's own image
        # always lives under the blog asset path (the content repo's validator
        # requires it), which is what distinguishes the two.
        image = doc.data["image"].to_s
        doc.data["card_image"] = image if image.start_with?("/assets/images/blog/")

        # Territory-qualified OG locale, same source and reasoning as the
        # generated page clones in _plugins/i18n-pages.rb.
        if lang != "en" && site.data["languages"]
          meta = site.data["languages"][lang]
          doc.data["locale"] = (meta && meta["og_locale"]) || lang
        end
      end
    end

    private

    # _blog/en/foo.md -> "en"; a post sitting directly in _blog/ is English too.
    def language_of(doc)
      parts = doc.relative_path.sub(%r{\A/?_blog/}, "").split("/")
      parts.length > 1 ? parts[0] : "en"
    end

    def brand(headline)
      return BRAND if headline.empty?
      headline.include?(BRAND) ? headline : "#{headline} - #{BRAND}"
    end
  end
end
