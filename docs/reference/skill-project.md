---
title: "project"
description: Project bootstrapping, milestone management, and idea capture
skill_name: project
category: task
workflow_tier: full
user_invocable: true
---

# project

Unified project skill: bootstraps new projects through structured discovery and research, manages milestone tracking and auditing, and captures ideas for the backlog. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## When to Use

- Bootstrap a new project from an idea through discovery, research, and roadmap
- Initialize a project with constitution, requirements, and architecture decisions
- Create, track, audit, or archive development milestones
- Review milestone progress and identify gaps
- Capture ideas to a backlog parking lot for later triage
- Review and promote accumulated ideas to specs or plans

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--mode` | `init`, `milestone`, `idea` | auto-detect | Force a specific project mode |
| `--action` | varies by mode | none | Sub-action within a mode (e.g., `create`, `track`, `audit`, `complete`, `gaps` for milestone; `capture`, `review`, `promote`, `list` for idea) |
| `--type` | `<project-type>` | none | In init mode, narrow research to a specific project type |
| `--milestone` | `<milestone-id>` | none | In milestone mode, target a specific milestone |
| `--idea` | `<description>` | none | In idea mode, the idea text to capture |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Init mode** (`--mode init`) | Full 6-phase workflow for bootstrapping a new project. Interactive discovery, parallel research, requirements extraction, constitution, and roadmap generation |
| **Milestone mode** (`--mode milestone`) | Full 6-phase workflow for creating, tracking, auditing, and archiving development milestones. Supports `--action create\|track\|audit\|complete\|gaps` |
| **Idea mode** (`--mode idea`) | Abbreviated workflow for capturing ideas to a backlog parking lot, reviewing/triaging accumulated ideas, or promoting ideas to specs/plans |
| **Auto-detection** (no `--mode`) | Detects mode from context: "bootstrap/scaffold/initialize" → init; "milestones/roadmap/progress" → milestone; "ideas/backlog/capture" → idea |
| `--verbosity short` | Status line only (e.g., "Project initialized at .temp/project-init/") |
| `--verbosity detailed` | Full structured output plus research notes, decision rationale, and all child agent outputs |

## Key Behaviors

- **Smart mode detection**: infers mode from task description keywords (bootstrap/scaffold → init, milestones/roadmap → milestone, ideas/backlog → idea)
- **Disambiguation prompt**: when intent is ambiguous, presents a clear choice between init, milestone, and idea modes
- **Stage-driven execution**: each mode loads its own stage file (`stages/init.md`, `stages/milestone.md`, `stages/idea.md`) with mode-specific workflow
- **Parallel research**: init mode uses child agents for parallel research on technology, architecture, and similar projects
- **Milestone lifecycle**: supports the full create → track → audit → complete lifecycle with gap analysis

## Workflow

Follows the 6-phase workflow for init and milestone modes. Idea mode uses abbreviated workflow.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal and detect mode (init, milestone, or idea) |
| 1. Research & Options | yes | Explore context; brief for idea mode, deep research for init |
| 2. Approach Selection | init, milestone | Present alternatives; skipped for idea mode |
| 3. Planning | init, milestone | Explicit task plan before execution; skipped for idea mode |
| 4. Execute | yes | Follow stage file execution instructions |
| 5. Validate & Learn | yes | Summary of what changed, what was verified, and next steps |

## Mode Detection

| Signal | Mode | Stage |
|--------|------|-------|
| New project, bootstrap, scaffold, setup, initialize, kickoff | init | `stages/init.md` |
| Milestones, roadmap, progress, tracking, audit, archive, definition of done | milestone | `stages/milestone.md` |
| Ideas, backlog, parking lot, capture, promote, defer, triage | idea | `stages/idea.md` |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown. Format varies by mode and is defined in each stage file. Verbosity adapts per `--verbosity`:

- **short**: Status line only
- **standard**: Full structured output from the stage file
- **detailed**: Standard output plus research notes, decision rationale, and all child agent outputs

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:spec --mode write` | Detailed feature specifications from roadmap phases |
| `/adk:plan --mode write` | Execution planning per roadmap phase |
| `/adk:code-review-pr` | Code review after development |
| `/adk:dev-build` | Feature implementation from project plans |

## Examples

```
/adk:project bootstrap a new CLI tool for managing dotfiles
/adk:project --mode init a SaaS dashboard for analytics
/adk:project --mode milestone --action create v1.0 release
/adk:project --mode milestone --action track
/adk:project --mode milestone --action audit v1.0
/adk:project --mode idea add dark mode support
/adk:project --mode idea --action review
/adk:project --mode idea --action promote
```
