---
title: 'test'
description: 'Use when you need interactive user acceptance testing that extracts testable deliverables and walks the user through manual verification with automatic failure diagnosis'
skill_name: test
category: task
workflow_tier: abbreviated
user_invocable: true
---

# test

Use `test` to you need interactive user acceptance testing that extracts testable deliverables and walks the user through manual verification with automatic failure diagnosis. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`test` belongs to the `task` layer and is declared at the `abbreviated` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<source>` | file path to spec, plan, or requirements doc | (required) | Document to extract test cases from |
| `--scope` | keyword filter | (all test cases) | Only include test cases matching these keywords |
| `--mode` | `interactive`, `auto-approve` | `interactive` | Whether to walk through each test case or run all automatically |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--mode` overrides keyword detection and sends the skill straight to a specific stage or behavioral branch.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. For narrow tasks with single execution path. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

---

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

Before extracting test cases or launching child agents, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

Read the source document to confirm it exists and contains testable content before proceeding.

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **`--mode interactive`** (default): presents each test case one-by-one for pass/fail/skip/blocked
- **`--mode auto-approve`**: runs all test cases without interactive prompts, reports results at end
- **`--scope <keywords>`**: filters extracted test cases to only those matching specified keywords
- **On failure**: launches diagnosis agent for root cause analysis and optional fix plan generation
- **`--verbosity short`**: pass/fail summary table only
- **`--verbosity detailed`**: full test steps, diagnosis details, and fix plans for failures

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

All output is markdown by default. Structure varies by deliverable type — see the skill-specific execution sections above for the exact format.

## Related Skills

### Adjacent Skills

- `/adk:dev-build --mode verify` for automated verification (tests, lint, types, build)
- `/adk:dev-build --mode debug` for investigating specific failures
- `/adk:plan --mode execute` for executing fix plans
- `/adk:spec --mode write` for writing the specifications that feed UAT

## Additional Reference

### UAT Storage

Save results to `.temp/uat/<source-slug>-uat.md`. Create the `.temp/uat/` directory if it does not exist.

### Required Child Agents

When the platform supports child agents, run at least these:

- **`adk-test-agent` (test case extractor)**: reads the source spec or plan and extracts concrete, testable behaviors with expected outcomes. Categorizes each as functional, edge-case, or non-functional.
- **Diagnosis agent**: when a test fails, investigates root cause using `/adk:dev-build --mode debug` patterns. Reports affected files, confidence level, and suggested fix.
- **Fix planner**: for failed items, generates fix plans ready for `/adk:plan --mode execute`.

### Extract Test Cases

Parse the source document for testable deliverables:

- User stories with acceptance criteria -> test cases
- Functional requirements -> verification scenarios
- Edge cases -> negative test cases
- Non-functional requirements -> performance/accessibility checks

When `scope` is provided, filter extracted test cases to only those matching the specified keywords.

Present the test plan:

```text

### UAT Test Plan

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

### Interactive Testing

Present each test case one at a time, in priority order (P1 first):

```text

### UAT [N/total] - <testable behavior>

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

### Diagnosis - <test case name>

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

### Fix Routing

For all failed items where the user chose "Generate fix plan":

- Group related failures into coherent fix tasks.
- Generate a plan compatible with `/adk:plan --mode execute`.
- Save to `.temp/plans/<source-slug>-fixes.md`.

If no fix plans were requested, skip this phase.

### 3. Verify

```text

### UAT Summary

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
- No: direct the user to run `/adk:plan --mode execute` with the generated fix plans.
- Re-test: return to Phase 2 for only the failed and skipped items.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:test <source>
/adk:test docs/spec.md
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:test docs/requirements.md --scope "authentication"
/adk:test .temp/plans/feature-plan.md --mode auto-approve
/adk:test docs/spec.md --scope "API" --verbosity short
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:test docs/prd.md --verbosity detailed
/adk:test docs/spec.md --scope "API" --verbosity short
```
