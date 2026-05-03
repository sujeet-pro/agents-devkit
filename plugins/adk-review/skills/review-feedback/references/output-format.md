# `review-feedback` — output format

## Per-turn status (each turn opens with this)

```
[adk-review:review-feedback] task=<slug> pr=<repo>#<num> phase=<0|1|2|3|4|5|6> mode=<auto|interactive>[+fix] mcp=<github-docker|gh-cli> classifications=A<n>/M<n>/D<n>/W<n>/R<n>
```

Classification counters: **A**pply-as-stated / **M**odify / **D**iscuss / **W**ont-fix / **R**esolved-already.

## Final report

Written to `.temp/task-<slug>/report.md`:

```markdown
# review-feedback report — <slug>

## Result
<one sentence on what was delivered>

## PR snapshot
- Repo: <owner>/<repo>
- PR: #<num> — <title>
- Author: <login>
- Head SHA: <sha>

## Classification summary
| Class | Count | Action |
| --- | --- | --- |
| apply-as-stated | 4 | Applied + replied + resolved |
| apply-with-modification | 1 | Applied (with mod) + replied + resolved |
| discuss-not-fix | 1 | Replied (with discussion link); thread left open |
| wont-fix | 0 | — |
| already-resolved | 0 | — |

## Per-comment table
| Comment URL | Class | Action | Commit SHA | Reply URL | Resolved |
| --- | --- | --- | --- | --- | --- |
| <url> | apply-as-stated | applied | abc1234 | <reply-url> | yes |
| <url> | apply-with-modification | applied | ghi9012 | <reply-url> | yes |
| <url> | discuss-not-fix | replied | n/a | <reply-url> | no (by design) |
| ... | | | | | |

## --fix log
| Logical fix | Comments addressed | Commit | Validation | Push |
| --- | --- | --- | --- | --- |
| Fix 1: admin role check + test | #1 + #5 | abc1234, def5678 | go test ./routes/... PASS | yes |
| Fix 2: rename processOrder | #2 | ghi9012 | go build PASS, lint PASS | yes |
| Fix 3: n+1 query | #3 | jkl3456 | go test ./db/... PASS | yes |
| Fix 4: typo | #4 | mno7890 | go build PASS | yes |

## Validation evidence
- Local checkout: <path> (branch: <head>, dirty: no after fixes committed)
- Tests: go test ./... PASS (link to log)
- Typecheck / lint: PASS

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | mcp client | gh-cli | both available; gh has faster cold start |
| 3 | grouping | 1 grouped, 4 individual | comments 1+5 share root cause |
| 5c | push | approved by user at gate | first push of session |
| 5d | resolve apply-* threads | yes | post-confirmation passed |
| 5d | resolve discuss-not-fix #6 | NO (by design) | reviewer accepts/counters |

## Threads left open
| Comment URL | Class | Reason |
| --- | --- | --- |
| <url> | discuss-not-fix | Linked Jira ticket CHK-1340; sync with @reviewer at next platform standup |

## Residual risk / follow-ups
<bulleted list, prioritized>
- Comment #6 (discuss): tracking at https://acme.atlassian.net/browse/CHK-1340. Suggested DM to @reviewer-name.
- Fix 3 (n+1) introduces a new query plan; watch DD `db.query.duration` over the next 24h.

## Artifact index
.temp/task-<slug>/
  prompt.txt                      verbatim user prompt + ISO ts
  feedback/
    pr-context/                   fetched PR + comments + reviews + threads
    classification.md             per-comment classification table
    replies-draft.md              drafted replies (with SHA placeholders)
    replies-postback.md           per-reply receipt + confirmation timing
    fix-log.md                    (--fix only) per-fix commit + validation
  validation/
    per-skill/review-feedback.md
  report.md                       this file
```

## `classification.md` shape

```markdown
# Classification

## Summary
- apply-as-stated: 4
- apply-with-modification: 1
- discuss-not-fix: 1
- wont-fix: 0
- already-resolved: 0

## Per-comment table
| ID | Author | File:line | Created | Class | Reasoning | Group |
| --- | --- | --- | --- | --- | --- | --- |
| 1234 | @bob | routes/admin.go:42 | 2026-04-30 | apply-as-stated | clear actionable; suggested fix correct | g1 (with #5) |
| 1235 | @carol | db/orders.go:88 | 2026-04-30 | apply-with-modification | agree; rename instead of extract | (single) |
| 1236 | @dan | db/orders.go:117 | 2026-04-30 | apply-as-stated | n+1 fix is correct as suggested | (single) |
| 1237 | @eve | utils.go:12 | 2026-04-30 | apply-as-stated | typo | (single) |
| 1238 | @bob | routes/admin.go:200 | 2026-04-30 | apply-as-stated | add test as suggested | g1 (with #1) |
| 1239 | @bob | services/order.go:250 | 2026-04-30 | discuss-not-fix | architectural; prefer sync | (single) |

## Groups
| Group | Comments | Logical fix | Reasoning |
| --- | --- | --- | --- |
| g1 | #1 + #5 | admin role check + test | both flag the missing role check on the admin endpoint; the test (#5) covers the fix (#1) |
```

