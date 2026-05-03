# `review-feedback` — artifact format

## `.temp/task-<slug>/` canonical layout

```
.temp/task-<slug>/
├── prompt.txt                              # verbatim user prompt + ISO ts + resolved PR URL
├── feedback-checkout/                      # (only when not using user's main checkout) isolated git worktree at PR head
│   └── <repo contents>
├── feedback/
│   ├── pr-context/
│   │   ├── pr.json                         # gh pr view --json output
│   │   ├── comments.json                   # /pulls/<num>/comments (paginated)
│   │   ├── issue-comments.json             # /issues/<num>/comments
│   │   ├── reviews.json                    # /pulls/<num>/reviews
│   │   ├── threads.json                    # GraphQL: thread + resolved state
│   │   └── repo-conventions.md             # AGENTS.md / CLAUDE.md / .cursorrules synthesis
│   ├── classification.md                   # per-comment 5-state classification + grouping
│   ├── replies-draft.md                    # drafted replies (with SHA placeholders before Phase 5b)
│   ├── replies-postback.md                 # per-reply receipt + confirmation timing
│   ├── post-receipts.json                  # machine-readable receipt set
│   └── fix-log.md                          # (--fix only) per-fix commit + validation
├── validation/
│   └── per-skill/
│       └── review-feedback.md
└── report.md                               # final consolidated report
```

## File-by-file purpose

| File | Lifecycle | Used by |
| --- | --- | --- |
| `prompt.txt` | Phase 0 (write-once) | audit / replay |
| `feedback-checkout/` | Phase 1 (worktree-add, only when not using main checkout) | apply step (Phase 5b) |
| `feedback/pr-context/*` | Phase 2 (write-once) | classify, apply, post |
| `feedback/classification.md` | Phase 3 (write-once after classify) | propose (Phase 4), apply (Phase 5b), post (Phase 5d) |
| `feedback/replies-draft.md` | Phase 5a (write-once; SHAs filled in 5b) | post (Phase 5d) |
| `feedback/post-receipts.json` | Phase 5d (write, then update on confirmation) | post-confirmation re-fetch |
| `feedback/replies-postback.md` | Phase 5d (write at end of confirmation) | report |
| `feedback/fix-log.md` | Phase 5b (append per fix) | report |
| `validation/per-skill/review-feedback.md` | every phase boundary (append) | universal validator |
| `report.md` | Phase 6 (write-once) | user surface |

## Naming conventions

- **Slug:** kebab-case derived from PR repo + number, prefixed with `feedback-` (e.g. `feedback-checkout-pr-2841`). Disambiguates from a `review-pr` run on the same PR.
- **Worktree path:** `.temp/task-<slug>/feedback-checkout/` ONLY when the user's main checkout is unavailable / dirty / on a different branch. Default: use the user's main checkout.
- **Receipt file:** JSON with `{reply_id, comment_id, file, line, comment_url, receipt_id, confirmed_at_ms, retries, thread_resolved}`.

## Rules

1. **Default to using the user's main checkout.** This skill applies fixes that the user typically wants to land in their main worktree (so they can `git diff` after). Only worktree-add when main checkout is dirty or on the wrong branch.
2. **Never write outside `.temp/task-<slug>/`** unless `--fix` is set. Under `--fix`, edits land in the actual checkout.
3. **The slug persists across phases** within a session.
4. **`.temp/` is in `.gitignore`** at the repo root. Verify before any write.
5. **Existing `.temp/task-<slug>/`** from a prior run is moved to `.archive/<iso-ts>/` first.
6. **All JSON files are pretty-printed.**
7. **Cross-references to `review-pr`'s post-confirmation protocol are by reference, not by copy.** This skill does NOT duplicate the protocol; it cites `/adk-review:review-pr` `references/post-confirmation.md`.

## Cross-reference: how this differs from `review-pr` artifact format

| Aspect | `review-pr` | `review-feedback` |
| --- | --- | --- |
| Slug prefix | (none — slug is just `<pr-slug>`) | `feedback-` (disambiguates from a parallel review-pr run) |
| Worktree | always (`review-checkout/`) | only when main checkout unavailable |
| `pr-context/` | yes (full PR context for review) | yes (focused on comments + threads) |
| `review/findings.md` | yes (new findings) | NO (this skill doesn't generate new findings) |
| `feedback/classification.md` | NO | yes (the core artifact) |
| `feedback/replies-draft.md` | only own-PR path | always (the core deliverable) |
| `review/postback.md` | yes (for posted findings) | NO (no findings posted) |
| `feedback/replies-postback.md` | NO | yes (per-reply receipts) |
| `review/reconciliation.md` | yes (existing-comment classification) | NO — but the WHOLE skill is reconciliation (the equivalent is `classification.md`) |
| `review/fix-log.md` | yes (--fix only) | yes (--fix only) |
