---
title: 'adk-plan-spec'
description: 'Author a structured spec - PRD, RFC, functional spec, or technical spec - with goals, non-goals, requirements, constraints, success criteria, and open questions. Use when implementation must be preceded by a written spec that the team can review, comment on, and align around. Do not use for short implementation plans (use adk-plan-roadmap) or for architectural design write-ups (use adk-plan-design).'
skill_name: adk-plan-spec
category: task
---
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
4. **Validate (per `plan-spec-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/plan-spec-<slug>-validator.md` before the final report.
5. **Self-review** - check against the validation list below.
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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-spec-clarifying-questions.md`) and reports the choices.

1. **Which spec type do you need: PRD (product), RFC (engineering proposal), functional spec (what), or technical spec (how)?** — _How to pick:_ PRD = stakeholder-facing, focuses on user value + acceptance criteria. RFC = peer-reviewed proposal, focuses on trade-offs. Functional = what behavior. Technical = how to build it.
2. **Who is the audience and what decision will they make?** — _How to pick:_ Engineering implementers → technical detail. PMs/leadership → outcome and trade-offs. Reviewers → comparison vs alternatives.
3. **What are the must-have requirements vs nice-to-haves?** — _How to pick:_ List 3-7 must-haves. Nice-to-haves go in a separate section so they do not block sign-off.

**Default report:** Spec markdown using the doc-type template + a one-paragraph TL;DR at the top.

**Detailed report (on request or `--verbose`):** Add: comparison table vs alternatives, sequence/state diagrams for non-trivial flows, error matrix, rollout plan, success metrics.

**Artifact:** `spec-document` — Markdown spec. Sections: TL;DR, Background, Goals, Non-goals, Requirements (testable), Interfaces, Acceptance Criteria, Open Questions, Risks, Rollout.

**Artifact path:** .temp/drafts/spec-<slug>.md (promote to docs/specs/ or a confluence page when signed off)

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/plan-spec-multi-repo.md` for full handling.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-spec-clarifying-questions.md`) and reports the choices.

1. **Which spec type do you need: PRD (product), RFC (engineering proposal), functional spec (what), or technical spec (how)?** — _How to pick:_ PRD = stakeholder-facing, focuses on user value + acceptance criteria. RFC = peer-reviewed proposal, focuses on trade-offs. Functional = what behavior. Technical = how to build it.
2. **Who is the audience and what decision will they make?** — _How to pick:_ Engineering implementers → technical detail. PMs/leadership → outcome and trade-offs. Reviewers → comparison vs alternatives.
3. **What are the must-have requirements vs nice-to-haves?** — _How to pick:_ List 3-7 must-haves. Nice-to-haves go in a separate section so they do not block sign-off.

## Default vs detailed output

**Default report:** Spec markdown using the doc-type template + a one-paragraph TL;DR at the top.

**Detailed report (on request or `--verbose`):** Add: comparison table vs alternatives, sequence/state diagrams for non-trivial flows, error matrix, rollout plan, success metrics.

**Artifact:** `spec-document` — Markdown spec. Sections: TL;DR, Background, Goals, Non-goals, Requirements (testable), Interfaces, Acceptance Criteria, Open Questions, Risks, Rollout.

**Artifact path:** .temp/drafts/spec-<slug>.md (promote to docs/specs/ or a confluence page when signed off)

## Multi-repo context

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/plan-spec-multi-repo.md` for full handling.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/plan-spec-anti-patterns.md` | Things to avoid when running this skill. |
| `references/plan-spec-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/plan-spec-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/plan-spec-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/plan-spec-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/plan-spec-multi-repo.md` | How to consume context from extra cloned or local-path repos. |
| `references/plan-spec-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/plan-spec-persona.md` | The agent persona that drives this skill. |
| `references/plan-spec-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/plan-spec-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/plan-spec-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
