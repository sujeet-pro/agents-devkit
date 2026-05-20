# workflow — adk-pr-reviews

Two scripts, two modes. The orchestrator is `scripts/run_batch.py`; the scan step is `scripts/scan_slack.py`.

## Modes

| Invocation | What happens |
|---|---|
| `/adk-pr-reviews` | Read queue.json5 → run reviews on every actionable entry. No slack scan. |
| `/adk-pr-reviews --scan` | First: refresh queue.json5 from slack (channels + replies, filtered). Then: run reviews on every actionable entry. |
| `/adk-pr-reviews --scan --dry-run` | Refresh queue but don't write; show what would change. |

Both modes honour `-p N` / `--parallelism N` for concurrent workers (default 1, cap 16).

## Pre-flight (both modes)

1. Resolve `queue.json5` path (positional, else `~/.agents-devkit/pr-reviews/queue.json5`).
2. Resolve `slack.json5` path (default `~/.agents-devkit/config/pr-reviews-slack.json5`).
3. Verify `claude` CLI on PATH (the batch spawns `claude -p` per non-skipped row).
4. Read both configs. Slack config is optional — missing means no reactions/reminders.

## Scan phase (--scan only)

`scan_slack.py` runs in a subprocess:

1. Resolve channel IDs from `channels[]` (cached after first resolution).
2. For each channel, read messages from the last `scan_days_default` days (or `--since N`).
3. For each message: extract URLs that match any `url_patterns[]` prefix.
4. If message has ≥1 PR URL:
   - Also pull thread replies (slack `conversations.replies`).
   - Collect every user mentioned in the main message + every reply + every replier.
5. **Filter** if `filter_mentioned_users` is set: keep the message ONLY if any configured user appears in the collected set.
6. **Extract supporting docs**: parse the same text + replies for Confluence / Jira / GDoc / Figma URLs.
7. **Cheap meta fetch** (`gh pr view --json`, BB REST) for each PR link found:
   - If `merged_at` is set:
     - If the message had exactly one PR link AND `status_emoji.merged != null` → react on slack with the merged emoji.
     - Drop the PR from the actionable set.
   - Otherwise: keep as a candidate.
8. **Merge** candidates with the existing `queue.json5`:
   - Dedupe by `(host, repo, pr_number)`.
   - Additive: union `supporting_docs[]`, preserve existing `slack` info (fill missing fields from scan), preserve user fields (`notes`), preserve user-set status.
   - Skip if existing status is `merged` (terminal).
9. Write back `queue.json5` (under fcntl lock).
10. Print summary: `{added, refreshed, skipped_merged}`.

## Review phase (both modes)

Concurrent up to `--parallelism N`. Per-row worker:

1. Try-acquire per-PR lock (`~/.agents-devkit/pr-reviews/<repo>_pr-<n>/.adk-pr-lock`). If held → skip with `status=skipped-locked`.
2. **Cheap meta fetch** (gh / bb) — `head_oid`, `merged_at`, `author`.
3. **Merged short-circuit**:
   - Update queue: `status=merged`, `last_checked_at=now`.
   - If `slack.n_pr_links_in_message == 1` AND `status_emoji.merged` set → add merged emoji.
   - Write `<task_dir>/state.json` with `merged=true, merged_at=…` (so `/adk-pr-review` agrees).
   - Done.
4. **Decision**:
   - `state.last_reviewed_head_oid != current head_oid` OR `state.re_review_required==true` → **REVIEW**.
   - Else → **SKIP-STABLE**.

### SKIP-STABLE path

- Bump `last_checked_at` on the queue entry.
- If `state.re_review_required==true` AND slack-link present AND `last_reviewed_at > reminder.after_hours` ago AND `last_reminder_at < min_hours_between_reminders` ago:
  - Resolve `tag_users` tokens (`author` → from PR meta, `thread_starter` → from slack info, literal `@name`/`U…` → resolve).
  - Format `message_template` with `{author}`, `{thread_starter}`, `{pending_findings}`, `{pr_link}`.
  - Post the reply via `chat.postMessage` with `thread_ts`.
  - Update queue: `status=reminded`, `slack.last_reminder_at=now`.

