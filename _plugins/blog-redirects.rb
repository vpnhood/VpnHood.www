# Redirect pages for retired blog posts.
#
# The map comes from redirects.yml in the VpnHood.Blog repo, staged by the build
# into _data/blog_redirects.yml (see CLAUDE.md "Blog"). Deleting a post would
# otherwise leave its URL returning 404, throwing away whatever ranking and
# inbound links it had earned; an entry there keeps the address working.
#
# GitHub Pages can't issue a 301, so each retired URL gets a tiny page carrying a
# canonical link to the destination plus an instant meta refresh — the redirect
# form Google treats as equivalent to a permanent redirect, and the same approach
# jekyll-redirect-from uses. The page is noindex so the stub itself never ranks.
#
# Validation lives in the blog repo (tools/validate-posts.py): a target must
# exist, a redirect may not point at another redirect, and a slug may not be both
# a live post and a redirect. This generator therefore trusts the data, but still
# skips an entry that would collide with a real page rather than overwrite it.
module VhBlogRedirects
  class Generator < Jekyll::Generator
    safe false

    def generate(site)
      redirects = site.data["blog_redirects"]
      return unless redirects.is_a?(Hash) && !redirects.empty?

      taken = site.pages.map(&:url).to_set
      site.collections["blog"]&.docs&.each { |doc| taken << doc.url }

      redirects.each do |old_slug, target|
        next if old_slug.to_s.empty? || target.to_s.empty?

        url = "/blog/#{old_slug}/"
        if taken.include?(url)
          Jekyll.logger.warn "Blog redirects:", "#{url} is a real page — skipping the redirect"
          next
        end

        site.pages << RedirectPage.new(site, url, target.to_s)
      end
    end
  end

  class RedirectPage < Jekyll::PageWithoutAFile
    def initialize(site, url, target)
      super(site, site.source, "", "index.html")
      data["permalink"] = url
      data["sitemap"] = false # jekyll-sitemap must not advertise a redirect stub
      data["layout"] = nil
      self.content = <<~HTML
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Redirecting&hellip;</title>
            <link rel="canonical" href="#{absolute(site, target)}" />
            <meta name="robots" content="noindex" />
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
