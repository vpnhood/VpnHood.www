# Redirect pages for retired site URLs.
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
    "/free-vpn/features/" => "/features/",
    # /free-vpn/free-vs-premium/ was only the compare table that /free-vpn/go-premium/
    # also renders. Search Console (Jun-Sep 2026) showed it ranking for brand terms at
    # 0.7% CTR and for no "free vs premium" query at all, so the duplicate went. The
    # "Free vs Premium" menu entry survives, pointing at /free-vpn/go-premium/#compareTable.
    "/free-vpn/free-vs-premium/" => "/free-vpn/go-premium/",
    # The blog was retired after two posts; the one worth keeping became a guide.
    "/blog/" => "/guides/",
    "/blog/welcome-to-the-vpnhood-blog/" => "/guides/",
    "/blog/what-is-split-tunneling/" => "/guides/what-is-split-tunneling/",
    # Legal documents moved to /legal/<scope>/<document>/ (.docs/legal-pages.md). The old
    # addresses are printed in installed apps, store listings and emails: never remove these.
    # /terms-of-use/ was every product's terms page before the per-product split, so it goes
    # to the index, not to the MANAGER terms; /legal/privacy-policy/ never existed but is the
    # address people guess.
    "/privacy-policy/" => "/legal/",
    "/terms-of-use/" => "/legal/",
    "/legal/privacy-policy/" => "/legal/",
    "/legal/terms-of-use/" => "/legal/",
    "/vpnhood-connect-privacy-policy/" => "/legal/vpnhood-connect/privacy-policy/",
    "/vpnhood-client-privacy-policy/" => "/legal/vpnhood-client/privacy-policy/",
    "/vpnhood-manager-privacy-policy/" => "/legal/vpnhood-manager/privacy-policy/",
    "/legal/vpnhood-connect-terms-of-use/" => "/legal/vpnhood-connect/terms-of-use/",
    "/legal/vpnhood-client-terms-of-use/" => "/legal/vpnhood-client/terms-of-use/",
    "/legal/vpnhood-manager-terms-of-use/" => "/legal/vpnhood-manager/terms-of-use/"
  }.freeze

  # Paths that only ever existed in English. Posts were never translated, so a
  # /<lang>/blog/ URL never existed and a stub there would be pure noise; legal pages
  # are English only by policy.
  ENGLISH_ONLY = ["/blog/", "/blog/welcome-to-the-vpnhood-blog/",
                  "/blog/what-is-split-tunneling/",
                  "/privacy-policy/", "/terms-of-use/", "/legal/privacy-policy/",
                  "/legal/terms-of-use/", "/vpnhood-connect-privacy-policy/",
                  "/vpnhood-client-privacy-policy/", "/vpnhood-manager-privacy-policy/",
                  "/legal/vpnhood-connect-terms-of-use/", "/legal/vpnhood-client-terms-of-use/",
                  "/legal/vpnhood-manager-terms-of-use/"].freeze

  class Generator < Jekyll::Generator
    safe false
    priority :low

    def generate(site)
      languages = (site.data["i18n"] || {}).keys - ["en"]
      taken = site.pages.map(&:url).to_set

      REDIRECTS.each do |from, to|
        emit(site, taken, from, to, "en")
        next if ENGLISH_ONLY.include?(from)

        languages.each { |lang| emit(site, taken, "/#{lang}#{from}", "/#{lang}#{to}", lang) }
      end
    end

    private

    def emit(site, taken, from, to, lang)
      if taken.include?(from)
        Jekyll.logger.warn "Legacy redirects:", "#{from} is a real page - skipping the redirect"
        return
      end

      site.pages << RedirectPage.new(site, from, to, lang)
      taken << from
    end
  end

  class RedirectPage < Jekyll::PageWithoutAFile
    def initialize(site, url, target, lang = "en")
      super(site, site.source, "", "index.html")
      data["permalink"] = url
      data["sitemap"] = false # jekyll-sitemap must not advertise a redirect stub
      data["layout"] = nil
      # The script keeps the #fragment (a meta refresh drops it); the refresh covers no-JS.
      self.content = <<~HTML
        <!doctype html>
        <html lang="#{lang}">
          <head>
            <meta charset="utf-8" />
            <title>Redirecting&hellip;</title>
            <link rel="canonical" href="#{absolute(site, target)}" />
            <meta name="robots" content="noindex" />
            <script>location.replace(#{target.to_json} + location.hash)</script>
            <meta http-equiv="refresh" content="0; url=#{target}" />
          </head>
          <body>
            <h1>Redirecting&hellip;</h1>
            <p><a href="#{target}">Continue to the new location</a></p>
          </body>
        </html>
      HTML
    end

    private

    def absolute(site, target)
      return target if target.start_with?("http://", "https://")
      "#{site.config["url"]}#{target}"
    end
  end
end
