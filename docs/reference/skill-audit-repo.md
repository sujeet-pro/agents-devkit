---
title: 'audit-repo'
description: 'Audit a code repository across security, performance, code quality, dependencies, test coverage, and architecture - producing a single severity-tiered report with file-anchored evidence per finding.'
artifact_kind: skill
skill_name: audit-repo
category: audit
---
# audit-repo

Audit a code repository across security, performance, code quality, dependencies, test coverage, and architecture - producing a single severity-tiered report with file-anchored evidence per finding. Use when the deliverable is a multi-dimensional health report on a checked-out repo, not a single-PR review or a doc review. Do not use to audit a deployed website (use adk-audit-site) or to fix the issues found (use adk-build-* skills).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-audit-repo` form via `agents-skills/`.

```text
/adk:audit-repo            # interactive run (Claude Code)
/adk:audit-repo --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-audit-repo` (resolved through the
`agents-skills/adk-audit-repo/` symlink).

## Source

Direct from `skills/audit-repo/SKILL.md` — this page is auto-generated.

Standalone task skill under the `@adk:audit` (a.k.a. `adk-audit`) category router. Inspects a checked-out repository across multiple dimensions in parallel and produces one consolidated report with severity-tiered findings, each anchored to a file path.

## When to use

- Health check before a release or handoff.
- Pre-acquisition / pre-onboarding code review of a repo as a whole.
- Periodic hygiene audit (security, perf, deps, test coverage, architecture drift).
- The deliverable is a markdown audit report at `.temp/reports/<slug>.md`.

## When NOT to use

- Single PR or local-branch review -> `@adk:review-pr` (a.k.a. `adk-review-pr`) / `@adk:review-local` (a.k.a. `adk-review-local`)
- Single doc review -> `@adk:docs-review` (a.k.a. `adk-docs-review`)
- Deployed-website audit -> `@adk:audit-site` (a.k.a. `adk-audit-site`)
- Fixing the findings -> `@adk:build-feature` (a.k.a. `adk-build-feature`) / `@adk:build-refactor` (a.k.a. `adk-build-refactor`) / `@adk:build-deps` (a.k.a. `adk-build-deps`)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<repo path>` | yes | Local checkout root (default: cwd) |
| `<dimensions>` | optional | Subset of: `security`, `performance`, `quality`, `dependencies`, `tests`, `architecture` (default: all) |
| `<depth>` | optional | `quick` / `standard` (default) / `deep` |
| `<output path>` | optional | Defaults to `.temp/reports/audit-repo-<slug>-<date>.md` |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate repo, dimensions, depth, output. Approval gate unless `--auto`.
2. **Inventory** - capture: file tree summary, primary languages, frameworks, build tools, package managers, test frameworks, total LOC, recent commit cadence.
3. **Run dimensions in parallel** - each dimension produces its own findings list:
   - **Security**: secrets in git, dep advisories, auth/n+z patterns, SQL/HTML/XSS sinks, CORS, env handling.
   - **Performance**: hot paths, N+1, sync IO in async paths, large bundles, build cache hygiene.
   - **Quality**: linter/typechecker output, duplicated code (~5%+ duplicate threshold), cyclomatic hotspots, dead code.
   - **Dependencies**: outdated direct deps, deprecated packages, unused deps, license risks.
   - **Tests**: framework presence, coverage where measurable, test-to-code ratio per package, flaky markers.
   - **Architecture**: module boundaries, circular deps, layering violations, drift from documented architecture.
4. **Aggregate** - merge findings into one ordered list. Deduplicate. Group by dimension under each severity.
5. **Validate** - reread each finding against the code to confirm it is real. Drop low-evidence findings.
6. **Report** - findings-first markdown using the template below.

## Severity ladder

| Label | Audit meaning |
| --- | --- |
| `Blocker` | Security hole, data loss risk, broken contract. Fix before next release. |
| `Critical` | Strongly impacts users / operators (perf cliff, accessibility failure on a code surface, broken core flow). |
| `Should Have` | Meaningful quality gain; defer with justification. |
| `May Have` | Optional improvement. |
| `Nitpick` | Style or convention. |
| `Question` | Auditor cannot tell from outside; needs owner clarification. |

## Finding template

```markdown
### [<Severity>] <One-line summary> (<dimension>)
- **File**: `path/to/file.ext:LINE-LINE` (or `manifest`, `lockfile`, `config`)
- **Issue**: <2-3 sentence explanation>
- **Evidence**: <quoted snippet, command output, or reproducible signal>
- **Suggested fix**: <concrete recommendation; route to ``@adk:build` (a.k.a. `adk-build`)-*` if implementation is needed>
- **Why this severity**: <one sentence>
```

## Report template

```markdown
# Repo Audit: <repo name>

## Summary
- Inventory: <languages>, <frameworks>, <package managers>, ~<LOC>
- Dimensions audited: <list>
- Findings: <N> Blocker, <N> Critical, <N> Should Have, <N> May Have, <N> Nitpick, <N> Question

## Top Risks
1. <one-line top risk>
2. <one-line top risk>

## Findings

### Blockers
<finding blocks>

### Critical
<finding blocks>

### Should Have
<finding blocks>

### May Have
<finding blocks>

### Nitpicks
<finding blocks>

### Questions
<finding blocks>

## Per-Dimension Notes
<short per-dimension narrative for context the findings cannot carry>

## Out of Scope
- <items not audited and why>

## Recommended Next Steps
1. <fix Blockers via `adk-build-*` skills>
2. <follow-up audit in <area> after fixes>
```

