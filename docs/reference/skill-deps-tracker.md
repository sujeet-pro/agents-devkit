---
title: "deps-tracker"
description: Track upstream dependencies and inspirations, detect changes, and sync skills
skill_name: deps-tracker
category: task
workflow_tier: full
user_invocable: true
---

# deps-tracker

Manages `manifest.json` at the repo root — the single source of truth for upstream sources that ADK skills copy or reference. Keeps skills in sync with their inspirations by detecting upstream changes, diffing mapped paths, and applying updates with user confirmation.

## When to Use

- Check if tracked upstream sources have new commits or changes
- Sync local skill files with upstream source repos
- Add a new upstream dependency or inspiration to track
- Remove a tracked source from the manifest
- View the current tracking status of all upstream sources
- Check if upstream tool documentation (llms.txt) has changed and skills need updating

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<action>` | `status`, `sync`, `add`, `remove`, `check`, `docs-check` | `status` | Primary action to perform |
| `--source` | `<name>` | all | Limit action to a single source entry in manifest.json |
| `--auto` | flag | off | Skip confirmations, apply all available updates |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`status`** | Read-only. Shows current tracking status for all sources — last sync timestamp, last commit, staleness estimate, and dependent skills |
| **`sync`** | Full 6-phase workflow. Checks upstream repos for changes, presents diffs, and applies updates with user confirmation (or `--auto`) |
| **`add`** | Guided workflow to add a new upstream source to manifest.json. Prompts for repo URL, type, source path, mapping, and referencing skills |
| **`remove`** | Removes a tracked source from manifest.json. Confirms before deletion |
| **`check`** | Read-only. Checks if tracked sources have been updated since last sync. Reports what changed but does NOT apply changes |
| **`docs-check`** | Read-only. For sources with a `docs` field, fetches `llms.txt` or `llms-full.txt` URLs and compares against current skill reference content. Reports which tool docs changed |
| `--source <name>` | Limits any action to the specified source only |
| `--auto` (with sync) | Applies all available updates without per-source confirmation |
| `--verbosity short` | One-line status per source |
| `--verbosity detailed` | Full diffs, commit messages, and file-level changelogs |

## Source Types

| Type | Behavior |
|------|----------|
| **copy** | Files are copied verbatim from upstream via path mapping. `sync` clones/fetches, diffs mapped paths against local copies, and applies updates |
| **ref** | Upstream is an inspiration, not a direct copy source. `sync` checks if referenced patterns have changed and flags skills for manual review |

## Key Behaviors

- **manifest.json as single source of truth**: all tracking metadata, source mappings, and sync timestamps live in one file at the repo root
- **Two source types**: `copy` (verbatim file sync) and `ref` (inspiration tracking with manual review)
- **Upstream change detection**: uses `git ls-remote` to compare upstream HEAD against last known commit without cloning
- **Docs-check for tool documentation**: fetches `llms.txt`/`llms-full.txt` URLs, compares against skill reference content, detects new features, deprecated features, changed syntax
- **Guided add workflow**: interactive prompts for repo URL, type, branch, source path, mapping, referencing skills, and notes
- **Diff-based sync**: for `type=copy`, produces concrete file-level diffs before applying; for `type=ref`, summarizes meaningful changes for manual review
- **Post-sync validation**: verifies copied files match upstream versions and manifest.json was updated correctly

## Workflow

Uses the 6-phase workflow for sync actions. Status, check, and docs-check are read-only operations.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm which sources to sync and whether `--auto` is active |
| 1. Research & Options | yes | Fetch upstream changes; clone or fetch repos; diff mapped paths |
| 2. Approach Selection | sync only | Present impact assessment — what changed and which skills are affected |
| 3. Planning | sync only | List concrete file operations to perform |
| 4. Execute | yes | Apply changes (copy files, update manifest.json, or flag for manual review) |
| 5. Validate & Learn | yes | Verify copies match upstream, confirm manifest updated, summarize changes |

## Skill-to-Source Mapping

| Source | Type | Skills |
|--------|------|--------|
| `diagramkit` | copy | `diagram-mermaid`, `diagram-excalidraw`, `diagram-drawio`, `diagram-graphviz`, `diagram` |
| `pagesmith` | ref | `docs-write`, `docs-repo`, `docs-review`, `docs-crud`, `docs-md` |
| `superpowers` | ref | `dev-build`, `plan`, `code-review-pr` |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation |
| `output-format` | producing output | short/standard/detailed verbosity |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents for parallel sync and diff analysis |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown. Format varies by action:

- **status**: Per-source block with repo URL, last sync date, last commit, dependent skills, and staleness indicator
- **check**: Summary table with source, type, last sync, upstream HEAD, and status (up-to-date vs. new commits)
- **docs-check**: Summary table with tool, source, llms.txt availability, status, and skills to review
- **sync**: Impact assessment with changed files, affected skills, and file operations; post-sync verification summary
- **add/remove**: Confirmation of manifest.json changes

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:setup` | Install required CLI tools (git) |
| `/adk:project` | Broader project management, milestones, and roadmaps |
| `/adk:research` | Deep investigation of upstream changes or new sources to track |

## Examples

```
/adk:deps-tracker status
/adk:deps-tracker docs-check
/adk:deps-tracker docs-check --source diagramkit
/adk:deps-tracker check --source diagramkit
/adk:deps-tracker sync --source pagesmith
/adk:deps-tracker sync --auto
/adk:deps-tracker add
/adk:deps-tracker remove --source superpowers
```
