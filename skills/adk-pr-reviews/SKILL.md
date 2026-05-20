---
name: adk-pr-reviews
description: |
  Batch driver over /adk-pr-review with optional slack scanning + reactions + reminders. Reads a JSON5 queue at `~/.agents-devkit/pr-reviews/queue.json5`; per-row entry has `pr_link` (required) + optional `slack` info + optional `supporting_docs[]` + auto `status`. Two modes: (default) read queue and run reviews; (--scan) first refresh the queue by scanning slack channels per `~/.agents-devkit/config/pr-reviews-slack.json5` (channels, url_patterns, filter_mentioned_users, status_emoji, reminder policy), then run reviews. Per non-skipped row: cheap meta-fetch → if merged → status=merged + react with merged emoji (only when message has one PR link) → drop; else compare head_oid vs prior review → skip-stable or run full /adk-pr-review pipeline → update slack reaction per status_emoji. Skip-stable rows whose findings are still open AND were last reviewed > N hours ago get a slack thread reminder tagging the PR author + thread starter. Parallel-safe via per-repo clone-lock + per-PR lock; -p N controls parallelism (default 1, cap 16). Designed for cron / periodic execution.
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "[<queue-path>] [--scan] [-p N | --parallelism N] [--dry-run] [--max-rows M] [--since <days>] [--slack-config <path>]"
metadata:
  category: code
  kind: task
  layer: 2
  paths: ["**/*.json5"]
  model: opus
  effort: high
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-github, adk-mcp-bitbucket, adk-mcp-atlassian, adk-mcp-statsig, adk-mcp-slack, adk-mcp-rag]
  needs_meta_info: [workspaces, repos]
  needs_cli: [git, ollama, gh, claude]
  needs_cli_optional: [scip-typescript, scip-python, scip-go, scip-java]
  forks_emitted: [parallelism, skip-policy, on-error-policy, scan-since-days]
---

# adk-pr-reviews — batch driver over /adk-pr-review

Wraps `/adk-pr-review` for a queue of PRs. JSON5 queue. Optional slack integration (channels scan, status reactions, comment reminders). Default mode is **auto** — no questions; `-i` for interactive. Narrates per `shared/narration.md`.

## Two configs

| File | Default location | Read by |
|---|---|---|
| `queue.json5` | `~/.agents-devkit/pr-reviews/queue.json5` | scan_slack + run_batch |
| `pr-reviews-slack.json5` | `~/.agents-devkit/config/pr-reviews-slack.json5` | scan_slack (channels, filters) + run_batch (status_emoji, reminder policy) |

Both are JSON5 (allows comments + trailing commas). Schema details:

- `references/queue-format.md`
- `references/slack-config.md`

## Inputs

- **`queue-path`** (positional, optional). Default: `~/.agents-devkit/pr-reviews/queue.json5`.
- **`-p N` (or `--parallelism N`)** (default 1, cap 16). Concurrent workers.
- **`--scan`**: refresh the queue from slack before running reviews. Reads `pr-reviews-slack.json5`.
- **`--since N`** (with `--scan`): override the slack-config's `scan_days_default`.
- **`--slack-config <path>`**: override the slack config path.
- **`--dry-run`**: walk + print plan; no reviews, no slack writes, no PR posts.
- **`--max-rows M`**: cap actionable rows.

## Decision per row (per-PR)

```
read entry from queue.json5 (pr_link, slack, supporting_docs, status, ...)
if status == "merged":                          skip (terminal)
acquire per-PR lock (fail fast)
cheap meta-fetch (gh / bb)
if pr.merged_at:
    status = "merged"
    if slack.n_pr_links_in_message == 1 AND status_emoji.merged != null:
        slack-react with merged emoji
    next
read state.json (canonical review state)
if state.last_reviewed_head_oid == current head_oid AND NOT state.re_review_required:
    bump last_checked_at
    if state.re_review_required AND slack.thread_ts AND last_reviewed > reminder.after_hours:
        post thread reminder tagging author + thread_starter (rate-limited per reminder.min_hours_between_reminders)
        status = "reminded"
    next
# OTHERWISE — run the review
write <task_dir>/forced-supporting-docs.json from entry.supporting_docs[]
run scripts/run_review.py <pr_link>         # worktree refresh + incremental reindex + precis
status = "in_review"; slack-react with in_review emoji
spawn `claude -p` headless against SKILL.md + precis.md → findings.json
run scripts/comment_resolver.py
run scripts/post_comments.py --confirmed yes # constitution §I.4 gate (the user's invocation is the confirmation)
run scripts/report.py
n_findings = len(findings.findings)
approved   = (PR.reviewDecision == "APPROVED") OR (findings.recommendation == "approve")
new_status = ("comments"  if n_findings > 0
              else "approved" if approved
              else "reviewed")
slack-react with new_status emoji
  # normal transition: remove previous emoji, add new
  # transition into `approved` or `merged`: SWEEP every other configured status emoji
  #   (so a stale `comments` / `in_review` doesn't sit alongside the final one)
update queue entry + state.json
```

## Slack reactions

The slack config maps status → emoji (or `null` to suppress).

**Normal transition** (e.g. `in_review` → `comments`):
1. Removes the previously-reacted emoji (tracked in `slack.last_reaction_status`).
2. Adds the new emoji.

