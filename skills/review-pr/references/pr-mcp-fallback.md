# MCP Fallback for `adk-review-pr`

This skill is provider-aware: GitHub or Bitbucket. For each provider it prefers the MCP server when configured, then falls back to the CLI / direct REST API.

## GitHub

### Preferred: `github` MCP server

If the `github` MCP server is configured, prefer it for:

- fetching PR metadata, diff, files, reviews, comments
- listing existing comments + replies
- posting inline review comments + summary review

Why MCP first: faster, structured response shapes, better diff line-anchor support.

### Fallback: `gh` CLI

If `github` MCP is missing:

```bash
gh pr view <n> --json title,body,baseRefName,headRefName,files,reviews,comments
gh pr diff <n>
gh pr review <n> --comment --body-file <path>
gh api repos/<owner>/<repo>/pulls/<n>/comments  # inline comments
gh api repos/<owner>/<repo>/issues/<n>/comments  # PR-level comments
```

Print this warning once per run: `Warning: github MCP server not configured; using gh CLI.`

### Install pointer

Generate a Personal Access Token (classic, scopes: `repo`, `read:org`) at https://github.com/settings/tokens. Run `adk-install` and pick `github` in the MCP step; it will prompt for `GITHUB_PAT` and persist it to `~/.zshenv`.

## Bitbucket

### Preferred: `bitbucket` MCP server

If a `bitbucket` MCP server is configured, prefer it for:

- fetching PR metadata, diff, files, comments, replies, tasks
- creating inline comments anchored to file:line ranges
- creating, resolving, and reopening Bitbucket tasks linked to inline comments
- posting PR-level summary comments

Bitbucket task semantics matter for this skill — task tracking is the must-fix mechanism for Blocker / Critical findings (see `pr-postback-protocol.md`).

### Fallback: direct REST API

If a Bitbucket MCP is missing, fall back to the REST API via `curl` + `jq`:

```bash
# PR metadata
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/$WS/$REPO/pullrequests/$N" | jq

# Diff
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/$WS/$REPO/pullrequests/$N/diff"

# Existing comments
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/$WS/$REPO/pullrequests/$N/comments?pagelen=100"

# Post inline comment
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":{"raw":"<markdown>"},"inline":{"path":"<path>","to":<line>}}' \
  "https://api.bitbucket.org/2.0/repositories/$WS/$REPO/pullrequests/$N/comments"

# Create task linked to a comment
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":{"raw":"<title>"},"comment":{"id":<comment_id>}}' \
  "https://api.bitbucket.org/2.0/repositories/$WS/$REPO/pullrequests/$N/tasks"
```

Print this warning once per run: `Warning: bitbucket MCP server not configured; using REST API via curl.`

### Install pointer

Generate an app password (https://bitbucket.org/account/settings/app-passwords/) with scopes: `Repositories: Read`, `Pull requests: Read & Write`. Run `adk-install` and pick `bitbucket` in the MCP step; it will prompt for `BITBUCKET_USER` + `BITBUCKET_APP_PASSWORD` and persist them.

## Provider auto-detect

Detect from the PR URL host:

| Host | Provider |
| --- | --- |
| `github.com`, `*.ghe.io`, GitHub Enterprise | `github` |
| `bitbucket.org` | `bitbucket` |
| anything else | STOP and clarify |

The Phase 1 validator (`pr-review-validator.md`) blocks on unrecognized hosts.

## Auth probing

Phase 1 of the validator runs:

- `gh auth status` for GitHub paths.
- A read-only `GET /user` against the Bitbucket API to confirm the app password works.

If auth fails, the validator emits BLOCKER with the install pointer above.
