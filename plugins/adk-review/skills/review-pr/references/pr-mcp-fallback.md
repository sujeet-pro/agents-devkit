# `review-pr` — GitHub MCP / `gh` CLI fallback

Both transports are first-class. The skill prefers `gh` when both are available (faster cold start, no Docker daemon dependency).

## Decision matrix

| Docker MCP reachable | `gh` CLI authed | Pick |
| --- | --- | --- |
| yes | yes | `gh-cli` (faster cold start) |
| yes | no | `github-docker` |
| no | yes | `gh-cli` |
| no | no | stop with the missing-thing list (suggest both install paths) |

The choice is recorded in `validation/per-skill/review-pr.md` for the session and reflected in the status banner.

## Why prefer `gh` when both are available

| Factor | github-docker | gh-cli |
| --- | --- | --- |
| Cold start | 2-5s (Docker pull / image extract on first use) | <100ms |
| Steady-state per-call latency | ~similar (200-500ms) | ~similar (200-500ms) |
| Auth | `GITHUB_PAT` env var | OAuth via `gh auth login` (more user-friendly) |
| Read-only enforcement | `GITHUB_READ_ONLY` env (blanket) | Per-command (`--dry-run` / scope) — finer control |
| Tool surface | Curated MCP tools (`pull_requests.create_review`, etc.) | Raw `gh api ...` access (everything) |
| Pagination | Auto-handled by MCP | Use `--paginate` |

For typical review-pr calls (read PR, post N comments, re-fetch), the latency is dominated by network round-trips, not the transport. The cold-start delta is the deciding factor.

## Operation map: review-pr's calls

The same operation can be done via either transport. Use this table when implementing:

| Operation | github-docker (MCP tool) | gh-cli command |
| --- | --- | --- |
| Get PR metadata | `pull_requests.get` | `gh pr view <num> --json title,body,baseRefName,headRefOid,author,additions,deletions,files,labels,reviewRequests,assignees,statusCheckRollup` |
| Get PR diff | `pull_requests.get_diff` | `gh pr diff <num> --patch` |
| List inline comments | `pull_requests.list_review_comments` | `gh api /repos/<repo>/pulls/<num>/comments --paginate` |
| List issue comments (top-level) | `issues.list_comments` | `gh api /repos/<repo>/issues/<num>/comments --paginate` |
| List reviews | `pull_requests.list_reviews` | `gh api /repos/<repo>/pulls/<num>/reviews --paginate` |
| Resolved-thread state | `pull_requests.list_review_threads` (GraphQL underneath) | `gh api graphql -f query='query { repository(owner:..., name:...) { pullRequest(number:...) { reviewThreads(first:100) { nodes { id, isResolved, comments(first:1) { nodes { id, path, line, body } } } } } } }'` |
| Post a review with inline comments | `pull_requests.create_review` (event=COMMENT) | `gh pr review --comment -F <body-file>` |
| Post a single inline comment | `pull_requests.create_review_comment` | `gh api -X POST /repos/<repo>/pulls/<num>/comments -f body='...' -f commit_id=<sha> -f path='...' -F line=N -f side=RIGHT` |
| Post a top-level (issue) comment | `issues.create_comment` | `gh pr comment <num> --body '...'` |
| Reply to an inline comment | `pull_requests.create_review_comment` (with `in_reply_to=<id>`) | `gh api -X POST /repos/<repo>/pulls/<num>/comments -f body='...' -F in_reply_to=<id>` |
| Resolve a thread | `pull_requests.resolve_thread` (GraphQL) | `gh api graphql -f query='mutation { resolveReviewThread(input: { threadId: "..." }) { thread { isResolved } } }'` |
| Push to head branch | (out of MCP scope) | `git push origin <head-branch>` (or via `gh` if the user prefers) |
| Get repo permissions | `repos.get` | `gh api /repos/<repo>` (look at `permissions.push`) |
| Get branch protection | `repos.get_branch_protection` | `gh api /repos/<repo>/branches/<base>/protection` |

## `GITHUB_READ_ONLY` semantics

`GITHUB_READ_ONLY=1` is the default. It causes the MCP server to refuse any write tool. The skill flips it to `0` for the post stage only, then back to `1`.

```
Phase 6a start:
  if mcp == "github-docker":
    GITHUB_READ_ONLY=0 (re-init MCP if needed)
  # gh-cli has no equivalent toggle; uses per-command scoping

  ... post comments ...

Phase 6a end:
  if mcp == "github-docker":
    GITHUB_READ_ONLY=1
```

For `gh-cli`, there's no global toggle. The skill relies on its own command allow-list (the `code-reviewer` and `security-reviewer` agents have `gh pr merge`, `gh pr review --approve`, `git push --force` disallowed at the agent level).

## Required `gh` scopes

For `--auto` (read + post comments):

```
gh auth login --scopes repo,read:org,read:project,write:discussion
```

For `--fix` (additionally push commits):

```
gh auth login --scopes repo,read:org,read:project,write:discussion,workflow
```

(The standard `repo` scope already grants push to non-protected branches; `workflow` is for cases where the `--fix` touches `.github/workflows/`.)

## Required `GITHUB_PAT` scopes (when using MCP)

Fine-grained PAT with:

| Permission | Read | Write |
| --- | --- | --- |
| Contents | yes | (yes only for --fix) |
| Pull requests | yes | yes |
| Issues | yes | yes |
| Actions | yes | no |
| Metadata | yes | n/a |
| `read:org` | yes | n/a |
| `read:project` | yes | n/a |

## Failover (mid-session)

If the chosen transport starts failing mid-session (e.g. Docker daemon crashed; `gh` rate-limited):

1. Log the failure to `validation/per-skill/review-pr.md`.
2. If the OTHER transport is available, switch and continue. Surface the switch in the status banner.
3. If neither is available, stop and surface — do NOT keep retrying the dead transport.

This is the one place re-attempting is OK: switching transport mid-session does not create duplicate comments because the receipt set is per-finding, not per-transport.

## Verifier

```bash
# MCP path
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PAT \
  -e GITHUB_TOOLSETS=context,repos,pull_requests \
  -e GITHUB_READ_ONLY=1 \
  ghcr.io/github/github-mcp-server:v1.0.3 \
  </dev/null  # initialize then exit; should print MCP banner

# gh path
gh auth status
gh api /user --jq .login
```

Both should succeed for the skill's preflight to pass.
