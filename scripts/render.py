#!/usr/bin/env python3
"""data/, the API snapshot and the blog posts → docs/snippets/ (offline)."""

import html
import json
import posixpath
import re
import sys
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from math import ceil
from pathlib import Path
from urllib.parse import urlencode

import markdown
import yaml
import zensical_ui
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown.extensions.toc import slugify
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "openaleph"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
DOCS_DIR = ROOT / "docs"
OUT_DIR = DOCS_DIR / "snippets"
BLOG_DIR = DOCS_DIR / "blog" / "posts"
# Where fetch.py puts flags (docs/assets/openaleph/flags/), as a site path.
FLAG_URL = "assets/openaleph/flags"
# Zensical's template lookup: the site's overrides, then the theme.
THEME_TEMPLATE_DIRS = [DOCS_DIR / "overrides", Path(zensical_ui.__file__).parent / "templates"]
# Posts in the news block
NEWS_POSTS = 3
POST_MARKDOWN_EXTENSIONS = ["attr_list", "md_in_html", "admonition", "footnotes", "tables", "fenced_code"]


class MissingData(Exception):
    """A file of the API snapshot is missing (no `make fetch` yet)."""


def load_yaml(name, key):
    with open(DATA_DIR / name) as f:
        return yaml.safe_load(f)[key] or []


def load_json(name):
    path = SNAPSHOT_DIR / name
    if not path.exists():
        raise MissingData(path.relative_to(ROOT))
    with open(path) as f:
        return json.load(f)


def compact(n):
    """199422052 -> '199m', 1488862 -> '1.5m', 642 -> '642'."""
    for size, suffix in ((1e9, "b"), (1e6, "m"), (1e3, "k")):
        if n >= size:
            value = n / size
            text = f"{value:.0f}" if value >= 10 else f"{value:.1f}".removesuffix(".0")
            return text + suffix
    return f"{n:,}"


def render_markdown(text):
    return Markup(markdown.markdown(text or ""))


def flatten(markup):
    # md_in_html reads block tags indented 4+ spaces as text, and a blank
    # line ends the raw block.
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


def empty_dir(path):
    """Empty in place: recreating the folder races on shared mounts."""
    path.mkdir(parents=True, exist_ok=True)
    for old in path.iterdir():
        old.unlink(missing_ok=True)


def write_block(name, markup, source):
    (OUT_DIR / name).write_text(flatten(markup) + "\n")
    print(f"{source} -> {(OUT_DIR / name).relative_to(ROOT)}")


class ReadtimeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.images = 0

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images += 1

    def handle_data(self, data):
        self.text.append(data)


def readtime(markup):
    """Minutes to read, counted like the blog plugin: 265 words a minute, plus
    12 seconds for the first image and a second less for each next (3 at least)."""
    parser = ReadtimeParser()
    parser.feed(markup)
    parser.close()
    seconds = ceil(len(re.split(r"\W+", "".join(parser.text))) / 265 * 60)
    delta = 12
    for _ in range(parser.images):
        seconds += delta
        delta = max(delta - 1, 3)
    return ceil(seconds / 60)


def relink(text, base):
    """Make the relative link and image targets in markdown relative to docs/,
    where index.md lives (`base` is the post's directory)."""
    def target(match):
        url = match.group(2)
        if re.match(r"[a-z][a-z0-9+.-]*:|[/#]", url):
            return match.group(0)
        return match.group(1) + posixpath.normpath(posixpath.join(base, url))
    return re.sub(r"(\]\()([^)\s]+)", target, text)


def latest_posts(count):
    """Newest posts, shaped like the blog plugin's for partials/post.html; links
    point at the sources, which Zensical resolves in raw HTML too."""
    posts = []
    for path in sorted(BLOG_DIR.rglob("*.md")):
        front, body = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(), re.S).groups()
        meta = yaml.safe_load(front) or {}
        if meta.get("draft"):
            continue
        created = meta["date"]
        if isinstance(created, dict):
            created = created["created"]
        if isinstance(created, date) and not isinstance(created, datetime):
            created = datetime(created.year, created.month, created.day, tzinfo=timezone.utc)
        title = meta.get("title") or re.search(r"^# (.+)$", body, re.M).group(1).strip()
        url = path.relative_to(DOCS_DIR).as_posix()
        # The excerpt is the text above `<!-- more -->`; its title becomes a
        # linked h2, as on the blog.
        excerpt = body.partition("<!-- more -->")[0]
        excerpt = re.sub(r"^# .+$", "", excerpt, count=1, flags=re.M)
        excerpt = relink(excerpt, posixpath.dirname(url))
        content = (
            f'<h2 id="{slugify(title, "-")}"><a class="toclink" href="{url}">{html.escape(title)}</a></h2>\n'
            + markdown.markdown(excerpt, extensions=POST_MARKDOWN_EXTENSIONS)
        )
        posts.append({
            "url": url,
            "content": content,
            "more": True,
            "authors": [],
            "categories": [
                {"title": name, "url": f"blog/category/{slugify(name, '-')}/"}
                for name in meta.get("categories") or []
            ],
            "config": {
                "date": {"created": created},
                "readtime": readtime(markdown.markdown(body, extensions=POST_MARKDOWN_EXTENSIONS)),
                "draft": False,
                "pin": False,
            },
        })
    # Stable: posts of the same day keep the file order, as on the blog.
    posts.sort(key=lambda post: post["config"]["date"]["created"], reverse=True)
    return posts[:count]


