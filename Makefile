# Run from the project root: snippet paths resolve against the working directory.

# .venv (make install) when present, else the tools on PATH (CI)
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
