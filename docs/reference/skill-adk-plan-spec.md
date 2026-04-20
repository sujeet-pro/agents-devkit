---
title: 'adk-plan-spec'
description: 'Author a structured spec - PRD, RFC, functional spec, or technical spec - with goals, non-goals, requirements, constraints, success criteria, and open questions. Use when implementation must be preceded by a written spec that the team can review, comment on, and align around. Do not use for short implementation plans (use adk-plan-roadmap) or for architectural design write-ups (use adk-plan-design).'
skill_name: adk-plan-spec
category: task
---

# adk-plan-spec

Author a structured spec - PRD, RFC, functional spec, or technical spec - with goals, non-goals, requirements, constraints, success criteria, and open questions. Use when implementation must be preceded by a written spec that the team can review, comment on, and align around. Do not use for short implementation plans (use adk-plan-roadmap) or for architectural design write-ups (use adk-plan-design).

## Skill body

# ADK Plan / Spec

Standalone task skill under the `adk-plan` category router. Turns a settled direction into a written spec that the team can review and commit to.

## When to use

- A new feature or system needs a PRD before engineering picks it up.
- A change with cross-team impact needs an RFC for review.
- A non-trivial backend or integration needs a technical spec.
- The deliverable is a markdown doc, not code.

## When NOT to use

- Direction is still ambiguous -> `adk-plan-brainstorm` first.
- The work is feature-scale; only a short ordered plan is needed -> `adk-plan-roadmap`.
- The deliverable is an architecture / system design -> `adk-plan-design`.
- The spec is for an existing public API doc -> `adk-docs-write`.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<topic>` | yes | What the spec covers |
| `<spec type>` | optional | `prd` / `rfc` / `functional` / `technical` (defaults from context) |
| `<output path>` | optional | Defaults to `.temp/drafts/spec-<slug>.md` |
| `<scope>` | optional | Path to limit repo inspection |
| `--auto` | optional | Skip approval gate |

## Workflow

1. **Confirm intent** - restate topic, spec type, target audience, and destination. Approval gate unless `--auto`.
2. **Gather context** - read related code, prior specs, design docs, and any brainstorm outputs. Capture `currentState` and `targetState` from evidence.
3. **Draft** - write the spec section by section using the template below. Mark unknowns explicitly.
4. **Self-review** - check against the validation list below.
5. **Report** - return the file path, a 3-bullet TL;DR, and the list of remaining open questions.

## Spec templates

Pick one based on type. Each section is required; if a section truly does not apply, write `N/A` with a one-line reason.

### PRD (Product Requirements)

```markdown
# <Topic> - PRD

## TL;DR
<3 bullets max>

## Background
<why this exists, who asked, what is true today>

## Goals
- <user / business outcome 1>
- <user / business outcome 2>

## Non-Goals
- <explicitly out of scope>

## Users / Personas
<who will use this and how>

## Requirements
### Must Have
- <requirement>
### Should Have
- <requirement>
### Could Have
- <requirement>

## Success Metrics
- <measurable outcome>

## Open Questions
- <question>

## Risks & Mitigations
- <risk> - <mitigation>
```

### RFC (Cross-team Change)

```markdown
# <Topic> - RFC

## TL;DR
<3 bullets>

## Motivation
<problem statement>

## Proposal
<the change in 1-2 paragraphs>

## Detailed Design
<sections as needed: API, data model, migration, rollout>

## Alternatives Considered
- <alternative> - <why rejected>

## Drawbacks
- <known cost>

## Open Questions
- <question>

## Adoption Plan
<how teams pick this up; deprecation if relevant>
```

### Functional / Technical Spec

```markdown
# <Topic> - Spec

## TL;DR
<3 bullets>

## Context
<state today, with file/URL references>

## Scope
- In scope: <bullets>
- Out of scope: <bullets>

## Requirements
- <requirement> [Must / Should / May]

## Design
<sections as needed: components, sequence, data shape, errors>

## Validation
- <how we will verify each requirement>

## Open Questions
- <question>

## Dependencies
- <upstream / downstream>
```

## Validation list

- Every requirement is testable or verifiable.
- Goals and non-goals are explicit and disjoint.
- Open questions are separated from settled decisions.
- Source-of-truth references (file paths, URLs) are concrete.
- TL;DR is at the top and stands alone.

## Output format

```
## Spec drafted: <type>
- File: <path>
- Topic: <topic>
- TL;DR:
  - <bullet>
  - <bullet>
  - <bullet>
- Open questions: <count>

Want a deeper look at any section?
```

## Anti-patterns

- Mixing requirements and design choices in the same bullets.
- Treating "best practice" as a requirement without a measurable outcome.
- Hiding open questions inside the body. Surface them in their section.
- Padding with "this section will describe..." preamble.
- Drafting code in the spec. Save it for `adk-build-feature`.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/working-artifacts.md` | The .temp/ rule for intermediate artifacts. |

<!-- adk:references:end -->

## References shipped with this skill

- `references/anti-patterns.md`
- `references/constitution.md`
- `references/examples.md`
- `references/output-format.md`
- `references/persona.md`
- `references/working-artifacts.md`
