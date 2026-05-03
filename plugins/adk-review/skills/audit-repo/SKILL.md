---
name: audit-repo
description: |
  Whole-repo multi-dimensional audit — security, performance, code quality, dependencies, test coverage, architecture — producing a single severity-tiered report with file-anchored evidence per finding. Read-only: NEVER opens PRs, NEVER pushes, NEVER mutates code. Inventory first (language / framework / dep manager / test framework / lint tool / CI provider), then per-dimension passes (run repo-native tools first; sample architecture by reading the largest files), then aggregate top-10 + per-dimension detail. Includes explicit "what's healthy" findings alongside problems. Use when the deliverable is a multi-file audit report (e.g. "what's the security posture of acme/checkout-api?", "audit the storefront repo before the M&A", "are we ready to open-source this?"). Do NOT use for PR review (use `review-pr`), single-PR sanity (use `audit-pr`), or any kind of fix work (use `code-*` skills).
metadata:
  category: audit
  kind: task
  layer: 7
  modes: [auto, interactive]
  needs_meta_info: [info, repos]
argument-hint: "[<repo-path>] [--dimensions <subset>] [--scope <path>] [--auto] [-i]"
---

# `audit-repo` — whole-repo multi-dimensional audit

Severity-tiered, file-anchored audit across security, performance, code quality, dependencies, test coverage, and architecture. Read-only. Top-10 findings up front; per-dimension detail below; explicit "what's healthy" alongside problems.

## When to use

- "audit the repo" / "audit acme/checkout-api"
- "what's the security posture of <repo>?"
- "give me the top issues across the codebase"
- Pre-M&A / pre-open-source / pre-handoff repo health check.
- Before adopting a new repo into the team's portfolio.

## When NOT to use

- PR review (single PR diff) → `/adk-review:review-pr` or `/adk-review:audit-pr`.
- Self-review of local changes → `/adk-review:review-code-changes`.
- Address existing reviewer comments → `/adk-review:review-feedback`.
- Any fix work → `/adk-code:*` (code-bugfix, code-refactor, etc.).
- Performance investigation tied to a live signal → `/adk-investigate:investigate-datadog`.

## Common prompts (auto-route triggers)

| Prompt pattern | Default flags |
| --- | --- |
| `"audit the repo"` | `--auto` |
| `"audit acme/checkout-api"` | `--auto` |
| `"what's the security posture of X?"` | `--auto --dimensions security` |
| `"top 10 issues in this codebase"` | `--auto` |
| `"audit before open-sourcing"` | `--auto --dimensions security,deps,docs` |
| `"audit the auth subsystem"` | `--auto --scope src/auth/` |
| `"walk me through the audit"` | `-i` |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<repo-path>` | optional | current working directory if `git rev-parse` succeeds |
| `--dimensions <subset>` | optional | all 6 (security, performance, quality, deps, test-coverage, architecture); subset comma-separated |
| `--scope <path>` | optional | restrict to a sub-path of the repo |
| `--auto` | optional | yes (default) |
| `-i` / `--interactive` | optional | mutually exclusive with `--auto` |

## Workflow

```
Phase 0 — prompt expand
  - Resolve repo path (arg → CWD walk-up to .git).
  - Slug from repo name (e.g. `audit-checkout-api-2026-05-03`); date-stamp because audits are point-in-time snapshots.
  - Determine dimensions subset.

Phase 1 — preflight
  - In a git repo.
  - bin/adk-info repos --check.
  - For each dimension: detect repo-native tools (npm audit, bandit, gosec, govulncheck, bundler-audit, jest, pytest, etc.).

Phase 2 — inventory
  - Per references/inventory.md: detect language(s), framework(s), dep manager,
    test framework, lint tool, CI provider, deployment style, observability
    stack (DD / NR / Sentry / etc.).
  - Read CONTRIBUTING / SECURITY / CODEOWNERS / AGENTS.md / .cursorrules / etc.
  - Capture LOC by language; top 20 largest files; top 20 most-changed files (via git log).

