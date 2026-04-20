---
title: 'adk-audit'
description: 'Category router for systematic audits of an entire codebase or a public website - covering security, performance, code quality, dependency health, accessibility, SEO, and UX as relevant. Use when the deliverable is an audit report (not a single PR review). Picks one of adk-audit-repo, adk-audit-site.'
skill_name: adk-audit
category: router
---

# adk-audit

Category router for systematic audits of an entire codebase or a public website - covering security, performance, code quality, dependency health, accessibility, SEO, and UX as relevant. Use when the deliverable is an audit report (not a single PR review). Picks one of adk-audit-repo, adk-audit-site.

## Skill body

# ADK Audit (Category Router)

Routes any "produce a structured audit report" intent to the right audit task. Activate one of the listed task skills below; do not audit directly from this router.

## When to use this category

- A repository needs a multi-dimensional health assessment (security, performance, quality, dependencies, test coverage, architecture).
- A public website or web app needs a multi-dimensional audit (performance / Core Web Vitals, accessibility, SEO, UX, basic security headers).
- Findings must be tiered, evidence-backed, and traceable to specific files or URLs.

## When NOT to use this category

- Reviewing a single PR or branch -> `adk-review-pr` / `adk-review-local`
- Reviewing a single doc -> `adk-docs-review`
- Researching one technical question -> `adk-plan-research`
- Building or fixing the issues found in an audit -> `adk-build-feature` / `adk-build-refactor`

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
| `adk-audit-repo` | Target is a code repository checked out locally; covers security, perf, quality, deps, tests, architecture | Target is a deployed website - use audit-site |
| `adk-audit-site` | Target is a publicly reachable URL; covers performance, accessibility, SEO, UX, basic security headers | Target is local code - use audit-repo |

## Severity ladder

Same labels as `adk-review`:

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
- Mixing implementation work into the audit. Audits report; fixes happen in `adk-build-*`.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |

<!-- adk:references:end -->

## References shipped with this skill

- `references/anti-patterns.md`
- `references/constitution.md`
