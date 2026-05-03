# `audit-pr` — artifact format

## `.temp/task-<slug>/` canonical layout

```
.temp/task-<slug>/
├── prompt.txt                              # verbatim user prompt + ISO ts + resolved PR URL
├── audit-checkout/                         # (only when not using main checkout) git worktree at PR head SHA
├── audit/
│   ├── pr-context/
│   │   ├── pr.json                         # gh pr view --json output
│   │   ├── diff.patch                      # gh pr diff --patch
│   │   └── ci-status.json                  # gh pr checks output (existing CI signal)
│   ├── results.md                          # canonical verdict + per-check table
│   ├── results.pre-fix.md                  # (--fix only) verdicts before fixes applied
│   ├── per-check/
│   │   ├── lint-clean.md
│   │   ├── typecheck-clean.md
│   │   ├── tests-added.md
│   │   ├── secrets-in-diff.md
│   │   ├── license-headers.md
│   │   ├── dep-licenses.md
│   │   ├── doc-updated.md
│   │   ├── a11y-regression.md              # only if conditional triggered
│   │   ├── perf-regression.md              # only if conditional triggered
│   │   └── bundle-size.md                  # only if conditional triggered
│   ├── fix-log.md                          # (--fix only) per-fix evidence
│   └── postback.md                         # (--post-comment only) PR comment receipt
├── validation/
│   └── per-skill/
│       └── audit-pr.md                     # per-phase validator log
└── report.md                               # final consolidated report
```

## File-by-file purpose

| File | Lifecycle | Used by |
| --- | --- | --- |
| `prompt.txt` | Phase 0 (write-once) | audit / replay |
| `audit-checkout/` | Phase 1 (worktree-add, only if main checkout unavailable) | per-check execution |
| `audit/pr-context/*` | Phase 2 (write-once) | per-check execution |
| `audit/results.md` | Phase 3 (write at end of all checks) | report; surfaced to user |
| `audit/results.pre-fix.md` | Phase 5b (--fix) snapshot before fix re-runs | report (diff vs results.md) |
| `audit/per-check/<name>.md` | Phase 3 (per-check write-once) | report; debugging |
| `audit/fix-log.md` | Phase 5b (append per fix) | report |
| `audit/postback.md` | Phase 5c (only if --post-comment) | report |
| `validation/per-skill/audit-pr.md` | every phase boundary (append) | universal validator |
| `report.md` | Phase 6 (write-once) | user surface |

## Naming conventions

- **Slug:** kebab-case derived from PR repo + number, prefixed `audit-` (e.g. `audit-storefront-pr-103`). Disambiguates from review-pr / review-feedback runs on the same PR.
- **Per-check file:** named exactly per the check's name in `references/check-catalog.md` (snake_case-or-kebab-case as appropriate; the check catalog defines the canonical name).
- **Worktree path:** `.temp/task-<slug>/audit-checkout/` only when main checkout unavailable. Default: use main checkout.

## Rules

1. **Default to using the user's main checkout.** Audit-pr is read-only on the diff (no edits unless `--fix`); no need to worktree by default.
2. **Never write outside `.temp/task-<slug>/`** unless `--fix` is set (in which case edits go to the actual checkout).
3. **The slug persists across phases** within a session.
4. **`.temp/` is in `.gitignore`** at the repo root. Verify before any write.
5. **Existing `.temp/task-<slug>/`** from a prior audit on the same PR is moved to `.archive/<iso-ts>/` first.
6. **All JSON files are pretty-printed.**
7. **Per-check output truncation:** stdout/stderr in `per-check/<name>.md` is truncated to 100 lines. Larger outputs reference the captured file (which lives elsewhere if needed).

## Cross-reference: how this differs from `review-pr` artifact format

| Aspect | `review-pr` | `audit-pr` |
| --- | --- | --- |
| `findings.md` (severity-tiered) | yes | NO |
| `results.md` (Pass/Warn/Fail) | NO | yes |
| `per-check/<name>.md` | NO | yes (one per check) |
| `reconciliation.md` | yes (existing comment classification) | NO (no comment touch) |
| `postback.md` | yes (default; review-pr posts findings) | only when `--post-comment` |
| Worktree | always | only when main checkout unavailable |
| Slug prefix | (none — `<pr-slug>`) | `audit-` |

## Per-check stdout capture

Each check writes:

- The exact command run (in markdown fenced block).
- The exit code.
- The stdout / stderr (truncated to 100 lines; full output in `audit/per-check/<name>.raw.txt` if larger).
- The verdict (PASS / WARN / FAIL / N/A / INCONCLUSIVE).
- The reason (one or two sentences).
- The mitigation (for WARN / FAIL).

Example (`per-check/lint-clean.md`):

```markdown
# lint-clean

## Verdict: PASS

## Command
```
npm run lint -- --max-warnings 0 src/billing/ src/api/
```

## Output
```
> storefront@1.0.0 lint
> eslint src/billing/ src/api/

(no output; lint clean)
```

## Exit code: 0

## Reason
0 errors, 0 warnings on the files changed in this PR.

## Files affected
(none — clean run)

## Mitigation (for WARN / FAIL)
(N/A — Pass)
```
