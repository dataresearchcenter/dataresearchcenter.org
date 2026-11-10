---
hide:
  - toc
---

<section class="screen screen--bg-yellow" markdown>

# Our open source stack

The libraries behind OpenAleph and our data work, in six layers: from storage at the bottom to the OpenAleph application on top. Each layer builds on the ones below it.

<div class="stack" markdown>

**6 · Application**
[OpenAleph](https://openaleph.org/docs/)
[openaleph-search](https://openaleph.org/docs/lib/openaleph-search/)

**5 · Analysis**
[ftm-analyze](https://openaleph.org/docs/lib/ftm-analyze/)
[juditha](https://docs.investigraph.dev/lib/juditha/)

**4 · Data creation**
[ingest-file](https://openaleph.org/docs/lib/ingest-file/)
[memorious](https://docs.investigraph.dev/lib/memorious/)
[investigraph](https://docs.investigraph.dev/)

**3 · Processing queue**
[openaleph-procrastinate](https://openaleph.org/docs/lib/openaleph-procrastinate/)

**2 · FollowTheMoney core**
[ftmq](https://docs.investigraph.dev/lib/ftmq/)
[ftm-lakehouse](https://openaleph.org/docs/lib/ftm-lakehouse/)

**1 · Storage**
[anystore](https://docs.investigraph.dev/lib/anystore/)
[putfs](https://putf.sh)

</div>

### 1 · Storage

- **[anystore](https://docs.investigraph.dev/lib/anystore/)**: store anything anywhere, with one interface to keep and retrieve keys, values and files in local folders, Redis, SQL databases, over HTTP or in cloud storage. ([GitHub](https://github.com/dataresearchcenter/anystore))
- **[putfs](https://putf.sh)**: fast HTTP blob storage on a plain filesystem, with simple PUT and GET requests, files on disk served by nginx, and no SDK or metadata database.

### 2 · FollowTheMoney core

- **[ftmq](https://docs.investigraph.dev/lib/ftmq/)**: queries and filters FollowTheMoney entities from files, streams or statement stores, with one query object that also compiles to SQL and to OpenAleph API parameters. ([GitHub](https://github.com/dataresearchcenter/ftmq))
- **[ftm-lakehouse](https://openaleph.org/docs/lib/ftm-lakehouse/)**: a data standard and archive storage for FollowTheMoney entities, documents and their metadata, from leaks to public collections, that tools like investigraph, memorious and OpenAleph write to and read from. ([GitHub](https://github.com/openaleph/ftm-lakehouse))

### 3 · Processing queue

- **[openaleph-procrastinate](https://openaleph.org/docs/lib/openaleph-procrastinate/)**: OpenAleph's task queue for its processing jobs, built on the PostgreSQL-based procrastinate library. ([GitHub](https://github.com/openaleph/openaleph-procrastinate))

### 4 · Data creation

- **[ingest-file](https://openaleph.org/docs/lib/ingest-file/)**: extracts the contents of documents, archives and emails of many file types into FollowTheMoney entities, keeping their folder structure, ready for OpenAleph. ([GitHub](https://github.com/openaleph/ingest-file))
- **[memorious](https://docs.investigraph.dev/lib/memorious/)**: a lightweight toolkit to crawl and scrape websites into document collections, continuing the discontinued original memorious. ([GitHub](https://github.com/dataresearchcenter/memorious))
- **[investigraph](https://docs.investigraph.dev/)**: an ETL framework that turns any data source into FollowTheMoney datasets, configured in YAML and extensible with Python where a source needs it. ([GitHub](https://github.com/dataresearchcenter/investigraph))

### 5 · Analysis

- **[ftm-analyze](https://openaleph.org/docs/lib/ftm-analyze/)**: analyzes FollowTheMoney entities during ingestion: detects languages and countries, extracts names, emails, phone numbers and IBANs, resolves names against known entities with juditha, and annotates them for search. ([GitHub](https://github.com/openaleph/ftm-analyze))
- **[juditha](https://docs.investigraph.dev/lib/juditha/)**: a fast lookup of canonical names that tells whether a name found by entity recognition matches a known company, person or sanctioned entity, even when spelling, accents or word order differ. ([GitHub](https://github.com/dataresearchcenter/juditha))

### 6 · Application

- **[OpenAleph](https://openaleph.org/docs/)**: the platform on top, which securely stores large amounts of documents and data and makes them searchable for investigative teams to work on together. ([GitHub](https://github.com/openaleph/openaleph), [about OpenAleph](openaleph.md))
- **[openaleph-search](https://openaleph.org/docs/lib/openaleph-search/)**: the Elasticsearch-based module that indexes, searches and matches FollowTheMoney entities in OpenAleph, and works on its own too. ([GitHub](https://github.com/openaleph/openaleph-search))

</section>
