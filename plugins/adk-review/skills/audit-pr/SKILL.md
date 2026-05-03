---
name: audit-pr
description: |
  Fast fixed-set audit on a single PR diff (NOT a deep review). Runs a parallel checklist: lint clean on changed files, typecheck clean, tests-added vs LOC-added heuristic, secrets-in-diff, license headers on new source files, dependency license compatibility, accessibility regressions if UI-touched, perf regressions if hot-path-touched, bundle size regression, doc-updated-for-behavior-change. Pass / Warn / Fail per check (NOT severity-tiered like review-pr). `--fix` only auto-fixes the safely-fixable subset (lint, license headers, docs TOC). Runs each check in parallel where independent. Use for fast pre-merge sanity. Do NOT use for deep semantic / architectural review (use `review-pr`), self-review of local changes (use `review-code-changes`), or whole-repo audit (use `audit-repo`).
metadata:
  category: audit
  kind: task
  layer: 7
  modes: [auto, interactive, fix]
  needs_mcp: [github]
  needs_meta_info: [info, repos, github]
argument-hint: "<pr-url-or-number> [--checks <subset>] [--fix] [--auto] [-i]"
---

# `audit-pr` — fast pre-merge sanity audit

Pass / Warn / Fail per check on a single PR diff. NOT severity-tiered. NOT deep semantic review. Designed for the moment between "PR opened" and "ready to merge" — confirms the boring stuff is OK.

## When to use

- "audit this PR" / "sanity-check the diff before merge"
- "is this PR safe to merge?"
- "run the pre-merge checks on <PR>"
- Routine pre-merge gate (e.g. as part of an automated CI-adjacent flow).
- Right before approving someone else's PR — quick check that it doesn't regress lint / tests / bundle.

## When NOT to use

- Deep semantic / architectural review → `/adk-review:review-pr`.
- Self-review of local changes (no PR yet) → `/adk-review:review-code-changes`.
- Address existing reviewer comments → `/adk-review:review-feedback`.
- Whole-repo audit → `/adk-review:audit-repo`.
- Performance investigation (not a check, an investigation) → `/adk-investigate:investigate-datadog` + `/adk-code:code-perf`.

## Common prompts (auto-route triggers)

| Prompt pattern | Default flags |
| --- | --- |
| `"audit this PR"` | `--auto` |
| `"sanity-check the diff"` | `--auto` |
| `"is <PR> safe to merge?"` | `--auto` |
| `"run pre-merge checks"` | `--auto` |
| `"audit + fix safe nits"` | `--fix` (only fixes lint, license headers, docs TOC) |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<pr-url-or-number>` | yes | inferred from current branch's open PR if omitted |
| `--checks <subset>` | optional | all 10 checks; subset is comma-separated names from `references/check-catalog.md` |
| `--auto` | optional | yes (default) |
| `-i` / `--interactive` | optional | mutually exclusive with `--auto` |
| `--fix` | optional | off; fixes only the safely-fixable subset (lint, license-header, docs-toc) |

## Workflow

```
Phase 0 — prompt expand
  - Resolve PR URL / number → repo, base, head, files-changed.
  - Locate local checkout via repos.md (or worktree-add).
  - Slug.
  - Determine mode + `--checks` subset.

Phase 1 — preflight
  - github MCP / gh CLI authed.
  - Local repo matches PR's repo.
  - For --fix: working tree clean.

Phase 2 — fetch context
  - PR metadata (head SHA, files-changed, additions/deletions).
  - Diff.
  - PR's existing CI status (gh pr checks).

