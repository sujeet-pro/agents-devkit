---
name: adk-dev-build
description: "adk - [full] [dev] Implement features, debug, enhance code, or run TDD — auto-detects mode from context"
user-invocable: true
argument-hint: "<task> [--mode implement|enhance|debug|tdd|verify|worktree|quick] [--fix] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Development

Unified development skill: implements features, debugs issues, enhances code, runs TDD, verifies work, and manages worktrees. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

## Reference Loading

Load reference files conditionally to minimize token usage:

| Reference | Load When |
|-----------|-----------|
| `workflow-6phase.md` | always (read only the section for the current phase) |
| `communication-style.md` | always |
| `preflight.md` | before preflight check |
| `output-formats.md` | when producing final output |
| `output-format-modes.md` | when producing final output |
| `principal-engineer.md` | Phase 0, complexity >= medium |
| `agentic-teams.md` | Phase 4, when launching child agents |
| `inline-interaction.md` | interactive phases, NOT --auto |
| `help-format.md` | when --help is passed |
| `project-guidelines.md` | Phase 1, when scanning project |
| `review-pipeline.md` | review skills only |
| `review-comment-template.md` | when posting review comments |
| `source-routing.md` | when target is external (PR, Confluence, Google Docs) |

## Help

### Parameters

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

### Behavior Variations

- **`--mode implement`**: Full 6-phase workflow for new features. All phases active.
- **`--mode enhance`**: Impact-aware enhancement of existing features. All phases active with focus on minimizing disruption.
- **`--mode debug`**: Systematic root cause investigation. Phases 2-5 skipped; follows fixed 4-phase debugging methodology.
- **`--mode tdd`**: Strict red-green-refactor cycle. All phases active with test-first enforcement.
- **`--mode verify`**: Evidence-based verification only. Phases 2-5 skipped; runs gate function for every claim.
- **`--mode worktree`**: Git worktree creation and setup. Phases 2-5 skipped; single setup operation.
- **`--mode quick`**: Fast execution for simple tasks. Phases 2-5 skipped; direct implementation with optional verification.

### Examples

```
/adk:dev-build add user authentication with JWT tokens
/adk:dev-build --mode debug the login form crashes on empty email
/adk:dev-build --mode tdd implement retry logic for API calls
/adk:dev-build --mode enhance refactor the caching layer to support TTL
/adk:dev-build --mode quick fix the typo in the README
/adk:dev-build --mode worktree feature/new-dashboard
/adk:dev-build --mode verify check all tests pass after the migration
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

Verify that the project's test runner, linter, and type-checker are available and working. If a build tool is configured, confirm it produces a clean build from the current state.

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. If `--tdd` flag is present, use tdd mode. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| Bug, error, fix, stack trace, crash, "not working", broken | debug | `stages/debug.md` |
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

## Common Phases

All modes share the 6-phase workflow from `/adk:workflow`. Each stage file defines which phases apply and what to do in each.

### Phase 0: Intent Expansion

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### Phase 1: Research & Options

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### Phase 2: Approach Selection

Use this phase when the stage surfaces alternatives or needs user confirmation beyond intent expansion. Simpler modes may skip it.

### Phase 3: Planning

Use this phase when the stage needs an explicit task plan before execution. Simpler modes may skip it and move directly from approval to execution.

### Phase 4: Execute

Follow the stage file's execution instructions.

If `--branch` is provided and the stage doesn't handle it explicitly, create the branch before execution:
```bash
git checkout -b <branch>
```

### Phase 5: Validate & Learn

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "Bug fixed in src/auth.ts: null check on email field")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus investigation notes, decision rationale, and all verification command outputs

## Adjacent Skills

- `/adk:plan --mode write` — standalone planning before development
- `/adk:spec --mode write` — write specifications before implementation
- `/adk:code-review-pr` — PR or local code review after development
- `/adk:code-review-repo` — whole-repo review when scope is architectural or broad
- `/adk:dev-refactor` — focused refactors (extract, rename, restructure) instead of feature work
- `/adk:dev-migrate` — framework or library upgrades with breaking-change analysis
- `/adk:dev-commit` — commit messages and PR descriptions when wrapping up
- `/adk:handoff` — pause long development sessions
