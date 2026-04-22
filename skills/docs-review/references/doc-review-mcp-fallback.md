# MCP Fallback for `adk-docs-review`

This skill is mode-aware. In `--mode local`, it reads files from disk (or fetches a URL with `curl`). In `--mode confluence`, it talks to Confluence via the Atlassian MCP, with a REST fallback.

## `--mode local`

No MCP needed. The skill reads:

- local Markdown / RST / HTML files from disk
- HTTP-fetchable docs via `curl` / `WebFetch` (no auth assumed; private docs require `--mode confluence`)

## `--mode confluence`

### Preferred: `plugin-atlassian-atlassian` MCP server

If the Atlassian MCP is configured, prefer it for:

- fetching the page content (current revision + revision history)
- listing existing inline + footer comments
- listing the auth identity's permissions on the space
- creating inline + footer comments
- replying on existing comment threads

Why MCP first: structured comment shapes, anchor-aware inline comment posting, native handling of Confluence's Atlassian Document Format vs Markdown conversion.

### Fallback: Confluence REST API

If the Atlassian MCP is missing, fall back to the REST API via `curl` + `jq`:

```bash
# Page content
curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" \
  "https://<your-domain>.atlassian.net/wiki/api/v2/pages/$PAGE_ID?body-format=storage" | jq

# Existing comments (inline + footer)
curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" \
  "https://<your-domain>.atlassian.net/wiki/api/v2/pages/$PAGE_ID/inline-comments"

curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" \
  "https://<your-domain>.atlassian.net/wiki/api/v2/pages/$PAGE_ID/footer-comments"

# Post inline comment (anchored on a text snippet)
curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" -X POST \
  -H "Content-Type: application/json" \
  -d '{"pageId":"'"$PAGE_ID"'","body":{"value":"<markdown>","representation":"wiki"},"inlineCommentProperties":{"textSelectionMatchCount":1,"textSelection":"<exact text from page>"}}' \
  "https://<your-domain>.atlassian.net/wiki/api/v2/inline-comments"

# Post footer comment
curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" -X POST \
  -H "Content-Type: application/json" \
  -d '{"pageId":"'"$PAGE_ID"'","body":{"value":"<markdown>","representation":"wiki"}}' \
  "https://<your-domain>.atlassian.net/wiki/api/v2/footer-comments"
```

Print this warning once per run: `Warning: Atlassian MCP server not configured; using Confluence REST API via curl.`

### Install pointer

Generate an Atlassian API token at https://id.atlassian.com/manage-profile/security/api-tokens. Run `adk-install` and pick `plugin-atlassian-atlassian` in the MCP step; it will prompt for `ATLASSIAN_USER` (your account email) + `ATLASSIAN_API_TOKEN` and persist them to `~/.zshenv`. The MCP also needs the Confluence site domain (e.g., `your-org.atlassian.net`).

## Mode auto-detect

Detect the mode from the doc target:

| Target shape | Mode |
| --- | --- |
| Local path (`./docs/foo.md`, `/Users/.../bar.md`) | `local` |
| `https://*.atlassian.net/wiki/...` URL | `confluence` |
| Other public URL (`https://docs.example.com/...`) | `local` (fetched via WebFetch; no comments to post) |

The user can override with explicit `--mode local` or `--mode confluence`.

## Auth probing

Phase 1 of the validator runs:

- Local mode: file-existence check on the path.
- Confluence mode: a read-only `GET /wiki/api/v2/spaces` against the API to confirm credentials work, then a permission probe on the target space.

If auth fails, the validator emits BLOCKER with the install pointer above.

## Anchor-text gotchas

When posting inline comments via the REST API, the `textSelection` MUST be a verbatim snippet from the current page. Common gotchas:

- Smart quotes (`"` vs `"`) — copy from the actual page, not from a Markdown source.
- Whitespace differences — Confluence collapses some whitespace; copy the rendered text.
- Multiple matches — set `textSelectionMatchCount` to `1` and ensure the snippet is unique on the page; otherwise post lands on the first match.

The Atlassian MCP handles most of this for you; the REST fallback does not. Prefer the MCP whenever possible for inline comment posting.
