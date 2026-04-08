---
title: "dev-build"
description: Implement features, debug, enhance code, or run TDD — auto-detects mode from context
skill_name: dev-build
category: task
workflow_tier: full
user_invocable: true
---

# dev-build

Unified development skill: implements features, debugs issues, enhances code, runs TDD, verifies work, and manages worktrees. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## When to Use

- Implement a new feature from scratch
- Debug a bug or investigate an error
- Enhance or improve existing functionality
- Run test-driven development (red-green-refactor)
- Verify that tests pass and the build is clean
- Create a git worktree for isolated parallel work
- Make a quick fix (typo, config tweak, constant change)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task>` | free text | required | Description of the development task |
| `--mode` | `implement` \| `enhance` \| `debug` \| `tdd` \| `verify` \| `worktree` \| `quick` | auto-detect | Force a specific development mode |
| `--fix` | flag | off | In debug mode, attempt fix after root cause found |
| `--branch` | `<name>` | none | Create/switch to feature branch before work |
| `--spec` | `<path>` | none | Load specification file as input |
| `--plan` | `<path>` | none | Load existing plan file as input |
| `--tdd` | flag | off | Force TDD mode (alias for `--mode tdd`) |
| `--full` | flag | off | In quick mode, run full verification |
| `--scope` | `<path>` | none | Limit analysis to specific files/directories |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Mode | Behavior |
|------|----------|
| `--mode implement` | Full 6-phase workflow for new features. All phases active. |
| `--mode enhance` | Impact-aware enhancement of existing features. All phases active with focus on minimizing disruption. |
| `--mode debug` | Systematic root cause investigation. Phases 2-5 skipped; follows fixed 4-phase debugging methodology. |
| `--mode tdd` | Strict red-green-refactor cycle. All phases active with test-first enforcement. |
| `--mode verify` | Evidence-based verification only. Phases 2-5 skipped; runs gate function for every claim. |
| `--mode worktree` | Git worktree creation and setup. Phases 2-5 skipped; single setup operation. |
| `--mode quick` | Fast execution for simple tasks. Phases 2-5 skipped; direct implementation with optional verification. |

## Stage Selection

If `--mode` is explicitly provided, the matching stage loads directly. If `--tdd` is present, TDD mode is used. Otherwise, mode is auto-detected from the task description:

| Signal | Mode | Stage File |
|--------|------|------------|
| Bug, error, fix, stack trace, crash, "not working", broken | debug | `stages/debug.md` |
| Test, TDD, test-first, test-driven, "write tests" | tdd | `stages/tdd.md` |
| Trivial, single file, typo, config tweak, constant, simple, quick, small | quick | `stages/quick.md` |
| Enhance, improve, refactor, optimize, upgrade, extend existing | enhance | `stages/enhance.md` |
| Worktree, isolated, parallel branch, workspace isolation | worktree | `stages/worktree.md` |
| Verify, check, confirm, validate (no production code changes) | verify | `stages/verify.md` |
| Default: new feature, greenfield, implement, build, create | implement | `stages/implement.md` |

### Ambiguous Complexity

When the task does not clearly match a single mode:

1. Estimate files affected, architectural decisions, and requirements clarity
2. **Trivial or Small** → quick mode
3. **Medium with clear approach** → quick mode with `--full` for extended verification
4. **Medium with unclear approach** → implement mode (planning phase will clarify)
5. **Too Complex** → implement mode

## Key Behaviors

- **Auto-detection**: infers mode from task description keywords, complexity, and context
- **Branch management**: `--branch` creates a feature branch before any work begins
- **Spec/plan input**: accepts external specification or plan files to guide implementation
- **Complexity-adaptive**: simpler tasks skip planning and approach phases; complex tasks use all 6 phases
- **Incremental verification**: runs tests and checks after each significant change

## Workflow

Follows the 6-phase workflow. Phase applicability varies by mode.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | all modes | Confirm goal and detect mode |
| 1. Research & Options | all modes | Explore codebase, understand context (brief for simpler modes) |
| 2. Approach Selection | implement, enhance, tdd | Present alternatives for complex tasks |
| 3. Planning | implement, enhance, tdd | Generate task plan before execution |
| 4. Execute | all modes | Apply changes per stage instructions |
| 5. Validate & Learn | all modes | Run tests, verify, produce summary |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. |
| `communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `output-format` | producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, progress dashboard. |

## Output Format

Output is markdown, adapted by `--verbosity`:

- **short**: Status line only (e.g., "Bug fixed in src/auth.ts: null check on email field")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus investigation notes, decision rationale, and all verification command outputs

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:plan --mode write` | Standalone planning before development |
| `/adk:spec --mode write` | Write specifications before implementation |
| `/adk:code-review-pr` | PR or local code review after development |
| `/adk:code-review-repo` | Whole-repo review when scope is architectural or broad |
| `/adk:dev-refactor` | Focused refactors (extract, rename, restructure) instead of feature work |
| `/adk:dev-migrate` | Framework or library upgrades with breaking-change analysis |
| `/adk:dev-commit` | Commit messages and PR descriptions when wrapping up |
| `/adk:handoff` | Pause long development sessions |

## Examples

```
/adk:dev-build add user authentication with JWT tokens
/adk:dev-build --mode debug the login form crashes on empty email
/adk:dev-build --mode tdd implement retry logic for API calls
/adk:dev-build --mode enhance refactor the caching layer to support TTL
/adk:dev-build --mode quick fix the typo in the README
/adk:dev-build --mode worktree feature/new-dashboard
/adk:dev-build --mode verify check all tests pass after the migration
```
