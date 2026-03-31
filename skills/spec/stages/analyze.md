# Cross-Artifact Consistency Analysis

This stage is **read-only**. It detects issues across specifications, plans, tasks, and implementation code but does NOT modify any artifacts. All changes are the user's responsibility after reviewing findings.

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Understand requirements, scan existing plans and context |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Execute the planning workflow |
| 5. Validate & Learn | yes | Validate plan completeness and feasibility |

## Preflight

Before starting analysis, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

Verify that the target path exists and contains at least one recognized artifact (spec, plan, task list, or constitution).

## Artifact Discovery

Starting from the provided `path`, discover all related artifacts by scanning the project:

- **Specifications**: `.temp/specs/**/*.md` -- feature specs with requirements, user stories, and acceptance criteria
- **Plans**: `.temp/plans/**/*.md` -- execution plans with task breakdowns and verification commands
- **Plan context**: `.temp/plans/**/*-context.md` -- decision logs from planning discussions
- **Constitution**: `.temp/constitution.md` or `.temp/specs/**/constitution.md` -- project principles and constraints
- **Implementation code**: source files referenced in plan task `Files:` entries or spec `Out of Scope` boundaries
- **Test files**: test files corresponding to implementation files discovered above

Build an artifact inventory before launching child agents. If no specs or plans are found at the target path, stop and suggest write mode or `/adk-plan` to create them.

### Artifact Inventory Display

```text
## Artifact Inventory

Specs found: N
Plans found: N
Constitution: found | not found
Implementation files referenced: N
Test files found: N

Proceeding with <depth> analysis...
```

## Depth Levels

- **quick**: completeness analyzer only, no code scanning, skip constitution compliance. Best for a fast sanity check on spec-to-plan coverage.
- **standard** (default): all four child agents, code scanning limited to files explicitly referenced in plans. Catches most issues without exhaustive search.
- **thorough**: all four child agents, full codebase scan for orphaned implementations and missing test coverage. Use for milestone reviews or pre-release audits.

## Required Child Agents

Run these child agents in parallel. Each agent receives the full artifact inventory and operates independently.

### Completeness Analyzer

Traces requirements forward through the artifact chain:

1. **Spec -> Plan**: every functional requirement and user story in the spec must map to at least one plan task. Flag requirements with no corresponding task.
2. **Plan -> Tasks**: every plan task must have a verification command. Flag tasks without verification.
3. **Tasks -> Implementation**: every plan task with a `Files:` entry must reference files that exist on disk. Flag tasks pointing to missing files.
4. **Implementation -> Tests**: every implementation file should have corresponding test coverage. Flag implementation files with no test file (at `thorough` depth only).

Produces a coverage chain with gap annotations.

### Consistency Checker

Scans for contradictions between artifacts:

1. **Spec vs Plan**: requirements that the plan interprets differently from the spec's intent (e.g., spec says "real-time" but plan describes batch processing).
2. **Plan vs Context**: decisions recorded in the context file that contradict task descriptions in the plan.
3. **Spec vs Implementation**: implementation behavior that deviates from spec requirements (at `standard` and `thorough` depth).
4. **Cross-spec conflicts**: when multiple specs exist, check for overlapping or contradictory requirements.
5. **Naming drift**: identifiers, feature names, or terminology used inconsistently across artifacts.

Produces a contradiction list with evidence from both sides.

### Constitution Compliance

Skip this agent if no constitution file is found.

1. Read the constitution's principles, constraints, and non-negotiables.
2. Check every spec requirement against constitution principles. Flag violations.
3. Check every plan task against constitution constraints. Flag deviations.
4. Check implementation patterns against constitution non-negotiables (at `thorough` depth).

Produces a compliance matrix: principle -> artifacts checked -> pass/violation.

### Gap Detector

Identifies orphaned or disconnected artifacts:

1. **Requirements with no implementation**: spec requirements that have plan tasks but no implementation files.
2. **Tasks with no tests**: plan tasks marked as verification-required but lacking test coverage.
3. **Orphaned code**: implementation files not referenced by any plan task (at `thorough` depth). These may be leftover from abandoned work or undocumented features.
4. **Dead references**: plan tasks referencing files that no longer exist or have been renamed.
5. **Missing acceptance criteria**: user stories without Given/When/Then scenarios or measurable acceptance criteria.

