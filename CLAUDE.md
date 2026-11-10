# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

The **production website for [dataresearchcenter.org](https://dataresearchcenter.org)**
(the Data and Research Center, DARC), built with [Zensical](https://zensical.org/)
(the Material for MkDocs successor) from `mkdocs.yml`, which Zensical reads
natively (`theme.variant: classic` keeps the Material look the CSS is built on).
Content is plain markdown under `docs/`, built and deployed to S3 by GitHub
Actions on push to `main`.

This is **no longer a shared template** for downstream DARC sites — other sites
clone this repo. Only the design layer (`darc-zensical.css`) is shared upstream.
Zensical doesn't support MkDocs `hooks` or third-party plugins outside its
[supported list](https://zensical.org/docs/compatibility/mkdocs/plugins/); its
templates are MiniJinja (no Python calls in overrides).

## Commands

```bash
make install     # .venv with zensical (plus pyyaml/jinja2/markdown for scripts/)

make fetch       # OpenAleph API + images → data/openaleph/, docs/assets/openaleph/ (network)
make render      # data/ + blog posts → docs/snippets/ (offline; build and serve run it first)
make build       # → ./site (the default target)
make serve       # http://localhost:8000 (live reload, snippet edits included)
make clean       # remove site/ and docs/snippets/ (the fetched data stays)

CI=true make build                     # also runs the image `optimize` plugin (needs `pngquant`)
```

Run `make` from the project root (snippet paths resolve against the working
directory). It uses `.venv` when present, else the tools on `PATH` (CI); every
target is repeatable, and `build` works offline from the last `fetch`.

## Architecture

```
docs/
  index.md               # pages (markdown); the landing page ends with the team (#who-we-are)
  what-we-do.md  projects.md  contact.md
  zone.md                # the darc.zone landing (search.openaleph.org), as its online iteration
  blog/                  # blog plugin (index.md + posts/), categories DARC and OpenAleph
  openaleph.md           # the OpenAleph open source project on one page, merged from openaleph.org
  openaleph/             # managed.md: the managed service; assets/icons/ (also used by openaleph.md)
  reference.md           # authoring reference (every component, copy-pasteable)
  typography.md
  assets/                # images (profiles, projects, blogs); openaleph/ is fetched (gitignored)
  stylesheets/           # darc-zensical.css is loaded from upstream URL — NOT stored here
    tokens.css           # project tokens (neutrals, accents, spacing, stroke, radii, shadows)
    components.css       # .screen, .hero, .btn, .grid.cards modifiers, profile cards, chips
    site.css             # layout chrome — drawer, header, footer, typography, list markers
    landing.css          # landing page — card variants, search pill, OpenAleph data blocks
    extra.css            # last-mile site overrides (kept small)
  overrides/             # Material template overrides
    main.html            # block site_nav swap: TOC left, nav as right overlay drawer
    blog.html            # blog listings + category buttons (`extra.blog_categories`)
    partials/            # header.html (3-col), footer.html, copyright.html, post.html,
                         # content.html (`hide: [title]` keeps the automatic h1, visually hidden)
    .icons/lucide        # local lucide SVGs (Material ships material/fontawesome/octicons/simple)
  snippets/              # make render (gitignored, `exclude_docs`): the blocks the landing pages include
data/
  topics.yml             # "Data behind the headlines" topics (editorial; fields in README.md)
  dataset_groups.yml     # Curated Collections (editorial)
  openaleph/             # make fetch (gitignored): API snapshot {metadata,statistics,collections,images,icons,flags}.json
scripts/
  fetch.py               # network: API snapshot → data/openaleph/, images + flags → docs/assets/openaleph/
  render.py              # offline: data/ → docs/snippets/<template>.html; docs/blog/posts → docs/snippets/news.html
  templates/             # the blocks (Jinja2), ports of the OpenAleph UI components (_macros.html)
  resize_assets.py       # downsize inlined images in place (one-off helper)
Makefile                 # install · fetch · render · build · serve · publish · clean (CI uses it too)
mkdocs.yml               # theme, palette, plugins (meta, blog, search off, optimize, redirects), nav, markdown_extensions
requirements.txt
.github/workflows/publish.yml   # CI: make fetch build (+ optimize) and sync ./site to S3
contrib/nginx.map         # 301s: openaleph.org pages + blog → here, legacy blog URLs, /who-we-are/
```

Note: `darc-zensical.css` is the shared cross-DARC design layer, loaded at build
time from the upstream
[`zensical-theme-darc`](https://github.com/dataresearchcenter/zensical-theme-darc)
repo via `extra_css` (there is **no local copy**). Keep it in sync upstream; don't
put project-specific tweaks there — use the local layers.

## Build & deploy

The `optimize` image plugin (`mkdocs.yml`) is `enabled: !ENV [CI, false]` — it runs
only in CI, needing the `pngquant` binary for PNG (JPG is native); without it the
build fails. Push to `main` runs `.github/workflows/publish.yml`: `pip install
-r requirements.txt`, pngquant, `make fetch build`, then sync `./site` to S3.
`make publish` does the same from a machine with S3 credentials.

## Snippets pipeline

`make fetch` (`scripts/fetch.py`, the only step with network access) resolves
the collection IDs in `data/*.yml` via the OpenAleph API (non-public ones are
dropped, with a warning), snapshots `/api/2/metadata` and `/api/2/statistics`
into `data/openaleph/`, and downloads topic images (Wikimedia via the Commons
API as 960px renditions; SVGs stay vector), group icons, the FtM schema icons
and country flags into `docs/assets/openaleph/`, emptied in place first.
Download failures are warnings. Env: `OPENALEPH_API_URL`,
`OPENALEPH_USER_AGENT` (default `openaleph`, which passes the Anubis
challenge), `BUILD_USER_AGENT` (image downloads; Wikimedia wants a
descriptive one).

`make render` (`scripts/render.py`, offline) empties `docs/snippets/` and
writes `news.html` (the newest posts through the blog's excerpt partial, see
Components) plus one block per `scripts/templates/*.html` from the YAML and
the snapshot, with the indentation flattened (Python-Markdown's `md_in_html`
misreads block tags indented 4+ spaces). Without a snapshot it warns and
leaves the OpenAleph blocks out, so a fresh clone still builds. Image and
flag paths are relative to `docs/` (`assets/openaleph/…`); Zensical rewrites
them for the including page, so `zone.md` works too.

Snippets: Zensical resolves `--8<--` paths against the working directory (not
`docs_dir`; `!relative` isn't supported), hence `docs/snippets/<name>.html`
and running `make` from the project root. `exclude_docs: /snippets/` keeps
the folder out of `site/`. `zensical serve` reloads on snippet edits because
they live under `docs/` (files outside aren't watched and are cached). A
missing snippet is dropped silently (`--strict` aborts).

Gotchas: a plain topic search term links to an exact-phrase search
(`/search?q="<term>"`), an object `{label, url}` renders as a purple
`.btn--query` pill; collection IDs are strings in `topics.yml` but integers
in `dataset_groups.yml` (compared via `str()`); index numbers: entities =
`things`, datasets = `collections`, countries = number of country keys,
documents = sum of schemata descending from `Document`.

## Design system

Tokens are layered:

1. `darc-zensical.css` (upstream) — `--oa-*` palette, `--font-sans`,
   `--font-mono`, scheme tokens (`--bg`, `--text`, `--md-*-color`),
   admonition + code highlight colors per scheme.
2. `tokens.css` (project) — semantic aliases (`--color-black`, `--color-white`),
   marketing section accents (`--bg-{white,black,green,orange,yellow,purple}`),
   spacing scale (`--xs`, `--s`, `--l`, `--xl`, `--section-y`), `--stroke-width: 3px`,
   `--radius-{card,chip-sm}`, `--shadow-button`, transitions,
   `--container-lg` (1024px content width), `--container-xl` (1280px:
   header and footer, via `.md-grid`, and the content of pages with
   `wide: true` in the front matter, like the landing page, except in
   `.screen--narrow` sections).
3. `components.css` + `site.css` — apply tokens to elements.

**Single border weight everywhere**: `var(--stroke-width)` (3px). To rescale
globally, change the one line in `tokens.css`.

## Components

Every component is plain markdown + a small wrapper class. No macros, no
Python plugins — the one exception is the landing pages' live OpenAleph data
blocks, pre-rendered by `scripts/render.py` and included with
`--8<-- "docs/snippets/<name>.html"` (see Snippets pipeline).
`render.py` also renders the News section, the newest blog posts
(`docs/snippets/news.html`, from `docs/blog/posts`): templates can't list posts
outside the blog, as the blog plugin is native and neither `nav` nor
`nav.pages` holds them. It renders the blog's own excerpt partial
(`partials/post.html`: the override, else the theme's, with the theme's
`partials/language.html` labels) with Jinja2, so the entries match the blog
listing; the post links point at the sources, which Zensical resolves in raw
HTML too (without flagging broken ones). Re-run `make render` after adding,
renaming or removing a post (CI renders it on every deploy).

| Component | Class(es) |
|---|---|
| Section / screen | `.screen` + `.screen--bg-{color}` + optional `.screen--full-height`, `.screen--narrow` (default width on a wide page) |
| Hero (landing) | `.hero.hero--landing` (single column, Sligoil-mono h1) |
| darc.zone hero (zone.md) | add `hero--zone`: large title with an orange `*emphasis*`, label tagline, narrower lede and search pill; index numbers in a row via `docs/snippets/stats_zone.html` (`scripts/templates/stats_zone.html`, `ul.stats.stats--row`) |
| Hero (2-col w/ media) | `.hero` containing one inner `<div markdown>` (content) and one image — order swaps sides; a screenshot fills its column, a logo or symbol (`.no-border`, `.section-icon`) sits inset |
| Buttons | `.btn` (secondary outline) + `.btn.btn--primary` (filled inverse) |
| Card grid | `<div class="grid cards" markdown>` + markdown list |
| Card full-width | `{ .card--full }` on a list item |
| Wide card grid, two per row | `<div class="grid grid--wide" markdown>` (one per row ≤900px) |
| Card grid, three per row | `<div class="grid grid--three" markdown>` (two ≤900px, one ≤640px) |
| Section headline | a section opening with `## …` gets a large h2 (`components.css`, every page); sections are h2, the page's one h1 is its title |
| Feature card (roomy, large title) | `<div class="card card--feature" markdown>` inside a `.grid` |
| Filled card | add `screen--bg-{color}` to a block card |
| Media card (image left, full row) | `.card.card--media` with `figure.card__media`, `.card__body`, optional `.card__footer` |
| Data card (templates: Curated Collections, Explore) | a block card opening with `header.card__header` (optional icon, `h3`, optional description, rule underneath); blocks follow evenly, not pushed to the bottom. Its rows (`CollectionList`, `Statistics__list`, also the topic cards' footer) share one style in `landing.css`: bold truncating label, muted details, mono count, no hover fill (only the label underlines) |
| Search pill | `<form role="search">` with an input and a `.btn` submit |
| Plan price | `**€200**{.price}` |
| Profile cards | add `profiles` to the grid: `<div class="grid cards profiles" markdown>` |
| Tag chips | `<kbd>` |
| Form / input | plain `<form>` + `<input>` (generic CSS) |
| Inline text utils | `.muted`, `.dim` |
| Image opt-outs | `{.no-border}`, `{.no-shadow}` |
| Image utilities | `{.center}`, `{.section-icon}` (centered feature symbol, max 200px) |
| Layer stack (linked boxes in labeled rows) | `<div class="stack" markdown>`, one paragraph per layer: `**label**` then links, one per line (open-source.md; Mermaid can't link nodes: the theme initializes it `strict`) |
| Diagram | ` ```mermaid ` block (superfences custom fence in `mkdocs.yml`), in `<div class="diagram" markdown>` to scroll on phones; colors follow the section (`--md-mermaid-*` redeclared on `.mermaid` in `components.css`) |

See `docs/reference.md` for copy-pasteable snippets.

## Layout chrome

- **Padding:** all horizontal padding lives on `main.md-main` (so wrapped
  `.screen` pages and plain-markdown pages like the blog match). `.screen`
  sections only pad vertically (see Sections). Material's content-container
  inset is neutralized in `components.css`.
- **Header**: 3-column grid (Sign in button from `extra.signin`, or the site
  title without it | centered subline `md-logo` | actions group with palette /
  source / burger). Always-visible burger. Site search is off (`search:
  enabled: false`; Zensical enables it unless told not to). The header sits
  in the page flow and scrolls away (`position: relative` in `site.css`, no
  `header.autohide`); the theme's only header switches are that flag and
  `navigation.tabs(.sticky)`, its stickiness is CSS.
- **Drawer**: `.md-sidebar--primary` repurposed as a right-side overlay panel
  (`max-width: min(22rem, 85vw)`, offset hard shadow, slides in via the
  `#__drawer` checkbox). Always rendered (`main.html` ignores `hide: navigation`,
  which the blog plugin sets on posts), except on a page with `hide: [menu]`
  (zone.md): no drawer there, and `site.css` hides the burger whenever the
  page has no drawer (in CSS, since instant navigation keeps the header). `site.css` has a mobile media block that
  re-flattens Material's mobile nav (static layout, no item borders/box-shadow,
  drops the integrated TOC).
- **TOC**: `.md-sidebar--secondary` moved to the LEFT at desktop widths;
  `main.html` hides it when empty (e.g. blog category pages). It stays
  sticky, at the top of the viewport (`top: 0 !important` beats the theme
  JS's inline offset, which is the header's height).
- **Blog**: every blog page (`body:has(.md-content__inner > .md-post,
  .md-content--post)`: index, category and archive listings, posts) sits on
  paper; the landing page's News excerpts sit deeper, so it doesn't. `site.css` paints `.md-main`; the content
  and TOC are light surfaces (see Sections), code blocks and admonitions
  included (not the overlay drawer, which also lives in `.md-main`). Each post has `categories: [DARC]` or
  `[OpenAleph]`; the plugin builds `/blog/category/{darc,openaleph}/`, linked
  from the category buttons on every listing (`overrides/blog.html`, from
  `extra.blog_categories`). The OpenAleph posts were merged from
  openaleph.org (images in `docs/assets/blogs/`).
- **Footer**: vanilla `.md-footer-meta` (links in `partials/copyright.html`),
  on the page's black (`--bg-black`, not upstream's pure #000; `site.css`).
- **Nav sections**: `navigation.indexes` makes a nav section's index page its
  link; the drawer indents the section's pages along a stroke and shows them
  in place on mobile too (no section at the moment: OpenAleph is one page).
- **Team**: the former `who-we-are.md` is the landing page's last section
  (`## Who we are`, so the anchor is `#who-we-are`). Its nav entry is a link,
  `./#who-we-are` (Zensical makes `./` relative on every page; a page path
  with an anchor isn't resolved). `/who-we-are/` redirects there, via
  `contrib/nginx.map` and the redirects plugin.
- **OpenAleph pages** (merged from openaleph.org): one page for the open
  source project and its features (`docs/openaleph.md`, at `/openaleph/`:
  hero, features, Get started `#get-started`, FAQ `#faq`, About `#about`),
  and the managed service on its own (`docs/openaleph/managed.md`). Links to openaleph.org pages are
  internal now, except `openaleph.org/docs/` (a separate site).
  `contrib/nginx.map` redirects the old openaleph.org URLs (pages, to those
  sections; blog, legacy post URLs, images) and this site's legacy blog URLs; it
  was generated from the build and checked entry by entry in nginx. Add an
  entry when a published URL changes.

## Sections

Sections are hard color blocks (no JS): each `.screen` paints its
`--section-accent` full-bleed via a `border-image` outset (no layout or scroll
overflow), and stacked sections butt against each other, spaced by
`--section-y` padding inside each. A black section at the top or bottom of a
page keeps no padding there, so single-section pages look as before.

The palette is slate-only. The DARC pages only use black sections, which match
the page; the colored sections are on the landing page. The light surfaces
rule in `components.css` makes light sections (and cards carrying a
`screen--bg-*` class), the blog's content and TOC, and the TOC beside a page
opening with a light section dark-on-light: it swaps `--color-white`/
`--color-black`, `--text`, the theme text tokens and the button shadows, and
sets upstream's light-scheme panel, code (syntax colors) and admonition
tokens, so inline code, code blocks and admonitions turn light too. Tokens
built on another token are redeclared there, since a var() inside a custom
property resolves where it's declared.

## Conventions

- This checkout is edited in parallel (an editor on the host, shared mount):
  re-read a file right before editing it and make targeted edits; stale
  buffers have overwritten changes before. Local servers: port 8000 (a local
  proxy intercepts 8765); stop them when done.
- `markdown` attribute on every wrapper `<div>` / `<section>` is required to
  keep Python-Markdown parsing inside HTML.
- `<br>` for line breaks inside headings (markdown's two-trailing-spaces and
  `\` rules don't apply in headings).
- Root font size is pinned at 125% (20px) at every width (`site.css`; Material
  grows it on wide screens); body text (`.md-typeset`, `.9rem`) is 18px.
- No light/dark scheme logic in the local CSS: the palette is slate-only,
  so rules are written for the dark page. Body text is `--color-white`
  (#fff8f1) at weight 400, pinned in `site.css`; light surfaces swap in
  `--oa-black` at 500 (`components.css`).
- Headings (`site.css`): h1 and h2 are Sligoil at 400 (its only weight;
  never bold); h3 and h4 bold Inter (Material defaults them to a thin
  ~300/400). Exceptions keep bold Inter h2s: component headings (in a
  `.hero` or a `.card--feature`, the landing page's 2x2) and the blog, where only the h1 is Sligoil (post
  excerpts `.md-post`, also in the landing page's News, and post pages
  `.md-content--post`).
- One h1 per page: its title (a hero's or `# Title`, else the theme's
  automatic one, visually hidden with `hide: [title]`); sections are `##`.
- Inline `<a>` in content (`.md-content a`) inherits color and gets a 2px
  underline; `.btn`, header permalinks and post-title `.toclink` opt out.
- Body unordered-list bullets render a custom check-mark SVG (`site.css`);
  card grids and task lists are excluded.
- Icons: UI chrome (menu, search, social) uses the **Material** set
  (`theme.icon`, `extra.social`). Shortcodes (`:lucide-x:`, `:material-x:`,
  `:simple-x:`, `:octicons-x:`, `:fontawesome-x:`) resolve via `pymdownx.emoji`
  with `material.extensions.emoji.{twemoji,to_svg}`. **Lucide** isn't shipped by
  Material — it's bundled locally in `docs/overrides/.icons/lucide/` and
  registered via the emoji `custom_icons` option, so `:lucide-*:` still works.

## For other DARC sites

This repo is no longer an upstream template — clone it as a starting point. To
adapt a clone, edit `mkdocs.yml` (`site_name`, `site_url`, `repo_url`, `nav`,
logos, `extra.signin`, `extra.social`), `docs/*.md`, and `docs/stylesheets/extra.css`. Don't
modify the upstream `darc-zensical.css` design layer (it's loaded by URL).
