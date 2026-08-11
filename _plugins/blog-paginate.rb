# Extra pages for the paginated blog index: /blog/page/2/, /blog/page/3/, ...
#
# jekyll-paginate only works on _posts and paginate-v2 is a dependency this does
# not need, so the pages are generated here — which also keeps the URLs ours and
# lets a translated tree paginate inside itself (/fa/blog/page/2/).
#
# This generator deliberately does as little as possible: it creates the extra
# page objects and stamps ONE integer, `paginator_page`. Everything else —
# which posts appear, how many pages there are, the prev/next links — is worked
# out in blog/index.html from site.blog.
#
# That split is not stylistic. Setting richer data on the EXISTING page-1 object
# looked fine but broke under `jekyll serve`: after a rebuild triggered by a
# _data change, the page that gets rendered is not the object the generator
# mutated, so page.paginator came back nil and the index rendered empty. A
# one-shot `jekyll build` never hit it, so production was fine and only local
# preview broke — the worst kind of bug to leave in. Page 1 now derives
# everything itself and cannot be affected.
#
# Runs at :low priority so blog-pages.rb (:normal) has already stamped each
# post's language.
module VhBlogPaginate
  class Generator < Jekyll::Generator
    safe false
    priority :low

    # Keep in step with vh_per_page in blog/index.html.
    PER_PAGE = 25

    def generate(site)
      collection = site.collections["blog"]
      return if collection.nil?

      published = collection.docs.reject { |d| d.data["published"] == false }

      # Collect first: the loop appends to site.pages, and a generated page is
      # itself a blog index, which would otherwise re-paginate forever.
      indexes = site.pages.select { |p| p.data["blog_index"] && p.data["paginator_page"].nil? }

      indexes.each do |index|
        lang = index.data["lang"] || "en"
        count = published.count { |d| (d.data["lang"] || "en") == lang }
        total = (count.to_f / PER_PAGE).ceil

        base = index.url.chomp("/") # "/blog" or "/fa/blog"
        (2..total).each { |number| site.pages << page_for(site, index, base, number) }
      end
    end

    private

    # A real Jekyll::Page re-read from blog/index.html — never `dup`, which shares
    # renderer state with its source (see _plugins/i18n-pages.rb).
    def page_for(site, index, base, number)
      copy = Jekyll::Page.new(site, site.source, File.dirname(index.relative_path), index.name)
      copy.data["lang"] = index.data["lang"] if index.data["lang"]
      copy.data["permalink"] = "#{base}/page/#{number}/"
      copy.data["paginator_page"] = number
      # Every title on the site carries the brand (.docs/seo-and-semantic-html.md §3),
      # and each page needs a distinct one so they don't read as duplicates.
      copy.data["title"] = index.data["title"].to_s.sub(" - VpnHood!", " - Page #{number} - VpnHood!")
      copy
    end
  end
end
