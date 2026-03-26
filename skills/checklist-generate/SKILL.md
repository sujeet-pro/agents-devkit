---
name: checklist-generate
description: "Use when you need to validate requirements quality before implementation — generates 'unit tests for English' that check completeness, clarity, and consistency of specifications"
user_invocable: true
arguments:
  - name: source
    description: "Path to specification, PRD, or requirements document"
    required: true
  - name: depth
    description: "Checklist depth: quick (key gaps only), standard, thorough (default: standard)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Requirements Quality Checklist

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

This skill generates "unit tests for English" -- quality checks that validate REQUIREMENTS, not implementation. Every checklist item is a concrete question about the specification itself: is it complete, clear, consistent, and testable? The output is a traceable checklist that catches gaps, ambiguities, and contradictions before a single line of code is written.

## Preflight

Before reading the source document or launching child agents, run:

`zsh scripts/check-skill-deps.zsh checklist-generate source=<source>`

Read the source document to confirm it exists and contains specification content before proceeding. If the source path does not resolve to a readable file, stop and ask the user for a corrected path.

## Checklist Storage

Save all checklists to `.temp/checklists/<source-slug>.md` in the current working directory. If `.temp/checklists/` does not exist, create it. Ensure `.temp/` is listed in `.gitignore`.

## Depth Profiles

- **quick**: key gaps and critical issues only. Target 10-20 checklist items. Focus on completeness and clarity of P1 requirements. Skip non-functional and dependency dimensions unless obvious gaps exist.
- **standard** (default): all nine quality dimensions. Target 30-60 checklist items. Full coverage of happy path, error, and edge cases.
- **thorough**: exhaustive analysis across all dimensions. Target 60-120 checklist items. Includes combinatorial edge cases, cross-requirement interaction checks, and detailed non-functional probes.

## Required Child Agents

When the platform supports child agents, run at least these in parallel:

- **Requirements analyst**: reads the source document end-to-end and evaluates completeness, clarity, and acceptance criteria quality. Produces a findings brief covering dimensions 1, 2, and 4 (Completeness, Clarity, Acceptance Criteria Quality). Maps every finding to a specific spec section using `[Spec SS.Y]` traceability markers, or tags it as `[Gap]` when the requirement is missing entirely.
- **Edge-case researcher**: identifies missing scenarios -- boundary conditions, empty states, concurrent access, error paths, and unhappy flows. Produces a scenario inventory covering dimensions 5 and 6 (Scenario Coverage, Edge Case Coverage). Tags findings with `[Spec SS.Y]` when a scenario should extend an existing requirement, or `[Gap]` when no requirement addresses it.
- **Consistency checker**: cross-references requirements against each other for contradictions, redundancies, and implicit assumptions. Produces a conflict/assumption report covering dimensions 3, 7, and 8 (Consistency, Non-Functional Requirements, Dependencies & Assumptions). Tags findings with `[Conflict]`, `[Ambiguity]`, or `[Assumption]` as appropriate, always referencing the specific sections involved.

## Quality Dimensions

Every checklist item must map to exactly one of these nine dimensions:

### 1. Completeness

Are all user flows covered? Are there features mentioned in the summary but missing from the detailed requirements? Do all user stories have corresponding functional requirements?

### 2. Clarity

Are requirements unambiguous? Could two developers read a requirement and build different things? Watch for weasel words: "appropriate," "intuitive," "fast," "user-friendly," "seamless," "etc."

### 3. Consistency

Do requirements contradict each other? Does the data model match the described behaviors? Are naming conventions uniform across the document?

### 4. Acceptance Criteria Quality

Are criteria measurable and testable? Can each criterion be verified with a concrete test? Do criteria use Given/When/Then or equivalent structured format? Are thresholds specific (e.g., "under 200ms" not "fast")?

### 5. Scenario Coverage

Are happy path, error, and edge cases explicitly covered? Is there a scenario for first-time use, returning user, and administrative override? Are failure recovery paths defined?

### 6. Edge Case Coverage

Are boundary conditions addressed? What happens with empty inputs, maximum-length inputs, concurrent modifications, network failures, partial data, and permission boundaries?

### 7. Non-Functional Requirements

Are performance targets defined with specific metrics? Are security requirements explicit (authentication, authorization, data encryption, audit logging)? Are accessibility standards specified (WCAG level)? Are scalability expectations stated?

### 8. Dependencies & Assumptions

Are external system dependencies listed with version constraints? Are third-party API contracts referenced? Are assumptions about user behavior, data volume, or infrastructure made explicit? Are fallback behaviors defined when dependencies are unavailable?

### 9. Ambiguities & Conflicts

Cross-cutting dimension that surfaces items tagged with `[Ambiguity]` or `[Conflict]` markers. These are requirements where intent is unclear or where two sections disagree.

## Traceability Rules

Every checklist item MUST include a traceability marker:

- `[Spec SS.Y]` -- traces to a specific section and subsection of the source document. Use the actual section numbering from the source. If the source uses named headings without numbers, use `[Spec "Heading Name"]`.
- `[Gap]` -- identifies a requirement that is missing entirely from the specification.
- `[Ambiguity]` -- identifies a requirement that could be interpreted in multiple ways.
- `[Conflict]` -- identifies two or more requirements that contradict each other. Reference all conflicting sections.
- `[Assumption]` -- identifies an unstated assumption that the specification relies upon.

Minimum 80% of checklist items must trace to a specific spec section via `[Spec SS.Y]`. The remaining 20% may use `[Gap]`, `[Ambiguity]`, `[Conflict]`, or `[Assumption]` markers. If the ratio falls below 80% traceable, the specification likely has structural issues -- note this in the summary.

