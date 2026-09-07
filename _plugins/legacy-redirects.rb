# Redirect pages for retired site URLs.
#
# Blog posts retire through _data/blog_redirects.yml (see _plugins/blog-redirects.rb);
# this is the equivalent for the pages in this repo, where the map is small enough to
# live in the plugin.
#
# The wrinkle a single stub would miss: every page carrying `i18n:` front matter is
# cloned into each /<lang>/ tree by _plugins/i18n-pages.rb, so retiring one page retires
# thirteen URLs. Each entry therefore emits a stub per language too, pointing at that
# language's copy of the destination rather than dumping a Persian visitor on the English
# page. Runs at :low so the clones already exist and a real page is never overwritten.
#
# A Cloudflare redirect rule on www.vpnhood.com, if one is configured, 301s at the edge
# and these stubs are never served. They are what covers the site when it is not.
module VhLegacyRedirects
  REDIRECTS = {
    # /free-vpn/features/ described five features for CONNECT only. CLIENT and CONNECT
    # now share one feature set, and /features/ explains all of them with child pages.
    "/free-vpn/features/" => "/features/"
  }.freeze

  class Generator < Jekyll::Generator
    safe false
    priority :low

    def generate(site)
      languages = (site.data["i18n"] || {}).keys - ["en"]
      taken = site.pages.map(&:url).to_set

      REDIRECTS.each do |from, to|
        emit(site, taken, from, to, "en")
        languages.each { |lang| emit(site, taken, "/#{lang}#{from}", "/#{lang}#{to}", lang) }
      end
    end

    private

    def emit(site, taken, from, to, lang)
      if taken.include?(from)
        Jekyll.logger.warn "Legacy redirects:", "#{from} is a real page - skipping the redirect"
        return
      end

      site.pages << VhBlogRedirects::RedirectPage.new(site, from, to, lang)
      taken << from
    end
  end
end
