---
name: adk-team
description: "adk - [full] [team] Use when dispatching multi-model tasks or coordinating agent teams"
user-invocable: true
argument-hint: "<task> [--mode multi|team] [--models ...] [--roles ...] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Team

Run tasks through multiple models for comparison/consensus, or dispatch a team of specialized agents working in parallel. Auto-detects the right mode from context, or accepts an explicit `--mode`.

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
/adk:team compare how opus and sonnet handle this refactoring task
/adk:team --mode multi --models opus,sonnet,haiku review this authentication flow
/adk:team --mode multi --strategy vote which approach is better for caching
/adk:team --mode team fix all 6 failing tests across 3 files
/adk:team --mode team --roles "api-designer,db-modeler,test-writer" design the user service
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| Compare models, consensus, multi-model, `--models` flag | multi | `stages/multi.md` |
| Team, roles, parallel agents, delegation, `--roles` flag, independent tasks | team | `stages/adk-team.md` |

### Disambiguation

When the intent is ambiguous, ask:

```text
Which agent orchestration mode?

[M] Multi-model -- run the same task through multiple models for comparison/consensus
[T] Team -- dispatch specialized agents with distinct roles for parallel work
```

After selecting the mode, load the corresponding stage file and follow its instructions.

## Common Phases

All modes share the 6-phase workflow from `/adk:workflow`. Each stage file defines which phases apply and what to do in each.

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

- `/adk:dev-build` -- feature implementation that may use agent teams internally
- `/adk:code-review-pr` -- code review that may use multi-model comparison
- `/adk:project` -- project initialization uses parallel research agents
