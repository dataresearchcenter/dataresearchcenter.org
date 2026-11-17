---
date: 2026-11-17
categories:
  - DARC
---

# Inside Deutsche Bank: Making 15 million files searchable, and helping journalists find their stories

> More than 200 journalists. Over 50 media outlets. More than 15 million files. A global investigation into Deutsche Bank required technology that could handle the scale, and people who knew how to help journalists make sense of the data. That's where we came in.

<!-- more -->

![project inside deutsche bank illustration](../../assets/projects/barracuda.jpg)

[Inside Deutsche Bank](https://inside-db.com/) is a global collaborative investigation based on a leak comprising more than 15 million files, covering Deutsche Bank's activities from the early 2010s onward. It is the largest cache of internal documents ever leaked to journalists from within a bank.

The leak was obtained by Indian journalist and author Josy Joseph and South African investigative journalist Khadija Sharife. The investigation is coordinated by Barracuda Media, a South African not-for-profit organisation, and brings together more than 200 journalists from over 50 media outlets worldwide.

Since spring 2026, we've provided technical and research support to the journalists working on the investigation. Our first priority was to make the data searchable as quickly as possible. But our work went well beyond processing the files. We helped journalists navigate the material, understand its context and find documents buried in millions of records.

The project also pushed us to improve [OpenAleph](https://openaleph.org/), our open-source investigative platform. All of the changes we made in response to the investigation have since become part of the software, benefiting everyone who uses it.

## Getting millions of files ready for journalists

With a leak of this size, speed matters. Journalists needed access to the material as soon as possible, so we worked on improving OpenAleph's existing ingestion and indexing processes to get documents searchable faster.

We optimized how Elasticsearch indexes documents, reducing the amount of information stored where it wasn't essential. We also improved how OpenAleph extracts and processes files, addressing some of the less obvious challenges we came across in the Deutsche Bank material.

One bizarre discovery was just how often people at Deutsche Bank embed entire documents inside other documents. An Excel spreadsheet could contain a PDF, or a Word document could hide an entire ZIP archive. Previously, these embedded files would go unnoticed during ingestion, leaving their contents out of search results.

We reworked parts of our `ingest-file` processing pipeline to extract these embedded files and process them as separate, searchable documents. The investigation also highlighted the need to support less common formats, including Excel's binary `.xlsb` format, which OpenAleph can now process.

These improvements became part of [OpenAleph 5.4.0, codenamed Matryoshka](https://darc.li/blog/2026/openaleph-matryoshka-is-here/).

## Making spreadsheets easier to search

The leak contained huge spreadsheets, from client lists and anti-money laundering (AML) tracking sheets to records of financial transactions. Journalists often needed to find out whether a particular name, company or other search term appeared in one of these files, and exactly where.

Downloading and manually searching spreadsheets containing thousands of rows wasn't practical or secure, so we [made it possible to search the contents of spreadsheets directly in OpenAleph](https://darc.li/blog/2026/openaleph-53-email-threads-table-exploration-and-entity-screening/), across an entire document or within specific columns. Journalists could then find relevant entries without having to download and work through enormous files themselves.

## Making emails easier to follow

Emails are often some of the most valuable material in an investigation, but they're also messy. The Deutsche Bank leak highlighted a few problems worth addressing.

For example, we found emails sent by assistants on behalf of their managers, where the sender's displayed name didn't match the email address. We updated OpenAleph's email interface to show both, for senders and recipients, making it easier to understand who was actually communicating.

We also improved how the software handles malformed email headers, unusual message structures and attachments that might otherwise be missed. And [with the release of OpenAleph 5.3.0](https://darc.li/blog/2026/openaleph-53-email-threads-table-exploration-and-entity-screening/), journalists can now view emails as conversations, grouping messages into threads rather than reviewing each one in isolation.

These changes make it easier to follow discussions and find the context behind individual messages.

## Translating documents on-premises

Working with a global bank means dealing with documents in different languages. [We developed a feature](https://darc.li/blog/2026/in-platform-translation-for-sensitive-documents/) that allows documents to be translated directly within on-premises OpenAleph installations, so journalists can work with material in other languages without having to move sensitive files to an external translation service like Google Translate.

## Finding people of interest across millions of documents

We also built and used OpenAleph's Screening feature, [known as percolation](https://darc.li/blog/2026/how-to-use-the-new-screening-feature/), to help journalists identify potentially important people and companies in the leak.

Percolation identifies entities mentioned in documents and checks whether they appear elsewhere in an OpenAleph instance. We had also uploaded reference datasets containing sanctions and politically exposed persons (PEPs) information. This allowed us to identify emails and other documents mentioning individuals and companies appearing in those lists.

Rather than relying on journalists to search for every name individually, OpenAleph could flag relevant mentions across the material, helping surface connections and documents worth investigating.

## Helping journalists find the needle in the haystack

Making millions of files searchable is only half the job. Helping journalists understand what they're looking at and find what they need is just as important.

Throughout the project, we provided ongoing research support, helping reporters run advanced searches, track down hard-to-find documents and follow up on leads.

A big part of this involved decoding the language of Deutsche Bank. The emails were full of banking acronyms, internal project names and references that could be difficult to understand without background knowledge. People were sometimes referred to by code names, and figuring out how client numbers were attributed to individuals and companies took some serious digging.

We documented these findings in the project's shared Wiki, adding guides to explain terminology, identify patterns and help journalists navigate the material. We also flagged potentially relevant documents and early leads to get investigations moving.

Sometimes this meant developing very specific searches. For example, we discovered that internal whistleblower accounts were referred to using the abbreviation "WB" followed by a number. We used regular expressions to search for these variations across the leak, helping us locate documents that mentioned the accounts even when they weren't described in full.

We also ran dozens of training sessions for participating journalists, covering everything from basic OpenAleph use to advanced search techniques. Along the way, we shared what we'd learned about the leak, the types of documents it contained and where interesting information might be hiding.

With millions of files, finding something isn't always as simple as searching for a name. You need to understand the terminology, know how information is recorded and have a good idea of where to look. Our experience as investigative journalists, combined with our knowledge of the software, helped us guide reporters through that process.

## From spreadsheets to a map of financial transactions

For one of the money laundering investigations, which comes out later this week, we built a tool to visualize transaction data contained in the leak.

Deutsche Bank had processed many of the payments. The spreadsheets provided a record of transactions, but following the money through rows and columns wasn't easy. Our tool turned that information into a visual representation, helping journalists explore connections and spot patterns.

## More than software support

Inside Deutsche Bank has been a huge lift, not just for the journalists involved, but for the technology and research support behind them.

We've worked on faster ingestion, more complete document extraction, better email handling, spreadsheet search, document translation and improved screening tools. We've also spent countless hours helping journalists understand the material, find elusive documents and turn initial hunches into concrete leads.

Much of this work was developed specifically in response to the demands of the investigation. And all of it has since become part of OpenAleph, meaning the wider investigative community benefits from what we learned along the way.

But the biggest lesson we learned is that handling a leak of this scale takes more than technology. You need people who understand the data, know how to search it, can spot what might be important and are available to help when journalists hit a wall.

That's what we bring to the table at DARC. We work with journalists and newsrooms to process large and complicated datasets, make them searchable, develop tools to explore them and provide the research support needed to get the most out of the material.

We've spent years making messy data searchable. Inside Deutsche Bank was another opportunity to put that experience to work, and to make the tools we build better for the next investigation.

And we're always happy to put that experience to work on the next big leak.
