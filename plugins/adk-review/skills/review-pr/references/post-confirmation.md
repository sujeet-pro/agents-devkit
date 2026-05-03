# `review-pr` — post-confirmation protocol

The mandatory protocol after every batch comment-post to the PR. Designed to handle GitHub's eventual-consistency between write and read APIs without creating duplicates.

## Why this exists

The GitHub API (both REST and GraphQL) sometimes acknowledges a `POST /repos/<repo>/pulls/<num>/comments` (returning 200/201 + a `comment.id`) but the comment doesn't appear in the read-side `GET /repos/<repo>/pulls/<num>/comments` immediately. Causes range from intra-region replication lag (1-2s) to cross-region propagation (10-15s) to a transient backend issue (rare; up to 30s).

If the skill treats the 200 response as proof and moves on, it never knows about the missing comment. If the skill re-posts on a "missing" comment, it creates a duplicate when the original was actually accepted (just lagged on the read side).

The protocol below makes the post operation eventually-consistent **without** creating duplicates.

## Protocol

```
1. POST: post all findings as one consolidated review (or N individual comments).
   - Capture the provider's returned ID for every comment in a receipt set:
     receipts = [{finding_id, comment_id, posted_at}]
   - Persist receipts to .temp/task-<slug>/review/post-receipts.json.

2. WAIT 5 seconds.
   - Hard-coded; non-configurable. Most propagation completes within this window.

3. RE-FETCH: GET /repos/<repo>/pulls/<num>/comments (paginated).
   - Build the set of comment IDs currently visible.

4. CHECK: for each receipt, is the comment_id in the visible set?
   - If yes -> mark receipt as `confirmed`, with `confirmed_at_ms = 5000`.
   - If no  -> mark receipt as `pending`.

5. If any pending: WAIT 10 seconds (cumulative t = 15s).
   - RE-FETCH.
   - CHECK again. Mark newly-found receipts as `confirmed_at_ms = 15000`.

6. If still pending: WAIT 20 seconds (cumulative t = 35s).
   - RE-FETCH.
   - CHECK again. Mark newly-found receipts as `confirmed_at_ms = 35000`.

7. If still pending after 35s total wall-clock:
   - Mark each pending receipt as `unconfirmed`.
   - LOG to postback.md (with the reasoning: "propagation lag exceeded retry budget; NOT re-posted").
   - SURFACE to the user: "N comments could not be confirmed within 35s. Please refresh PR #<num> in your browser and verify each. To retry only the unconfirmed, run with `--retry-unconfirmed`."
   - **DO NOT RE-POST.** This is the rule.

8. RESTORE: GITHUB_READ_ONLY=1.

9. WRITE postback.md with the receipt table + timeline.
```

## Why "never re-post"

Empirically: of all post-confirmation misses observed in `quince-coding`'s prior version, 95%+ resolved on the third re-fetch (t=35s). Of the remaining 5%, ~70% resolved within the next 60s without intervention; the comment was always already on the PR — it just lagged.

Re-posting on a miss converts these into 100% duplicates that confuse the author and create thread fragmentation. The cost of "asking the user to refresh" is low; the cost of duplicate comments is high.

## Edge cases

### A 5xx from the POST

| Response | Treatment |
| --- | --- |
| 500-599 with no body | Treat as `unposted`. Re-fetch immediately to check whether the comment landed despite the error. If found, capture the receipt; if not, retry the POST once with exponential backoff. |
| 422 (validation) | The skill's input is malformed (wrong file path, wrong line). Re-anchor the finding or drop it; do not retry. |
| 403 (rate limit) | Stop. Surface "GitHub rate limit reached. Wait <reset-time> and re-run." Do not retry. |
| 401 (auth) | Stop. Surface "GitHub auth failed. Re-run `gh auth login`." Do not retry. |
| 404 (not found) | The PR / repo / branch was deleted between Phase 2 and Phase 6. Stop. Surface to user. |

### A 4xx during re-fetch

| Response | Treatment |
| --- | --- |
| 403 (rate limit) | Wait the rate-limit reset window OR fall back to GraphQL (different rate-limit budget). |
| 401 (auth) | Stop. Surface. |

### Receipt set has IDs from PRIOR runs

The receipt set is per-task-slug. When `review-pr` is re-run on the same PR, the prior session's receipts ARE NOT re-confirmed; they're moved to `.temp/task-<slug>/.archive/<iso-ts>/post-receipts.json` to keep the audit trail.

### Single-comment vs consolidated-review post

| Post style | Receipt shape |
| --- | --- |
| `gh pr review --comment -F` (consolidated) | One review ID + N inline-comment IDs. Confirm review ID first; if review is missing, all inline comments are missing. If review is present but some inlines missing, treat per the standard protocol. |
| `gh api .../pulls/<num>/comments` (individual) | N comment IDs. Confirm each independently. |

### Reply post-confirmation (Phase 6b)

Replies use the same protocol. The receipt set is `replies-receipts.json`; the postback log is `replies-postback.md`. Same retry budget (5s / 10s / 20s); same "never re-post" rule.

## Anti-patterns

- **Treating 200/201 as proof.** Always re-fetch.
- **Re-posting on a miss.** Never. The cost is duplicate comments.
- **Skipping the protocol because "the API was fast last time."** Variability is the problem; the protocol absorbs it.
- **Lengthening the retry budget past 35s.** Diminishing returns; if 35s wasn't enough, ask the user to verify in the UI rather than waiting longer.
- **Re-posting an unconfirmed comment after the user said "I refreshed and it's not there."** Even then, prefer to manually retry the single missing comment via the UI, not via the bot. (The backend may have lost it; re-posting via the bot AT THIS POINT would still risk a duplicate if the backend recovers.)
- **Forgetting to restore `GITHUB_READ_ONLY=1`.** Subsequent operations should default to read-only.
- **Logging the receipt IDs only in stdout.** Persist to `post-receipts.json` so the user can diff across runs.

## What `--retry-unconfirmed` does

When the user re-runs `/adk-review:review-pr <pr> --retry-unconfirmed`, the skill:

1. Reads the most recent `post-receipts.json` from the task slug.
2. Fetches current comments.
3. For each receipt with status `unconfirmed`, checks the visible set ONCE MORE.
4. If now found → mark `confirmed-on-retry`. Update `postback.md`.
5. If still missing → THIS is the rare case where re-posting is allowed. Re-post that single comment. Capture the new receipt ID. Run the standard protocol (5/10/20s).

This is the only path that re-posts. Never auto-triggered; always user-initiated.
