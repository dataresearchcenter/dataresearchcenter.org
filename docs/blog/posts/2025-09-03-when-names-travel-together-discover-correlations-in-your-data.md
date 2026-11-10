---
date: 2025-09-03
categories:
  - OpenAleph
---

# When Names Travel Together: Discover Correlations in Your Data

> How OpenAleph 5 Surfaces Connections 

<!-- more -->

One of the cornerstones of OpenAleph is its search functionality. In version 5 of our investigative software, we have improved search and highlighting, but we also went a step further. The **Discovery Dashboard** and **Closely Correlated Names** are two new experimental features designed to help users uncover interesting connections in their data.

The new [Discovery page](https://search.openaleph.org/datasets/469#mode=discovery) is available to explore in our public OpenAleph instance. Using the [search function](https://search.openaleph.org/datasets/469?cslimit=30&csq=frontex#mode=search) in this instance reveals the feature that surfaces closely correlated names.

## The Discovery Dashboard

All datasets in OpenAleph 5 now include a Discovery Dashboard, allowing users to see, at a glance, the names of people, companies, and locations that appear most frequently in the source data. Those that appear most often are listed at the top, along with all closely correlated names for each. These names are extracted by the Named Entity Recognition algorithm in [ftm-analyze](https://openaleph.org/docs/lib/ftm-analyze/) and further refined by supporting libraries. 

## Closely Correlated Names

When searching in OpenAleph 5, a new section appears at the top of the results listing names that are closely correlated with your search term. Clicking any of these names triggers a search for both the original term and the correlated name.

These correlations come from an ElasticSearch feature called [*significant terms*](https://www.elastic.co/docs/reference/aggregations/search-aggregations-bucket-significantterms-aggregation), which we will explore in detail in a separate deep-dive blog post. In short, a name that is closely correlated with a search term appears more frequently alongside that term in the source documents. For example, from the ElasticSearch documentation:

> If the term "H5N1" exists in only 5 documents in a 10 million document index but shows up in 4 of the 100 documents returned in a user’s search, that is significant and probably very relevant. 5/10,000,000 vs 4/100 is a big swing in frequency.

Calculating this correlation is deterministic, meaning the most closely correlated names for a given term will always be the same, as long as the source documents do not change. We really like it when algorithms are predictable.

## Delivering Insights Without Sacrificing Security

True to our mission, these features rely on algorithms that run locally, without exposing any user data to third parties. There are no large language models or chatbots involved, no hallucinated data, and no made-up references.

All suggestions OpenAleph 5 provides are based on the source data, and nothing alters information a user has uploaded.

## Under the Hood

These features have been built on top of a large refactoring of the OpenAleph codebase. We have extracted the code that handles ElasticSearch indexing and search functionality into [openaleph-search](https://github.com/openaleph/openaleph-search), which can also be used from the command line to execute queries. We are fully leveraging [FollowTheMoney 4](https://github.com/opensanctions/followthemoney), and we have extracted the Named Entity Recognition logic into a stand-alone library called [ftm-analyze](https://openaleph.org/docs/lib/ftm-analyze/). Extracted names are further refined using [Juditha](https://github.com/dataresearchcenter/juditha), and we're already testing and refining another library that can answer the question, "*Is this the name of a location?*" 

We would love to hear your feedback about these features, or stories of insights that have surfaced from your data, over on [our Discourse](https://darc.social/).
