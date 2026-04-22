# PR Postback Protocol

How and when to post draft findings back to the remote PR. The default is dry-run; posting requires explicit approval (or `--auto`). Posting is the LAST step of the workflow, never the first action a finding takes.

## Modes

| Mode | What posts | When to use |
| --- | --- | --- |
| `dry-run` (default) | Nothing is posted; the report is shown to the user | First-pass review; user wants to inspect findings before they hit the PR |
| `post` | All approved findings + summary comment + (Bitbucket) tasks | After the user accepts findings, or after `--auto` validates them |
| `--auto` | All validated, non-duplicate findings + summary comment + tasks, with no approval gate | Trusted batch reruns; CI-style usage |

## Pre-post gate

Before posting ANY comment to the remote PR, ALL of these must pass (per `pr-review-validator.md`):

- PR diff fetched and matches the URL provided.
- Code read in current state (post-PR), not from cache or memory.
- Reconciliation pass per `pr-comment-reconciliation.md` complete; duplicates removed.
- Every finding to be posted has evidence (file:line + quoted snippet).
- Every finding to be posted is rendered with the `pr-review-comment-format.md` shape.
- For Bitbucket: task strategy decided per finding (create / keep / resolve / none).

If any check fails: STOP, surface what's missing, ask the user (or, under `--auto`, fix the gap and re-run the gate).

## Posting order

Post in this order so the PR thread reads left-to-right correctly:

1. Inline comments — one per finding, anchored to the precise line range from the PR diff.
2. (Bitbucket) tasks — created against their linked inline comments.
3. Reconciliation replies — on existing threads, in thread-creation order.
4. Summary comment — posted last so it reflects the actual state after step 1-3.

## One finding = one inline comment

Never staple multiple findings into one inline comment. If two findings share a location, consolidate them per `pr-review-comment-format.md` consolidation rules into a single F-ID and post one inline comment that lists both sub-issues.

## Summary comment

The summary comment is the verdict + counts + Blockers/Critical lists. It MUST follow the shape in `pr-review-comment-format.md` (`## Review summary` section).

Rules:

- Lists Blockers + Critical only by name; everything else as counts.
- Always closes with the validation block (diff fetched, code read, reconciliation done, posted counts).
- Never repeats inline-comment text.

## Verdict rules

The summary's `Verdict` line drives provider state:

| Verdict | When | Provider action |
| --- | --- | --- |
| `request-changes` | At least one Blocker, OR multiple Criticals OR a single Critical that materially blocks the PR | GitHub: `--request-changes`; Bitbucket: do NOT mark as needing work without explicit user approval (Bitbucket conventions vary) |
| `comment` | No Blockers; one or more Should Have / May Have / Nitpick / Question | GitHub: `--comment`; Bitbucket: post as comment, no approval-state change |
| `approve` | No findings worth posting, OR only `Praise` | NEVER auto-set this. Show the report and ask the user to approve the PR manually. |

NEVER auto-approve. NEVER auto-merge. Even with `--auto`, the verdict stops at posting comments and (where applicable) creating tasks; the actual `Approve` button is always a human action.

## Provider mapping

### GitHub

- Inline: `gh pr review <n> --comment --body-file <path>` per file:line, OR github MCP `pull_request_comments_create`.
- Summary: `gh pr review <n> --request-changes --body-file <summary>` OR `--comment`.
- No task concept; use checklists in the summary body if blockers are needed.

### Bitbucket

- Inline: bitbucket MCP `pull-request-comment-create` with `inline.path` + `inline.from`/`inline.to`.
- Tasks: bitbucket MCP `pull-request-task-create` linked to the inline comment ID.
- Summary: bitbucket MCP `pull-request-comment-create` (no inline anchor).
- Bitbucket comments do NOT support nested admonitions; keep Markdown to bold + headers + lists + fenced code.

## Re-posting safety

If the post step fails partway through (network, rate limit, permission), record what was successfully posted in the report, then offer:

- `retry-remaining` — re-post only the items that failed.
- `dry-run` — switch back to dry-run mode and show what's left.
- NEVER duplicate a successfully-posted comment.

Track posted comments by their provider-returned IDs in the in-session state so retries are idempotent.

## After posting

The report MUST end with:

```
## Postback summary
- Inline comments posted: <n> (IDs: <list or omitted>)
- Tasks created: <n>  (Bitbucket only)
- Tasks resolved: <n>  (Bitbucket only)
- Tasks reopened: <n>  (Bitbucket only)
- Reconciliation replies posted: <n>
- Summary comment posted: <YES | N/A>
- Verdict: <approve | request-changes | comment>
- Failed to post (with reason): <list or none>
```