**Terminal-positive transition** (`* → approved` or `* → merged`):
1. Sweeps **every** configured status emoji off the message (defensive — in case a prior reaction wasn't tracked, or the user manually reacted with an old emoji).
2. Adds the final emoji.

Result: once a PR is approved or merged, only the `:approved:` / `:merged:` (or whatever you mapped) remains. The `:warning:` / `:eyes:` / `:changes-requested:` from earlier states are gone.

**Reactions are skipped** when the original slack message contained more than one PR link (`n_pr_links_in_message > 1`) — a reaction can't be unambiguously attributed. Reminders still work because they name the specific PR in the reply text.

### Status taxonomy

| Status | Meaning | Trigger |
|---|---|---|
| `pending` | newly added, not yet reviewed | scan or hand-add |
| `in_review` | review currently running | start of REVIEW path |
| `comments` | review completed with open findings | findings > 0 |
| `reviewed` | review completed with no findings; no host approval yet | findings == 0, not approved |
| `approved` | host APPROVED OR `recommendation:approve`, no open findings | findings == 0, approved |
| `merged` | PR merged on host (terminal — never downgrades) | `merged_at` set |
| `error` | last attempt failed; retried next batch | exception in worker |
| `reminded` | last action was a slack thread reminder | skip-stable + reminder posted |

`needs_fix` is an alias of `comments` (legacy name; still recognised by the script for back-compat).

## Reminders

When a PR has been reviewed but findings remain open, and 24+ hours pass (configurable), and the PR has a slack thread, the script posts a reply tagging the PR author + the slack thread starter (configurable):

```
PR review pending — please address the 3 open comments above. cc <@U_AUTHOR> <@U_THREAD_STARTER>
```

Rate-limited per PR (`reminder.min_hours_between_reminders`, default 24h).

## Generating the queue from slack (`--scan`)

`scan_slack.py` reads channels → messages → replies → extracts PR URLs → applies the `filter_mentioned_users` filter → cheap-meta-checks each candidate. Merged PRs get the merged emoji on the slack thread (if single-PR-message) and are dropped from the actionable set. Non-merged PRs are merged into `queue.json5` (additive — preserves your hand-set fields).

Run `--scan` alone (no review) by passing `--dry-run`:

```
/adk-pr-reviews --scan --dry-run --since 14
```

Or scan-then-review:

```
/adk-pr-reviews --scan -p 3
```

Run review-only (no scan):

```
/adk-pr-reviews -p 3
```

## Parallel-safety

| Lock | Scope |
|---|---|
| Per-PR lock | Full review duration. Same PR in two tabs / two workers → second one fails fast. |
| Per-repo clone-lock | Brief — `git fetch` + `git worktree add`. Different repos don't contend. |
| Queue write-lock | Milliseconds — single-row JSON5 update. |

5–6 reviews of the same repo across tabs: brief contention on clone-lock, otherwise concurrent.

## What gets persisted

Per-PR (canonical — `<task_dir>/state.json`):

```json
{ "last_reviewed_head_oid": "abc…", "last_reviewed_at_utc": "...",
  "approved_no_comments": false, "re_review_required": true,
  "last_n_findings": 3, "merged": false }
```

Queue (slack-side bookkeeping + UX hint — `~/.agents-devkit/pr-reviews/queue.json5`):

```json5
{
  pr_link: "...",
  slack: { permalink, channel_id, message_ts, thread_ts, thread_starter_user_id,
           n_pr_links_in_message, last_reaction_status, last_reminder_at },
  supporting_docs: [...],
  status: "comments",     // pending | in_review | reviewed | comments | approved | merged | error | reminded
  last_checked_at: "...",
  notes: "user-owned",
}
```

## Posting policy (constitution §I.4)

Every shared-state mutation (PR comments, slack reactions, slack reminder messages) is gated on per-invocation confirmation. The user's invocation of `/adk-pr-reviews` IS that confirmation — the skill surfaces the plan before starting:

> About to scan slack channels and review N PRs. Will post inline comments + apply reactions/reminders per slack.json5. OK to proceed?

Under `--dry-run`: NO writes anywhere (no PR posts, no slack reactions, no slack reminders, no queue rewrite).

## References (loaded as needed)

| Aspect | File |
|---|---|
| Workflow (scan + review + reminders) | `references/workflow.md` |
| Queue JSON5 format | `references/queue-format.md` |
| Slack config format | `references/slack-config.md` |
| Hard rules + refusals | `references/rules.md` |

## Cross-skill dependencies

- Wraps `/adk-pr-review` — all of that skill's hard rules apply per row.
- Constitution: `shared/constitution.md` (§I.4 posting gate, §VI.1 host scope, §VII secrets).
- Paths: `shared/paths.md`.
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`.

## Notes for the maintainer

- The batch spawns one `claude -p` per non-skipped row — each is a billed API call on Opus.
- Slack rate limits apply; the script retries with `Retry-After`.
- A future companion (`/adk-pr-list-fetch`) could auto-populate via Bitbucket project-list / GH search APIs — currently slack is the only source.
- Cron example:
  ```
  0 */2 * * * cd <ADK_REPO> && python3 skills/adk-pr-reviews/scripts/run_batch.py \
    --scan -p 3 \
    >> ~/.agents-devkit/pr-reviews/queue.log 2>&1
  ```
