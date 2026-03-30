---
name: spec
description: "[full] [spec] Use when analyzing specs, writing specifications, generating checklists, or writing constitutions"
user-invocable: true
argument-hint: "<topic> [--mode analyze|write|checklist|constitution] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Specification

Unified specification skill: writes feature specs, analyzes cross-artifact consistency, generates requirements quality checklists, and creates project constitutions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `analyze`, `write`, `checklist`, `constitution` | auto-detect | Force a specific specification mode |
| `--spec` | `<path>` | none | Path to existing spec (implies analyze mode unless combined with `--mode`) |
| `--depth` | `quick`, `standard`, `thorough` | `standard` | Analysis/checklist depth level |
| `--action` | `create`, `update`, `audit` | auto-detect | Constitution action type |
| `--scope` | `<path>` | none | Limit analysis to specific sections or files |
| `--format` | `markdown`, `google-doc`, `confluence` | `markdown` | Output format for constitution |
| `--interactive` | `interactive`, `auto-approve` | `interactive` | Review mode for interactive sections |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode analyze`**: Read-only cross-artifact consistency analysis. Detects issues across specs, plans, tasks, and implementation. Runs child agents in parallel for completeness, consistency, constitution compliance, and gap detection.
- **`--mode write`**: Interactive feature specification creation. Captures requirements through clarification questions, launches domain/research/review child agents, produces spec with user stories, acceptance criteria, and edge cases.
- **`--mode checklist`**: Requirements quality validation. Generates "unit tests for English" that check completeness, clarity, and consistency. Produces traceable checklist with severity ratings and quality score.
- **`--mode constitution`**: Project governance document creation/update/audit. Creates versioned non-negotiable principles and quality gates that all downstream work must comply with.

### Examples

```
/spec write a feature spec for user notifications
/spec --mode analyze .temp/specs/notifications/
/spec --mode checklist .temp/specs/notifications/spec.md
/spec --mode constitution
/spec --mode constitution --action update
/spec --mode constitution --action audit
/spec --spec .temp/specs/auth/spec.md
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from context:

| Signal | Mode | Stage File |
|---|---|---|
| "analyze", "validate", "check consistency", "verify", references existing spec via `--spec` | analyze | `stages/analyze.md` |
| "write spec", "define requirements", "draft specification", "feature spec", default for new topics | write | `stages/write.md` |
| "checklist", "quality check", "validate requirements", "unit tests for English" | checklist | `stages/checklist.md` |
| "constitution", "governance", "principles", "quality gates", "non-negotiable" | constitution | `stages/constitution.md` |

### Ambiguous Input

When invoked as `/spec` with no qualifying action:

1. If the user references an **existing** spec or document -> analyze mode
2. Otherwise -> write mode

After selecting the mode, load the corresponding stage file and follow its instructions.

## Common Phases

All modes share the 6-phase workflow from `references/workflow-6phase.md`. Each stage file defines which phases apply.

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

### Phase 5: Validate & Learn

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Summary line only (e.g., "Spec written to .temp/specs/notifications/spec.md")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus all child agent findings, decision rationale, and traceability matrices

## Adjacent Skills

- `/plan` -- create implementation plans from specifications
- `/develop` -- implement code from plans
- `/review` -- code review against specifications
