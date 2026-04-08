# Investigative Loop Workflow

Shape: **confirm → loop(investigate → hypothesize → test → refine) → summarize**

For tasks where the scope is unknown upfront and discovery is iterative. The workflow is a loop, not a pipeline — each iteration refines understanding until a root cause or answer is found.

## When to Use

- Debugging (root cause analysis)
- Dependency change investigation
- Performance investigation
- Incident triage
- Exploratory audits focused on a specific issue

## Steps

### 1. Confirm

Establish the goal and bounds for investigation.

- Restate what is being investigated
- Define success criteria (what counts as "found it")
- Set bounds: max iterations, time budget, scope limits
- Identify known context (error messages, stack traces, reproduction steps)
- For `--auto`: state goal and proceed without confirmation

### 2. Investigation Loop

Iterate until root cause is found or max iterations reached.

Each iteration:

#### 2a. Investigate

Gather evidence relevant to the current hypothesis (or broadly if no hypothesis yet).

- Read relevant code, logs, error messages, test output
- Search for patterns, recent changes, related issues
- Narrow the search space based on previous iterations

#### 2b. Hypothesize

Form a specific, testable hypothesis about the cause.

- State the hypothesis clearly: "The bug is caused by X because Y"
- List evidence supporting and contradicting the hypothesis
- If no hypothesis forms, identify what additional information would help

#### 2c. Test

Validate or invalidate the hypothesis with concrete evidence.

- Run targeted tests, add logging, reproduce the issue
- Check if the hypothesis explains all observed symptoms
- Record the result: confirmed, partially confirmed, or invalidated

#### 2d. Refine

Based on test results, either converge or pivot.

- If confirmed: move to summarize
- If partially confirmed: narrow the hypothesis and loop again
- If invalidated: form a new hypothesis based on what was learned
- Update the investigation log with what was tried and learned

### Exit Conditions

- Root cause confirmed with evidence
- Fix applied and verified (when `--fix` is active)
- Max iterations reached (default: 10)
- User requests stop

### 3. Summarize

Present findings and next steps.

- Root cause (or best hypothesis if not fully confirmed)
- Evidence chain: what was investigated, what was found
- Fix applied (if `--fix` was active) with verification results
- Remaining unknowns or risks
- Prevention recommendations

## `--auto` Behavior

Step 1 states goal without waiting for confirmation. Loop runs autonomously. Summary is produced at the end.

## Artifacts

Save investigation log to `.temp/<task-slug>/investigation.md`, updated after each loop iteration. Final summary saved to `.temp/<task-slug>/summary.md`.

## Complexity Scaling

| Step | Small | Medium/Large |
|------|-------|--------------|
| Confirm | 1-line: "Investigating X" | Full: scope, bounds, known context |
| Loop max iterations | 3 | 10 |
| Summarize | 2-3 bullet findings | Full root cause analysis + prevention |
