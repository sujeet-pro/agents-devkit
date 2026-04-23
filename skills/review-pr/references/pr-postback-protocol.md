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

## Post-confirmation (mandatory)

Posting is not "done" the moment the create-comment API returns 2xx. GitHub and Bitbucket can take several seconds to make a freshly-created comment visible on the PR's read API (eventual consistency, propagation lag, indexing). Every post run MUST end with a confirmation pass that re-fetches the PR and verifies each posted item shows up.

**Procedure (run after the Postback step, before declaring Phase 4 complete):**

1. **Capture the post receipt** — for every successful post call, record the provider-returned ID, the kind (`inline` / `task` / `reply` / `summary`), and (where the API returns it) the `html_url` / `links.html.href`. Store the set in `.temp/notes/review-pr-<provider>-<n>-post-receipt.json`.
2. **Wait, then re-fetch.** Sleep 5 seconds, then re-fetch the PR's full comment + task graph (the same API used in the Fetch context step). Do NOT use cached state from before the post.
3. **Match every receipt ID against the fetched data.** For each entry in the receipt set, confirm the same ID is present (and, where applicable, on the expected file:line / against the expected parent thread). Build a `confirmed` / `missing` table.
4. **Retry on miss.** If any entries are `missing`:
    - Wait 10 seconds, re-fetch, re-match.
    - If still missing, wait 20 seconds, re-fetch, re-match.
    - Total retry budget: 3 attempts (5s + 10s + 20s = 35s wall-clock).
5. **Final outcome.**
    - All confirmed → write `Post-confirmation: OK` into the validator log and the report's `## Postback summary` block.
    - Some still missing after the full retry budget → record each unconfirmed entry as `WARN` in the validator log AND in the report's `## Postback summary` block (with the receipt ID, kind, and `html_url` if available). Surface the suggestion to manually open the PR and confirm. Do NOT re-post — the API said 2xx; a duplicate post would create real duplicates if the comment is just lagged.

**Why we don't auto-re-post on a miss:** the most common cause of "I can't see my comment" is propagation lag on the read side, not a failed write. Re-posting would create real duplicates if the original comment lands a moment later. Surfacing the WARN is the safer default; the user can re-run the skill (which will reconcile via `pr-comment-reconciliation.md` and detect the duplicate) if they want to retry.

**Special case — 5xx / network drop on the original post call:** treat that as a failed post (not a confirmation miss). Use the `retry-remaining` flow above, NOT the post-confirmation retry budget.

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
- Post-confirmation: <OK after <retries> retry / WARN: <n> entries unconfirmed after 35s — see validator log>
- Unconfirmed (if any): <id> (<kind>) <html_url>
```
