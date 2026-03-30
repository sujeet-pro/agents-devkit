---
name: team
description: "[full] [team] Use when dispatching multi-model tasks or coordinating agent teams"
user-invocable: true
argument-hint: "<task> [--mode multi|team] [--models ...] [--roles ...] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Team

Run tasks through multiple models for comparison/consensus, or dispatch a team of specialized agents working in parallel. Auto-detects the right mode from context, or accepts an explicit `--mode`.

Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `multi`, `team` | auto-detect | Force a specific agent orchestration mode |
| `--models` | comma-separated model names | `opus,sonnet` | In multi mode, which models to run the task through |
| `--strategy` | `merge`, `vote`, `best-of` | `merge` | In multi mode, how to combine results |
| `--timeout` | `<seconds>` | none | Maximum time to wait for child agents |
| `--roles` | comma-separated role names | none | In team mode, custom roles for agents |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode multi`**: Abbreviated workflow. Runs the same task through multiple models in parallel and merges results with a consensus pass. Phases 2-5 skipped.
- **`--mode team`**: Abbreviated workflow. Dispatches specialized agents with distinct roles to work on independent sub-tasks in parallel. Phases 2-5 skipped.

### Examples

```
/team compare how opus and sonnet handle this refactoring task
/team --mode multi --models opus,sonnet,haiku review this authentication flow
/team --mode multi --strategy vote which approach is better for caching
/team --mode team fix all 6 failing tests across 3 files
/team --mode team --roles "api-designer,db-modeler,test-writer" design the user service
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| Compare models, consensus, multi-model, `--models` flag | multi | `stages/multi.md` |
| Team, roles, parallel agents, delegation, `--roles` flag, independent tasks | team | `stages/team.md` |

### Disambiguation

When the intent is ambiguous, ask:

```text
Which agent orchestration mode?

[M] Multi-model -- run the same task through multiple models for comparison/consensus
[T] Team -- dispatch specialized agents with distinct roles for parallel work
```

After selecting the mode, load the corresponding stage file and follow its instructions.

## Common Phases

All modes share the 6-phase workflow from `references/workflow-6phase.md`. Each stage file defines which phases apply and what to do in each.

### Phase 0: Intent Expansion

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### Phase 1: Research & Options

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### Phase 2: Approach Selection

Both multi and team modes usually skip this phase after intent confirmation unless the user needs to choose a strategy.

### Phase 3: Planning

Both multi and team modes usually skip this phase after approval unless coordination needs an explicit task split.

### Phase 4: Execute

Follow the stage file's execution instructions.

### Phase 5: Validate & Learn

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "3 agents dispatched, all completed, results merged")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus full child agent outputs, disagreement analysis, and confidence scoring

## Adjacent Skills

- `/develop` -- feature implementation that may use agent teams internally
- `/review` -- code review that may use multi-model comparison
- `/project` -- project initialization uses parallel research agents
