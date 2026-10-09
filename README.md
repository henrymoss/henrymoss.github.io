# henrymoss.github.io

**Mathematical AI for Decision and Discovery** — Henry Moss's group in the
School of Mathematical Sciences, Lancaster University. Built with Jekyll and
served by GitHub Pages from `master`.

The site is a single page. Everything on it comes from four data files plus
`_pages/index.html`; there are no posts and no per-paper pages.

The group name lives in `_config.yml` as `title`; it is the header wordmark and
feeds every page title.

## Editing the content you'll actually touch

Most updates are one-line edits to a data file — no templates involved.

| What | Where |
|---|---|
| Publications | `_data/publications.yml` |
| Group members and visitors | `_data/people.yml` |
| Industry collaborators (About panel) | `_data/collaborations.yml` |
| Top navigation | `_data/navigation.yml` |
| About text, announcement strip | `_pages/index.html` |

### Adding a publication

Add an entry at the top of `_data/publications.yml`:

```yaml
- title: "Paper title"
  authors: "Surname, Surname, Moss"
  venue: "NeurIPS 2026"
  year: 2026
  thumbnail: /images/figures/something.png
  arxiv: https://arxiv.org/abs/...
```

`title` and `thumbnail` are required. For the link target you need at least one
of `pdf` (a file under `files/papers/`), `arxiv`, or `link` (publisher page) —
the thumbnail and title link to the first one present. `code`, `honour` and
`award` are optional; `honour` renders a red pill (spotlight, oral), `award` a
darker one (prizes).

Separate authors with `, ` — the template splits on that and bolds `Moss`
automatically, so don't add any markup to the `authors` string yourself.

The page groups the list by `year` on its own, newest year first, so the year
banner comments in the file are only an editing aid. To lift a paper out of its
year and into the **Preprints** block at the top, add:

```yaml
  under_review: true
```

That block is hidden entirely while nothing carries the flag.

### Adding a person

Add to `members` (or `visitors`) in `_data/people.yml`. If you have no photo,
point `image` at a generated initials card in `images/people/`. `topic` is
recorded in the file but is not currently shown on the team cards.

Photos taken from someone's institutional profile page should only go up once
that person is happy for theirs to appear here.

## Images

Three scripts generate the images that are not photographs. Each owns its own
files — don't make two of them write the same one — and all are safe to re-run:

```bash
python3 tools/gen_assets.py   # headshot crop, initials cards for new members
python3 tools/gen_logo.py     # images/logo-header.svg, images/favicon.svg
python3 tools/gen_og.py       # images/og-card.png, the link-preview card
```

`logo-header.svg` is the animated hop-scotch mark in the header bar. It carries
its own `<style>`, so it animates inside a plain `<img>` with no page CSS and
no JavaScript, and holds still under `prefers-reduced-motion`. It is drawn
light-on-dark for the navy bar.

`og-card.png` is what Slack, LinkedIn and the rest show when the site is
shared. It has to be a raster file — essentially no platform renders SVG there
— so `gen_og.py` redraws the lockup with Pillow rather than reusing the SVG.
`_config.yml` points `og_image` at it, and every page falls back to it.

Replace any generated image with a real one by dropping a file into `images/`
and updating the path that refers to it. Real photos and real figures are better
than the placeholders wherever you have them.

Nothing prunes `images/` or `files/` automatically. When you drop a publication
or swap a thumbnail, delete the orphan by hand — these directories are the
bulk of the repository.

## Previewing changes before you push

```bash
python3 tools/serve.py
```

Then open <http://localhost:8000>. It watches the source files and rebuilds
within about half a second of a save — edit, refresh, repeat. Ctrl-C to stop,
and `python3 tools/serve.py 8080` if the port is taken.

If a change breaks the build, it prints the error and keeps serving the last
good version, so the browser never goes blank.

This needs no bundler and no Jekyll — just Ruby plus three pure-Ruby gems:

```bash
gem install --user-install liquid kramdown kramdown-parser-gfm
```

`tools/serve.py` wraps `tools/preview.rb`, which implements only the subset of
Jekyll this site uses. It is for eyeballing layout and content; GitHub Pages
still does the authoritative build, and that is where `feed.xml`, `sitemap.xml`
and the `redirect_from` stubs are generated.

Because `preview.rb` renders with the plain `liquid` gem, `_pages/index.html`
deliberately sticks to stock Liquid filters rather than Jekyll's `group_by` and
`where_exp`, which do not exist there and would silently pass their input
straight through.

### Running real Jekyll instead (optional)

Only worth it if you need to check the generated feed, sitemap or redirects.
It requires a system package, because several Jekyll dependencies have native
extensions:

```bash
sudo apt install ruby-dev build-essential
gem install --user-install bundler
bundle install
bundle exec jekyll serve
```
