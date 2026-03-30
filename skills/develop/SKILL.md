---
name: develop
description: "[full] [develop] Use when implementing features, debugging, enhancing code, or running TDD — auto-detects mode from context"
user-invocable: true
argument-hint: "<task> [--mode implement|enhance|debug|tdd|verify|worktree|quick] [--fix] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Development

Unified development skill: implements features, debugs issues, enhances code, runs TDD, verifies work, and manages worktrees. Auto-detects the right mode from context, or accepts an explicit `--mode`.

Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`.

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
/develop add user authentication with JWT tokens
/develop --mode debug the login form crashes on empty email
/develop --mode tdd implement retry logic for API calls
/develop --mode enhance refactor the caching layer to support TTL
/develop --mode quick fix the typo in the README
/develop --mode worktree feature/new-dashboard
/develop --mode verify check all tests pass after the migration
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

All modes share the 6-phase workflow from `references/workflow-6phase.md`. Each stage file defines which phases apply and what to do in each.

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

- `/plan --mode write` — standalone planning before development
- `/review` — code review after development
- `/handoff` — pause long development sessions
- `/spec --mode write` — write specifications before implementation
