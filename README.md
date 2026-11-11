# hyperbyte.cloud

The static site for hyperbyte.cloud. The HTML in this repo is the source: edit
pages directly. Nothing is pulled from Ghost any more.

## After editing

```bash
python3 tools/build.py
```

This rewrites `sitemap.xml` and `rss.xml` from the pages, then checks that every
local link and image resolves, that nothing loads from a third party, that each
indexable page has a title, description and canonical, and that no page still
contains a `[TO CONFIRM]` marker. It exits non-zero on any problem.
`--draft` skips the `[TO CONFIRM]` check.

When you change a blog post, update its `article:modified_time` meta tag and the
`dateModified` field in its JSON-LD; the sitemap and feed read those.

## Layout

- `index.html`, `<slug>/index.html`: pages and posts
- `404.html`: served for unknown paths; configure the web server to use it
- `assets/site.css`, `assets/site.js`: styles and the mobile menu
- `assets/fonts.css`, `assets/fonts/`: Inter, served locally (SIL OFL 1.1)
- `assets/social-card.png`: 1200x630 share image used as `og:image` on every page
- `assets/media/`: images used in posts
- `home/`, `blog/`, `blog.html`, `hyperbytedb/`: redirects to their new URLs
