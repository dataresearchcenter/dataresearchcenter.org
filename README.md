# dataresearchcenter.org

Production website for the **Data and Research Center (DARC)** —
<https://dataresearchcenter.org>.

Built with [Zensical](https://zensical.org/) from `mkdocs.yml`.
Content is plain markdown under `docs/`, built and deployed to S3 on every push to
`main`.

> **Other DARC sites:** clone this repo as a starting point. It is no longer a
> shared upstream template/boilerplate — only the design layer is shared
> (see [Design system](#design-system)).

## Setup

```bash
make install        # .venv with Zensical and the scripts' dependencies
```

## Develop & build

Everything goes through the Makefile (run it from the project root; it uses
`.venv` when present, else the tools on `PATH`). Every target can be repeated.

```bash
make fetch          # live OpenAleph data for the landing pages (network; once, and to refresh)
make serve          # http://localhost:8000 with live reload
make build          # → ./site (the default target)
make render         # just the snippets, after editing data/*.yml, scripts/templates/ or the blog
make clean          # remove site/ and docs/snippets/
```

`make fetch` writes an API snapshot to `data/openaleph/` and images to
`docs/assets/openaleph/`; `make render` (part of `build` and `serve`) turns
them and the newest blog posts into `docs/snippets/`, which the landing pages
include. All three folders are gitignored. Without a snapshot the site still
builds, minus the OpenAleph blocks (`make render` says so).

Image optimization (the `optimize` plugin) runs in CI only — it's gated on
`CI=true`. To run it locally you also need the `pngquant` binary (`apt install
pngquant` / `brew install pngquant`):

```bash
CI=true make build
```

Push to `main` runs `make fetch build` in GitHub Actions and syncs `./site` to
S3; `make publish` does the same from a machine with S3 credentials.

## Layout

```
docs/
  *.md                   pages (index with the team section, what-we-do, projects, contact)
  blog/                  blog plugin: index + posts/ (categories DARC, OpenAleph)
  openaleph.md           OpenAleph project page (merged from openaleph.org)
  openaleph/             managed service page + icons
  zone.md                darc.zone landing (search.openaleph.org)
  reference.md           component authoring reference
  stylesheets/           tokens · components · site · landing · extra
  overrides/             Material template overrides (header, footer, main, nav)
  snippets/              rendered by make render (gitignored): OpenAleph blocks, latest posts
  assets/openaleph/      fetched by make fetch (gitignored): topic images, icons, flags
data/
  topics.yml             "Data behind the headlines" topics (editorial)
  dataset_groups.yml     Curated Collections (editorial)
  openaleph/             API snapshot from make fetch (gitignored)
scripts/
  fetch.py  render.py    the snippets pipeline (make fetch / make render)
  templates/             the blocks' Jinja2 templates
  resize_assets.py       downsize inlined images in place (one-off helper)
contrib/nginx.map        permanent redirects (openaleph.org, legacy blog URLs, /who-we-are/)
Makefile                 install · fetch · render · build · serve · publish · clean
mkdocs.yml               theme, nav, markdown_extensions, plugins (read by Zensical)
requirements.txt
.github/workflows/publish.yml   make fetch build (+ optimize) and sync ./site to S3
```

## Editorial data

The landing page (`docs/index.md`) and the darc.zone page (`docs/zone.md`)
show live data from [search.openaleph.org](https://search.openaleph.org):
index numbers, "Data behind the headlines" topics, Curated Collections and the
Explore lists, plus the newest blog posts in the News section.

| What | Where |
|---|---|
| Page copy, section order, buttons, plans | `docs/index.md`, `docs/zone.md` (plain markdown) |
| Topics: title, markdown description, image + attribution, countries, search terms, collection IDs | `data/topics.yml` |
| Dataset groups: label, description, markdown `content`, icon, collection IDs | `data/dataset_groups.yml` |
| Block markup | `scripts/templates/` |
| Styles | `docs/stylesheets/landing.css` |

Collection names, categories and counts, the index numbers, the Explore lists
and country names come from the API, so the YAML only needs IDs and codes.
Collections that aren't public are left out; `make fetch` warns about each.
A topic's plain search term links to an exact-phrase search; an object
`{label, url}` renders as a custom-link pill.

Images are downloaded by `make fetch`, so reference them by their original
URL: Wikimedia images (on `upload.wikimedia.org`, or mirrors like
`assets.ftm.store` whose `attribution.source_url` is a Wikimedia file page)
are fetched as 960px renditions via the Commons API, SVGs stay vector,
anything else is downloaded as-is. If a download fails, `make fetch` warns and
the card renders without the image.

After editing the YAML, run `make fetch` (new collection IDs or images) or
`make render` (text only), then build.

## Authoring

[`docs/reference.md`](docs/reference.md) has copy-pasteable markdown for every
component — screens, heroes, card grids, profile cards, buttons, chips,
admonitions, icons.

## Design system

The shared, cross-DARC design layer is `darc-zensical.css`, loaded at build time
from [`zensical-theme-darc`](https://github.com/dataresearchcenter/zensical-theme-darc).
Keep project-specific styling out of it — use the local layers instead:

- `docs/stylesheets/tokens.css` — design tokens (colors, spacing, stroke, radii)
- `docs/stylesheets/components.css` — `.screen`, `.hero`, `.grid.cards`, `.btn`, profile cards
- `docs/stylesheets/site.css` — layout chrome (drawer, header, footer, typography, list markers)
- `docs/stylesheets/landing.css` — landing page (card variants, search pill, OpenAleph blocks)
- `docs/stylesheets/extra.css` — last-mile overrides
