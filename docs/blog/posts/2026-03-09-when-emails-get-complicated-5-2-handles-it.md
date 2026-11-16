---
date: 2026-03-09
categories:
  - OpenAleph
---

# When Emails Get Complicated: 5.2 Handles It

> How we found out and fixed the discrepancies between a RFC and the real world

<!-- more -->

Churchill [famously once said](https://richardlangworth.com/worst-form-of-government), "**Email** is the worst form of digital communication, except for all those other forms that have been tried."

A chunk of the work in the OpenAleph 5.2 release has gone into improving how we parse emails. Our [`ingest-file` library ](https://github.com/openaleph/ingest-file)can process individual emails (.eml, .msg, and friends) as well as full inbox backups (.pst, mbox, and others). At its core, the job is quite simple: extract all the text from each email and index it so it’s searchable.

In practice, things get more complicated. Beyond text extraction, [`ingest-file`](https://github.com/openaleph/ingest-file) also extracts the attachments from emails, making them searchable, and creates [FollowTheMoney Person](https://followthemoney.tech/explorer/schemata/Person/) entities from senders and recipients, calendar invites, and even contacts shared via attachments. As you might expect, this kind of processing is complex, and occasionally buggy.

We’re not going to tumble down the rabbit hole of “[what exactly counts as a valid e-mail address?](https://www.netmeister.org/blog/email.html)” here. Instead, this post highlights a few concrete improvements we’ve made in [OpenAleph 5.2](./2026-03-09-openaleph-5-2-strengthening-email-and-breaking-language-barriers.md) to make email parsing more robust, more accurate, and a little less painful overall.

## Multiple people can share the same email address

There’s a whole list of [falsehoods programmers believe about email](https://beesbuzz.biz/code/439-Falsehoods-programmers-believe-about-email), and one we explicitly tackled is the idea that an email address always belongs to exactly one person. Outlook, for example, supports [delegated access](https://support.microsoft.com/en-us/office/share-and-access-another-person-s-mailbox-or-folder-in-outlook-a909ad30-e413-40b5-a487-0ea70b763081) to emails: emails sent this way show up as coming from `<invitee>` on behalf of `<manager>`.

Because `ingest-file` creates Person entities from email senders and recipients, delegate access can result in a single Person entity with one email address and multiple names. To make this clearer, we’ve updated the OpenAleph email view to always display both the name *and* the email address (in pointy brackets), making it easier to distinguish delegate access from the more common one-person-per-address case.

## We dislike hierarchies, except when it comes to file types

File type detection in `ingest-file` prioritizes the most specific file type available. When a file is uploaded directly, OpenAleph determines how to process it based primarily on the file type, typically inferred from the file extension. This helps ensure that emails are handled by their dedicated ingestors rather than being processed as generic HTML or plain text.

Attachments, however, are more complicated. Emails often include metadata that declares an attachment’s MIME type, but this information isn’t always present or reliable, and file extensions alone can be misleading. To improve accuracy, we fall back to the detection algorithms provided by the [`python-magic` library](https://pypi.org/project/python-magic/) when an attachment’s type isn’t clear. These changes significantly improve how attachments are identified, routed to the correct ingestor, and ultimately rendered in the OpenAleph UI as intended.

## Extract all the attachments

Correctly identifying attachments is only half the battle. In email threads where entire messages are inlined inside other emails, Python’s standard email parser can fail to tell where the message body ends and an attachment begins, causing attachments to be missed entirely. Since our priority is to make as much uploaded content searchable as possible, we went looking for alternative extraction methods.

After experimenting with several Python libraries and binary tools, we landed on `ripmime`, a utility that can bulk-extract all attachments from an email. We keep track of which attachments were already successfully extracted, so we don’t re-ingest duplicates pulled out by `ripmime`.

This approach does come with a downside: attachments extracted by `ripmime` can sometimes be associated with the wrong email in a thread. For example, if a reply includes an attachment but the message structure is mangled, `ripmime` may still extract the attachment, but assign it to the original email instead of the reply. It’s not perfect, but it beats missing the attachment entirely.

## "I can fix him!" applied to headers

Finally, we embarked on the perilous journey of fixing email [headers](https://datatracker.ietf.org/doc/html/rfc5322#section-2.2). In theory (and even more so in practice), the amount and placement of whitespace in headers [varies wildly](https://datatracker.ietf.org/doc/html/rfc5322#appendix-A.6.3). One rule does hold, though: a header needs a colon to be considered valid.

The Python standard library’s email module helpfully flags messages with broken headers. We added code that attempts to “fix” these headers by inserting missing colons. The logic is simple: insert a colon before the first whitespace to reconstruct a plausible header name and value. In some cases, a header that’s badly mangled may still become parseable just by containing a colon somewhere, allowing the rest of the message to be decoded.

Still, just like people, not all headers can be fixed. That’s one reason we always run `ripmime` after attempting header repairs. We’ve found cases where it successfully extracts attachments even when headers are beyond saving.

If you’ve run into other email parsing quirks or bugs while using OpenAleph, we’d love to hear about them at [**darc.social**](https://darc.social/).
