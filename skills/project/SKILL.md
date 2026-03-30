---
name: project
description: "[full] [project] Use when initializing projects, managing milestones, or capturing ideas"
user-invocable: true
argument-hint: "<action> [--mode init|milestone|idea] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Project

Unified project skill: bootstraps new projects through structured discovery and research, manages milestone tracking and auditing, and captures ideas for the backlog. Auto-detects the right mode from context, or accepts an explicit `--mode`.

Load references: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`. For Medium/Large: also load `references/agentic-teams.md`, `references/principal-engineer.md`.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `init`, `milestone`, `idea` | auto-detect | Force a specific project mode |
| `--action` | varies by mode | none | Sub-action within a mode (e.g., `create`, `track`, `audit`, `complete`, `gaps` for milestone; `capture`, `review`, `promote`, `list` for idea) |
| `--type` | `<project-type>` | none | In init mode, narrow research to a specific project type |
| `--milestone` | `<milestone-id>` | none | In milestone mode, target a specific milestone |
| `--idea` | `<description>` | none | In idea mode, the idea text to capture |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode init`**: Full 6-phase workflow for bootstrapping a new project. Interactive discovery, parallel research, requirements extraction, constitution, and roadmap generation.
- **`--mode milestone`**: Full 6-phase workflow for creating, tracking, auditing, and archiving development milestones. Supports `--action create|track|audit|complete|gaps`.
- **`--mode idea`**: Abbreviated workflow for capturing ideas to a backlog parking lot, reviewing/triaging accumulated ideas, or promoting ideas to specs/plans.

### Examples

```
/project bootstrap a new CLI tool for managing dotfiles
/project --mode init a SaaS dashboard for analytics
/project --mode milestone --action create v1.0 release
/project --mode milestone --action track
/project --mode milestone --action audit v1.0
/project --mode idea add dark mode support
/project --mode idea --action review
/project --mode idea --action promote
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| New project, bootstrap, scaffold, setup, initialize, kickoff | init | `stages/init.md` |
| Milestones, roadmap, progress, tracking, audit, archive, definition of done | milestone | `stages/milestone.md` |
| Ideas, backlog, parking lot, capture, promote, defer, triage | idea | `stages/idea.md` |

### Disambiguation

When the intent is ambiguous, present the options:

```text
Which project action?

[1] Initialize a new project (--mode init)
    Bootstrap from idea through discovery, research, and roadmap.

[2] Manage milestones (--mode milestone)
    Create, track, audit, or archive roadmap milestones.

[3] Capture an idea (--mode idea)
    Park an idea for later, review the backlog, or promote items.
```

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

### Phase 5: Validate & Learn

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "Project initialized at .temp/project-init/")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus research notes, decision rationale, and all child agent outputs

## Adjacent Skills

- `/spec --mode write` -- detailed feature specifications from roadmap phases
- `/plan --mode write` -- execution planning per roadmap phase
- `/review` -- code review after development
- `/develop` -- feature implementation from project plans