def render_news():
    """news.html, through the blog's excerpt partial."""
    env = Environment(loader=FileSystemLoader(THEME_TEMPLATE_DIRS))
    env.filters["url"] = lambda url: url
    env.filters["date"] = lambda value: f"{value:%B} {value.day}, {value.year}"
    lang = env.get_template("partials/language.html").make_module({"config": {"theme": {"language": "en"}}})
    partial = env.get_template("partials/post.html")
    markup = "".join(partial.render(post=post, lang=lang) for post in latest_posts(NEWS_POSTS))
    write_block("news.html", re.sub(r"<!--.*?-->", "", markup, flags=re.S), "partials/post.html")


class Page:
    def __init__(self):
        self.metadata = load_json("metadata.json")
        self.statistics = load_json("statistics.json")
        self.collections = load_json("collections.json")
        self.images = load_json("images.json")
        self.icons = load_json("icons.json")
        self.flags = set(load_json("flags.json"))
        self.ui = self.metadata["app"]["ui_uri"].rstrip("/")

    def stats(self):
        """Index numbers, as on the OpenAleph UI home."""
        schemata, statistics = self.metadata["schemata"], self.statistics
        documents = sum(
            count
            for name, count in statistics["schemata"].items()
            if "Document" in schemata.get(name, {}).get("schemata", [])
        )
        return [
            ("entities", statistics["things"]),
            ("datasets", statistics["collections"]),
            ("countries", len(statistics["countries"])),
            ("documents", documents),
        ]

    def resolve(self, ids):
        # Like CollectionList: IDs the API didn't return (not public) are skipped.
        categories = self.metadata["categories"]
        resolved = []
        for collection_id in ids or []:
            collection = self.collections.get(str(collection_id))
            if collection:
                resolved.append({
                    **collection,
                    "category_label": categories.get(collection["category"]),
                    "url": f"{self.ui}/datasets/{collection['id']}",
                })
        return resolved

    def search_term(self, term):
        if isinstance(term, dict):
            url = term["url"]
            return {
                "label": term["label"],
                "url": self.ui + url if url.startswith("/") else url,
                "query": True,
            }
        # Plain terms search for the exact phrase.
        query = urlencode({"q": f'"{term}"'})
        return {"label": term, "url": f"{self.ui}/search?{query}", "query": False}

    def image(self, key):
        # Local copy downloaded by fetch.py; without one the item renders imageless.
        if key and key not in self.images:
            print(f"warning: no local copy of {key}, run `make fetch`", file=sys.stderr)
        return self.images.get(key)

    def flag(self, code):
        return f"{FLAG_URL}/{code}.svg" if code in self.flags else None

    def topic(self, topic):
        countries = self.metadata["countries"]
        image = topic.get("image")
        local = self.image(image["url"]) if image else None
        return {
            **topic,
            "image": {**image, **local} if local else None,
            "countries": [
                {"name": countries.get(c, c.upper()), "flag": self.flag(c)}
                for c in topic.get("countries") or []
            ],
            "search_terms": [self.search_term(t) for t in topic.get("search_terms") or []],
            "collections": self.resolve(topic.get("collections")),
        }

    def group(self, group):
        return {
            **group,
            "icon": self.image(group.get("icon")),
            "collections": self.resolve(group.get("collections")),
        }

    def schema_icon(self, schema):
        # Same lookup as the UI's IconRegistry.getSchemaIcon
        return self.icons.get(schema.lower()) or self.icons.get("info")

    def explore(self):
        """Top entity types, dataset categories and countries, as on the OpenAleph UI home."""
        meta, stats = self.metadata, self.statistics
        lists = [
            ("schema", stats["schemata"], "search", "filter:schema",
             lambda k: meta["schemata"].get(k, {}).get("plural", k)),
            ("category", stats["categories"], "datasets", "collectionsfilter:category",
             lambda k: meta["categories"].get(k, k)),
            ("country", stats["countries"], "datasets", "collectionsfilter:countries",
             lambda k: meta["countries"].get(k, k.upper())),
        ]
        return [
            {
                "kind": kind,
                "entries": [
                    {
                        "label": label(key),
                        "count": count,
                        "url": f"{self.ui}/{path}?{urlencode({param: key})}",
                        "icon": self.schema_icon(key) if kind == "schema" else None,
                        "flag": self.flag(key) if kind == "country" else None,
                    }
                    for key, count in sorted(counts.items(), key=lambda kv: -kv[1])
                ],
            }
            for kind, counts, path, param, label in lists
        ]

    def context(self):
        return {
            "stats": self.stats(),
            "topics": [self.topic(t) for t in load_yaml("topics.yml", "topics")],
            "groups": [self.group(g) for g in load_yaml("dataset_groups.yml", "groups")],
            "explore": self.explore(),
        }


def render():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["compact"] = compact
    env.filters["markdown"] = render_markdown
    env.filters["thousands"] = lambda n: f"{n:,}"

    empty_dir(OUT_DIR)
    # Independent of the fetched data: first.
    render_news()

    try:
        context = Page().context()
    except MissingData as missing:
        print(f"warning: {missing} is missing, run `make fetch`; the OpenAleph blocks are left out", file=sys.stderr)
        return
    for template in sorted(TEMPLATE_DIR.glob("[!_]*.html")):
        markup = env.get_template(template.name).render(context)
        write_block(template.name, markup, f"templates/{template.name}")


if __name__ == "__main__":
    render()
