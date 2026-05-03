# `context-gather` — anti-patterns

- **Quoting >15 words from any source.** Copyright + attribution discipline. Use `≤15 words` per excerpt; paraphrase the rest.
- **Silently skipping a 404 / access-denied URL.** Surface it in the Sources table and explain what to fix.
- **Pasting raw Slack chatter.** Summarize. The user wants the gist, not the transcript.
- **Treating screenshots as primary content.** They require manual download. Note them as `attachments noted; not downloaded`.
- **Following links recursively.** One hop only. If the Jira ticket links to a Confluence page, mention it but don't fetch unless the user explicitly says so.
- **Using this skill as a generic WebFetch.** It's specifically for the named source types. For arbitrary URLs, recommend `WebFetch` instead.
- **Downloading attachments without opt-in.** "the deck is attached; pulling it" → no. Ask first.
- **Cross-referencing without evidence.** If you say "the Slack thread references the Jira ticket", quote the message that contains the link.
- **Ignoring last-modified timestamps.** Old content can be wrong; surface the date so the user can judge.
- **Prepending "according to the source" to every sentence.** Cite once at the section header; subsequent sentences are implicitly from that source.
- **Failing to deduplicate.** If two sources cover the same artifact, summarize each separately and cross-reference. Don't summarize the same content twice.
