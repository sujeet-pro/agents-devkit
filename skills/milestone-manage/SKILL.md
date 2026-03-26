---
name: milestone-manage
description: "Use when creating, tracking, auditing, or archiving development milestones and roadmap progress"
user_invocable: true
arguments:
  - name: action
    description: "Action: create, track, audit, complete, gaps (default: track)"
    required: false
  - name: milestone
    description: "Milestone ID or name to operate on"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Milestone Management

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

Milestones are high-level roadmap checkpoints that group phases, requirements, and definitions of done. Each action in this skill operates on milestone files stored in `.temp/milestones/`.

## Preflight

Before any milestone operation, run:

`zsh scripts/check-skill-deps.zsh milestone-manage`

## Milestone Storage

Save all milestones to `.temp/milestones/<milestone-id>.md` in the current working directory. If `.temp/milestones/` does not exist, create it and ensure `.temp/` is listed in `.gitignore`.

Use this milestone file format:

```markdown
---
milestone_id: <id>
created: <ISO-8601>
updated: <ISO-8601>
skill: milestone-manage
status: active | completed | archived
---

# Milestone: <name>

## Overview
<Why this milestone exists, what it delivers, and its success criteria>

## Requirements
- R1: <requirement description>
- R2: <requirement description>
- R3: <requirement description>

## Phases
- [ ] Phase 1: <description> — Requirements: R1, R2
- [ ] Phase 2: <description> — Requirements: R3, R4
- [ ] Phase 3: <description> — Requirements: R5

## Definition of Done
- <criterion 1>
- <criterion 2>
- <criterion 3>

## Notes
<Additional context, links, or decisions>
```

## Actions

### 1. Create (`action: create`)

Define a new milestone with phases, requirements mapping, and definition of done. This is an interactive, phase-by-phase process.

#### Required Child Agents

Launch at least these child agents in parallel:

- **Requirements analyst**: reads the codebase, existing plans, and project context to identify all requirements that should map to this milestone. Produces a requirements inventory.
- **Phase planner**: groups requirements into logical phases with clear boundaries, dependencies, and ordering. Ensures phases can be tracked independently.
- **Definition-of-done reviewer**: drafts measurable completion criteria for each phase and the milestone overall. Ensures criteria are verifiable, not aspirational.

#### Flow

1. **Gather context.** Ask the user for the milestone name, high-level goal, and any known requirements. In `auto-approve` mode, infer from the codebase and existing plans.

2. **Identify requirements.** Launch the requirements analyst to scan the codebase and existing plans in `.temp/plans/`. Present a numbered requirements list for approval.

3. **Group into phases.** Launch the phase planner to organize requirements into ordered phases. Present each phase interactively:

   ```
   ## Phase [N/total]: <phase name>

   Description: <what this phase delivers>
   Requirements: R1, R2
   Dependencies: Phase N-1 (if any)
   Estimated scope: <small | medium | large>

   Accept? [Y]es | [E]dit | [S]kip | [M]erge with another phase
   ```

   In `auto-approve` mode, present all phases but continue without waiting for confirmation.

4. **Define completion criteria.** Launch the definition-of-done reviewer. Present criteria for approval:

   ```
   ## Definition of Done

   Milestone-level:
   - [ ] <criterion>
   - [ ] <criterion>

   Per-phase:
   - Phase 1: <criterion>
   - Phase 2: <criterion>

   Accept? [Y]es | [E]dit
   ```

5. **Write milestone file.** Save to `.temp/milestones/<milestone-id>.md` with status `active`.

6. **Confirm.** Report the milestone ID, phase count, and requirement count.

### 2. Track (`action: track`)

Scan plans, tasks, and git history to determine completion status of each phase and requirement. Present a progress dashboard.

#### Required Child Agents

Launch at least these child agents in parallel:

- **Plan scanner**: reads all plans in `.temp/plans/` and matches completed tasks to milestone requirements and phases. Produces a coverage map.
- **Git scanner**: reads recent git history (`git log`, `git diff`) to identify commits, merges, and tags that relate to milestone phases. Produces a commit-to-phase mapping.
- **Status synthesizer**: merges plan and git data into a unified progress view. Flags discrepancies between plan status and actual git activity.

#### Flow

1. **Load milestone.** If `milestone` is provided, load that file. Otherwise, scan `.temp/milestones/*.md` and let the user choose, or report on all active milestones.

2. **Scan sources.** Launch plan scanner and git scanner in parallel.

3. **Synthesize status.** For each phase, determine:
   - **Complete**: all mapped requirements have completed tasks and verification
   - **In Progress**: some requirements have completed or in-progress tasks
   - **Not Started**: no tasks or commits map to this phase's requirements

4. **Calculate coverage.** For each requirement, check whether at least one completed task or verified commit addresses it. Report coverage percentage per phase and overall.

5. **Present dashboard.**

   ```
   ## Milestone Progress: <name>
   Status: active | Updated: <timestamp>

   | Phase | Status | Requirements | Coverage |
   |-------|--------|-------------|----------|
   | Phase 1 | ✓ Complete | R1, R2 | 100% |
   | Phase 2 | ◐ In Progress | R3, R4 | 50% |
   | Phase 3 | ○ Not started | R5 | 0% |

   Overall: NN% complete

   ### Recent Activity
   - <commit hash>: <message> → Phase 2 / R3
   - <commit hash>: <message> → Phase 1 / R2

   ### Blockers
   - Phase 2 / R4: no matching tasks found in plans
   ```

