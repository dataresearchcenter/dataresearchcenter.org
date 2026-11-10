---
date: 2026-03-09
categories:
  - OpenAleph
---

# OpenAleph 5.2: Strengthening Email and Breaking Language Barriers

> This release focuses on two major improvements: making email ingestion more reliable and introducing secure, local document translation. It also includes a UI glow-up, so OpenAleph is looking fresher than ever.

<!-- more -->

### Making email parsing less painful

Email is one of the juiciest data types in investigations and one of the most complicated. Formats differ, metadata can be fragile, and attachments are often where crucial evidence lives.

With **OpenAleph 5.2**, we focused on making email ingestion more reliable and robust behind the scenes.

This release strengthens how OpenAleph processes email data to help ensure investigators don't miss critical material (like attachments) or structural details (like headers) that can be essential for understanding communication and uncovering evidence.

OpenAleph has long been able to process both individual emails and full mailbox archives, but doing this reliably is far from simple, especially when extracting attachments, interpreting messy message structures, and generating accurate Person entities from senders and recipients. In this release, we focused on strengthening that existing pipeline. 

Improvements include more dependable attachment extraction (even from broken or nested threads), smarter file-type detection when metadata is missing or misleading, clearer handling of delegated emails sent “on behalf of” others, and repair attempts for malformed headers. Together, these changes reduce data loss, improve accuracy, and make email evidence more complete and searchable for investigators.

If you want the full technical deep dive, you can read our [detailed release post here](./2026-03-09-when-emails-get-complicated-5-2-handles-it.md).

And we're not done with email yet. In our next release, we'll continue the email improvement train by rolling out UI updates the community has been asking for, improving how OpenAleph displays and helps you work with email data, making it easier to understand conversations and navigate context.

## Local translations for FollowTheMoney documents

This release also brings something many of you have been asking for: **built-in document translation**.

We’re introducing [**local translations for FollowTheMoney Documents**](./2026-03-09-in-platform-translation-for-sensitive-documents.md), inspired by the preliminary work and invaluable knowledge exchange with the International Consortium of Investigative Journalists (ICIJ), whose rockstar tech team built [**ES Translator**](https://github.com/ICIJ/es-translator).

Our approach focuses on privacy, security, and investigative practicality.

OpenAleph 5.2 integrates open source machine learning models, either [**Argos**](https://github.com/argosopentech/argos-translate) or [**Apertium**](https://wiki.apertium.org/wiki/Main_Page) to perform translations **locally**. That means you no longer need to send potentially sensitive information to external cloud services like Google Translate. Documents can now be translated directly where you work, instantly and safely.

This doesn’t just help with reading documents. You can also apply translation during ingest, enabling cross-language search. For example, if you search in English for documents containing the word *“contract”*, you’ll also get results for documents containing the German equivalent, *“vertrag.”*

If you're interested in the technical details, we’ve published [a deeper release note](./2026-03-09-in-platform-translation-for-sensitive-documents.md) describing the approach, deployment options, and how self-hosted instances can switch models and control translation globally or per document.

We plan to expand this translation feature and build a more intuitive user experience around it. In a future release, users will be able to translate entire collections of documents. Currently, the original language of a document is detected automatically. Future updates will improve the accuracy of this detection and allow users to manually set a document’s language when needed.

And just today, our friends at OpenSanctions released [FollowTheMoney 4.6.0](https://github.com/opensanctions/followthemoney/releases/tag/v4.6.0), which we’ve already integrated into this release.

OpenAleph 5.2 continues our focus on making investigative data easier to explore, safer to work with, and more powerful across borders and languages.

As always, thank you to the community for helping shape OpenAleph. Feel free to reach out with questions or feedback about OpenAleph on our [Discourse forum](https://darc.social/).
