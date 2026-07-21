# review — target dispatch

Route by the shape of the target → sub-flow → how the diff (or content) is resolved. Every route stays read-only until a `--fix` or an explicit post is confirmed (`rules.md`).

| Target shape | Sub-flow | How to resolve |
|---|---|---|
| GitHub PR URL | pr (most common) | `gh pr view <url> --json title,body,author,baseRefName,headRefName,headRefOid,additions,deletions,files` for metadata + `gh pr diff <url>` for the diff. Read existing threads with `gh pr view <url> --json comments,reviews` so you don't re-raise resolved feedback. |
| `.` or a local directory path | working-tree | `git diff $(git merge-base HEAD origin/<default>)...HEAD` for the branch's change; `git diff` (or `git diff --staged`) for uncommitted work. State which you diffed. |
| a single tracked file path | file | Read the file; if it's dirty, `git diff -- <path>`. Review only what changed unless the whole file is the ask. |
| a markdown / doc file | doc | Read the doc and review prose — structure, unsupported claims, dead links, stale citations — not the code dimensions. |
| a comment-thread URL (PR review thread / issue) | thread | Fetch the thread — `gh api` for a GitHub thread, `WebFetch` for a plain web URL — then assess the exchange (is the concern resolved? still open?). |

Routing is by data, not vibes. If several inputs match, the strongest discriminator wins: **GitHub PR URL > comment-thread URL > local path > single file > doc file.**

## GitHub vs the rest

- **GitHub** (PRs, threads, issues) is always the **`gh` CLI** — never the GitHub MCP, never raw REST with a token. Assume `gh auth login` is done.
- **Local** targets are always `git` directly (`git diff`, `git merge-base`).
- A **raw web URL** (a doc or thread not on GitHub) is `WebFetch`.
- **Bitbucket / GitLab / other-forge** PR URLs are out of scope — refuse them (`rules.md`).

## When the classifier is wrong

If the picked sub-flow doesn't fit — a "PR URL" that 404s, a path that isn't a git repo, a doc that's actually code — say so in Phase 1 ("this looks like a working-tree review, not a PR; confirm or correct?") and proceed on the corrected route. Don't silently force a bad fit, and don't invent a diff you couldn't resolve.
