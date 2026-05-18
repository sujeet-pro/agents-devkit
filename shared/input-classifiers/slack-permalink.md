# input classifier: Slack permalink

## Pattern

```
https?://<workspace>.slack.com/archives/<CHANNEL_ID>/p<TIMESTAMP>
https?://<workspace>.slack.com/archives/<CHANNEL_ID>/p<TIMESTAMP>?thread_ts=...
```

Where `<TIMESTAMP>` is the Slack `ts` field with the dot removed (e.g., `p1715789432123456` → `ts=1715789432.123456`).

## Fetch via

`adk-mcp-slack` (`slack-mcp-server`) — `conversations.history` + `conversations.replies` for the parent + thread.

If the MCP isn't loaded (no `SLACK_BOT_TOKEN` and no `SLACK_USER_TOKEN`):
- Skip with `[skipped] [slack]` note in context.md.
- Do not fall back to scraping (no public Slack URL endpoint).

## Extract into context.md

```markdown
### [slack] permalink — <channel-name> (<channel-id>)
url: <full URL>
fetched: <ts>
parent author: <user>
parent text (≤80 words): <quote with ≤15-word verbatim segments, paraphrase the rest>
thread length: <N replies>
thread excerpt: <last 3 substantive, quoted ≤15 words each>
references in thread: <PR URLs, Jira keys, DD links found in the thread>
```

## Hints

- `/adk-investigate`: alert permalinks are common starting points. Extract symptom + symptom-time.
- `/adk-implement`: thread may contain refinement of a spec.
- `/adk-document --type slack-summary`: condense a long thread.

## Privacy

- Don't include user emails or message bodies verbatim in long quotes. Paraphrase.
- DM channels (`D...`-prefixed channel IDs): only fetch if the user explicitly says so.
