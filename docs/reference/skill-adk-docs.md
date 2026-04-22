---
title: 'adk-docs'
description: 'Category router for technical documentation work - writing or reviewing READMEs, runbooks, API docs, ADRs, onboarding guides, migration guides, changelogs, and similar. Use when the deliverable is a markdown document (or its destination publish format), not code or a spec. Picks one of adk-docs-write, adk-docs-review.'
skill_name: adk-docs
category: router
---
# ADK Docs (Category Router)

Routes any "produce or improve a documentation artifact" intent to the right docs task. Activate one of the listed task skills below; do not draft directly from this router.

## When to use this category

- Authoring a new doc: README, runbook, API reference, onboarding guide, migration guide, ADR, tech-radar entry, RFC follow-up.
- Reviewing an existing doc for accuracy, freshness, structure, or readability.
- Refreshing project docs after a code change so they no longer drift from reality.

## When NOT to use this category

- Writing a spec or PRD before implementation -> `adk-plan-spec`
- Writing the *commit message* / PR description / changelog from a diff -> `adk-publish-commit`
- Designing UI copy for a product surface -> `adk-frontend-design`
- Reviewing code (not docs) -> `adk-review`

## Shared workflow

Every task in this category honors the same five steps. The task skills tailor the content of each step.

1. **Confirm intent** - identify doc target (file path or destination), audience (engineer, operator, user), tone, and success criteria.
2. **Gather** - read the source-of-truth (code, configs, diffs, prior version, related docs). Pull repo evidence first.
3. **Draft / critique** - produce the markdown (write) or the findings-first review (review).
4. **Validate** - run a checklist appropriate to the doc type (links, code blocks, examples actually run, freshness vs. code).
5. **Report** - lead with the doc path or the headline finding; show what changed; flag remaining open questions.

## Task selection

| Task skill | Use when | Do NOT use when |
| --- | --- | --- |
| `adk-docs-write` | Authoring a new doc, expanding an existing one, or refreshing it from current code | Critiquing an existing doc - use review |
| `adk-docs-review` | Existing doc must be checked for accuracy, structure, completeness, or freshness | The doc does not exist yet - write it first |

## Doc-type cheatsheet

| Doc type | Primary template content |
| --- | --- |
| README | Purpose, quick start, install, usage, contributing, license |
| Runbook | Trigger, symptoms, immediate mitigation, root-cause checks, recovery steps |
| API reference | Endpoint or function signature, request/response, errors, examples |
| ADR | Context, decision, alternatives, consequences |
| Onboarding | Day-1 checklist, environment setup, first PR, who to ask |
| Migration guide | Why, scope, breaking changes, before/after examples, rollback |
| Tech radar entry | Item, ring (adopt / trial / assess / hold), rationale, signals |

## Markdown rules

- Cross-platform-safe markdown only: headings, bullets, numbered lists, fenced code blocks, tables, links, blockquotes.
- Avoid HTML-only structures and renderer-specific extensions when the doc may be pasted into PR comments or external tools.
- Code blocks must specify a language tag.
- Every claim about runtime behavior cites a file path or command output.

## Activation

Once you have picked a task, load `adk-docs-<task>` and follow it. Each task skill is fully standalone - everything it needs is in its own folder.

## Anti-patterns

- Drafting docs inside this router. Always hand off to a task skill.
- Documenting wished-for behavior. Read the code first.
- Padding with "this guide explains how to..." preamble. Lead with content.
- Letting examples bit-rot - if you cite a command, it must work as written.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/docs-clarifying-questions.md`) and reports the choices.

1. **Is the doc new or existing?** — _How to pick:_ New → adk-docs-write. Existing (suspect drift, want quality bar, audit) → adk-docs-review.

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `docs-routing-decision` — Inline message.

**Artifact path:** (none)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/docs-clarifying-questions.md`) and reports the choices.

1. **Is the doc new or existing?** — _How to pick:_ New → adk-docs-write. Existing (suspect drift, want quality bar, audit) → adk-docs-review.

## Default vs detailed output

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `docs-routing-decision` — Inline message.

**Artifact path:** (none)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/docs-anti-patterns.md` | Things to avoid when running this skill. |
| `references/docs-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/docs-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/docs-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/docs-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/docs-persona.md` | The agent persona that drives this skill. |
| `references/docs-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
