# `review-code-changes` — artifact format

## `.temp/task-<slug>/` canonical layout for review-code-changes

```
.temp/task-<slug>/
├── prompt.txt                         # verbatim user prompt + ISO ts + repo + branch + baseline ref + baseline source
├── review/
│   ├── scope.md                       # per-source breakdown (branch / staged / unstaged / untracked)
│   ├── raw-findings.md                # pre-de-noise, per-dimension
│   ├── findings.md                    # canonical, severity-sorted, scope-source-tagged
│   ├── fix-log.md                     # (--fix only) per-fix evidence
│   ├── lint-output.txt                # (if cheap lint pre-pass ran) raw lint output
│   └── repo-conventions.md            # synthesis of AGENTS.md / CLAUDE.md / .cursorrules
├── validation/
│   └── per-skill/
│       └── review-code-changes.md     # per-phase validator log
└── report.md                          # final consolidated report
```

## File-by-file purpose

| File | Lifecycle | Used by |
| --- | --- | --- |
| `prompt.txt` | Phase 0 (write-once) | audit / replay |
| `review/scope.md` | Phase 2 (write-once) | input to dimension passes (Phase 3); referenced in `report.md` |
| `review/raw-findings.md` | Phase 3 (write-once per dimension pass) | input to de-noise → `findings.md` |
| `review/findings.md` | Phase 4 (write-once after sort) | propose (Phase 4), apply (Phase 5b) |
| `review/fix-log.md` | Phase 5b (append per fix) | report |
| `review/lint-output.txt` | Phase 1 (optional, write-once) | informs the style dimension |
| `review/repo-conventions.md` | Phase 1 (write-once) | dimension pass context |
| `validation/per-skill/review-code-changes.md` | every phase boundary (append) | universal validator |
| `report.md` | Phase 6 (write-once) | user surface |

## Naming conventions

- **Slug:** kebab-case derived from the current branch name (e.g. `feature-pricing-rework`). If branch is `HEAD` (detached), use `detached-<short-sha>`.
- **No worktree.** Unlike `review-pr`, this skill works directly on the user's working tree (the whole point is to review what's there).
- **Lint output is raw stdout.** Plain text; not parsed into findings (the style dimension does that selectively).

## Rules

1. **Never write outside `.temp/task-<slug>/`** unless `--fix` is set. Under `--fix`, edits land in the actual repo working tree (that's the whole point).
2. **Working tree mtime tracked.** Every in-scope file's mtime is recorded at end of Phase 2; compared at end of Phase 3 to detect mid-review edits.
3. **`.temp/` is in `.gitignore`** at the repo root. Verify before any write.
4. **Existing `.temp/task-<slug>/`** from a prior run on the same branch is NOT overwritten — moved to `.temp/task-<slug>/.archive/<iso-ts>/`. Lets the user diff successive review runs.
5. **No remote artifact.** No `gh pr` JSON dumps; no MCP receipts; no comment URLs. The skill is local-only.
6. **`fix-log.md` exists only when `--fix` was set.** Don't create the empty file otherwise.
7. **Slugs persist across runs.** Re-running on the same branch reuses the slug; new artifacts go in (under archive).

## Working-tree mtime check (mid-review change detection)

```
At end of Phase 2:
  for each in-scope file:
    record mtime in scope.md as `mtime_t0`

At end of Phase 3:
  for each in-scope file:
    fresh_mtime = os.stat(file).st_mtime
    if fresh_mtime > mtime_t0:
      mark `dirty_during_review = true` in scope.md
      append to validation/per-skill/review-code-changes.md
      surface in report.md

In findings.md:
  any finding on a `dirty_during_review` file is annotated:
    > NOTE: this file was modified during the review pass.
    > Findings may be stale; re-run for accuracy.
```

This is informational; it doesn't block the report. The user decides whether to re-run.

## Cross-reference: how this differs from `review-pr` artifact format

| Aspect | `review-pr` | `review-code-changes` |
| --- | --- | --- |
| Worktree | yes (`review-checkout/` at the PR's head SHA) | no — direct on the working tree |
| `pr-context/` | populated with PR JSON / comments / reviews | absent (no PR yet) |
| `review/postback.md` | present (post receipts + confirmation) | absent (no posting) |
| `review/replies-draft.md` | present in own-PR path | absent (no PR comments to reply to) |
| `review/reconciliation.md` | present (existing comment classification) | absent |
| `review/scope.md` | absent (PR has well-defined scope) | present (4-source breakdown) |
| `review/lint-output.txt` | absent (lint runs as a dimension pass at Phase 3) | optional (cheap pre-pass at Phase 1) |
