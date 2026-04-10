---
title: 'dev-build'
description: 'Implement features, debug, enhance code, or run TDD — auto-detects mode from context'
skill_name: dev-build
category: task
workflow_tier: full
user_invocable: true
---

# dev-build

Use `dev-build` to implement features, debug, enhance code, or run TDD — auto-detects mode from context. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`dev-build` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `implement`, `enhance`, `debug`, `tdd`, `verify`, `worktree`, `quick` | auto-detect | Force a specific development mode |
| `--fix` | flag | off | In debug mode, attempt fix after root cause found |
| `--branch` | `<name>` | none | Create/switch to feature branch before work |
| `--spec` | `<path>` | none | Load specification file as input |
| `--plan` | `<path>` | none | Load existing plan file as input |
| `--tdd` | flag | off | Force TDD mode (alias for `--mode tdd`) |
| `--full` | flag | off | In quick mode, run full verification |
| `--scope` | `<path>` | none | Limit analysis to specific files/directories |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Parameter Notes

- `--mode` overrides keyword detection and sends the skill straight to a specific stage or behavioral branch.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always, family varies by mode | Complex Build (`--mode implement,tdd`), Standard Task (`--mode enhance`), Quick Action (`--mode quick,verify,worktree`), Investigative Loop (`--mode debug`). `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

Verify that the project's test runner, linter, and type-checker are available and working. If a build tool is configured, confirm it produces a clean build from the current state.

### Common Phases

Mode determines the workflow family. Each stage file defines the workflow steps for its mode.

### 1. Confirm

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### 2. Research

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### 3. Select Approach

Use this phase when the stage surfaces alternatives or needs user confirmation beyond intent expansion. Simpler modes may skip it.

### 4. Plan

Use this phase when the stage needs an explicit task plan before execution. Simpler modes may skip it and move directly from approval to execution.

### 5. Execute

Follow the stage file's execution instructions.

If `--branch` is provided and the stage doesn't handle it explicitly, create the branch before execution:
```bash
git checkout -b <branch>
```

### 6. Validate

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **`--mode implement`**: Uses Complex Build workflow for new features.
- **`--mode enhance`**: Impact-aware enhancement of existing features. Uses Standard Task workflow with focus on minimizing disruption.
- **`--mode debug`**: Systematic root cause investigation. Uses Investigative Loop workflow for this mode.
- **`--mode tdd`**: Strict red-green-refactor cycle. Uses Complex Build workflow with test-first enforcement.
- **`--mode verify`**: Evidence-based verification only. Uses Quick Action workflow for this mode.
- **`--mode worktree`**: Git worktree creation and setup. Uses Quick Action workflow for this mode.
- **`--mode quick`**: Fast execution for simple tasks. Uses Quick Action workflow for this mode.

### Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. If `--tdd` flag is present, use tdd mode. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| Bug, error, fix, stack trace, crash, "not working", broken | debug | `stages/debug.md` (uses `adk-debugger` agent) |
| Test, TDD, test-first, test-driven, "write tests" | tdd | `stages/tdd.md` |
| Trivial, single file, typo, config tweak, constant, simple, quick, small | quick | `stages/quick.md` |
| Enhance, improve, refactor, optimize, upgrade, extend existing | enhance | `stages/enhance.md` |
| Worktree, isolated, parallel branch, workspace isolation | worktree | `stages/worktree.md` |
| Verify, check, confirm, validate (no production code changes) | verify | `stages/verify.md` |
| Default: new feature, greenfield, implement, build, create | implement | `stages/implement.md` |

### Ambiguous Complexity

When the task does not clearly match a single mode:

1. Estimate files affected, architectural decisions, and requirements clarity using the quick mode complexity thresholds.
2. **Trivial or Small** -> quick mode
3. **Medium with clear approach** -> quick mode with `--full` for extended verification
4. **Medium with unclear approach** -> implement mode (planning phase will clarify)
5. **Too Complex** -> implement mode

After selecting the mode, load the corresponding stage file and follow its instructions.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "Bug fixed in src/auth.ts: null check on email field")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus investigation notes, decision rationale, and all verification command outputs

## Related Skills

### Adjacent Skills

- `/adk:plan --mode write` — standalone planning before development
- `/adk:spec --mode write` — write specifications before implementation
- `/adk:code-review-pr` — PR or local code review after development
- `/adk:code-review-repo` — whole-repo review when scope is architectural or broad
- `/adk:dev-refactor` — focused refactors (extract, rename, restructure) instead of feature work
- `/adk:dev-migrate` — framework or library upgrades with breaking-change analysis
- `/adk:dev-commit` — commit messages and PR descriptions when wrapping up
- `/adk:handoff` — pause long development sessions

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:dev-build
/adk:dev-build add user authentication with JWT tokens
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:dev-build --mode debug the login form crashes on empty email
/adk:dev-build --mode tdd implement retry logic for API calls
/adk:dev-build --mode enhance refactor the caching layer to support TTL
/adk:dev-build --mode quick fix the typo in the README
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:dev-build --verbosity detailed
```
