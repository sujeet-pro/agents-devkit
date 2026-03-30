# Init Stage

This stage takes a project idea from initial concept through structured discovery, parallel research, requirements extraction, and roadmap generation. The output is a complete project specification ready for execution by downstream DevKit skills.

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze project requirements and existing structure; Focused research on chosen approach, proposal at .temp/proposal/ |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes; Iterate on proposal with user feedback |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Execute project setup or management tasks |
| 5. Validate & Learn | yes | Verify project structure and configuration |

## Artifact Storage

Save all artifacts to `.temp/project-init/` in the current working directory:

- `PROJECT.md` -- vision and scope
- `REQUIREMENTS.md` -- v1/v2/out-of-scope categorized requirements
- `ROADMAP.md` -- phased execution plan mapped to requirements
- `CONSTITUTION.md` -- non-negotiable project principles and quality gates

If `.temp/project-init/` does not exist, create it and ensure `.temp/` is listed in `.gitignore`.

Use this frontmatter format for each artifact:

```markdown
---
project_idea: <short summary>
created: <ISO-8601>
updated: <ISO-8601>
skill: project
status: draft | approved
---
```

## Phase 1: Interactive Discovery

Iterative conversation to capture the project vision. The goal is to remove ambiguity before research begins.

### Discovery Questions

Ask about each of these areas, one at a time:

- **Problem**: What problem does this solve? Who feels this pain today?
- **Users**: Who is the target user? What is their technical level?
- **Success**: What does success look like? How will it be measured?
- **Constraints**: What are the hard constraints (timeline, team size, existing systems, budget)?

### Capped Clarification

Ask a maximum of **6 questions**, prioritized by `Impact x Uncertainty` (highest first). If the `type` argument was provided, skip questions whose answers are already implied by the project type.

### Bulk Skip

If the user replies "skip all remaining", use the AI's best judgment for every unresolved discovery question and note these as AI-inferred in the PROJECT.md artifact.

### Vision Summary

Continue the discovery loop until the vision is clear. Then present a vision summary for approval:

```text
## Project Vision Summary

Problem: <what pain this solves>
Users: <target audience>
Success: <what success looks like>
Constraints: <non-negotiable constraints>

Does this capture your vision? [Y]es | [E]dit | [R]estart
```

- **Yes**: lock the vision and proceed to Phase 2. Save to `.temp/project-init/PROJECT.md`.
- **Edit**: let the user revise specific fields. Stay in the edit loop until the user accepts.
- **Restart**: discard and begin Phase 1 again.

In `auto-approve` mode, present the summary but continue without waiting for confirmation.

## Phase 2: Parallel Research

Launch 4 child agents in parallel using the Research Team shape from the child-agent contract:

- **Domain researcher**: ecosystem landscape, competing solutions, best practices, market positioning. Focuses on the problem space and how others have solved it.
- **Stack researcher**: technology options, framework comparisons, community health, maintenance trajectory. If `type` was provided, narrow research to that project type.
- **Architecture researcher**: patterns, scalability approaches, integration points, data modeling strategies. Evaluates architectural options against the constraints from Phase 1.
- **Pitfall researcher**: common failures in similar projects, anti-patterns, risks, regulatory concerns. Identifies what has gone wrong for others and why.

### Merge Rules

Merge results in the parent session:

- Deduplicate overlapping findings across agents.
- Preserve minority opinions when they change risk assessment.
- Mark single-agent findings as lower confidence until corroborated.
- Prefer official docs and real-world case studies over generic advice.

### Interactive Research Review

Present research highlights interactively, ordered by impact (highest first):

```text
## Research Finding [N/total] - [category: domain|stack|architecture|pitfall]

Finding: <key insight>
Source: <where this came from>
Impact: <how this affects the project>
Confidence: NN%

Action: [A]cknowledge | [D]iscuss further | [S]kip
```

### Actions

- **Acknowledge**: accept the finding and incorporate it into project context.
- **Discuss further**: open a conversation about the finding. Stay in the discussion loop until the user acknowledges or skips.
- **Skip**: defer to the end. After all other findings are processed, return to skipped items for a final decision.

### Bulk Acknowledge

If the user replies "acknowledge all remaining", accept all unprocessed findings.

In `auto-approve` mode, present all findings as a consolidated list and acknowledge them automatically.

## Phase 3: Requirements Extraction

Extract requirements from the vision (Phase 1) and research findings (Phase 2). Present each requirement interactively for scope categorization:

