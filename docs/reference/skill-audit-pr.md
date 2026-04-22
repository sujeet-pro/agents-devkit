---
title: 'audit-pr'
description: 'Thinner, faster audit scoped to a single PR — different from `@adk:review-pr` (a.'
artifact_kind: skill
skill_name: audit-pr
category: audit
---
# audit-pr

Thinner, faster audit scoped to a single PR — different from `@adk:review-pr` (a.k.a. `adk-review-pr`) which is a deep findings-first review. `audit-pr` runs a fixed set of "quick checks" against the PR's diff: lint, typecheck, test count vs lines added, secrets in diff, license headers, OSS-license compatibility, accessibility regressions if UI-touched, performance regressions if hot-path-touched. Use for fast pre-merge sanity checks or as an extra gate in `@adk:auto`'s D1 phase. Do not use for deep code review (use `@adk:review-pr`).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-audit-pr` form via `agents-skills/`.

```text
/adk:audit-pr            # interactive run (Claude Code)
/adk:audit-pr --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-audit-pr` (resolved through the
`agents-skills/adk-audit-pr/` symlink).

## Source

Direct from `skills/audit-pr/SKILL.md` — this page is auto-generated.

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
6. Phase 4 validator. Report.

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

## References

Standard set + `references/check-recipes.md` (per-check command per stack).


## Related skills

- [`audit`](./skill-audit.md) — `@adk:audit` (a.k.a. `adk-audit`)
- [`audit-repo`](./skill-audit-repo.md) — `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
- [`build`](./skill-build.md) — `@adk:build` (a.k.a. `adk-build`)
- [`review`](./skill-review.md) — `@adk:review` (a.k.a. `adk-review`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
- [`validate-browser`](./skill-validate-browser.md) — `@adk:validate-browser` (a.k.a. `adk-validate-browser`)