### REVIEW path

1. **Forced supporting docs**: write `<task_dir>/forced-supporting-docs.json` with the queue entry's `supporting_docs[]`. The `/adk-pr-review` orchestrator's `fetch_supporting_docs.py` reads this and merges with PR-body-found URLs.
2. Run `run_review.py <pr_url>` (env `ADK_PR_LOCK_HELD=1` since we already hold the lock) → worktree refresh + incremental re-index + precis.
3. Set status to `in_review`, react with `status_emoji.in_review` (if set).
4. Spawn `claude -p` headless with SKILL.md / precis.md / finding.template.json → `findings.json`.
5. Run `comment_resolver.py` + `post_comments.py --confirmed yes` + `report.py`.
6. Compute outcome:
   - `n_findings = len(findings.findings)`
   - `approved = (PR.reviewDecision == APPROVED) OR (findings.recommendation == approve)`
   - `re_review_required = n_findings > 0`
   - `new_status =`
     - `comments`  if `re_review_required`
     - `approved`  elif `approved`
     - `reviewed`  else (clean review, no host approval yet)
7. Persist:
   - Per-PR state.json: `last_reviewed_head_oid`, `last_reviewed_at_utc`, `approved_no_comments`, `re_review_required`, `last_n_findings`.
   - Queue entry: `status=new_status`, `last_checked_at=now`, `slack={…, last_reaction_status=new_status}`.
8. Update slack reaction: remove `last_reaction_status` emoji, add `new_status` emoji.

## Concurrency model

Three locks:

| Lock | Held by | Held for |
|---|---|---|
| Per-PR lock | run_batch.process_entry → try_file_lock | full duration of one PR's review |
| Per-repo clone-lock | run_review's ensure_repo_clone + create_worktree | seconds (git fetch + worktree-add) |
| Queue write-lock | queue_io.update_pr_entry | milliseconds (single-row update) |

5–6 reviews of the same repo: brief contention on the clone-lock, otherwise concurrent.
Different repos: no contention at all.

## State files

Per-PR (canonical for review status — `<task_dir>/state.json`):

```json
{
  "phases": { ... },
  "last_reviewed_head_oid": "abc123...",
  "last_reviewed_at_utc": "2026-05-20T14:00:00Z",
  "approved_no_comments": false,
  "re_review_required": true,
  "last_n_findings": 3,
  "merged": false
}
```

Queue (UX hint + slack bookkeeping — `~/.agents-devkit/pr-reviews/queue.json5`):

```json5
{
  pr_link: "...",
  status: "comments",
  last_checked_at: "2026-05-20T14:00:00Z",
  slack: { ..., last_reaction_status: "comments", last_reminder_at: null },
  supporting_docs: [ ... ],
  notes: "...",
}
```

Source of truth for re-review decisions is the **state.json**; queue.json5 is for slack-side bookkeeping + user-friendly status display.

## Failure handling

- Cheap meta failure → row marked `status=error`, with the message in `notes`. Batch continues.
- `claude -p` non-zero / malformed JSON → row marked `status=error`. Batch continues.
- Slack API failure on a single reaction → logged, row continues; reaction will retry on next status transition.
- Slack API rate-limit → automatic retry per `slack_sdk` (we sleep on Retry-After).
- Per-PR lock held → row marked `status=skipped-locked` with note.

A row that errors stays at `error` status on the queue. The next batch invocation retries it (cheap meta first).

## Cron example

```cron
0 */2 * * * cd <ADK_REPO> && python3 skills/adk-pr-reviews/scripts/run_batch.py \
  --scan -p 3 \
  >> ~/.agents-devkit/pr-reviews/queue.log 2>&1
```

Every two hours: refresh queue from slack, run reviews on actionable rows, log everything.

The job naturally drains as PRs merge: scan drops merged ones from the actionable set, batch only re-touches rows whose head_oid changed or have open findings older than `reminder.after_hours`.
