---
name: dev-migrate
description: "adk - [full] [dev] Migrate frameworks, libraries, or language versions — analyze breaking changes, map to codebase, execute migration plan"
user-invocable: true
argument-hint: "<source> to <target> [--scope <path>] [--dry-run] [--auto] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: complex-build
---

# Migration

Analyze and execute framework, library, or language version migrations. Reads official migration guides, maps breaking changes to your codebase, generates a step-by-step plan, and applies changes with validation.

## Shared Skills

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

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<source>` | framework/library name + version | required | Current framework, library, or version |
| `to <target>` | framework/library name + version | required | Target framework, library, or version |
| `--scope` | `<path>` | entire repo | Limit analysis to specific files/directories |
| `--dry-run` | flag | off | Analyze and plan only, do not apply changes |
| `--auto` | flag | off | Skip confirmations, execute full migration |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Behavior Variations

- **Same library, version bump**: reads changelogs and migration guides, identifies breaking changes, applies fixes
- **Different library**: maps API surface differences, generates adapter patterns or direct replacements
- **Language version**: updates syntax, deprecated API usage, config files, and CI configuration
- **`--dry-run`**: produces analysis and plan only — no code changes
- **`--auto`**: executes the full migration without confirmation gates

### Examples

```text
/adk:dev-migrate react@17 to react@19
/adk:dev-migrate webpack to vite --scope packages/frontend
/adk:dev-migrate python 3.9 to python 3.12
/adk:dev-migrate express to fastify --dry-run
/adk:dev-migrate jest to vitest --auto
```

---

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If any declared dependency is missing, stop and tell the user what to install before proceeding.

---

## Migration Process

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
## Migration Impact

| Breaking Change | Files Affected | Effort | Risk | Codemod Available |
|-----------------|----------------|--------|------|-------------------|
| API renamed     | 12 files       | Low    | Low  | Yes (jscodeshift)  |
| Config format   | 3 files        | Medium | Low  | No                 |
| Plugin API      | 5 files        | High   | Med  | No                 |
```

### 4. Migration Plan

Generate ordered waves of changes:

- **Wave 1**: Configuration and build setup changes
- **Wave 2**: Direct API renames (codemod-assisted when available)
- **Wave 3**: Behavioral changes requiring manual review
- **Wave 4**: Plugin/extension updates
- **Wave 5**: Test updates and cleanup

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

## Output Format

```markdown
# Migration Report: <source> → <target>

## Summary
- **Files analyzed**: N
- **Files changed**: N
- **Breaking changes resolved**: N/M
- **Tests passing**: N/M

## Changes by Wave

### Wave 1: Configuration
- [file list with changes]

### Wave 2: API Updates
- [file list with changes]

## Remaining Manual Steps
- [ ] item 1
- [ ] item 2

## Known Risks
- Risk 1: description and mitigation
```

---

## Adjacent Skills

- `/adk:research` for deep-diving into migration guides and community patterns
- `/adk:dev-build` for implementing complex changes during migration
- `/adk:audit` for post-migration quality check
- `/adk:code-review-pr` for reviewing the migration PR