Produces a gap inventory with artifact references.

## Consolidation

After all child agents complete, merge their findings:

1. Deduplicate overlapping findings (e.g., a gap found by both the completeness analyzer and the gap detector).
2. Assign severity based on impact:
   - **CRITICAL**: contradictions that would cause incorrect implementation, constitution violations on non-negotiable principles
   - **HIGH**: requirements with no plan coverage, plan tasks pointing to missing files, cross-spec conflicts
   - **MEDIUM**: missing test coverage, naming drift, tasks without verification commands
   - **LOW**: minor terminology inconsistencies, orphaned code that may be intentional, style differences between artifacts
3. Assign category: `gap`, `contradiction`, `violation`, `ambiguity`
4. Sort findings by severity (critical first), then by category.

## Interactive Review

When `--interactive` is `interactive` (the default), present each finding to the user one at a time:

```text
## Finding [N/total] - [severity: CRITICAL|HIGH|MEDIUM|LOW] - [category: gap|contradiction|violation|ambiguity]

Artifacts involved: <spec, plan, tasks, code -- list which artifacts are part of this finding>
Description: <what is inconsistent, missing, or violated>
Evidence: <specific references with file paths, section names, line numbers, or quoted text>

Suggested resolution: <concrete action to fix the issue, referencing specific files and sections>

Action: [A]ccept | [E]dit suggestion | [R]eject | [S]kip
```

### Actions

- **Accept**: record the finding and its suggested resolution in the consistency report.
- **Edit suggestion**: let the user revise the suggested resolution text. Stay in the edit loop until the user accepts or rejects the revised version.
- **Reject**: discard the finding entirely (user disagrees it is an issue).
- **Skip**: defer to the end. After all other findings are processed, return to skipped items for a final decision.

### Loop Rules

1. Process findings in severity order (CRITICAL first, then HIGH, MEDIUM, LOW).
2. If the user says "accept all remaining", record all unprocessed findings with their default resolutions.
3. If the user says "reject all remaining", discard all unprocessed findings.
4. Group related findings when they share the same root cause and present them together with a note explaining the relationship.

### Auto-Approve Mode

When `--interactive` is `auto-approve`, skip the interactive loop. Accept all findings automatically and proceed directly to the traceability matrix and report.

## Traceability Matrix

After the interactive review (or immediately in `auto-approve` mode), generate a traceability matrix showing coverage across the artifact chain:

```text
## Traceability Matrix

| Requirement | Spec Section | Plan Task | Implementation | Tests | Status |
|-------------|-------------|-----------|----------------|-------|--------|
| <req-id or summary> | <section ref> | <task ref or MISSING> | <file path or MISSING> | <test file or MISSING> | COVERED / GAP / PARTIAL |
| ... | ... | ... | ... | ... | ... |

Coverage Summary:
- Fully covered: N/total (NN%)
- Partially covered: N/total (NN%)
- Not covered: N/total (NN%)
```

At `quick` depth, the matrix covers spec-to-plan only. At `standard`, it extends through implementation. At `thorough`, it includes test coverage.

## Consistency Report

Output the final consistency report:

```text
## Consistency Analysis Report

Artifacts analyzed:
- Specs: N
- Plans: N
- Constitution: yes/no
- Implementation files: N
- Test files: N

Analysis depth: <quick|standard|thorough>

### Finding Summary

| Severity | Count | Accepted | Rejected | Skipped |
|----------|-------|----------|----------|---------|
| CRITICAL | N | N | N | N |
| HIGH | N | N | N | N |
| MEDIUM | N | N | N | N |
| LOW | N | N | N | N |

### Accepted Findings

#### [1] [SEVERITY] [category] - <short description>
Artifacts: <list>
Resolution: <accepted or edited resolution text>

#### [2] ...

### Traceability Matrix
<matrix from above>

### Recommendations
1. <highest-priority action item based on accepted findings>
2. <next action item>
...
```

Save the report to `.temp/specs/consistency-report.md` (or `.temp/plans/consistency-report.md` if the analysis was plan-rooted). If the file already exists, append a timestamped section rather than overwriting.
