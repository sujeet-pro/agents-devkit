# `review-pr` — output format

## Per-turn status (each turn opens with this)

```
[adk-review:review-pr] task=<slug> pr=<repo>#<num> ownership=<own|peer> phase=<0|1|2|3|4|5|6|7> mode=<auto|interactive>[+fix] mcp=<github-docker|gh-cli> findings=B<n>/C<n>/S<n>/M<n>/N<n>/Q<n>
```

Severity counters use the canonical letters: **B**locker / **C**ritical / **S**hould-have / **M**ay-have / **N**itpick / **Q**uestion.

## Final report

Written to `.temp/task-<slug>/report.md`:

```markdown
# review-pr report — <slug>

## Result
<one sentence — what was delivered: posted N findings to PR <repo>#<num>; pushed M fix commits; re-fetch confirmed K/N IDs.>

## PR snapshot
- Repo: <owner>/<repo>
- PR: #<num> — <title>
- Author: <login> (ownership: <own|peer>)
- Base: <base-ref> @ <base-sha>
- Head: <head-ref> @ <head-sha>
- Files changed: +<add>/-<del> across <n> files
- Status checks: <green|yellow|red> (links)

## Findings posted
| Severity | File | Issue | Comment URL | Confirmed |
| --- | --- | --- | --- | --- |
| Blocker | routes/admin.go:42 | Missing role check | <url> | yes (5s) |
| Critical | db/orders.go:117 | n+1 in loop | <url> | yes (10s) |
| Should-Have | tests/admin_test.go:- | No test for new endpoint | <url> | yes (5s) |
| Should-Have | tests/db_test.go:- | No test for n+1 path | <url> | yes (5s) |
| Nitpick | CHANGELOG.md:- | Not updated | <url> | yes (5s) |

## Findings NOT posted
<empty in the all-confirmed case; otherwise lists each unconfirmed / dropped / out-of-diff / re-tiered finding with one-line reason>

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | mcp client | gh-cli | both available; gh has faster cold start |
| 0 | ownership | peer | author=alice, local=sujeet |
| 3 | dimensions run | all six | default; review.md doesn't override |
| 4 | dedupe count | 5 dropped | 5 of 12 existing comments overlapped our drafts |
| 5 | post-mode | one consolidated review | preferred over 5 individual comments |
| 6a | post-confirmation IDs | 5/5 confirmed | 4 at 5s, 1 at 10s |

## Existing-comment reconciliation
| Existing comment | Classification | Treatment |
| --- | --- | --- |
| @bob "extract helper" (line 88) | pushback | author replied disagreeing; we don't re-raise |
| @carol "missing test" (line 117) | resolved-stale | issue still in code at line 117; flagged in our findings |
| @dan "typo in docstring" (line 12) | resolved-confirmed | verified addressed |
| ... (truncated) | | |

## --fix log (when --fix was set)
| Finding | Commit SHA | Validation | Reply posted |
| --- | --- | --- | --- |
| Blocker | a1b2c3d | go test ./... PASS | <reply-url> |
| Critical | b2c3d4e | go test ./... PASS, golangci-lint PASS | <reply-url> |
| ... | | | |

## Validation evidence
- Local worktree: `.temp/task-<slug>/review-checkout/` (head=<sha>)
- MCP health: <github-docker|gh-cli> reachable
- Tests: <command> PASS / FAIL (link to log)
- Lint: <command> PASS / FAIL
- Branch protection: <base-ref> required-checks=<list>; force-push allowed=<bool>

## Residual risk / follow-ups
<bulleted list, prioritized>
- The Critical n+1 fix introduces a new query plan; watch DD `db.query.duration` over the next 24h.
- The new admin endpoint has unit-test coverage; integration test for the role check is a recommended follow-up (not Blocker).

## Artifact index
.temp/task-<slug>/
  prompt.txt           verbatim user prompt + ISO timestamp
  pr-context/          fetched PR metadata, diff, comments, history
  review/
    raw-findings.md    pre-reconciliation findings (per-dimension)
    findings.md        post-reconciliation, severity-sorted
    reconciliation.md  per-existing-comment classification table
    postback.md        per-finding receipt + confirmation timing
    replies-draft.md   (own-PR path only) draft replies
    fix-log.md         (--fix only) per-fix commit + validation
  validation/
    per-skill/review-pr.md
  report.md            this file
```

## `findings.md` shape

Each finding is a card. Severity-sorted; within a tier, dimension-grouped if 5+ findings of one tier.

