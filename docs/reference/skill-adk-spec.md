---
title: 'adk-spec'
description: 'Write product requirements, technical specifications, API specs, or feature acceptance criteria. Use when defining what to build before planning how'
skill_name: adk-spec
category: task
workflow_tier: full
user_invocable: true
---

# adk-spec

Use `adk-spec` to write product requirements, technical specifications, API specs, or feature acceptance criteria. Use when defining what to build before planning how. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-spec` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<topic>` | free text | required | What the spec should cover |
| `--type` | `prd`, `technical`, `api`, `feature`, `acceptance` | auto-detected | Spec type to produce |
| `--scope` | path | none | Limit context gathering to one area of the codebase |
| `--auto` | flag | off | Skip confirmations, emit the spec without interactive review cycles |
| `--help` | flag | off | Show the skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

### Phase 1: Discover
Understand the problem space. Gather existing specs, related code, prior decisions, and stakeholder constraints.

**Gate**: confirm topic, spec type, intended audience, scope, and when relevant the current state, target state, desired confidence, and artifact preference with the user. Skip if `--auto`.

### Phase 2: Research
Dispatch `adk-research` for technical constraints, prior art, domain standards, and competitor approaches. Check the codebase for existing interfaces, data models, and patterns the spec must align with.

### Phase 3: Define
Write functional requirements, acceptance criteria, and constraints using the type-specific steps in `spec-templates.md` (PRD, technical, API, feature, acceptance). Each requirement must be:
- testable (or explicitly marked aspirational)
- unambiguous (vague language flagged with resolution requests)
- traceable (linked to a stakeholder need or technical constraint)

### Phase 4: Structure
Apply the matching skeleton from `spec-templates.md` and organize requirements into the template:
- **Scope and goals** -- what is being specified and why
- **Non-goals** -- what is explicitly excluded
- **Requirements** -- functional, non-functional, with priority
- **Constraints** -- technical, timeline, compliance
- **Risks and mitigations** -- known risks with proposed responses
- **Open questions** -- unknowns that need stakeholder input, separated from the spec body

### Phase 5: Review
Self-review against a completeness checklist:
- Are all requirements testable?
- Is any language ambiguous?
- Are non-functional requirements covered?
- Are dependencies and assumptions called out?
- Is the spec internally consistent?

**Gate**: present the spec for user review. Skip if `--auto`.

### Phase 6: Deliver
Present the spec with:
- coverage assessment (fully specified vs. gaps)
- open questions for stakeholders
- suggested next step (usually `adk-plan`)
- ask whether deeper detail is needed on any section

See `references/workflow.md` for full phase details, type-specific flows, and edge cases.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/spec-templates.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm scope and spec type before writing; review requirements iteratively; `--auto` skips confirmations but still validates.
- **Plan First** -- discover the problem space, research constraints, define requirements, then structure. No spec without understanding.
- **Brainstorm Before Writing** -- when scope, artifact type, or blast radius is still unsettled, use the brainstorming workflow to close the direction first.
- **Concise by Default** -- requirements are precise and testable, not verbose. Open questions are separated, not buried.
- **Parallel Agentic Teams** -- dispatch `adk-research` for technical constraints, prior art, and domain standards.
- **Principal Engineer Lens** -- challenge scope before accepting it. Ask: is this the right abstraction level? Are we specifying what we need, or what we think we need?

### Persona

**Requirements Architect**

- **Mission**: produce clear, complete, testable specifications that bridge stakeholder intent and implementation reality. Specs define WHAT to build and WHY -- never HOW.
- **Voice**: precise, structured, unambiguous. Flags vague language explicitly rather than resolving it with assumptions.
- **Hard rules**: every requirement must be testable or labeled aspirational; separate WHAT from HOW; do not invent constraints the stakeholder has not stated; do not present inferred requirements as confirmed.
- **Evidence expectations**: domain research cited for claims beyond the codebase; existing code patterns referenced when specs touch established systems; dependencies identified with current integration state.

See `references/persona.md` for the full persona definition.

### When To Use

- before starting implementation, to lock down requirements
- when requirements are unclear or underspecified
- when multiple stakeholders need alignment on scope and behavior
- to define API contracts before building endpoints
- to write acceptance criteria for QA or automated testing
- to capture non-functional requirements (performance, security, accessibility)

### When NOT To Use

- implementation plans (use `adk-plan`)
- post-build documentation (use `adk-write-docs`)
- researching feasibility without a spec deliverable (use `adk-research`)
- reviewing existing code (use `adk-review-local-changes`)

### Pre-flight

Run `python3 scripts/preflight.py` before starting.
- `git` and `python3` must be available on PATH.
- If `--scope` is provided, verify the path exists in the repository.
- Verify the spec-templates reference file is loadable (`references/spec-templates.md`).
- If the topic is too vague to determine a spec type (and `--type` is not provided), stop and ask.

### Interaction Protocol

- **Confirm topic and type** (Phase 1): topic, spec type, audience, scope. Skipped with `--auto`.
- **Section-by-section review** (Phase 3-4): present major sections for feedback; user responds with `ok`, feedback, `skip`, or `done`.
- **Flag ambiguity explicitly**: highlight vague or untestable language and propose concrete alternatives inline.
- **Open questions separated**: unknowns are listed at the end, never buried in the spec body.
- **Suggest next step**: after approval, recommend the logical follow-up (usually `adk-plan`).

### Parallel Agents

| Agent | Dispatched When | Role |
| --- | --- | --- |
| `adk-research` | Phase 2: technical constraints, domain standards, prior art, competitor analysis | Focused research with citations |

### Validation

- every requirement is testable or explicitly marked as aspirational
- ambiguous language is flagged with a resolution request
- non-functional requirements are present where applicable
- dependencies and assumptions are called out
- the spec is internally consistent (no contradictions between sections)
- open questions are separated from the spec body

### Spec: <title>

**Type**: <prd | technical | api | feature | acceptance>
**Audience**: <who reads this>
**Status**: draft

### Scope
<what is being specified>

### Non-Goals
<what is explicitly out of scope>

### Requirements
<numbered, testable requirements with priority>

### Constraints
<technical, timeline, compliance>

### Risks
<known risks with mitigations>

### Open Questions
<unknowns needing stakeholder input>

---

### Coverage Assessment

- Fully specified: <sections>
- Gaps: <sections needing more detail>

### Suggested Next Step

→ `adk-plan` to translate this spec into an implementation plan.

Need deeper detail on any section?
```

### Anti-Patterns / Red Flags

- **Specifying HOW instead of WHAT** -- specs define behavior and constraints, not implementation steps. That is `adk-plan`'s job.
- **Untestable requirements** ("the system should be fast", "the UI should be intuitive") -- quantify or flag as aspirational.
- **Inventing constraints** -- do not add constraints the stakeholder has not stated. Inferred constraints must be labeled.
- **Burying open questions** -- unknowns belong in a dedicated section, not scattered through the spec.
- **Skipping non-functional requirements** -- performance, security, and accessibility requirements are easy to forget and expensive to add later.
- **Mixing confirmed and inferred requirements** -- every requirement must indicate whether it was stated by the stakeholder or inferred from context.

### Related Skills

- `adk-brainstorm` -- settle direction and artifact choice before writing the spec
- `adk-plan` -- translate specs into implementation plans
- `adk-research` -- deep research for spec content
- `adk-write-docs` -- post-build documentation

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-spec <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-spec --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-spec <prompt-text> --auto
```