6. **Update milestone file.** Set the `updated` timestamp. If all phases are complete, suggest running `action: complete`.

### 3. Audit (`action: audit`)

Verify that all phases meet their definitions of done. Flag unmet requirements, missing verification, and gaps.

#### Required Child Agents

Launch at least these child agents in parallel:

- **Criteria verifier**: for each definition-of-done criterion, checks whether evidence exists (completed tasks, passing tests, merged PRs, documentation). Produces a pass/fail list.
- **Requirements tracer**: traces every requirement to at least one completed task or commit. Flags requirements with no evidence of completion.
- **Gap analyst**: identifies requirements that are partially met, phases with incomplete verification, and definitions of done that lack measurable evidence.

#### Flow

1. **Load milestone.** Load the specified milestone or prompt the user to select one.

2. **Run verification.** Launch all three child agents in parallel against the milestone file and codebase.

3. **Present audit report.**

   ```
   ## Milestone Audit: <name>

   ### Phase-by-Phase Results

   #### Phase 1: <name> — PASS ✓
   - R1: Verified — <evidence>
   - R2: Verified — <evidence>
   - Definition of done: Met

   #### Phase 2: <name> — FAIL ✗
   - R3: Verified — <evidence>
   - R4: UNMET — no completed tasks or commits found
   - Definition of done: Not met — missing <criterion>

   ### Summary
   | Phase | Result | Unmet Requirements | Missing Criteria |
   |-------|--------|-------------------|-----------------|
   | Phase 1 | PASS | 0 | 0 |
   | Phase 2 | FAIL | 1 | 1 |

   ### Recommended Actions
   - R4: Create a plan to address <requirement description>
   - Phase 2 DoD: <specific action to meet criterion>
   ```

4. **Suggest remediation.** For each failure, suggest a concrete next step: create a plan, write a task, or run a verification command.

### 4. Complete (`action: complete`)

Archive a milestone, tag the release, and generate a summary.

#### Flow

1. **Pre-check.** Run `action: audit` first. If any phase fails, warn the user and ask for confirmation before proceeding. In `auto-approve` mode, proceed only if the audit passes; otherwise stop and report failures.

2. **Generate summary.** Produce a completion summary:

   ```
   ## Milestone Complete: <name>

   ### Timeline
   Created: <date> | Completed: <date> | Duration: <N days>

   ### Phases Delivered
   - Phase 1: <description> — <date completed>
   - Phase 2: <description> — <date completed>

   ### Requirements Fulfilled
   - R1: <description> — verified
   - R2: <description> — verified

   ### Key Commits
   - <hash>: <message>
   - <hash>: <message>

   ### Metrics
   - Total phases: N
   - Total requirements: N
   - Plans created: N
   - Commits linked: N
   ```

3. **Tag release.** If the user confirms (or in `auto-approve` mode), create a git tag:

   ```
   git tag -a milestone/<milestone-id> -m "Milestone complete: <name>"
   ```

   Do not push the tag unless the user explicitly requests it.

4. **Archive milestone.** Update the milestone file:
   - Set `status: archived`
   - Set `updated` to current timestamp
   - Append the completion summary to the file

5. **Report.** Confirm archival and report the tag name.

### 5. Gaps (`action: gaps`)

Identify unmet requirements and create new phases to fill them.

#### Required Child Agents

Launch at least these child agents in parallel:

- **Coverage analyzer**: compares all milestone requirements against completed tasks, commits, and verification evidence. Produces a list of unmet and partially met requirements.
- **Phase designer**: for each gap, designs a new phase with clear scope, tasks, and definition of done. Groups related gaps into minimal new phases.

#### Flow

1. **Load milestone.** Load the specified milestone or prompt the user to select one.

2. **Analyze coverage.** Launch the coverage analyzer against the milestone and all plans in `.temp/plans/`.

3. **Identify gaps.** Categorize each requirement:
   - **Fully met**: completed tasks and verification exist
   - **Partially met**: some work done but incomplete
   - **Unmet**: no evidence of work

4. **Design new phases.** Launch the phase designer for unmet and partially met requirements. Present proposed phases interactively:

   ```
   ## Gap Analysis: <milestone name>

   ### Unmet Requirements
   - R4: <description> — no matching tasks
   - R7: <description> — partial, missing verification

   ### Proposed New Phases

   #### Phase N+1: <name>
   Requirements: R4, R7
   Tasks:
   - [ ] <task description>
   - [ ] <task description>
   Definition of done: <criterion>

   Add this phase? [Y]es | [E]dit | [S]kip
   ```

   In `auto-approve` mode, present proposals but add all non-skipped phases without waiting for confirmation.

5. **Update milestone file.** Append approved new phases to the milestone. Update the `updated` timestamp.

6. **Suggest next steps.** Recommend running `action: track` to see updated progress, or `/devkit:plan-write` to create execution plans for the new phases.

## Workflow Modes

- **interactive** (default): confirms at each decision point. User can accept, edit, skip, or merge proposals.
- **auto-approve**: proceeds without confirmation. Presents outputs for visibility but does not block on user input. Stops only on audit failures in `action: complete`.

## Adjacent Skills

- `/devkit:project-init` for bootstrapping a new project before setting milestones
- `/devkit:plan-write` for creating execution plans from milestone phases
- `/devkit:plan-track` for monitoring individual plan progress
- `/devkit:plan-execute` for executing plans that fulfill milestone requirements