```markdown
## Blocker

### [Blocker] Missing role check on new admin endpoint
- File: routes/admin.go:42-58
- Dimension: security
- Confidence: high
- Evidence:
  ```
  router.POST("/admin/users/delete", adminHandler.DeleteUser)
  ```
- Issue: the new route is registered in the admin group but the handler doesn't call `RequireRole("admin")` like the other admin handlers in this file.
- Fix: add `c.Use(middleware.RequireRole("admin"))` to the handler, or move the route to a sub-group already wrapped with the role middleware.
- Impact if unfixed: any authenticated user can delete any other user.
- References: see admin handler pattern at `routes/admin.go:18-31` for the existing convention.

## Critical

### [Critical] N+1 query in checkout-summary handler
- File: db/orders.go:117-129
- Dimension: performance
- Confidence: high
- Evidence:
  ```
  for _, order := range orders { db.Find(&order.Items) }
  ```
- Issue: per-iteration `Find` against `order_items` runs 1 query per order; the wrapping handler iterates over up to 1000 orders for the dashboard view.
- Fix: pre-load with `Preload("Items")` on the initial `orders` query.
- Impact if unfixed: dashboard p99 will scale linearly with the order count; observed in pre-prod canary at 800ms p99 with 200 orders.
- References: similar pattern fixed in `db/users.go:88` last quarter.
```

## `postback.md` shape

```markdown
# Postback log

## Posted
| Finding ID | File:line | Severity | Comment URL | Receipt ID | Confirmed at |
| --- | --- | --- | --- | --- | --- |
| f-001 | routes/admin.go:42 | Blocker | https://github.com/acme/checkout-api/pull/2841#discussion_r1234 | 1234 | 5s |
| f-002 | db/orders.go:117 | Critical | https://github.com/acme/checkout-api/pull/2841#discussion_r1235 | 1235 | 10s |
| ... | | | | | |

## NOT posted
| Finding ID | Reason |
| --- | --- |
| f-007 | duplicate of @bob's existing comment at line 88 |
| f-008 | line shifted between Phase 3 and Phase 6; re-anchor failed |

## Post-confirmation timeline
- t=0s   : posted 5 comments via `gh pr review --comment -F`.
- t=5s   : re-fetch → 4/5 receipt IDs found. Missing: 1235.
- t=10s  : re-fetch → 5/5 found (confirmed).
- t=15s  : restored GITHUB_READ_ONLY=1.

## Skipped
- f-009 | discarded by user under -i mode | reason: false positive on closer read
```

## `reconciliation.md` shape

```markdown
# Existing-comment reconciliation

## Summary
- Total existing items walked: 12 (8 inline comments + 3 issue-comments + 1 review)
- still-open: 5
- resolved-confirmed: 3
- resolved-stale: 1
- pushback: 1
- clarify: 2

## Per-comment table
| Comment URL | Author | Created | Classification | Treatment |
| --- | --- | --- | --- | --- |
| <url> | @bob | 2026-04-30 | pushback | not re-raised; @bob's reasoning held up on re-read |
| <url> | @carol | 2026-04-29 | resolved-stale | flagged as Should-Have in findings |
| <url> | @dan | 2026-04-28 | resolved-confirmed | verified addressed at routes/admin.go:42 |
| ... | | | | |
```

## `replies-draft.md` shape (own-PR path only)

```markdown
# Reply drafts

## Reply to @bob (line 88, "extract helper")
- Classification: pushback (we initially disagreed; on re-read, @bob is right)
- Template: fix-applied
- Draft:
  > Good call. Extracted in <commit-sha>. Renamed `processOrder` → `processOrderItem` to clarify the per-item scope.

## Reply to @carol (line 117, "missing test")
- Classification: still-open
- Template: fix-applied
- Draft:
  > Added test at `db/orders_test.go:42-58` (commit <sha>) covering the n+1 path with 100 orders.

## Reply to @dan (line 88, "is this thread-safe?")
- Classification: clarify
- Template: clarification
- Draft:
  > Yes — the surrounding `orderMu.Lock()` (line 102) covers this block. Added a comment at line 117 to make it obvious.
```

## `fix-log.md` shape (--fix only)

```markdown
# Fix log

## f-001 [Blocker] Missing role check
- Commit: a1b2c3d
- Files: routes/admin.go (+3/-0), routes/admin_test.go (+24/-0)
- Validation:
  - `go test ./routes/...` PASS (4/4)
  - `golangci-lint run ./routes/...` PASS (0 issues)
- Reply posted: <url>
- Comment resolved: yes (after reply post-confirmation)

## f-002 [Critical] N+1 query
- Commit: b2c3d4e
- Files: db/orders.go (+1/-1), db/orders_test.go (+30/-0)
- Validation:
  - `go test ./db/...` PASS (12/12)
  - Local benchmark: BenchmarkCheckoutSummary 200 → from 820ms to 47ms.
- Reply posted: <url>
- Comment resolved: yes
```
