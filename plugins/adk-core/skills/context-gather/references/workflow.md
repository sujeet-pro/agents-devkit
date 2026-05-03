# `context-gather` — per-source fetch protocol

## Phase 0 — extract URLs

Regex set (see `references/source-classifiers.md` for the canonical list):

```
\b(?:https?://)?(?:[a-z0-9-]+\.)?(?:atlassian\.net|atlassian\.com)/(?:browse|wiki/spaces)/[A-Z0-9-/]+
\b(?:https?://)?docs\.google\.com/(?:document|spreadsheets|presentation)/d/[A-Za-z0-9_-]+
\b(?:https?://)?mail\.google\.com/mail/[a-z0-9/]+
\b(?:https?://)?[a-z0-9-]+\.slack\.com/archives/[A-Z0-9]+/p[0-9]+
\b(?:https?://)?github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/(?:pull|issues)/\d+
```

Classify each match by domain. Deduplicate.

## Phase 1 — preflight

For each detected source type:

| Source | Connector / Tool |
| --- | --- |
| Jira / Confluence | Atlassian workspace connector (Rovo) |
| GDoc / GSheet | Google Drive workspace connector |
| Gmail | Gmail workspace connector |
| Slack | Slack workspace connector |
| GitHub | github MCP (Docker) OR `gh` CLI fallback |

Run `bin/adk-mcp-health` to confirm reachability. Stop with the missing-thing list if any required connector isn't ready.

## Phase 2 — fetch per source

### Jira

Tool: Atlassian connector → `getIssue(key)`.

Fields to capture: `key`, `fields.summary`, `fields.status.name`, `fields.assignee.displayName`, `fields.reporter.displayName`, `fields.priority.name`, `fields.description` (excerpts ≤15 words), `fields.labels`, AC (parsed from description), `fields.updated`.

### Confluence

Tool: Atlassian connector → `getPage(spaceKey, title)` or by ID.

Fields: title, author, last-modified, top-level headings, 2-3 key excerpts (≤15 words each).

### GDoc / GSheet / GSlides

Tool: Google Drive connector → `getDocument(id)` (or equivalent).

Fields: title, owner, last-modified, structure (heading list), 2-3 excerpts.

### Slack message / thread

Tool: Slack workspace connector.

For a message URL `https://workspace.slack.com/archives/C123/p1715...`:
1. Pull the parent message.
2. If it's the start of a thread, pull all replies.
3. If it's mid-thread, pull the parent + replies.

Fields: channel, primary author, message count, summary of discussion, action items.

### Gmail thread

Tool: Gmail workspace connector. Requires explicit thread URL.

Fields: subject, participants, message count, summary.

### GitHub PR

Tool: github MCP (`get_pull_request`) or `gh pr view <url> --json ...`.

Fields: title, body, base/head branch, author, state, mergeable, files-changed list, top 3-5 comments by reaction count.

### GitHub Issue

Tool: github MCP (`get_issue`) or `gh issue view <url> --json ...`.

Fields: title, body, author, state, labels, top comments.

## Phase 3 — summarize per source

For each source:

```markdown
### <Title> (<source-type>; updated <YYYY-MM-DD>)
- Source: <URL>
- Author: <name>
- Status: <status / state / N/A>
- Summary (paraphrased, ≤80 words):
  ...
- Excerpts (≤15 words each):
  - "..."
  - "..."
- Action items detected:
  - <person> asked: "<paraphrase>"
  - <person> owns: "<paraphrase>"
```

## Phase 4 — deduplicate + cross-reference

If two sources cover the same artifact (e.g. Slack thread links the same Jira ticket), summarize each separately and cross-reference in the `Cross-references` section.

## Phase 5 — write context.md

Final structure per `references/output-format.md`. Single file: `.temp/task-<slug>/context.md`.

## Failure modes

- **Access denied** — note in the report; suggest the fix (e.g. "enable Atlassian connector in workspace settings").
- **404** — same as above; do not retry.
- **Connector not reachable** — preflight should have caught this; if it slips through, surface and stop.
- **Rate-limited** — back off; surface in report.
