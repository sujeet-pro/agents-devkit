---
title: 'dev-migrate'
description: 'Migrate frameworks, libraries, or language versions — analyze breaking changes, map to codebase, execute migration plan'
skill_name: dev-migrate
category: task
workflow_tier: full
user_invocable: true
---

# dev-migrate

Use `dev-migrate` to migrate frameworks, libraries, or language versions — analyze breaking changes, map to codebase, execute migration plan. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`dev-migrate` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<source>` | framework/library name + version | required | Current framework, library, or version |
| `to <target>` | framework/library name + version | required | Target framework, library, or version |
| `--scope` | `<path>` | entire repo | Limit analysis to specific files/directories |
| `--dry-run` | flag | off | Analyze and plan only, do not apply changes |
| `--auto` | flag | off | Skip confirmations, execute full migration |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family complex-build` | always | Complex Build workflow: confirm → research → select approach → plan → execute → validate. Full human-in-the-loop for architectural decisions. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Markdown default. |
| `/adk:principal-engineer` | always for migrations | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch `adk-migration-analyst` for migration analysis (usage mapping, changelogs, breaking changes, file-level impact). For larger scopes, split into parallel focused agents: usage analyzer, changelog researcher, migration planner, risk assessor. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

---

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If any declared dependency is missing, stop and tell the user what to install before proceeding.

---

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **Same library, version bump**: reads changelogs and migration guides, identifies breaking changes, applies fixes
- **Different library**: maps API surface differences, generates adapter patterns or direct replacements
- **Language version**: updates syntax, deprecated API usage, config files, and CI configuration
- **`--dry-run`**: produces analysis and plan only — no code changes
- **`--auto`**: executes the full migration without confirmation gates

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```markdown
# Migration Report: <source> → <target>

## Related Skills

### Adjacent Skills

- `/adk:research` for deep-diving into migration guides and community patterns
- `/adk:dev-build` for implementing complex changes during migration
- `/adk:audit` for post-migration quality check
- `/adk:code-review-pr` for reviewing the migration PR

## Additional Reference

### Migration Process

### 1. Usage Analysis

- Scan the codebase for all imports, usages, and configuration of the source library
- Count affected files and categorize by usage pattern
- Identify the most critical usage sites (high-traffic paths, complex integrations)
- Check for plugins, extensions, or wrappers that depend on the source

### 2. Changelog Research

- Read the official migration guide for source → target
- Identify all breaking changes and their recommended fixes
- Check for available codemods or automated migration tools
- Search for community migration experiences and gotchas

### 3. Impact Mapping

Map each breaking change to specific files in the codebase:

```

### Migration Impact

| Breaking Change | Files Affected | Effort | Risk | Codemod Available |
|-----------------|----------------|--------|------|-------------------|
| API renamed     | 12 files       | Low    | Low  | Yes (jscodeshift)  |
| Config format   | 3 files        | Medium | Low  | No                 |
| Plugin API      | 5 files        | High   | Med  | No                 |
```

> **Gate**: Present impact analysis to user for review before generating migration plan. Skip if `--auto`.

### 4. Migration Plan

Generate ordered waves of changes:

- **Wave 1**: Configuration and build setup changes
- **Wave 2**: Direct API renames (codemod-assisted when available)
- **Wave 3**: Behavioral changes requiring manual review
- **Wave 4**: Plugin/extension updates
- **Wave 5**: Test updates and cleanup

> **Gate**: Present migration plan to user for approval before execution. Skip if `--auto`.

### 5. Execution

- Apply each wave sequentially
- Run available tests after each wave
- Flag regressions immediately and offer rollback or fix
- Track progress with file-level granularity

### 6. Validation

- Run full test suite
- Check for remaining references to old API
- Verify build succeeds with new configuration
- Produce a migration summary with statistics

---

### Summary

- **Files analyzed**: N
- **Files changed**: N
- **Breaking changes resolved**: N/M
- **Tests passing**: N/M

### Changes by Wave

### Wave 1: Configuration
- [file list with changes]

### Wave 2: API Updates
- [file list with changes]

### Remaining Manual Steps

- [ ] item 1
- [ ] item 2

### Known Risks

- Risk 1: description and mitigation
```

---

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:dev-migrate <source> <target>
/adk:dev-migrate react@17 to react@19
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:dev-migrate webpack to vite --scope packages/frontend
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:dev-migrate jest to vitest --auto
```
