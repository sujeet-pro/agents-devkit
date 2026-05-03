# `context-gather` — source classifiers

Canonical regex patterns + connector mapping.

## Patterns

| Source | Regex (case-insensitive) | Connector |
| --- | --- | --- |
| Jira issue | `\b(?:https?://)?[a-z0-9-]+\.atlassian\.net/browse/[A-Z][A-Z0-9]*-\d+` | Atlassian workspace |
| Confluence page | `\b(?:https?://)?[a-z0-9-]+\.atlassian\.net/wiki/spaces/[A-Z0-9]+/(?:pages/\d+\|.*)` | Atlassian workspace |
| Google Doc | `\b(?:https?://)?docs\.google\.com/document/d/[A-Za-z0-9_-]+` | Google Drive workspace |
| Google Sheet | `\b(?:https?://)?docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+` | Google Drive workspace |
| Google Slides | `\b(?:https?://)?docs\.google\.com/presentation/d/[A-Za-z0-9_-]+` | Google Drive workspace |
| Gmail thread | `\b(?:https?://)?mail\.google\.com/mail/(?:u/\d+/)?#[a-z]+/[a-z0-9]+` | Gmail workspace |
| Slack message | `\b(?:https?://)?[a-z0-9-]+\.slack\.com/archives/[A-Z0-9]+/p\d+` | Slack workspace |
| GitHub PR | `\b(?:https?://)?github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/pull/\d+` | github MCP / gh CLI |
| GitHub issue | `\b(?:https?://)?github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/issues/\d+` | github MCP / gh CLI |

## Tool selection per source

| Source | Tool path |
| --- | --- |
| Jira / Confluence | Atlassian connector tools (`getIssue`, `getPage`) |
| GDoc / GSheet / GSlides | Google Drive connector tools |
| Gmail | Gmail connector tools |
| Slack | Slack connector tools |
| GitHub | github MCP if reachable, else `gh` CLI |

## Fallbacks

- If the workspace connector is not enabled, the skill stops with: "<Connector> not enabled on this workspace; ask your Claude admin to enable it. Source URL: <url>."
- For GitHub specifically: the github MCP is preferred; `gh` CLI is the fallback. If neither is available, stop.
- Generic web URLs (anything not matching the patterns above) are NOT handled by this skill — recommend `WebFetch` instead.

## Edge cases

- **Trailing slashes / query strings** — strip before matching.
- **URL-shortened links** — not auto-resolved (would require an outbound HTTP call). Surface as "shortener URL; resolve manually before passing to context-gather".
- **Authenticated URLs with `/?token=...`** — the token is captured but never logged; use only for the fetch.
- **Markdown links `[text](url)`** — extract just the URL.
- **Nested links inside the linked content** — NOT followed (one-hop rule).
