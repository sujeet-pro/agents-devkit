---
name: test
description: "[abbreviated] [utility] Use when you need interactive user acceptance testing that extracts testable deliverables and walks the user through manual verification with automatic failure diagnosis"
user-invocable: true
argument-hint: "<source> [--scope] [--mode] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
dependencies:
  commands: [git]
workflow-tier: abbreviated
---

# User Acceptance Testing

`references/agentic-teams.md` and `references/preflight.md`.

UAT verifies that the implementation achieves its goals from the user's perspective. This skill extracts testable deliverables from specs/plans and walks the user through each one interactively.

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<source>` | file path to spec, plan, or requirements doc | (required) | Document to extract test cases from |
| `--scope` | keyword filter | (all test cases) | Only include test cases matching these keywords |
| `--mode` | `interactive`, `auto-approve` | `interactive` | Whether to walk through each test case or run all automatically |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Behavior Variations

- **`--mode interactive`** (default): presents each test case one-by-one for pass/fail/skip/blocked
- **`--mode auto-approve`**: runs all test cases without interactive prompts, reports results at end
- **`--scope <keywords>`**: filters extracted test cases to only those matching specified keywords
- **On failure**: launches diagnosis agent for root cause analysis and optional fix plan generation
- **`--verbosity short`**: pass/fail summary table only
- **`--verbosity detailed`**: full test steps, diagnosis details, and fix plans for failures

### Examples

```
/test docs/spec.md
/test docs/requirements.md --scope "authentication"
/test .temp/plans/feature-plan.md --mode auto-approve
/test docs/prd.md --verbosity detailed
/test docs/spec.md --scope "API" --verbosity short
```

---

## Preflight

Before extracting test cases or launching child agents, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

Read the source document to confirm it exists and contains testable content before proceeding.



Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`.


## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze requirements and context |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Execute the main workflow |
| 5. Validate & Learn | yes | Validate output quality and completeness |

## Output Format

All output is markdown by default. Structure varies by deliverable type — see the skill-specific execution sections above for the exact format.


## UAT Storage

Save results to `.temp/uat/<source-slug>-uat.md`. Create the `.temp/uat/` directory if it does not exist.

## Required Child Agents

When the platform supports child agents, run at least these:

- **Test case extractor**: reads the source spec/plan and extracts concrete, testable behaviors with expected outcomes. Categorizes each as functional, edge-case, or non-functional.
- **Diagnosis agent**: when a test fails, investigates root cause using `/develop --mode debug` patterns. Reports affected files, confidence level, and suggested fix.
- **Fix planner**: for failed items, generates fix plans ready for `/plan --mode execute`.

## Phase 1: Extract Test Cases

Parse the source document for testable deliverables:

- User stories with acceptance criteria -> test cases
- Functional requirements -> verification scenarios
- Edge cases -> negative test cases
- Non-functional requirements -> performance/accessibility checks

When `scope` is provided, filter extracted test cases to only those matching the specified keywords.

Present the test plan:

```text
## UAT Test Plan

Source: <document path>
Test cases extracted: N

Categories:
- Functional: N
- Edge cases: N
- Non-functional: N

Action: [P]roceed | [A]dd test case | [R]emove test case | [E]dit
```

### Actions

- Proceed: move to Phase 2 with the current test plan.
- Add: let the user describe a new test case. Assign category and priority, then re-display the plan.
- Remove: let the user pick a test case to remove by number. Re-display the plan.
- Edit: let the user revise a test case by number. Stay in the edit loop until the user accepts.

## Phase 2: Interactive Testing

Present each test case one at a time, in priority order (P1 first):

```text
## UAT [N/total] - <testable behavior>

Category: [functional|edge-case|non-functional]
Priority: [P1|P2|P3]

Steps to verify:
1. <step 1>
2. <step 2>
3. <step 3>

Expected result: <what should happen>

Result: [P]ass | [F]ail (describe issue) | [S]kip | [B]locked (can't test)
```

### On Pass

Record the result and move to the next test case.

### On Failure

When the user reports a failure:

1. Capture the failure description from the user.
2. Launch the diagnosis agent to investigate root cause.
3. Present diagnosis:

```text
## Diagnosis - <test case name>

Root cause: <identified cause>
Confidence: NN%
Affected files: <file list>

Suggested fix: <brief description>

Action: [G]enerate fix plan | [D]efer to backlog | [R]e-investigate
```

- Generate fix plan: queue the failure for Phase 3 fix routing.
- Defer to backlog: record as a known issue without generating a fix plan.
- Re-investigate: run the diagnosis agent again with additional context from the user.

### On Skip

Record as skipped. After all other test cases are processed, return to skipped items for a final decision.

### On Blocked

When the user cannot test (missing environment, external dependency, etc.):

1. Record as blocked with the reason.
2. Suggest a workaround if possible.
3. Add to "Blocked Items" in the UAT report.

### Loop Rules

1. Process test cases in priority order (P1 first, then P2, then P3).
2. If the user says "pass all remaining", record all unprocessed test cases as passed.
3. If the user says "skip all remaining", record all unprocessed test cases as skipped.
4. When `mode` is `auto-approve`, run all test cases without interactive prompts and report results at the end.

## Phase 3: Fix Routing

For all failed items where the user chose "Generate fix plan":

- Group related failures into coherent fix tasks.
- Generate a plan compatible with `/plan --mode execute`.
- Save to `.temp/plans/<source-slug>-fixes.md`.

If no fix plans were requested, skip this phase.

## Phase 4: Summary

```text
## UAT Summary

Source: <document>
Total test cases: N

Results:
- Passed: N
- Failed: N
- Skipped: N
- Blocked: N

Pass rate: NN%

Fix plans generated: N (saved to <path>)
Blocked items: N (require manual resolution)
```

Save the full summary to `.temp/uat/<source-slug>-uat.md`.

If pass rate < 100%, ask:

```text
Accept current state? [Y]es (ship with known issues) | [N]o (fix first) | [R]e-test failed items
```

- Yes: close the UAT session and record the accepted state.
- No: direct the user to run `/plan --mode execute` with the generated fix plans.
- Re-test: return to Phase 2 for only the failed and skipped items.

## Adjacent Skills

- `/develop --mode verify` for automated verification (tests, lint, types, build)
- `/develop --mode debug` for investigating specific failures
- `/plan --mode execute` for executing fix plans
- `/spec --mode write` for writing the specifications that feed UAT
