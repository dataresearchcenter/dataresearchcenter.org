# dataresearchcenter.org – the Zensical site and the snippets its landing pages
# include (scripts/, data/). Run from the project root. Every target can be
# repeated; only `fetch` needs the network.
#
#   make install    .venv with Zensical and the scripts' dependencies
#   make fetch      OpenAleph API + images → data/openaleph/, docs/assets/openaleph/
#   make render     data/ + blog posts → docs/snippets/ (offline; build and serve run it)
#   make build      → site/ (the default; CI=true also optimizes images)
#   make serve      http://localhost:8000 with live reload
#   make publish    fetch, build, then sync site/ to S3
#   make clean      remove site/ and docs/snippets/ (the fetched data stays)

# The project venv (make install) when present, else the tools on PATH (CI).
PYTHON ?= $(or $(wildcard .venv/bin/python),python3)
ZENSICAL ?= $(or $(wildcard .venv/bin/zensical),zensical)

.DEFAULT_GOAL := build
.PHONY: install fetch render build serve publish clean

install:
	test -x .venv/bin/python || python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

fetch:
	$(PYTHON) scripts/fetch.py

render:
	$(PYTHON) scripts/render.py

build: render
	$(ZENSICAL) build

serve: render
	$(ZENSICAL) serve

publish: fetch build
	aws s3 --endpoint-url https://s3.investigativedata.org sync ./site s3://dataresearchcenter.org

clean:
	rm -rf site docs/snippets
