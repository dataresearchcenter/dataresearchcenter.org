# Run from the project root: snippet paths resolve against the working directory.

# .venv (make install) when present, else the tools on PATH (CI)
PYTHON ?= $(or $(wildcard .venv/bin/python),python3)
ZENSICAL ?= $(or $(wildcard .venv/bin/zensical),zensical)

.DEFAULT_GOAL := build
.PHONY: install fetch render build serve zone publish clean

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

# darc.zone: the zone page as its root. Its asset paths are relative (../assets/…)
# and resolve to /assets/… there.
zone: build
	rm -rf site-zone && mkdir site-zone
	cp site/zone/index.html site-zone/
	cp -r site/assets site/stylesheets site/javascripts site-zone/

publish: fetch build zone
	putfs sync ./site putfs://static.darc.zone/darc.li
	putfs sync ./site-zone putfs://static.darc.zone/darc.zone

clean:
	rm -rf site site-zone docs/snippets