## `replies-draft.md` shape

```markdown
# Reply drafts

## Reply to comment #1 (routes/admin.go:42, @bob)
- Class: apply-as-stated
- Template: apply-stated
- SHA placeholder: <abc1234> (filled after Phase 5b)
- Draft:
  > Done in <abc1234>. Added `RequireRole("admin")` to the route group; matches the pattern at routes/admin.go:18-31.
  >
  > — /adk-review:review-feedback

## Reply to comment #2 (db/orders.go:88, @carol)
- Class: apply-with-modification
- Template: apply-modified
- SHA placeholder: <ghi9012>
- Draft:
  > Done in <ghi9012> with a small modification: renamed `processOrder` to `processOrderItem` (clarifies the per-item scope) instead of extracting a helper. Extracting would have forced 14 callers to wire in a context.Context. Happy to revisit if we add a second per-item codepath.
  >
  > — /adk-review:review-feedback

## Reply to comment #6 (services/order.go:250, @bob)
- Class: discuss-not-fix
- Template: discuss
- Draft:
  > Good architectural point — this is non-trivial and I'd rather discuss in person than turn it into a thread. Tracked at https://acme.atlassian.net/browse/CHK-1340.
  >
  > Suggesting we sync at the next platform standup, or DM me on Slack.
  >
  > — /adk-review:review-feedback
```

## `replies-postback.md` shape

```markdown
# Replies postback

## Posted
| Reply for comment | Reply URL | Receipt ID | Confirmed at | Thread resolved |
| --- | --- | --- | --- | --- |
| #1 | <url> | r-7891 | 5s | yes |
| #2 | <url> | r-7892 | 5s | yes |
| #3 | <url> | r-7893 | 10s | yes |
| #4 | <url> | r-7894 | 5s | yes |
| #5 | <url> | r-7895 | 5s | yes |
| #6 | <url> | r-7896 | 5s | NO (by design — discuss-not-fix) |

## NOT posted
| Reply for comment | Reason |
| --- | --- |

## Post-confirmation timeline
- t=0s   : posted 6 replies (5 individual + 1 to discuss thread)
- t=5s   : re-fetch → 5/6 confirmed (r-7893 missing)
- t=10s  : re-fetch → 6/6 confirmed
- t=12s  : resolved 5 threads (apply-* only); thread #6 left open

## Resolution actions
- Resolved threads (5): #1, #2, #3, #4, #5
- Left open (1): #6 (discuss-not-fix)
```

## `fix-log.md` shape (`--fix` only)

```markdown
# Fix log

## Fix 1: admin role check + test (comments #1, #5)
- Delegated to: /adk-code:code-bugfix
- Commits:
  - abc1234 — add RequireRole middleware
  - def5678 — add unit test for admin endpoint role check
- Files changed: routes/admin.go (+3/-0), routes/admin_test.go (+24/-0)
- Validation:
  - `go test ./routes/...` PASS (4/4)
  - `golangci-lint run ./routes/...` PASS
- Pushed: yes (in batch with all fixes)

## Fix 2: rename processOrder (comment #2)
- Applied: inline edit
- Commit: ghi9012
- Files changed: db/orders.go (+12/-12), db/orders_test.go (+8/-8), services/order.go (+5/-5)
- Validation:
  - `go build ./...` PASS
  - `golangci-lint run` PASS
- Pushed: yes

## Fix 3: n+1 query (comment #3)
- Delegated to: /adk-code:code-bugfix
- Commit: jkl3456
- Files changed: db/orders.go (+1/-1), db/orders_test.go (+30/-0)
- Validation:
  - `go test ./db/...` PASS (12/12)
  - benchmark: BenchmarkCheckoutSummary 200 from 820ms to 47ms
- Pushed: yes

## Fix 4: typo (comment #4)
- Applied: inline edit
- Commit: mno7890
- Files changed: utils.go (+1/-1)
- Validation:
  - `go build` PASS
- Pushed: yes
```
