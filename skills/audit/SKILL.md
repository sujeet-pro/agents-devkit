---
name: audit
description: Category router for systematic audits of an entire codebase or a public website - covering security, performance, code quality, dependency health, accessibility, SEO, and UX as relevant. Use when the deliverable is an audit report (not a single PR review). Picks one of adk-audit-repo, adk-audit-site.
metadata:
  category: audit
  kind: router
  layer: 7
  modes: [auto]
---

# ADK Audit (Category Router)

Routes any "produce a structured audit report" intent to the right audit task. Activate one of the listed task skills below; do not audit directly from this router.

## When to use this category

- A repository needs a multi-dimensional health assessment (security, performance, quality, dependencies, test coverage, architecture).
- A public website or web app needs a multi-dimensional audit (performance / Core Web Vitals, accessibility, SEO, UX, basic security headers).
- Findings must be tiered, evidence-backed, and traceable to specific files or URLs.

## When NOT to use this category

- Reviewing a single PR or branch -> `@adk:review-pr` (a.k.a. `adk-review-pr`) / `@adk:review-local` (a.k.a. `adk-review-local`)
- Reviewing a single doc -> `@adk:docs-review` (a.k.a. `adk-docs-review`)
- Researching one technical question -> `@adk:plan-research` (a.k.a. `adk-plan-research`)
- Building or fixing the issues found in an audit -> `@adk:build-feature` (a.k.a. `adk-build-feature`) / `@adk:build-refactor` (a.k.a. `adk-build-refactor`)

## Shared workflow

Every task in this category honors the same six steps. The task skills tailor the content of each step.

1. **Confirm intent** - identify the target (repo path or URL), the dimensions to audit, the depth (`quick` / `standard` / `deep`), and the deliverable destination (markdown report under `.temp/reports/<slug>.md` by default).
2. **Inventory** - capture the surface: file tree, languages, frameworks, build tools, deps (repo) - or page tree, key user flows, third-party scripts (site).
3. **Run dimensions** - execute the chosen audit dimensions in parallel where independent. Each dimension produces its own findings.
4. **Aggregate** - merge findings into a single report, ordered by severity, deduplicated, with per-dimension subsections.
5. **Validate** - sanity check that every finding has a file path / URL / DOM selector and is reproducible.
6. **Report** - findings-first markdown; per-finding evidence and recommended fix; explicit "out of scope" list.

## Task selection

| Task skill | Use when | Do NOT use when |
| --- | --- | --- |
| `@adk:audit-repo` (a.k.a. `adk-audit-repo`) | Target is a code repository checked out locally; covers security, perf, quality, deps, tests, architecture | Target is a deployed website - use audit-site |
| `@adk:audit-site` (a.k.a. `adk-audit-site`) | Target is a publicly reachable URL; covers performance, accessibility, SEO, UX, basic security headers | Target is local code - use audit-repo |

## Severity ladder

Same labels as `@adk:review` (a.k.a. `adk-review`):

| Label | Audit meaning |
| --- | --- |
| `Blocker` | Security hole, data loss risk, or contract breaking. Fix before next release. |
| `Critical` | Strongly impacts users (perf cliff, accessibility failure, broken core flow). |
| `Should Have` | Meaningful quality gain; defer with justification. |
| `May Have` | Optional improvement. |
| `Nitpick` | Style / convention only. |
| `Question` | Auditor cannot tell from outside; needs owner clarification. |

## Output destination

Audit reports go under `.temp/reports/<slug>.md` by default. Promote to a tracked path (`docs/audits/...`) only when the report is a deliverable.

## Activation

Once you have picked a task, load `adk-audit-<task>` and follow it. Each task skill is fully standalone - everything it needs is in its own folder.

## Anti-patterns

- Auditing inside this router. Always hand off to a task skill.
- Findings without evidence (no file path, no URL, no measurement).
- "Best practice" findings the codebase does not actually need.
- Mixing implementation work into the audit. Audits report; fixes happen in ``@adk:build` (a.k.a. `adk-build`)-*`.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/audit-clarifying-questions.md`) and reports the choices.

1. **Is the target a code repo (local checkout) or a deployed website (URL)?** — _How to pick:_ Repo → adk-audit-repo. Website → adk-audit-site.

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `audit-routing-decision` — Inline message.

**Artifact path:** (none)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/audit-clarifying-questions.md`) and reports the choices.

1. **Is the target a code repo (local checkout) or a deployed website (URL)?** — _How to pick:_ Repo → adk-audit-repo. Website → adk-audit-site.

## Default vs detailed output

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `audit-routing-decision` — Inline message.

**Artifact path:** (none)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/audit-anti-patterns.md` | Things to avoid when running this skill. |
| `references/audit-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/audit-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/audit-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/audit-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/audit-persona.md` | The agent persona that drives this skill. |
| `references/audit-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