## Phase 1: Source Analysis

Read the source document and build a structural map:

1. Identify all sections and subsections with their numbering or heading names.
2. Catalog all user stories, functional requirements, non-functional requirements, edge cases, and acceptance criteria.
3. Note the document type (PRD, spec, RFC, user stories, etc.) to calibrate expectations.

Present the structural overview:

```text
## Source Analysis

Document: <filename>
Type: <PRD|spec|RFC|user stories|other>
Sections: N
User stories: N
Functional requirements: N
Non-functional requirements: N
Acceptance criteria: N
Edge cases documented: N

Depth: <quick|standard|thorough>
Estimated checklist items: N

Action: [P]roceed | [C]hange depth | [S]cope to sections
```

### Actions

- Proceed: move to Phase 2 with the current depth.
- Change depth: switch to a different depth profile and re-estimate.
- Scope to sections: limit checklist generation to specific sections of the document.

## Phase 2: Checklist Generation

Launch child agents in parallel to analyze the source document across all nine quality dimensions. Merge their findings:

1. Deduplicate items that multiple agents flagged.
2. Assign severity to each item: critical, high, medium, or low.
3. Assign a sequential ID to each item: `CHK-001`, `CHK-002`, etc.
4. Sort by severity (critical first), then by dimension order within each severity level.

Severity guidelines:
- **critical**: requirement is missing, contradictory, or untestable for a core user flow. Blocks implementation.
- **high**: requirement is ambiguous or incomplete for an important flow. Likely causes rework.
- **medium**: requirement is unclear or missing for a secondary flow. May cause confusion.
- **low**: minor clarity improvement or nice-to-have edge case. Unlikely to block progress.

## Phase 3: Interactive Review

When `mode` is `interactive` (default), present each checklist item one at a time:

```text
## Check [N/total] - [category] - [severity: critical|high|medium|low]

[CHK-NNN] <checklist question>
Traces to: [Spec SS.Y] or [Gap] or [Ambiguity] or [Conflict] or [Assumption]

Status: [pass] Requirement meets this | [fail] Gap found (describe) | [?] Needs clarification
```

Wait for the user to respond with one of:

- **pass**: the requirement adequately addresses this check. Record as passed.
- **fail**: a gap exists. Capture the user's description of the gap. Record as failed with the gap description.
- **?**: the user cannot determine the answer. Record as needing clarification with any notes the user provides.

### Loop Rules

1. Process checks in severity order (critical first).
2. If the user says "pass all remaining", record all unprocessed items as passed.
3. If the user says "fail all remaining", record all unprocessed items as failed and prompt for a blanket note.
4. If the user says "skip to category", jump to the next item in the named dimension.
5. Group consecutive items from the same dimension together when possible for reviewer flow.

### Auto-Approve Mode

When `mode` is `auto-approve`, skip the interactive loop. Instead, auto-assess each checklist item by re-reading the relevant spec section:

- If the spec section directly and unambiguously addresses the check, mark as `pass`.
- If the spec section is missing or does not address the check, mark as `fail`.
- If the spec section partially addresses it or is ambiguous, mark as `?`.

Present the full results at once and move to Phase 4.

## Phase 4: Summary

Display:

```text
## Requirements Quality Checklist Summary

Source: <document path>
Depth: <quick|standard|thorough>
Total checks: N

Results:
- Passed: N
- Failed: N
- Needs clarification: N

By severity:
- Critical: N passed / N failed / N unclear
- High: N passed / N failed / N unclear
- Medium: N passed / N failed / N unclear
- Low: N passed / N failed / N unclear

By dimension:
- Completeness: N/N passed
- Clarity: N/N passed
- Consistency: N/N passed
- Acceptance Criteria Quality: N/N passed
- Scenario Coverage: N/N passed
- Edge Case Coverage: N/N passed
- Non-Functional Requirements: N/N passed
- Dependencies & Assumptions: N/N passed
- Ambiguities & Conflicts: N/N passed

Traceability: NN% of items trace to a spec section

Quality score: NN/100
```

### Quality Score Calculation

- Start at 100.
- Each failed critical item: -10 points.
- Each failed high item: -5 points.
- Each failed medium item: -2 points.
- Each failed low item: -1 point.
- Each "needs clarification" item at critical/high: -3 points.
- Floor at 0.

### Recommendations

Based on the results, provide actionable next steps:

- If quality score >= 80: "Specification is ready for implementation planning. Consider addressing remaining gaps."
- If quality score 50-79: "Specification needs revision before implementation. Focus on critical and high severity items first."
- If quality score < 50: "Specification requires significant rework. Recommend running `/devkit:spec-write` to rebuild from the ground up."

If any failed items exist, ask:

```text
Action: [R]evise spec (generate amendment notes) | [E]xport checklist only | [H]andoff to spec-write
```

- Revise: generate a `.temp/checklists/<source-slug>-amendments.md` file listing all failed items with recommended spec changes, organized by section.
- Export: save the checklist as-is to `.temp/checklists/<source-slug>.md` for manual follow-up.
- Handoff: recommend the user run `/devkit:spec-write` with the checklist as input context.

## Output

Checklist saved to `.temp/checklists/<source-slug>.md`. The file includes:

1. Source document metadata (path, type, date analyzed).
2. Full checklist with all items, their status, severity, dimension, and traceability markers.
3. Summary statistics.
4. Quality score.
5. Amendment notes (if the user chose "Revise" in Phase 4).

## Adjacent Skills

- `/devkit:spec-write` for writing or rewriting specifications that feed this checklist
- `/devkit:spec-analyze` for cross-artifact consistency checking
- `/devkit:verify-uat` for testing implementation against the specification
