---
name: audit-pr
description: |
  Thinner, faster audit scoped to a single PR — different from `@adk:review-pr` (a.k.a. `adk-review-pr`) which is a deep findings-first review. `audit-pr` runs a fixed set of "quick checks" against the PR's diff: lint, typecheck, test count vs lines added, secrets in diff, license headers, OSS-license compatibility, accessibility regressions if UI-touched, performance regressions if hot-path-touched. Use for fast pre-merge sanity checks or as an extra gate in `@adk:auto`'s D1 phase. Do not use for deep code review (use `@adk:review-pr`).
metadata:
  category: audit
  kind: task
  layer: 7
  modes: [auto, review, fix]
---

# audit-pr — quick fixed-set audit on a PR diff

## When to use

- Fast pre-merge sanity check on a PR.
- Pre-merge automation gate.

## When NOT to use

- Deep code review with severity reasoning → `@adk:review-pr`.
- Whole-repo audit → `@adk:audit-repo` (a.k.a. `adk-audit-repo`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<pr-url>` | yes | GitHub PR URL (gh CLI). Bitbucket PR URL also supported via MCP. |
| `<task-slug>` | yes | |
| `<checks>` | optional | Comma-separated subset (default: all) |
| `--mode` | optional | `review` (report) / `fix` (auto-apply) |

## Checks (fixed list)

| # | Check | Tool |
| --- | --- | --- |
| 1 | Lint clean on changed files | repo-native (eslint / ruff / golangci-lint / etc.) |
| 2 | Typecheck clean on changed files | repo-native (tsc / mypy / go vet) |
| 3 | Tests added vs LOC added | heuristic: `tests-added / loc-added > 0.2` for non-doc PRs |
| 4 | No secrets in diff | `gitleaks` or built-in regex (AKIA[0-9A-Z]{16}, etc.) |
| 5 | License headers on new source files | repo convention from `.licenseheaderrc` if present |
| 6 | New deps' OSS-license compatibility | `license-checker` against repo allowlist |
| 7 | Accessibility regressions (UI-touched) | call `@adk:validate-browser --mode a11y-audit` against built preview |
| 8 | Performance regressions (hot-path-touched) | call repo-native bench script if `bench/` exists |
| 9 | Bundle size regression (UI-touched) | repo-native (`build` + size diff vs base) |
| 10 | Doc updated for behavior changes | heuristic: API change → docs/ touched |

Each check returns `pass` / `warn` / `fail` plus a one-line evidence.

## Workflow

1. Phase 1 validator. PR URL parses; gh CLI authed (or MCP).
2. Fetch PR diff via `gh pr diff <N>`.
3. For each check (parallel where possible), run; capture result.
4. Aggregate to a `audit.md` table.
5. (`fix` mode): for fixable findings (lint auto-fix, license-header insertion, doc TOC regen), apply via a follow-up commit. Push.
6. (Optional) Post a single inline summary comment on the PR if requested. Capture the provider-returned ID into the in-session post receipt set.
7. **Verify posted comment (post-confirmation, if any comment was posted):** wait 5s, re-fetch the PR's comment graph, confirm the receipt ID re-appears. On miss, retry at 10s and 20s (3-attempt total budget, 35s wall-clock). Final result is `OK` or `WARN: unconfirmed` — surface the unconfirmed ID + html_url in the report. Do NOT re-post on a miss; propagation lag would create real duplicates.
8. Phase 4 validator. Report.

## Mode

- `review` (default): write `audit.md` with table; do NOT push commits.
- `fix`: apply auto-fixable; push as a `chore: audit-pr autofix` commit.
- `auto`: review then offer to run fix.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/audit.md` | Per-check table + evidence |
| (gh) | Optional inline comment summarizing pass/fail |

## Anti-patterns

- Running deep semantic review here (use `review-pr`).
- Failing the audit on style nits (those are Nitpicks; do not block).
- Pushing autofix commits without an explicit `--mode fix`.
- Auto-fixing license issues silently — always flag for human review of the new dep.
- Treating "the API returned 2xx" as proof the inline summary comment is on the PR. If a comment was posted, always run the post-confirmation re-fetch + retry budget (5s → 10s → 20s) before declaring Phase 4 done.
- Re-posting on a post-confirmation miss. Log a `WARN` with the receipt ID + html_url and let the user check; never re-post automatically.

## References

Standard set + `references/check-recipes.md` (per-check command per stack).
