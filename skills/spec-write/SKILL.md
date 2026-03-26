---
name: spec-write
description: "Use when defining what to build through formal feature specifications that separate intent from implementation, with interactive clarification and acceptance criteria"
user_invocable: true
arguments:
  - name: feature
    description: "Description of the feature to specify"
    required: true
  - name: scope
    description: "Scope: greenfield, brownfield, enhancement (default: greenfield)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence (default: markdown)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Feature Specification

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Specs define the "what" and "why" — never the "how." No technology choices, no implementation details, no framework references. Those belong in `/devkit:plan-write`.

## Preflight

Before starting specification work, run:

`zsh scripts/check-skill-deps.zsh spec-write format=<format>`

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

1. **Summary** — one-paragraph feature overview
2. **Problem Statement** — what pain this solves, with evidence if available
3. **User Stories** — prioritized (P1/P2/P3), each independently testable with Given/When/Then acceptance scenarios
4. **Functional Requirements** — measurable, technology-agnostic, user-focused
5. **Non-Functional Requirements** — performance, security, accessibility expectations
6. **Edge Cases & Error Scenarios** — explicit handling for failure modes
7. **Out of Scope** — what this spec explicitly does NOT cover
8. **Assumptions** — what the spec takes for granted
9. **Clarifications** — captured Q&A from Phase 2
10. **Review & Acceptance Checklist** — verifiable criteria for spec completeness

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

## Adjacent Skills

- `/devkit:plan-write` for turning spec into implementation plan
- `/devkit:project-init` for full project bootstrapping
- `/devkit:checklist-generate` for requirements quality validation
- `/devkit:spec-analyze` for cross-artifact consistency checking
