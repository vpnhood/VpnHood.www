# SEO & Semantic-HTML Conventions

Conventions for keeping VpnHood.www accessible and SEO-correct. These are
**binding rules for any markup change** — pages, shared includes (`header.html`,
`footer.html`, `faq.html`), and components. They complement the "SEO" section in
`CLAUDE.md` (which covers jekyll-seo-tag, JSON-LD, sitemap/robots); this file
covers the semantic-HTML side: heading outlines, title branding, SVG a11y, and
link lists.

Core principle, applied throughout: **if a piece of text is not part of the
page's content outline, it is not a heading** — and **visual size is a CSS
concern, never a reason to pick a heading level.**

---

## 1. Heading outline — one H1, no skipped levels

Every page must form a clean outline: `h1 → h2 → h3 …`, descending one level at a
time. Going back *up* any number of levels is fine; skipping *down* a level
(e.g. `h1` then `h3`) is not.

- **Exactly one `<h1>` per page** = the page's main title (the hero
  `section-title`). Never a second H1.
- **Don't skip levels.** A section title under the page H1 is `<h2>`; a card or
  item under that section is `<h3>`; and so on.
- **Tag = semantic level; size = class.** Decouple appearance from level using
  Bootstrap's `.h1`–`.h6` size classes. `<h3 class="h5">Foo</h3>` is level 3 in
  the outline but *looks* like an h5. This is the mechanism for re-leveling a
  heading **without changing how it looks** — always carry the original size as
  a `.hN` class when you change a tag (unless a class already sets the size, e.g.
  `.section-title` = 40px).
- **Non-outline text must not be a heading.** Decorative, boilerplate, brand, or
  navigation text is not content outline → use `<div>`/`<p>`/`<span>`. Real
  examples already fixed in this repo:
  - the pre-loader splash "VpnHood!" in `header.html` → `<div>`;
  - the off-canvas menu brand "VpnHood! connect" → `<div class="h4 …">`;
  - the footer column labels `.footer-module-title` (Free VPN / Solutions /
    Support / Developers) → `<div>` (they are navigation, repeated on every
    page; as `<h2>` they diluted the content h2s on all 21 pages).

### Section markup pattern

The ported "section head" pattern must map to the outline like this:

| Visual element            | Element / class                                  | Outline role        |
|---------------------------|--------------------------------------------------|---------------------|
| Eyebrow / kicker          | `<p class="vh-txt-grad-purple-400">` in `.section-label` | **not a heading** |
| Section title             | `<h2 class="section-title …">`                   | section (h2)        |
| Card / feature / sub-item | `<h3 …>` (+ `.hN` size class as needed)          | subsection (h3)     |

The eyebrow is a label for the title, not a separate outline node, so it is a
`<p>`. The eyebrow's styling is bound to `.section-label > p` in
`_sass/theme/_default.scss` (and `#resilient .section-label > p` in
`_sass/pages/_home.scss`) — keep the selector and the element in sync.

### FAQ component (`_includes/faq.html`)

The question heading level is context-dependent:
- `heading=true` (default, on content pages): the FAQ section title is `<h2>`, so
  each question renders `<h3>`.
- `heading=false` (the `/faq` page, which supplies its own page `<h1>`): each
  question renders `<h2>`.

This is driven by the `q_level` assign at the top of the include — don't hardcode
the question tag.

### Verify before committing markup changes

After `bundle exec jekyll build`, every page in `_site` must be single-H1,
first-heading-H1, and skip-free. Quick audit:

```bash
python - <<'PY'
import re, glob
bad = 0
for f in sorted(glob.glob("_site/**/index.html", recursive=True)):
    hs = [int(m.group(1)) for m in re.finditer(r'<h([1-6])\b', open(f, encoding="utf-8").read())]
    if not hs: continue
    v = []
    if hs[0] != 1: v.append("first=h%d" % hs[0])
    if hs.count(1) != 1: v.append("%d h1" % hs.count(1))
    for i in range(1, len(hs)):
        if hs[i] > hs[i-1] + 1: v.append("skip h%d->h%d" % (hs[i-1], hs[i]))
    if v: bad += 1; print(f, v)
print("pages with violations:", bad)   # must be 0
PY
```

---

## 2. Title tags — brand on every page

- A page's `<title>` comes from front-matter `title:` (rendered
  `{{ page.title }}` in `header.html`); `og:title` and the Twitter title derive
  from it via seo-tag. So `title:` is the single source for all three.
- **Every `title:` must contain the "VpnHood!" brand.** seo-tag runs with
  `title=false`, so it does **not** append the brand — you must include it.
- Convention: `Descriptive Keywords | VpnHood!`, or `… | VpnHood! CONNECT` for
  CONNECT product pages. The home page is brand-first:
  `VpnHood! — Free, Secure & Open-Source VPN`.
- The brand belongs in the **title tag**, not in a duplicate H1. One descriptive
  H1 per page + brand in the title/`og:title` + the Organization JSON-LD is the
  SEO-optimal arrangement — don't reintroduce a brand H1 to "boost" the keyword.

Audit titles for the brand:

```bash
for f in $(find . -name '*.html' -not -path './_site/*' -not -path './_reference/*'); do
  t=$(awk '/^---/{n++;next} n==1 && /^title:/{sub(/^title:[ ]*/,"");print;exit}' "$f")
  [ -n "$t" ] && ! echo "$t" | grep -qi vpnhood && echo "MISSING brand: $f -> $t"
done
```

---

## 3. Inline SVG accessibility

Every inline `<svg>` is either decorative or meaningful — mark it accordingly:

- **Decorative icon** (redundant with adjacent visible text): add
  `aria-hidden="true"` to the `<svg>`. This is the default for the icons on this
  site (feature bullets, chevrons, contact-card glyphs, etc.).
- **Icon-only link/button** (an `<a>`/`<button>` whose only content is an SVG,
  with no visible text): put an `aria-label` on the **link/button** (e.g.
  `aria-label="VpnHood on LinkedIn"`); the inner `<svg>` stays `aria-hidden`.
  Without this, a screen reader announces only the URL.

A bare `<svg>` with neither attribute is a defect.

---

## 4. Lists for groups of links

A group of related links is a list — `<ul><li>` — not loose `<a>`s in a wrapper.
Put layout utilities on the `<ul>` and strip the default list chrome:

```html
<ul class="d-flex align-items-center gap-3 list-unstyled mb-0">
  <li><a aria-label="VpnHood on LinkedIn" …>…</a></li>
  …
</ul>
```

Applies to the footer nav columns (already lists) and the footer social-icon row.
Screen readers then announce "list, N items," which is the correct grouping.

---

## Why this matters (rationale, in one place)

- A single descriptive H1 + clean outline is how search engines and assistive
  tech read a page's structure; duplicate/boilerplate/skipped headings muddy it.
- Repeating generic navigation labels (footer columns) as H2 on every page makes
  them compete with real content topics — boilerplate dilution. Demote to
  non-headings.
- The brand keyword earns the most in the `<title>`; a hidden duplicate H1 earns
  almost nothing and breaks the outline.
- `aria-hidden`/`aria-label` on SVGs and list semantics for link groups are
  low-cost, high-value a11y wins that also keep the DOM clean for crawlers.
