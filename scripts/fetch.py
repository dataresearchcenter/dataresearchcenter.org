#!/usr/bin/env python3
"""OpenAleph API snapshot → data/openaleph/, images and flags → docs/assets/openaleph/."""

import hashlib
import json
import mimetypes
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlparse
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = DATA_DIR / "openaleph"
# Images and flags go straight into the docs (gitignored), published here.
ASSET_URL = "assets/openaleph"
ASSET_DIR = ROOT / "docs" / ASSET_URL
IMAGE_DIR = "images"
FLAG_DIR = "flags"

API_URL = os.environ.get("OPENALEPH_API_URL", "https://search.openaleph.org/api/2")
# search.openaleph.org sits behind an Anubis challenge; this UA is let through.
USER_AGENT = os.environ.get("OPENALEPH_USER_AGENT", "openaleph")
# Image downloads; Wikimedia asks for a descriptive UA with contact details.
BUILD_USER_AGENT = os.environ.get(
    "BUILD_USER_AGENT",
    "dataresearchcenter.org build (https://github.com/investigativedata/investigativedata.io)",
)

SOURCES = {
    "topics.yml": "topics",
    "dataset_groups.yml": "groups",
}
COLLECTION_FIELDS = ("id", "foreign_id", "label", "category", "count", "countries")
BATCH_SIZE = 100
# One of Wikimedia's standard thumbnail steps; ~2x the widest rendering.
IMAGE_WIDTH = 960
# The sources the OpenAleph UI renders schema icons and country flags from.
FTM_ICONS_URL = "https://cdn.jsdelivr.net/npm/@opensanctions/followthemoney@{version}/dist/generated/icons.json"
FLAG_URL = "https://cdn.jsdelivr.net/npm/flag-icons@7.5.0/flags/4x3/{code}.svg"


def request(url, user_agent=USER_AGENT):
    return urlopen(Request(url, headers={"User-Agent": user_agent}), timeout=60)


def get(path, params=None):
    url = f"{API_URL}/{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    with request(url) as response:
        return json.load(response)


def load_sources():
    items = {}
    for src_name, key in SOURCES.items():
        with open(DATA_DIR / src_name) as f:
            items[key] = yaml.safe_load(f)[key] or []
    return items


def collection_ids(sources):
    # IDs are strings in topics.yml and integers in dataset_groups.yml.
    ids = {str(i) for items in sources.values() for item in items for i in item.get("collections") or []}
    return sorted(ids, key=int)


def fetch_collections(ids):
    collections = {}
    for start in range(0, len(ids), BATCH_SIZE):
        batch = ids[start : start + BATCH_SIZE]
        params = [("filter:collection_id", i) for i in batch] + [("limit", len(batch))]
        for collection in get("collections", params)["results"]:
            collections[collection["id"]] = {k: collection.get(k) for k in COLLECTION_FIELDS}
    return collections


def fetch_metadata():
    metadata = get("metadata")
    model = metadata["model"]
    return {
        "app": metadata["app"],
        "categories": metadata["categories"],
        "countries": model["types"]["country"]["values"],
        # Plural labels for the Explore lists; ancestors to tell which
        # statistics count as documents.
        "schemata": {
            name: {"plural": schema.get("plural", name), "schemata": schema["schemata"]}
            for name, schema in model["schemata"].items()
        },
    }


def wikimedia_file(image):
    """Return (api_url, "File:…") for an image hosted on or sourced from Wikimedia."""
    url = urlparse(image["url"])
    if url.hostname == "upload.wikimedia.org":
        # /wikipedia/<wiki>/[thumb/]<x>/<xy>/<file>[/<thumbnail>]
        parts = url.path.split("/")
        name = parts[6] if parts[3] == "thumb" else parts[5]
        host = "commons.wikimedia.org" if parts[2] == "commons" else f"{parts[2]}.wikipedia.org"
        return f"https://{host}/w/api.php", "File:" + unquote(name)
    # Mirrors like assets.ftm.store: go back to the Wikimedia file page.
    source = urlparse((image.get("attribution") or {}).get("source_url") or "")
    if source.hostname and source.hostname.endswith(("wikimedia.org", "wikipedia.org")) and "/wiki/File:" in source.path:
        return f"https://{source.hostname}/w/api.php", unquote(source.path.split("/wiki/", 1)[1])
    return None


