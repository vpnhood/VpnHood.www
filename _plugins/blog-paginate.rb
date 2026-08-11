# Pagination for the blog index.
#
# jekyll-paginate only works on _posts, and jekyll-paginate-v2 is another
# dependency for something this small — so the pages are generated here instead,
# which also keeps the URLs ours: /blog/ is page 1, then /blog/page/2/, and a
# translated tree paginates inside itself (/fa/blog/page/2/).
#
# Runs at :low priority so blog-pages.rb (:normal) has already stamped every
# post's permalink and language — this reads doc.url.
#
# SEO: each page is self-canonical with its own title. Google's guidance is not
# to canonicalise page 2 back to page 1 (that hides its posts from indexing),
# and rel=prev/next has not been an indexing signal since 2019 — the visible
# links are what matter, so that is all this emits.
module VhBlogPaginate
  class Generator < Jekyll::Generator
    safe false
    priority :low

    PER_PAGE = 10

    def generate(site)
      collection = site.collections["blog"]
      return if collection.nil?

      posts = collection.docs
                        .reject { |d| d.data["published"] == false }
                        .sort_by { |d| d.data["date"] || Time.at(0) }
                        .reverse

      # Collect first: the loop appends to site.pages, and a generated page is
      # itself a blog index, which would otherwise re-paginate forever.
      sources = site.pages.select { |p| p.data["blog_index"] && p.data["paginator"].nil? }

      sources.each do |index|
        lang = index.data["lang"] || "en"
        mine = posts.select { |d| (d.data["lang"] || "en") == lang }
        total = [(mine.length.to_f / PER_PAGE).ceil, 1].max

        base = index.url.chomp("/")   # "/blog" or "/fa/blog"

        (1..total).each do |number|
          slice = mine[(number - 1) * PER_PAGE, PER_PAGE] || []
          data = paginator(base, number, total, slice)

          if number == 1
            index.data["paginator"] = data
          else
            site.pages << page_for(site, index, base, number, data)
          end
        end
      end
    end

    private

    def paginator(base, number, total, posts)
      {
        "page" => number,
        "total_pages" => total,
        "posts" => posts,
        "previous_page" => (number > 1 ? number - 1 : nil),
        "previous_page_path" => (number > 1 ? path_for(base, number - 1) : nil),
        "next_page" => (number < total ? number + 1 : nil),
        "next_page_path" => (number < total ? path_for(base, number + 1) : nil),
      }
    end

    def path_for(base, number)
      number <= 1 ? "#{base}/" : "#{base}/page/#{number}/"
    end

    # A real Jekyll::Page re-read from blog/index.html — never `dup`, which shares
    # renderer state with its source (see _plugins/i18n-pages.rb).
    def page_for(site, index, base, number, data)
      copy = Jekyll::Page.new(site, site.source, File.dirname(index.relative_path), index.name)
      copy.data["lang"] = index.data["lang"] if index.data["lang"]
      copy.data["permalink"] = path_for(base, number)
      copy.data["paginator"] = data
      # Every title on the site carries the brand (.docs/seo-and-semantic-html.md §3),
      # and each page needs a distinct one so they don't read as duplicates.
      copy.data["title"] = index.data["title"].to_s.sub(" - VpnHood!", " - Page #{number} - VpnHood!")
      copy
    end
  end
end
