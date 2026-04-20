---
title: 'adk-plan-design'
description: 'Author an architecture or system design - high-level design, low-level design, ADR, or technical design doc - covering components, interfaces, data flow, sequencing, failure modes, and trade-offs. Use when the work is large enough that the team needs an architecture write-up before implementation. Do not use for short implementation plans (use adk-plan-roadmap), product specs (use adk-plan-spec), or UI mockups (use adk-frontend-design).'
skill_name: adk-plan-design
category: task
---

# adk-plan-design

Author an architecture or system design - high-level design, low-level design, ADR, or technical design doc - covering components, interfaces, data flow, sequencing, failure modes, and trade-offs. Use when the work is large enough that the team needs an architecture write-up before implementation. Do not use for short implementation plans (use adk-plan-roadmap), product specs (use adk-plan-spec), or UI mockups (use adk-frontend-design).

## Skill body

# ADK Plan / Design

Standalone task skill under the `adk-plan` category router. Produces an architecture or technical design document with components, interfaces, sequencing, failure modes, and trade-offs.

## When to use

- A new subsystem, service, or module needs a high-level design (HLD) before build.
- A specific implementation choice needs a low-level design (LLD) or technical design doc (TDD).
- An ADR is needed to record an architectural decision and the reasoning behind it.
- The change is broad enough that the team needs a shared mental model before code.

## When NOT to use

- Direction is still unsettled -> `adk-plan-brainstorm`
- The deliverable is a product spec, not an architecture -> `adk-plan-spec`
- Feature-scale work needing only an ordered plan -> `adk-plan-roadmap`
- A UI / interaction design -> `adk-frontend-design`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<topic>` | yes | What is being designed |
| `<doc type>` | optional | `hld` / `lld` / `tdd` / `adr` (defaults from context) |
| `<output path>` | optional | Defaults to `.temp/drafts/design-<slug>.md` |
| `<scope>` | optional | Path or system surface to limit inspection |
| `--auto` | optional | Skip approval gate |

## Workflow

1. **Confirm intent** - restate topic, doc type, audience, and destination. Approval gate unless `--auto`.
2. **Gather context** - read related code, existing design docs, prior ADRs, and any spec or brainstorm output. Capture today's architecture as evidence.
3. **Draft** - write the design section by section using the template below. Include at least one diagram in mermaid (delegate to `adk-visualize-diagram` if the diagram is complex).
4. **Trade-off pass** - explicitly list 2-3 alternatives considered and why each was rejected.
5. **Failure-mode pass** - list how the design fails, what observable signals appear, and how recovery works.
6. **Self-review** - check against the validation list below.
7. **Report** - return the file path, a 3-bullet TL;DR, and the list of open decisions.

## Doc templates

### HLD (High-Level Design)

```markdown
# <Topic> - HLD

## TL;DR
<3 bullets>

## Context
<problem, scope, today's architecture - with evidence>

## Goals & Non-Goals
- Goals: <bullets>
- Non-goals: <bullets>

## Architecture
<mermaid component / context diagram>
<short paragraph per major component>

## Data Flow
<mermaid sequence or flow diagram for the primary path>

## Interfaces
- <component A -> component B>: <protocol, payload shape, errors>

## Alternatives Considered
- <alt> - <why rejected>

## Failure Modes
- <failure> - <signal> - <recovery>

## Risks & Open Decisions
- <risk> - <owner / next step>

## Rollout
<how this lands in production>
```

### LLD / TDD (Low-Level / Technical Design)

```markdown
# <Topic> - LLD

## TL;DR
<3 bullets>

## Scope
<one component / module / endpoint>

## Detailed Design
<class / module structure, data shapes, state machine, algorithms>

## Sequence
<mermaid sequence diagram>

## API
<exact signatures, request / response, errors, status codes>

## Data Model
<schema or types>

## Concurrency / Consistency
<locking, transactions, ordering guarantees>

## Failure Modes
- <failure> - <signal> - <recovery>

## Test Plan
- Unit: <what>
- Integration: <what>
- Performance: <if applicable>
```

### ADR (Architecture Decision Record)

```markdown
# ADR-<NNN>: <Decision title>

## Status
<Proposed | Accepted | Superseded by ADR-XXX>

## Context
<what forces are in play>

## Decision
<what we are doing>

## Alternatives
- <alt> - <why rejected>

## Consequences
- Positive: <bullets>
- Negative: <bullets>
- Neutral: <bullets>
```

## Validation list

- Architecture diagram is present and matches the prose.
- Every interface lists protocol, payload shape, and errors.
- At least 2 alternatives are considered with explicit rejection rationale.
- Failure modes include both signal and recovery.
- Open decisions are separated from settled ones.
- Rollout / migration story is concrete (not "TBD").

## Output format

```
## Design drafted: <type>
- File: <path>
- Topic: <topic>
- TL;DR:
  - <bullet>
  - <bullet>
  - <bullet>
- Diagrams: <count>
- Open decisions: <count>

Want a deeper look at any section?
```

## Anti-patterns

- One-option design (no alternatives = no decision).
- Diagrams that contradict the prose.
- Skipping failure modes because "it shouldn't happen".
- Putting implementation code in the design doc. Save for `adk-build-feature`.
- Letting "open decisions" hide a Blocker - either decide or escalate.

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
