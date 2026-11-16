---
date: 2025-09-05
categories:
  - OpenAleph
---

# A Look Inside OpenAleph 5’s ElasticSearch Improvements

> An expert deep dive into the code changes that power the improved search and discovery experience in OpenAleph 5.

<!-- more -->

Looking back at the development of OpenAleph 5, refactoring the codebase and upgrading libraries gave us a more accurate, culturally aware representation of stored data and improved our ability to find names in source documents. We still have many ideas to push this further. Some will appear in upcoming OpenAleph 5 updates, while more complex features are planned for OpenAleph 6 at the end of the year. Here’s a look at what we’ve done so far.

## Improving Data Representation

Searching for names in non-Latin alphabets was a weak point in earlier versions. Tokenization issues and a brute-force approach to Latinizing names often caused searches to miss Cyrillic, Arabic, or other scripts.

We now use [Rigour](https://github.com/opensanctions/rigour), developed by the [OpenSanctions](https://www.opensanctions.org/) team, which [maps](https://rigour.followthemoney.tech/data/) different forms of a [name](https://rigour.followthemoney.tech/names/) across alphabets to a single Wikidata QID. This means a search in Cyrillic can return results for the same name in other alphabets.

After documents are uploaded, OCR is applied if raw text is unavailable. Named Entity Recognition (NER) then extracts names, or Mentions, which can be people, places, companies, or organizations. Raw NER often includes entities that don’t map to real-world names. In OpenAleph 5, we filter these using [Juditha](https://docs.investigraph.dev/lib/juditha/), which cross-checks extracted entities against multiple databases of documented names.

We are also developing a dedicated process for filtering location names, with a standalone library coming soon. If you have ideas for filtering or identifying names, we’d love to discuss them on our [Discourse forum](https://darc.social/).

## Harnessing the Power of ElasticSearch 

We upgraded our deployments to ElasticSearch 9.

After trialing and testing [a new task queue implementation](https://github.com/openaleph/openaleph-procrastinate), we were confident enough to change our ElasticSearch index structure, since re-indexing all data has become a much more streamlined process. The improved status page lets us track long-running operations, and querying Postgres directly for failed tasks is far easier than digging through Redis.

We consolidated our ElasticSearch setup into just four indexes:

- **Interval** entities (defining connections between entities)
- **Document** entities
- **Page** and **Pages** entities (optimized for full-text search and highlighting terms in context)
- All other FollowTheMoney entities inheriting from the **Thing** schema

For highlighting, we apply different strategies to the Page and Pages index, allowing proper highlighting of user search terms, including extracted Mentions.

Search results in OpenAleph 5 also prioritize entities with richer information, encouraging merging across datasets, through cross-referencing, or building entities that combine data from multiple sources.

## Discovery and Correlations

The most exciting outcome of this work is the Discovery Dashboard and the closely correlated terms feature. We’ve published a separate [blog post](./2025-09-03-when-names-travel-together-discover-correlations-in-your-data.md) on both, along with a deeper look at the ElasticSearch [significant terms](https://www.elastic.co/docs/reference/aggregations/search-aggregations-bucket-significantterms-aggregation#significantterms-aggregation-parameters) function that powers them.

What matters here is that correlated terms become more useful as we improve filtering of Mentions, making sure extracted names actually correspond to real-world entities.

## OCR and Beyond

Extracting names still depends heavily on the quality of OCR when documents lack raw text. We currently use tesserocr, but continue to test alternatives with an eye toward more accurate, deterministic results. If you know of promising OCR algorithms or libraries, [we'd love to hear about them](https://darc.social/).