def wikimedia_rendition(api_url, title):
    """URL and size of a web-sized thumbnail; SVGs stay vector."""
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": IMAGE_WIDTH,
        "titles": title,
    }
    with request(f"{api_url}?{urlencode(params)}", BUILD_USER_AGENT) as response:
        info = json.load(response)["query"]["pages"][0]["imageinfo"][0]
    if info["mime"] == "image/svg+xml":
        return info["url"], info["width"], info["height"]
    return info["thumburl"], info["thumbwidth"], info["thumbheight"]


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def download(url, name):
    """Save url to docs/assets/openaleph/images/<slug>-<hash>.<ext>, return the published path."""
    with request(url, BUILD_USER_AGENT) as response:
        ext = mimetypes.guess_extension(response.headers.get_content_type()) or ""
        body = response.read()
    digest = hashlib.sha1(url.encode()).hexdigest()[:8]
    path = f"{IMAGE_DIR}/{slugify(Path(name).stem)}-{digest}{ext}"
    (ASSET_DIR / path).write_bytes(body)
    return f"{ASSET_URL}/{path}"


def fetch_image(image):
    wikimedia = wikimedia_file(image)
    if wikimedia:
        url, width, height = wikimedia_rendition(*wikimedia)
        return {"src": download(url, wikimedia[1].removeprefix("File:")), "width": width, "height": height}
    name = Path(urlparse(image["url"]).path).name
    return {"src": download(image["url"], name), "width": None, "height": None}


def empty_dir(path):
    """Empty in place: recreating the folder races on shared mounts."""
    path.mkdir(parents=True, exist_ok=True)
    for old in path.iterdir():
        old.unlink(missing_ok=True)


def fetch_images(sources, ui_url):
    """Map each image and icon reference in the YAML to its local copy."""
    empty_dir(ASSET_DIR / IMAGE_DIR)
    images = {}
    wanted = [topic["image"] for topic in sources["topics"] if topic.get("image")]
    for group in sources["groups"]:
        if group.get("icon"):
            # Relative icons live in the OpenAleph UI's static folder.
            icon = group["icon"]
            wanted.append({"key": icon, "url": icon if icon.startswith("http") else f"{ui_url}/static/{icon}"})
    for image in wanted:
        key = image.get("key", image["url"])
        try:
            images[key] = fetch_image(image)
        except (URLError, TimeoutError, ValueError, KeyError, IndexError) as e:
            # The page renders the card without this image.
            print(f"warning: could not download {image['url']}: {e}", file=sys.stderr)
    return images


def fetch_schema_icons(ftm_version):
    """FtM icon paths per lowercase schema name, at the version the API runs."""
    with request(FTM_ICONS_URL.format(version=ftm_version), BUILD_USER_AGENT) as response:
        return json.load(response)


def fetch_flag(code):
    try:
        with request(FLAG_URL.format(code=code), BUILD_USER_AGENT) as response:
            (ASSET_DIR / FLAG_DIR / f"{code}.svg").write_bytes(response.read())
        return code
    except HTTPError as e:
        # Pseudo-codes like zz (global) have no flag, as in the UI.
        if e.code != 404:
            print(f"warning: could not download flag {code}: {e}", file=sys.stderr)
    except (URLError, TimeoutError) as e:
        print(f"warning: could not download flag {code}: {e}", file=sys.stderr)
    return None


def fetch_flags(countries):
    """Download a flag for each country code; return the codes that have one."""
    empty_dir(ASSET_DIR / FLAG_DIR)
    with ThreadPoolExecutor(max_workers=8) as pool:
        return sorted(code for code in pool.map(fetch_flag, countries) if code)


def write(name, data):
    with open(OUT_DIR / name, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"-> {(OUT_DIR / name).relative_to(ROOT)}")


def fetch():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()

    metadata = fetch_metadata()
    write("metadata.json", metadata)
    statistics = get("statistics")
    write("statistics.json", statistics)
    write("icons.json", fetch_schema_icons(metadata["app"]["ftm_version"]))
    topic_countries = {c for topic in sources["topics"] for c in topic.get("countries") or []}
    write("flags.json", fetch_flags(sorted(set(statistics["countries"]) | topic_countries)))

    ids = collection_ids(sources)
    collections = fetch_collections(ids)
    write("collections.json", collections)
    # Non-public collections are skipped on the page, like CollectionList does.
    missing = [i for i in ids if i not in collections]
    if missing:
        print(f"warning: collections not publicly available: {', '.join(missing)}", file=sys.stderr)

    write("images.json", fetch_images(sources, metadata["app"]["ui_uri"].rstrip("/")))


if __name__ == "__main__":
    fetch()
