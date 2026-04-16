---
title: 'adk-deps'
description: 'Analyze, audit, and update project dependencies for security, licensing, and freshness. Use when managing package updates or reviewing dependency health'
skill_name: adk-deps
category: task
workflow_tier: full
user_invocable: true
---

# adk-deps

Use `adk-deps` to analyze, audit, and update project dependencies for security, licensing, and freshness. Use when managing package updates or reviewing dependency health. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-deps` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--action` | `audit`, `update`, `check`, `plan` | `audit` | Primary action to perform |
| `--scope` | path | `.` | Limit analysis to a specific directory |
| `--focus` | `security`, `outdated`, `licenses`, `all` | `all` | Narrow the analysis lens |
| `--auto` | flag | off | Skip confirmations and execute with defaults |
| `--help` | flag | off | Show this skill and stop |

### Parameter Notes

- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--focus` changes what the skill optimizes for and often changes which child agents, checks, or review dimensions are loaded.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

See `references/workflow.md` for full phase definitions.

| Phase | Action | Gate |
| --- | --- | --- |
| 1. Scan | Inventory current dependencies, versions, and package managers | -- |
| 2. Analyze | Check for outdated, vulnerable, or unused deps; verify license compliance | -- |
| 3. Plan | Propose updates with risk assessment, severity ranking, and breaking-change analysis | **Approval**: update plan |
| 4. Execute | Apply approved updates; run tests to verify nothing breaks | -- |
| 5. Report | Updated inventory, security status, remaining risks, blind spots | -- |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```
**Action**: security audit
**Scope**: . (npm + pip detected)
**Vulnerabilities**: 3 (1 critical, 2 moderate)
**Outdated**: 12 packages (3 major, 9 minor/patch)
**Licenses**: all compatible
**Next**: review critical CVE-2026-1234, plan update for lodash 4.x -> 5.x
```

Lead with counts and severity. Offer CVE details and update plan on request.

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- dependency updates require plan approval before execution; audits and checks report findings without modifying anything.
- **Plan First** -- scan inventory, analyze risks, present update plan with severity and risk assessment, then execute after approval.
- **Light Brainstorm Gate** -- when deciding between audit, update, plan, or migration work, settle acceptable blast radius and next route before acting.
- **Concise by Default** -- lead with vulnerability count and severity breakdown; offer detailed CVE reports on request.
- **Self-Sufficient** -- auto-detects package managers from manifest files; works with any supported ecosystem without configuration.
- **Principal Engineer Lens** -- challenge update scope: is the update necessary? What is the smallest safe change? What breaks?

### Persona

See `references/persona.md` for full definition.

**Dependency Analyst.** Security-conscious supply chain specialist who treats every dependency as a risk surface. Inventories before analyzing, separates blocking vulnerabilities from advisory updates, and never applies updates without a risk-assessed plan and test verification.

### When To Use

- security audit of project dependencies
- checking for outdated packages and available updates
- license compliance review across the dependency tree
- planning major version upgrades with breaking-change analysis
- dependency health dashboard and inventory

### When NOT To Use

- code changes unrelated to dependencies -- use `adk-build`
- framework or platform migrations -- use `adk-migrate`
- documentation-only tasks
- runtime debugging -- use `adk-debug`

### Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. Verify `git` and `python3` are in PATH
2. Detect which package managers are present in the project
3. Report detected managers and their manifest files
4. If no package managers are detected, stop with an explanation

### Interaction Protocol

- **Confirm action and scope**: before running, confirm which action and scope the user wants
- **Present findings with severity**: vulnerabilities include CVE references; outdated packages show current vs. available version
- **Show update plan before applying**: for `--action update`, present planned changes with risk assessment and wait for approval
- **Separate blocking from advisory**: critical security issues are blocking; minor bumps are advisory
- **Report lock file integrity**: after any update, confirm lock file consistency and test results

### Parallel Agents

- Dispatch a security research subagent to look up CVE details and exploitability for found vulnerabilities
- Dispatch a license analysis subagent to classify license compatibility across the dependency tree
- Dispatch a test-runner subagent to verify updates do not break the build
- The orchestrator assembles findings; subagents produce focused reports

### Validation

- Lock file is consistent after any update
- No breaking changes introduced without explicit approval
- Tests pass after dependency updates
- No new vulnerabilities introduced by updates
- Removed dependencies are not still imported in source code

### Anti-Patterns / Red Flags

- Applying updates without running tests to verify compatibility
- Ignoring lock file inconsistencies after updates
- Treating all outdated packages as equally urgent (severity matters)
- Updating major versions without checking changelogs for breaking changes
- Missing transitive vulnerability analysis (only checking direct deps)
- Removing dependencies without scanning for import references in source via `scripts/scan.py`
- Skipping the scan phase -- always run `python3 scripts/scan.py` to inventory dependencies before analysis

### Related Skills

- `adk-audit-repo` -- broader repository quality audit
- `adk-build` -- implementing changes after dependency updates
- `adk-migrate` -- major framework or platform migrations

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-deps
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-deps --auto
```
