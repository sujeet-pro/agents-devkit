# `context-gather` — per-source extraction recipe

## Jira

URL pattern: `https://<host>.atlassian.net/browse/<KEY>`
MCP call: `jira.get_issue(KEY)`
Extract: summary, status, assignee, reporter, parent, links, last 5 comments, AC (from description's "Acceptance Criteria" section if present).

## Confluence

URL pattern: `https://<host>.atlassian.net/wiki/spaces/<SPACE>/pages/<ID>/<title>`
MCP call: `confluence.get_page(ID)`
Extract: title, version, breadcrumb (space + ancestor titles), body (first 2000 chars), last 3 comments.

## Google Docs

URL pattern: `https://docs.google.com/document/d/<DOC_ID>/`
MCP call: `google-drive.get_document(DOC_ID)`
Extract: title, last-modified, body (first 5000 words), comments.

## Slack

URL pattern: `https://<workspace>.slack.com/archives/<CHANNEL_ID>/p<TS>`
MCP call: `slack.get_thread_replies(channel, ts)`
Extract: channel name, OP message (user, ts, text), all replies (user, ts, text), file URLs (no content).

## Gmail

URL pattern: `https://mail.google.com/mail/u/0/#inbox/<MSG_ID>`
MCP call: `gmail.get_thread(thread_id)`
Extract: subject, all messages (sender, ts, body), attachment names (no content).

## GitHub PR

URL pattern: `https://github.com/<org>/<repo>/pull/<N>`
CLI: `gh pr view <N> --repo <org>/<repo> --json title,body,state,reviews,comments`
Extract: title, body, state (open/merged/closed), all reviews + comments.

## GitHub Issue

URL pattern: `https://github.com/<org>/<repo>/issues/<N>`
CLI: `gh issue view <N> --repo <org>/<repo> --json title,body,state,comments`

## Other (public web URL)

Use `WebFetch` (read-only HTTP) and summarize the visible content. Never use for paywalled or auth-required URLs.