Phase 3 — fixed-set checks (parallel where independent; per references/check-catalog.md)
  Always-run checks:
    1. lint-clean         (run repo-native lint on changed files)
    2. typecheck-clean    (tsc / mypy / go build / equivalent)
    3. tests-added        (heuristic: lines-added-to-tests vs total lines-added)
    4. secrets-in-diff    (delegate to security-reviewer agent)
    5. license-headers    (new source files have repo-required license header)
    6. dep-licenses       (new deps have repo-compatible licenses)
    7. doc-updated        (behavior change implies CHANGELOG / README touch)
  Conditional checks (run if relevant):
    8. a11y-regression    (UI files touched — run axe-core or repo's a11y tool)
    9. perf-regression    (hot-path files touched — run repo's perf budget script)
    10. bundle-size       (frontend repo with bundle-budget)

Phase 4 — propose
  - Show check results: Pass / Warn / Fail per check.
  - For -i: walk each Warn/Fail; ask user how to proceed.

Phase 5a — report (no `--fix`)
  - Write .temp/task-<slug>/audit/results.md.
  - Surface: Pass count / Warn count / Fail count / overall verdict.

Phase 5b — fix (--fix only)
  - For lint: run the lint tool's auto-fix mode.
  - For license-header: prepend the repo-required header to new source files.
  - For docs-toc: regenerate the doc TOC.
  - DO NOT fix tests-added, perf-regression, secrets-in-diff, etc. (not auto-fixable).
  - Validate fixes with the original check (e.g. lint after auto-fix → re-run lint, expect 0 errors).
  - If --fix should also push: ask first (push-gate); else leave dirty for user to commit.

Phase 5c — postback (optional)
  - If --post-comment, post a Pass/Warn/Fail summary as a PR comment (with post-confirmation).
  - Default: NO posting (audit-pr is informational; review-pr is the comment-poster).

Phase 6 — final report
  - .temp/task-<slug>/report.md
```

See `references/workflow.md` for stage detail and `references/how-it-works.md` for diagrams.

## Persona

> Fast gatekeeper. Pass / Warn / Fail per check, not severity-tiered. Doesn't opine on design (that's `review-pr`'s job). Parallelizes where possible; doesn't block on nits (those are `Warn`, not `Fail`). The output is a 30-second scan: green = ship; yellow = consider; red = stop.

See `references/persona.md`.

## Constitution

**Must do:**

1. Be FAST. Parallelize all independent checks.
2. Pass / Warn / Fail per check — never use the 6-tier severity system from `review-pr`.
3. Run repo-native tools first (`npm run lint`, `tsc`, `go test`); fall back to heuristics only when no tool is available.
4. Treat nits as `Warn`, not `Fail`. Don't block on style.
5. Run a check if and only if it's relevant (e.g. `a11y-regression` only if UI files were touched).
6. Honor `~/.config/adk/review.md.ignore_in_repos[<repo>]` filter for irrelevant checks.

**Must not do:**

1. Deep semantic review. That's `review-pr`'s job.
2. Block on nits. Style noise → `Warn`.
3. Auto-fix anything outside the safely-fixable subset (lint, license-header, docs-toc).
4. Push without asking, even under `--auto --fix`.
5. Post a comment by default. Audit-pr is informational; comment-posting is `review-pr`'s job. Use `--post-comment` for explicit opt-in.
6. Mark a check `Fail` for a tool that isn't installed. Mark `N/A` with the install command.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Running serial when parallel is possible (slow).
- Marking style nits as `Fail` (over-strict).
- Marking a missing tool as `Fail` (mis-attributed; use `N/A`).
- Ignoring conditional checks (e.g. running `a11y-regression` on a backend-only diff).
- Auto-fixing tests-added or perf-regression. Not safely-fixable.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/audit/results.md` | Pass/Warn/Fail per check + overall verdict |
| `.temp/task-<slug>/audit/per-check/<name>.md` | Per-check evidence (command + output) |
| `.temp/task-<slug>/audit/fix-log.md` | (`--fix` only) per-fix evidence |
| `.temp/task-<slug>/audit/postback.md` | (if `--post-comment`) PR comment receipt |
| `.temp/task-<slug>/report.md` | Executive summary |

See `references/output-format.md` and `references/artifact-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Fast-gatekeeper persona + status banner + posture |
| `references/workflow.md` | Detailed Phase 0-6 stage list with checkpoints |
| `references/modes.md` | What `--auto` / `-i` / `--fix` mean for `audit-pr` |
| `references/interaction-contract.md` | Canonical interaction contract (mirrored byte-identical from adk-core) |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 3-4 worked examples (clean PR, mixed results, --fix flow) |
| `references/output-format.md` | results.md / per-check/<name>.md / fix-log.md shapes |
| `references/artifact-format.md` | `.temp/task-<slug>/audit/*` canonical paths |
| `references/validator.md` | Per-check gates (especially: parallel safety; never severity-tier) |
| `references/how-it-works.md` | Mermaid: phase flow, parallel check fan-out, --fix loop |
| `references/clarifying-questions.md` | Under -i; defaults under --auto |
| `references/check-catalog.md` | The 10 checks with: detection trigger, command, pass/warn/fail thresholds, fix-strategy |
| `references/pass-warn-fail.md` | The verdict rubric (when does a check Pass vs Warn vs Fail) |

## Additional links

- `/adk-review:review-pr` `references/post-confirmation.md` — used if `--post-comment` is set.
- `/adk-review:review-pr` `references/pr-mcp-fallback.md` — github MCP / gh CLI decision.
- The repo's lint config (`.eslintrc`, `golangci.yml`, `pyproject.toml`, etc.) — detected at preflight.
- The repo's CI config (`.github/workflows/`) — to know which checks run upstream.