Phase 3 — dimension passes (parallel where possible; per references/dimension-passes.md)
  Always-run dimensions:
    - security        (delegate to security-reviewer agent + npm audit / bandit / gosec / govulncheck / bundler-audit)
    - performance     (cheap heuristics: read top 20 hot-path files; flag anti-patterns)
    - quality         (lint over the whole repo; cyclomatic complexity; god-class detection)
    - deps            (outdated, vulnerable, transitive risk; license compatibility; orphaned)
    - test-coverage   (run repo's coverage tool; identify untested critical paths)
    - architecture    (sample top 20 largest files + per-module concerns; flag boundary violations / cyclic deps)

Phase 4 — aggregate
  - Per references/aggregation.md:
    - Sort all findings by severity (Blocker / Critical / Should-Have / May-Have / Nitpick / Question).
    - Pick the Top-10 (by severity, then by impact-area breadth).
    - Group remaining findings per dimension.
    - Add explicit "what's healthy" findings (the things going RIGHT — surface them!).

Phase 5 — propose
  - Show Top-10 + per-dimension counts.
  - For -i: walk each Top-10 finding; allow re-tier / discard.
  - For --auto: keep aggregation as-is.

Phase 6 — write report
  - .temp/reports/audit-<slug>.md (NOT .temp/task-<slug>/ because audits are
    repo-wide, not task-tied; per artifact-format.md):
    - Executive summary (1 page)
    - Top-10 (severity-sorted; file-anchored)
    - Per-dimension detail
    - "What's healthy" section
    - Recommendations (prioritized)
    - Methodology + scope (what was/wasn't covered)
  - .temp/reports/audit-<slug>-evidence/ — per-finding evidence directory.

Phase 7 — final report
  - Surface the .temp/reports/audit-<slug>.md path + the Top-10 + the verdict.
  - Suggest natural follow-ups (each Top-10 finding may map to /adk-code:* or /adk-review:* or /adk-investigate:*).
```

See `references/workflow.md` for stage detail and `references/how-it-works.md` for diagrams.

## Persona

> Strategic auditor. Surfaces top-10 issues, not every linter warning. Names ARCHITECTURAL concerns over style nits. Includes explicit "what's healthy" findings (so the engineering team doesn't get demoralized). Read-only — never opens a PR from this skill, never proposes fixes inline (recommendations are referenced to the right `/adk-code:*` skill instead).

See `references/persona.md`.

## Constitution

**Must do:**

1. Inventory FIRST. Don't run dimension passes until you know the language / framework / tools.
2. Run repo-native tools BEFORE heuristics. `npm audit` over a regex; `pytest --cov` over a guess.
3. Top-10 findings up front. The reader scans these in 30 seconds.
4. Include "what's healthy" findings (top 5; explicit). The reader knows what NOT to break.
5. File-anchored evidence per finding (file:line range + ≤15-word verbatim quote).
6. Severity-tier per `~/.config/adk/review.md.severity_bar` overrides.
7. Methodology section (what was covered, what wasn't, how long it took, what tools were used).
8. Recommendations sorted by severity AND effort (low-effort high-impact items first).

**Must not do:**

1. Open a PR from this skill. Read-only.
2. Push. Read-only.
3. Auto-fix anything. Recommendations are pointers to other skills, not actions.
4. Modify any file outside `.temp/`.
5. Quote secrets verbatim (security findings name the type / file / line; never the bytes).
6. Pad findings to hit "10". If there are fewer than 10 real findings, surface fewer (and surface that the repo is in good shape).
7. Re-litigate every TODO comment. TODOs are sometimes tech debt, usually not. Don't pad.
8. Audit without running the repo's own tooling first.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- 600 findings of varying severity dumped together. Use Top-10 + per-dimension organization.
- "TODO comments are tech debt" — sometimes; usually not. Don't pad.
- Auditing without running the repo's own tooling first.
- Skipping the "what's healthy" section. Engineers need to know what's working.
- Opening a PR from this skill. Never. Read-only.

## Output

| Path | Content |
| --- | --- |
| `.temp/reports/audit-<slug>.md` | The full audit report |
| `.temp/reports/audit-<slug>-evidence/inventory.md` | Repo inventory snapshot |
| `.temp/reports/audit-<slug>-evidence/<dimension>.md` | Per-dimension findings |
| `.temp/reports/audit-<slug>-evidence/healthy.md` | "What's healthy" findings |
| `.temp/reports/audit-<slug>-evidence/methodology.md` | Tools used, scope, time |
| `.temp/reports/audit-<slug>-evidence/per-finding/<id>.md` | Per-finding deep evidence (when needed) |

See `references/output-format.md` and `references/artifact-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Strategic-auditor persona + status banner + posture |
| `references/workflow.md` | Detailed Phase 0-7 stage list with checkpoints |
| `references/modes.md` | What `--auto` / `-i` mean for `audit-repo` (no `--fix`) |
| `references/interaction-contract.md` | Canonical interaction contract (mirrored byte-identical from adk-core) |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 3-4 worked examples (full audit, scoped audit, dimension subset, M&A audit) |
| `references/output-format.md` | audit-<slug>.md / per-dimension shapes |
| `references/artifact-format.md` | `.temp/reports/audit-<slug>(-evidence)/` canonical paths |
| `references/validator.md` | Per-phase gates (inventory before dimension passes; tools before heuristics) |
| `references/how-it-works.md` | Mermaid: phase flow, dimension fan-out, aggregation funnel |
| `references/clarifying-questions.md` | Under -i; defaults under --auto |
| `references/inventory.md` | Detection rules: language / framework / dep manager / test / lint / CI / observability |
| `references/dimension-passes.md` | Per-dimension audit checklists (the 6 dimensions) |
| `references/aggregation.md` | Top-10 selection rule + per-dimension grouping + "what's healthy" inclusion rules |

## Additional links

- The repo's `SECURITY.md` / `CONTRIBUTING.md` / `CODEOWNERS` / `AGENTS.md` / `CLAUDE.md` / `.cursorrules` (always; cheap to read).
- Documented architecture diagrams (look for `docs/architecture.md`, `docs/adr/`, etc.).
- The repo's CI workflows (`.github/workflows/`, `.gitlab-ci.yml`, etc.) — informs the quality dimension.
- If the repo is a service, `~/.config/adk/datadog.md` for observability context (used by performance dimension).
