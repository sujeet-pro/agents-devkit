# `review-pr` — artifact format

## `.temp/task-<slug>/` canonical layout for review-pr

```
.temp/task-<slug>/
├── prompt.txt                         # verbatim user prompt + ISO timestamp + resolved PR URL + ownership
├── review-checkout/                   # isolated git worktree at the PR's head SHA
│   └── <repo contents>
├── pr-context/
│   ├── pr.json                        # gh pr view --json output
│   ├── diff.patch                     # gh pr diff --patch
│   ├── comments.json                  # /pulls/<num>/comments (paginated)
│   ├── issue-comments.json            # /issues/<num>/comments (top-level)
│   ├── reviews.json                   # /pulls/<num>/reviews (paginated)
│   ├── threads.json                   # GraphQL: thread + resolved state
│   ├── template.md                    # .github/pull_request_template.md (read from worktree)
│   ├── codeowners.txt                 # .github/CODEOWNERS (read from worktree)
│   ├── author-history.md              # author's last 5 PRs in this repo
│   ├── repo-conventions.md            # AGENTS.md / CLAUDE.md / .cursorrules synthesis
│   └── jira-context.md                # (optional) linked Jira ticket via Atlassian connector
├── review/
│   ├── raw-findings.md                # pre-reconciliation, per-dimension
│   ├── findings.md                    # canonical post-reconciliation, severity-sorted
│   ├── reconciliation.md              # per-existing-comment classification
│   ├── postback.md                    # per-finding receipt + confirmation timing
│   ├── post-receipts.json             # machine-readable receipt set (for retry / debugging)
│   ├── replies-draft.md               # (own-PR path only) draft replies
│   ├── replies-postback.md            # (own-PR path only) reply receipts
│   ├── fix-log.md                     # (--fix only) per-fix commit + validation
│   └── pushback-context.md            # (when reconciling pushback) author's reasoning + our re-evaluation
├── validation/
│   └── per-skill/
│       └── review-pr.md               # per-phase validator log
└── report.md                          # final consolidated report
```

## File-by-file purpose

| File | Lifecycle | Used by |
| --- | --- | --- |
| `prompt.txt` | Phase 0 (write-once) | audit / replay |
| `review-checkout/` | Phase 1 (worktree-add) | dimension passes (Phase 3), fix application (Phase 6c) |
| `pr-context/*` | Phase 2 (write-once) | dimension passes, reconciliation, fix |
| `review/raw-findings.md` | Phase 3 (write-once per dimension pass) | input to reconciliation (Phase 4) |
| `review/findings.md` | Phase 4 (write-once after reconcile) | propose (Phase 5), post (Phase 6a) |
| `review/reconciliation.md` | Phase 4 (write-once) | report; surfaced in `report.md` |
| `review/post-receipts.json` | Phase 6a (write, then update on confirmation) | post-confirmation re-fetch |
| `review/postback.md` | Phase 6a (write at end of confirmation) | report |
| `review/replies-draft.md` | Phase 6b (write-once if own-PR) | propose, post |
| `review/replies-postback.md` | Phase 6b (write at end of confirmation) | report |
| `review/fix-log.md` | Phase 6c (append per fix) | report |
| `validation/per-skill/review-pr.md` | every phase boundary (append) | universal validator (auto's Phase 5) |
| `report.md` | Phase 7 (write-once) | user surface |

## Naming conventions

- **Slug:** kebab-case derived from PR repo + number (e.g. `checkout-api-pr-2841`). Date-prefix only on collision.
- **Worktree path:** `.temp/task-<slug>/review-checkout/`. Always nested under the task; never at the repo root.
- **Receipt file:** JSON with `{finding_id, file, line, severity, comment_url, receipt_id, confirmed_at_ms, retries}`.
- **Fix branch:** `<head-branch>-review-fixes-from-<reviewer-login>` if the reviewer pushes their own commits to a peer's PR. Same head branch if the reviewer is the author.

## Rules

1. **Never write outside `.temp/task-<slug>/`** until the user signs off. (Exception: when `--fix` pushes commits to the PR's head branch — that's a remote write, governed by the push-gate rule.)
2. **The slug persists across phases** — the same task accumulates artifacts across the review.
3. **Worktree is durable for the session.** Don't delete after Phase 7; the user may want to inspect findings against the worktree state. Pruning is the user's call.
4. **All JSON files are pretty-printed** (2-space indent) so the user can read them.
5. **All MD files include an ISO timestamp** in the first line (`<!-- generated 2026-05-03T14:00Z by review-pr -->`).
6. **Existing files in `.temp/task-<slug>/`** from a prior `review-pr` run on the same PR are NOT overwritten — they're moved to `.temp/task-<slug>/.archive/<iso-ts>/` first. Lets the user diff successive review runs.
7. **`.temp/` is in `.gitignore`** at the repo root. Verify before any write.
