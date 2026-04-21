---
name: adk-plan-design
description: Author an architecture or system design - high-level design, low-level design, ADR, or technical design doc - covering components, interfaces, data flow, sequencing, failure modes, and trade-offs. Use when the work is large enough that the team needs an architecture write-up before implementation. Do not use for short implementation plans (use adk-plan-roadmap), product specs (use adk-plan-spec), or UI mockups (use adk-frontend-design).
---

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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **What artifact: HLD (system overview), LLD (component-level detail), ADR (single decision), or migration plan?** — _How to pick:_ HLD = new service or major rewrite. LLD = inside an existing service. ADR = single irreversible decision (DB choice, framework swap). Migration = move from A to B.
2. **Which non-functional requirements are hard constraints (latency, throughput, availability, cost, regulatory)?** — _How to pick:_ List the top 3 with numeric thresholds. Anything below the threshold is a constraint; anything above is a target.
3. **What is the blast radius (single service, multiple services, public API, data model)?** — _How to pick:_ Single service = LLD enough. Multiple services = HLD + per-service LLD. Public API = include API versioning + deprecation plan. Data model = include migration script and rollback.

**Default report:** Design markdown with one mermaid diagram, alternatives table, failure modes, rollout.

**Detailed report (on request or `--verbose`):** Add: component-level interface signatures, sequence diagram per primary flow, capacity/cost calculations, security threat model, observability plan.

**Artifact:** `design-document` — Markdown design doc. Sections: Context, Constraints, Proposal (with diagrams), Alternatives Considered, Failure Modes, Observability, Rollout, Open Questions.

**Artifact path:** .temp/drafts/design-<slug>.md (promote to docs/architecture/ or docs/adr/NNN-<slug>.md when signed off)

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/multi-repo.md` for full handling.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **What artifact: HLD (system overview), LLD (component-level detail), ADR (single decision), or migration plan?** — _How to pick:_ HLD = new service or major rewrite. LLD = inside an existing service. ADR = single irreversible decision (DB choice, framework swap). Migration = move from A to B.
2. **Which non-functional requirements are hard constraints (latency, throughput, availability, cost, regulatory)?** — _How to pick:_ List the top 3 with numeric thresholds. Anything below the threshold is a constraint; anything above is a target.
3. **What is the blast radius (single service, multiple services, public API, data model)?** — _How to pick:_ Single service = LLD enough. Multiple services = HLD + per-service LLD. Public API = include API versioning + deprecation plan. Data model = include migration script and rollback.

## Default vs detailed output

**Default report:** Design markdown with one mermaid diagram, alternatives table, failure modes, rollout.

**Detailed report (on request or `--verbose`):** Add: component-level interface signatures, sequence diagram per primary flow, capacity/cost calculations, security threat model, observability plan.

**Artifact:** `design-document` — Markdown design doc. Sections: Context, Constraints, Proposal (with diagrams), Alternatives Considered, Failure Modes, Observability, Rollout, Open Questions.

**Artifact path:** .temp/drafts/design-<slug>.md (promote to docs/architecture/ or docs/adr/NNN-<slug>.md when signed off)

## Multi-repo context

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/multi-repo.md` for full handling.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/multi-repo.md` | How to consume context from extra cloned or local-path repos. |
| `references/output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |

<!-- adk:references:end -->