## Depth modes

| Mode | Behavior |
| --- | --- |
| `quick` | One pass per dimension, ~30 minutes for a small repo, surface-level findings |
| `standard` | Default; deeper grep / read; runs available analyzers (linter, type checker, audit) |
| `deep` | All of standard + sample-based code review of hot files + per-package per-file metrics |

## Anti-patterns

- Findings without a file anchor.
- "Best practice" findings the codebase does not actually need.
- Mixing fixes into the audit. The audit reports; fixes happen via `adk-build-*`.
- Letting nitpicks bury Blockers in the summary.
- Padding the report with restated inventory text - inventory is at the top, once.
- Reporting "no findings" without listing what was inspected. Show the work.

## Examples

```
adk-audit-repo --dimensions security,dependencies --depth standard
```

```
adk-audit-repo /path/to/repo --depth deep --output .temp/reports/audit-repo-acme-2026-04.md
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/audit-repo-clarifying-questions.md`) and reports the choices.

1. **Which dimensions to audit (security / performance / quality / dependencies / tests / architecture / all)?** — _How to pick:_ All for new audits. Narrow when re-auditing a specific area or under time pressure.
2. **Depth: quick / standard / deep?** — _How to pick:_ Quick = surface scan, ~30 min. Standard = run available analyzers (linter/typechecker/audit). Deep = sample-based code review of hot files + per-package metrics.
3. **Are there extra repos to clone for cross-repo context (mono-repo subprojects, shared libs)?** — _How to pick:_ Pass URLs or paths. Each gets its own findings section in the report.

**Default report:** Top-of-file summary (counts per severity, top 3 risks) + severity-grouped findings + per-dimension notes + out-of-scope.

**Detailed report (on request or `--verbose`):** Add: file tree + LOC/language inventory, every analyzer command + output, suppressed findings list with reason, recommended fix order with effort estimate.

**Artifact:** `audit-report` — Markdown report.

**Artifact path:** .temp/reports/audit-repo-<slug>-<date>.md (raw analyzer output in .temp/notes/audit-<slug>/<dimension>.txt)

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/audit-repo-multi-repo.md` for full handling.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/audit-repo-clarifying-questions.md`) and reports the choices.

1. **Which dimensions to audit (security / performance / quality / dependencies / tests / architecture / all)?** — _How to pick:_ All for new audits. Narrow when re-auditing a specific area or under time pressure.
2. **Depth: quick / standard / deep?** — _How to pick:_ Quick = surface scan, ~30 min. Standard = run available analyzers (linter/typechecker/audit). Deep = sample-based code review of hot files + per-package metrics.
3. **Are there extra repos to clone for cross-repo context (mono-repo subprojects, shared libs)?** — _How to pick:_ Pass URLs or paths. Each gets its own findings section in the report.

## Default vs detailed output

**Default report:** Top-of-file summary (counts per severity, top 3 risks) + severity-grouped findings + per-dimension notes + out-of-scope.

**Detailed report (on request or `--verbose`):** Add: file tree + LOC/language inventory, every analyzer command + output, suppressed findings list with reason, recommended fix order with effort estimate.

**Artifact:** `audit-report` — Markdown report.

**Artifact path:** .temp/reports/audit-repo-<slug>-<date>.md (raw analyzer output in .temp/notes/audit-<slug>/<dimension>.txt)

## Multi-repo context

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/audit-repo-multi-repo.md` for full handling.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/audit-repo-anti-patterns.md` | Things to avoid when running this skill. |
| `references/audit-repo-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/audit-repo-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/audit-repo-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/audit-repo-multi-repo.md` | How to consume context from extra cloned or local-path repos. |
| `references/audit-repo-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/audit-repo-persona.md` | The agent persona that drives this skill. |
| `references/audit-repo-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/audit-repo-review-comment-format.md` | Standard finding format with stable IDs and severities. |
| `references/audit-repo-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/audit-repo-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->


## Related skills

- [`audit`](./skill-audit.md) — `@adk:audit` (a.k.a. `adk-audit`)
- [`audit-site`](./skill-audit-site.md) — `@adk:audit-site` (a.k.a. `adk-audit-site`)
- [`build`](./skill-build.md) — `@adk:build` (a.k.a. `adk-build`)
- [`build-deps`](./skill-build-deps.md) — `@adk:build-deps` (a.k.a. `adk-build-deps`)
- [`build-feature`](./skill-build-feature.md) — `@adk:build-feature` (a.k.a. `adk-build-feature`)
- [`build-refactor`](./skill-build-refactor.md) — `@adk:build-refactor` (a.k.a. `adk-build-refactor`)
- [`docs-review`](./skill-docs-review.md) — `@adk:docs-review` (a.k.a. `adk-docs-review`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