```text
## Requirement [N/total]

Description: <requirement>
Category: <functional|non-functional|technical>
Source: <which phase or finding this came from>

Scope: [1] v1 (must-have) | [2] v2 (future) | [3] Out of scope
```

### Auto-Categorize

Support "auto-categorize remaining" -- the AI suggests scope for every unprocessed requirement based on the constraints and priorities from Phase 1. Present the batch for confirmation:

```text
## Auto-Categorized Requirements

v1 (must-have):
- <req 1>
- <req 2>

v2 (future):
- <req 3>

Out of scope:
- <req 4>

Action: [A]ccept all | [E]dit individually | [R]eject and categorize manually
```

In `auto-approve` mode, auto-categorize all requirements and continue.

### Requirements Artifact

After categorization is complete, save to `.temp/project-init/REQUIREMENTS.md` with three sections:

```markdown
## v1 -- Must-Have
- [ ] <requirement with category tag>

## v2 -- Future Enhancement
- [ ] <requirement with category tag>

## Out of Scope
- <requirement with rationale for exclusion>
```

## Phase 4: Constitution

Define non-negotiable project principles (maximum 5-7). These are the rules that should never be broken during implementation, regardless of time pressure.

Present each principle interactively:

```text
## Principle [N/total]

Name: <principle name>
Description: <what it means and why it matters>
Applies to: <which phases or activities this governs>

Action: [A]ccept | [E]dit | [R]eject | [A]dd new
```

### Actions

- **Accept**: lock the principle into the constitution.
- **Edit**: let the user revise the principle. Stay in the edit loop until the user accepts or rejects.
- **Reject**: discard the principle entirely.
- **Add new**: let the user propose a new principle not suggested by the AI.

### Quality Gates

After principles are defined, propose quality gates that enforce them:

- Test coverage expectations (unit, integration, e2e)
- Linting and formatting rules
- Accessibility standards (WCAG level if applicable)
- Performance budgets
- Security requirements
- Documentation standards

Present quality gates in the same interactive format as principles.

In `auto-approve` mode, present the full constitution and continue without waiting for confirmation.

Save to `.temp/project-init/CONSTITUTION.md`.

## Phase 5: Roadmap Generation

Generate a phased roadmap mapped to v1 requirements from Phase 3. Each phase should be a deployable increment where possible.

Present each phase for approval:

```text
## Phase [N] - <name>

Requirements covered:
- <req 1>
- <req 2>

Estimated complexity: [small|medium|large]
Dependencies: <prior phases needed>
Key deliverables: <what is shipped at the end of this phase>

Action: [A]ccept | [E]dit | [R]eorder | [M]erge with another phase
```

### Actions

- **Accept**: lock the phase into the roadmap.
- **Edit**: let the user revise scope, ordering, or deliverables.
- **Reorder**: move the phase to a different position in the sequence.
- **Merge**: combine with another phase. Prompt the user to select which phase to merge with.

### Roadmap Rules

1. Every v1 requirement must appear in exactly one phase.
2. Phases respect dependency ordering -- no phase depends on a later phase.
3. Earlier phases should deliver user-visible value sooner.
4. Each phase should be completable independently and result in a working state.

In `auto-approve` mode, present the full roadmap and continue without waiting for confirmation.

Save to `.temp/project-init/ROADMAP.md`.

## Phase 6: Summary & Approval

Present the complete project specification:

```text
## Project Initialization Complete

Artifacts created:
- PROJECT.md -- <one-line vision summary>
- REQUIREMENTS.md -- N v1, N v2, N out-of-scope
- ROADMAP.md -- N phases covering all v1 requirements
- CONSTITUTION.md -- N principles, N quality gates

All artifacts saved to .temp/project-init/

Action: [A]pprove all | [R]evisit section
```

### Actions

- **Approve all**: mark all artifacts as `status: approved` and complete the skill.
- **Revisit section**: return to the specified phase (1-5) for revisions. After revisions, return to this summary.

## Mode Behavior

| Phase | `interactive` (default) | `auto-approve` |
|-------|------------------------|----------------|
| 1. Discovery | Full Q&A loop | Full Q&A loop (always interactive) |
| 2. Research | Finding-by-finding review | Consolidated list, auto-acknowledge |
| 3. Requirements | One-by-one categorization | Auto-categorize, show summary |
| 4. Constitution | Principle-by-principle review | Show full constitution, continue |
| 5. Roadmap | Phase-by-phase approval | Show full roadmap, continue |
| 6. Summary | Approval gate | Show summary, auto-approve |

Phase 1 is always interactive regardless of mode, because the discovery conversation is essential for project quality.
