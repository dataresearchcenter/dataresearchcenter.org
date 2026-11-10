# CLAUDE.md

## What this is

The website of the Data and Research Center (DARC),
[dataresearchcenter.org](https://dataresearchcenter.org), built with
[Zensical](https://zensical.org/) from `mkdocs.yml` (`theme.variant: classic`:
the Material look the CSS is built on). Content is markdown under `docs/`;
push to `main` builds and deploys to S3.

Other DARC sites clone this repo; only `darc-zensical.css` is shared, from
[`zensical-theme-darc`](https://github.com/dataresearchcenter/zensical-theme-darc).
Zensical has no MkDocs `hooks` and only its
[supported plugins](https://zensical.org/docs/compatibility/mkdocs/plugins/);
templates are MiniJinja (no Python calls).

## Commands

```bash
make install     # .venv with Zensical and the scripts' dependencies
make fetch       # OpenAleph API + images → data/openaleph/, docs/assets/openaleph/ (network)
make render      # data/ + blog posts → docs/snippets/ (offline; build and serve run it)
make build       # → site/ (default target; CI=true also runs the optimize plugin, needs pngquant)
make serve       # http://localhost:8000, live reload
make publish     # fetch, build, sync site/ to S3
make clean       # remove site/ and docs/snippets/
```

Run `make` from the project root (snippet paths resolve against the working
directory). It uses `.venv` when present, else the tools on `PATH` (CI). All
targets are repeatable; `build` works offline from the last `fetch`.

## Layout

```
docs/
  index.md               landing page; ends with the team (#who-we-are)
  what-we-do.md  projects.md  contact.md  open-source.md
  zone.md                darc.zone landing (search.openaleph.org) with plans and the sign up guide; `header: zone`
  openaleph.md           OpenAleph open source project (merged from openaleph.org)
  openaleph/managed.md   the managed service; openaleph/assets/icons/
  blog/                  blog plugin: index.md, posts/ (categories DARC, OpenAleph)
  reference.md  typography.md   authoring aids (not in the nav)
  assets/                images; assets/openaleph/ is fetched (gitignored)
  stylesheets/           tokens.css · components.css · site.css · landing.css
  javascripts/scroll-color.js  page, header and drawer take the color of the section at mid-viewport
  overrides/             main.html, blog.html, partials/{header,content,logo,post,copyright}.html
  snippets/              make render output (gitignored, `exclude_docs`)
data/
  topics.yml  dataset_groups.yml   editorial (fields in README.md)
  openaleph/             make fetch output (gitignored)
scripts/
  fetch.py  render.py  templates/  resize_assets.py
contrib/nginx.map        301s: openaleph.org pages and blog, legacy blog URLs, /who-we-are/
.github/workflows/publish.yml      pip install, pngquant, make fetch build, S3 sync
```

## Snippets pipeline

- `fetch.py` resolves the collection IDs in `data/*.yml` via the API
  (non-public ones are dropped with a warning), snapshots `/api/2/metadata` and
  `/api/2/statistics`, and downloads topic images (Wikimedia as 960px
  renditions via the Commons API, SVGs as is), group icons, FtM schema icons and
  flags. Download failures are warnings. Env: `OPENALEPH_API_URL`,
  `OPENALEPH_USER_AGENT` (default `openaleph` passes the Anubis challenge),
  `BUILD_USER_AGENT` (image downloads).
- `render.py` writes one block per `scripts/templates/*.html` and `news.html`
  (the newest posts through the blog's `partials/post.html`, as templates can't
  list posts outside the blog). Without a snapshot it warns and skips the
  OpenAleph blocks. Re-run it after adding or renaming a post.
- Pages include blocks with `--8<-- "docs/snippets/<name>.html"`: Zensical
  resolves snippet paths against the working directory (`!relative` isn't
  supported) and drops a missing snippet silently.
- `md_in_html` misreads block tags indented 4+ spaces: `render.py` flattens the
  indentation.
- Collection IDs are strings in `topics.yml`, integers in `dataset_groups.yml`.
  Index numbers: entities = `things`, datasets = `collections`, countries =
  country keys, documents = schemata descending from `Document`.

## CSS

Load order (`extra_css`): `darc-zensical.css` (upstream, by URL: palette
`--oa-*`, `--font-sans`/`--font-mono` and their `@font-face` on the DARC CDN,
scheme tokens), then:

- `tokens.css`: `--color-white`/`--color-black` (text and fills, swapped on
  light surfaces), `--bg-*` section colors, `--stroke-width` (2px, every
  border), radii, `--shadow-button`, `--container-lg` (1024px),
  `--container-xl` (1280px: header, footer, `wide: true` pages) and `--page-x`
  (the page's side padding, also the zone header's).
- `components.css`: the authoring components (table below).
- `site.css`: chrome (drawer, TOC, header, footer), typography, blog.
- `landing.css`: the generated blocks, News, the darc.zone hero.

`theme.font: false`: no Google Fonts. The palette is slate only, so rules are
written for the dark page; light sections are dark-on-light through the light
surfaces rule in `components.css`, which also sets the upstream light-scheme
code and admonition tokens.

## Components

See `docs/reference.md` for snippets. Wrapper `<div>`/`<section>` need the
`markdown` attribute.

| Component | Markup |
|---|---|
| Section | `<section class="screen screen--bg-{white,black,green,orange,yellow,purple}">`, `.screen--full-height`, `.screen--narrow` (default width on a wide page) |
| Section headline | `## …` first in a section |
| Hero, landing | `.hero.hero--landing` |
| Hero, darc.zone | `.hero.hero--landing.hero--zone`; numbers via `stats_zone.html` (`ul.stats.stats--row`) |
| Hero, two columns | `.hero` with a `<div markdown>` and an image; source order sets the sides. A logo or symbol (`.no-border`, `.section-icon`) sits inset, a screenshot fills the column |
| Buttons | `.btn`, `.btn.btn--primary`; a paragraph of buttons is an action row |
| Card grid | `<div class="grid cards">` + list; `{ .card--full }`; `.grid--wide` (2 per row), `.grid--three` |
| Block cards | `<div class="card">` in a `.grid`: `.card--feature`, `.card--media` (`figure.card__media`, `.card__body`, `.card__footer`), filled with `screen--bg-*` |
| Data card (templates) | `header.card__header` first; rows `CollectionList` / `Statistics__list` share one style |
| Profile cards | `<div class="grid cards profiles">` |
| Search pill | `<form role="search">` with an input and a `.btn` |
| Plan price | `**€200**{.price}` |
| Chips | `<kbd>` |
| Utilities | `.muted`, `.dim`, `{.no-border}`, `{.no-shadow}`, `{.center}`, `{.section-icon}` |
| Layer stack | `<div class="stack">`, a paragraph per layer: `**label**`, then links, one per line |
| Diagram | ` ```mermaid ` in `<div class="diagram">`; Mermaid can't link nodes (`strict`) |

## Layout chrome

- Horizontal padding is on `main.md-main` only; `.screen` pads vertically and
  paints its color full-bleed (`border-image`) until `scroll-color.js` runs;
  then the page background takes the color of the section at mid-viewport
  (`body.bg--*`, as on the old openaleph.org), fading in .4s, and every
  section's text and tokens follow it (cards keep their own).
- Header (`partials/header.html`): site name (`extra.brand`) | logo |
  actions (Login / Sign up from `extra.signin`, burger). Sticky, hidden while
  scrolling down (`header.autohide`); its height follows `--header-logo`, as
  does the anchor scroll margin. Site search is off. `javascripts/scroll-color.js`
  gives it the page's `screen--bg-*` class (light surfaces show
  `extra.logo_light`; `partials/logo.html` renders both logos). Front
  matter `header: zone`: smaller logo left, Login / Sign up, no drawer; CSS on
  a page marker (`.page--header-zone`, `partials/content.html`), as instant
  navigation keeps the header.
- Drawer: the primary sidebar as a right overlay, also on blog posts (`main.html`
  ignores `hide: navigation`); none on `header: zone` pages. Front matter
  `drawer:` (h2 ids, e.g. index.md) lists those sections above the pages.
  Colored like the header.
- TOC on the left at desktop, hidden when empty, sticky at the top.
- Blog pages (listings, posts) sit on paper; post categories are `[DARC]` or
  `[OpenAleph]`, with buttons from `extra.blog_categories`.
- Team: `## Who we are` on the landing page; nav link `./#who-we-are`.
- OpenAleph: `/openaleph/` (`#get-started`, `#faq`, `#about`) and
  `/openaleph/managed/`. Add a `contrib/nginx.map` entry when a published URL
  changes.

## Conventions

- The checkout is edited in parallel (host editor, shared mount): re-read a
  file right before editing and make targeted edits. Local servers on port
  8000; stop them when done.
- Root font size is 20px at every width; body text 18px.
- Headings: h1 and h2 Sligoil 400 (its only weight), h3/h4 bold Inter. Hero,
  feature card and blog h2s are bold Inter.
- One h1 per page (`hide: [title]` keeps the automatic one, visually hidden);
  sections are `##`.
- `<br>` for line breaks in headings.
- Content links inherit the color, with a 2px underline.
- Unordered lists get check-mark bullets, except in card grids and task lists.
- Icons: `:lucide-*:`, `:material-*:`, `:simple-*:`, `:octicons-*:`,
  `:fontawesome-*:` (bundled with Zensical); UI chrome uses Material icons.
- Comments only where the code would surprise.
