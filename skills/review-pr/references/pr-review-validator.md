# PR Review Validator

The validator gate this skill MUST run before posting anything to the remote PR and again before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes.

## Phase 1: Pre-execution gate

Run before reading any code.

| Check | Pass criteria | If fail |
| --- | --- | --- |
| PR URL provided | Non-empty, parses as a github.com / GHE / bitbucket.org URL | BLOCKER — ask the user |
| Provider auth | `gh auth status` succeeds OR github MCP authenticated; bitbucket MCP authenticated OR `BITBUCKET_*` env vars present | BLOCKER — point at install instructions in `pr-mcp-fallback.md` |
| Network reachability | Can fetch the PR's metadata endpoint | BLOCKER — surface error verbatim |
| `--auto` validity | If `--auto` is set: no `--post-mode dry-run` override, no Approve verdict requested | BLOCKER — clarify the conflict |
| Diff size sanity | `<= 5000 changed lines` OR user explicitly approved a large-PR review | WARN — propose batching |

## Phase 2: Mid-flow gates (between workflow phases)

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `diff-fetched` | After Fetch context, before Read code | PR diff retrieved AND matches the PR URL the user gave | BLOCKER — re-fetch or stop |
| `code-read` | After Read code, before Run dimension passes | Every changed file read in its post-PR state; immediate dependencies surveyed | BLOCKER — finish reading |
| `reconciled` | After Reconcile, before Tier findings | Every existing comment / reply / task classified per `pr-comment-reconciliation.md` | BLOCKER — finish reconciliation |
| `findings-tiered` | After Tier findings, before Validate | Every finding has Severity, Type, Confidence, file:line, quoted evidence | BLOCKER — drop or fix the unbacked findings |

## Phase 3: Pre-post validation

Run immediately before the Postback phase. EVERY check must be `OK` (no BLOCKER, WARNs surfaced) before any comment is posted.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Findings reproducible from diff | Re-run the dimension-pass checks against the current diff snapshot; every finding still triggers | Hash of diff + per-finding match snippet |
| Comment shape compliance | Every drafted inline comment matches `pr-review-comment-format.md` template | Template-validation result per finding |
| Duplicate detection | No drafted comment duplicates an existing thread (per `pr-comment-reconciliation.md`) | Duplicate report (should be empty) |
| Task strategy declared | Every Blocker / Critical has a task action (create / keep / resolve / none) | Task-action map |
| Verdict honesty | Verdict matches the highest-severity finding (Blockers → request-changes; no Blockers → comment; only Praise → defer to user) | Verdict justification |
| Posting permissions | Auth identity has comment-write permission on the PR | `whoami` + permission probe |

## Phase 4: Post-execution validation

Run after Postback (or after the report in dry-run mode).

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| All approved findings posted | Postback summary count matches accepted-findings count | Provider-returned comment IDs |
| All reconciliation replies posted | Reply count matches reconciliation pipeline count | Provider-returned reply IDs |
| Summary comment posted (or N/A) | Summary present at the PR-level OR explicit dry-run mode | Provider-returned summary ID |
| Tasks reconciled (Bitbucket) | Task counts in postback summary match planned counts | Task IDs + states |
| Post-confirmation pass | After waiting 5s, every receipt ID re-appears in a fresh fetch of PR comments / replies / tasks. On miss, retry at 10s and 20s (3 attempts total, 35s budget). All receipts confirmed → OK. Any unconfirmed after the budget → WARN with the ID + html_url surfaced in the report. Per `pr-postback-protocol.md` "Post-confirmation". | Per-receipt match map (`confirmed` / `missing`), wall-clock spent, retry count |
| `.temp/reports/review-pr-<provider>-<n>.md` written | File exists, contains the full report | File path + size |
| No silent skips | Every finding flagged in Phase 3 has a posting outcome (posted / failed / dropped with reason) | Outcome table |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading code) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not post. Surface the failing check, fix it, re-run Phase 3 from the top.
- **Phase 4 partial failure**: Record what posted; offer `retry-remaining` per `pr-postback-protocol.md`. Never re-post a successful comment.
- **Phase 4 post-confirmation WARN**: Do NOT re-post the unconfirmed entries — the API said 2xx; a duplicate post would create real duplicates if propagation is just lagged. Surface the unconfirmed IDs in the report; the user can re-run the skill (which will reconcile via `pr-comment-reconciliation.md` and detect the duplicate) if they want to retry.

## Status banner

The validator sets the run's status banner (per `pr-reviewer-persona.md`):

- `REVIEW-DRAFT (dry-run)` — Phases 1-3 passed; Phase 4 N/A because dry-run.
- `AWAITING-APPROVAL-TO-POST` — Phases 1-3 passed; awaiting user approval before Postback.
- `REVIEW-POSTED <n inline> + <summary>` — Phase 4 OK.
- `REVIEW-RECONCILED <n existing> kept / <n> stale` — included whenever reconciliation found existing threads.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/review-pr-<provider>-<n>-validator.md` for audit. Format:

```
## Phase 1
- PR URL: OK (https://...)
- Provider auth: OK (gh, user=...)
- ...

## Phase 2
- diff-fetched: OK (sha=..., 12 files)
- code-read: OK (12/12 files)
- reconciled: OK (4 threads classified)
- findings-tiered: OK (8 findings)

## Phase 3
- Findings reproducible: OK (8/8)
- ...

## Phase 4
- Inline posted: 6 (IDs: ...)
- Post-confirmation: OK after 1 retry (5s), 6/6 receipts re-appeared
   | WARN: 1 unconfirmed after 35s — id=12345 kind=inline url=https://github.com/...#discussion_r12345
- ...
```
