---
title: "dev-migrate"
description: Migrate frameworks, libraries, or language versions — analyze breaking changes, map to codebase, execute migration plan
skill_name: dev-migrate
category: task
workflow_tier: full
user_invocable: true
---

# dev-migrate

Analyze and execute framework, library, or language version migrations. Reads official migration guides, maps breaking changes to your codebase, generates a step-by-step plan, and applies changes with validation.

## When to Use

- Upgrade a library or framework to a new major version
- Switch from one library to an equivalent alternative (e.g., webpack → vite)
- Upgrade a language runtime version (e.g., Python 3.9 → 3.12)
- Analyze breaking changes before committing to a migration
- Run a dry-run migration to assess effort and risk

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<source>` | framework/library name + version | required | Current framework, library, or version |
| `to <target>` | framework/library name + version | required | Target framework, library, or version |
| `--scope` | `<path>` | entire repo | Limit analysis to specific files/directories |
| `--dry-run` | flag | off | Analyze and plan only, do not apply changes |
| `--auto` | flag | off | Skip confirmations, execute full migration |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| Same library, version bump | Reads changelogs and migration guides, identifies breaking changes, applies fixes |
| Different library | Maps API surface differences, generates adapter patterns or direct replacements |
| Language version | Updates syntax, deprecated API usage, config files, and CI configuration |
| `--dry-run` | Produces analysis and plan only — no code changes |
| `--auto` | Executes the full migration without confirmation gates |

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

Map each breaking change to specific files in the codebase with a table showing the breaking change, files affected, effort, risk, and whether a codemod is available.

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

## Key Behaviors

- **Research-driven**: reads official migration guides, changelogs, and community patterns before planning
- **Wave-based execution**: groups changes into ordered waves to isolate risk
- **Codemod detection**: checks for available automated migration tools before manual changes
- **Impact mapping**: maps every breaking change to specific files with effort and risk estimates
- **Rollback-ready**: each wave can be reverted independently if regressions are detected

## Workflow

Follows the 6-phase workflow. All phases apply for migrations.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm source, target, scope, and constraints |
| 1. Research & Options | yes | Read official migration guides, changelogs, breaking changes, community patterns |
| 2. Approach Selection | yes | Present migration strategies: incremental, big-bang, strangler pattern |
| 3. Planning | yes | Map breaking changes to specific files, create ordered migration waves |
| 4. Execute | yes | Apply changes wave by wave, run tests after each wave |
| 5. Validate & Learn | yes | Full test suite, manual verification of critical paths |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping. |
| `communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `output-format` | producing output | short/standard/detailed verbosity. Markdown default. |
| `principal-engineer` | always for migrations | Five PE questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Migration team: usage analyzer, changelog researcher, migration planner, risk assessor. |
| `interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

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

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:research` | Deep-diving into migration guides and community patterns |
| `/adk:dev-build` | Implementing complex changes during migration |
| `/adk:audit` | Post-migration quality check |
| `/adk:code-review-pr` | Reviewing the migration PR |

## Examples

```
/adk:dev-migrate react@17 to react@19
/adk:dev-migrate webpack to vite --scope packages/frontend
/adk:dev-migrate python 3.9 to python 3.12
/adk:dev-migrate express to fastify --dry-run
/adk:dev-migrate jest to vitest --auto
```
