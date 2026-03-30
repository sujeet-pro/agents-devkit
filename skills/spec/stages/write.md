# Feature Specification

Specs define the "what" and "why" -- never the "how." No technology choices, no implementation details, no framework references. Those belong in `/plan`.

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Understand requirements, scan existing plans and context; Focused research on chosen approach, proposal at ./temp/proposal/ |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes; Iterate on proposal with user feedback |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Execute the planning workflow |
| 5. Validate & Learn | yes | Validate plan completeness and feasibility |

## Preflight

Before starting specification work, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Spec Storage

Save all specs to `.temp/specs/<feature-slug>/spec.md` in the current working directory. If `.temp/` does not exist, create it and ensure it is listed in `.gitignore`.

## Required Child Agents

Run at least these child agents in parallel:

- **Domain analyst**: reads the codebase to understand existing domain model, patterns, and constraints. Produces a domain brief with entity inventory and boundary map.
- **Requirements researcher** (`research-agent`): researches similar features in comparable products, identifies edge cases and user expectations. Produces a research brief with competitive analysis and edge case inventory.
- **Spec reviewer** (`doc-reviewer`): reviews the draft spec for completeness, clarity, testability, and consistency. Flags requirements that are ambiguous, untestable, or conflicting.

## Phase 1: Feature Intake

Capture what the user wants to build in plain language. Do NOT ask about technology.

- What problem does this solve?
- Who is the user?
- What does success look like?

Record the answers as the foundation for the specification.

## Phase 2: Interactive Clarification

Max 5 questions, prioritized by (Impact x Uncertainty). Present one at a time:

```text
## Clarification [N/5] - [category: scope|security|UX|data|behavior|edge-case]

Question: <specific question about unclear requirement>

Why this matters: <impact if left undefined>

Your answer (or "skip" to let AI decide):
```

Categories: scope, security/privacy, UX flow, data model, behavior edge cases, integration boundaries.

Record answers in the spec's Clarifications section.

## Phase 3: Spec Draft

Launch child agents to analyze the domain and research comparable features. Merge their findings, then generate the specification with these sections:

1. **Summary** -- one-paragraph feature overview
2. **Problem Statement** -- what pain this solves, with evidence if available
3. **User Stories** -- prioritized (P1/P2/P3), each independently testable with Given/When/Then acceptance scenarios
4. **Functional Requirements** -- measurable, technology-agnostic, user-focused
5. **Non-Functional Requirements** -- performance, security, accessibility expectations
6. **Edge Cases & Error Scenarios** -- explicit handling for failure modes
7. **Out of Scope** -- what this spec explicitly does NOT cover
8. **Assumptions** -- what the spec takes for granted
9. **Clarifications** -- captured Q&A from Phase 2
10. **Review & Acceptance Checklist** -- verifiable criteria for spec completeness

## Phase 4: Interactive Review

Launch the spec reviewer agent against the draft. Consolidate findings with the draft, then present each spec section for user approval:

```text
## Section [N/10] - <section name>

<section content>

Action: [A]ccept | [E]dit | [R]eject & rewrite | [S]kip
```

### Actions

- Accept: lock the section as-is.
- Edit: let the user revise the section content. Stay in the edit loop until the user accepts or rejects the revised version.
- Reject & rewrite: regenerate the section from scratch based on user feedback.
- Skip: defer to the end. After all other sections are processed, return to skipped items for a final decision.

### Loop Rules

1. Process sections in order (1 through 10).
2. If the user says "accept all remaining", lock all unprocessed sections.
3. If the user says "reject all remaining", flag all unprocessed sections for rewrite.

## Phase 5: Acceptance Checklist

Walk the user through the acceptance checklist:

```text
## Checklist [N/total]

Criterion: <verifiable criterion>
Status: [pass] Met | [fail] Not met (describe gap) | [?] Unclear
```

If any criterion is not met, loop back to the relevant section for revision before finalizing.

## Output

Spec saved to `.temp/specs/<feature-slug>/spec.md`. Display summary:

```text
## Specification Complete

Feature: <name>
User Stories: N (P1: N, P2: N, P3: N)
Acceptance Criteria: N
Edge Cases: N
Clarifications Captured: N
```
