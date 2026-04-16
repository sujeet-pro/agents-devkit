---
name: adk-SKILL-NAME
description: One-line description of what this skill does and when to use it.
compatibility: Self-contained published skill for npx skills. Works best when [tools/services] are available.
user-invocable: true
argument-hint: "<task> [--flag value] [--auto] [--help]"
workflow-tier: full
maturity: experimental
workflow-family: standard-task
tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, WebSearch, WebFetch]
metadata:
  area: development
dependencies:
  commands: [git, python3]
  mcp-servers: []
---

# ADK Skill Title

## Overview
One short paragraph on the outcome this skill produces and the approach it takes.

## When To Use
- concrete trigger scenario
- another trigger scenario
- NOT for <out-of-scope case> -- use `adk-other-skill` instead
- NOT for <another out-of-scope case>

## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/research-protocol.md`
- `references/_shared/output-format.md`
- `references/workflow.md`
- `references/persona.md`

## Parameters
| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What should be done |
| `--flag` | `option-a`, `option-b` | `option-a` | Narrow the scope or mode |
| `--scope` | path | repo root | Limit analysis to a directory or file |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Print this skill summary and stop |

## Pre-flight
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}` before starting.
- **Required**: `git`, `python3` must be in PATH
- **Optional**: list any optional tools and what degrades without them
- **MCP**: list required MCP servers; if missing, print setup instructions and stop
- If any required dependency is missing, stop and show install instructions.

## Workflow
1. **Confirm intent** -- restate the task, scope, and expected outcome. Ask the user to confirm or refine. Skip if `--auto`.
2. **Inspect** -- read only the code, docs, or sources needed for this task.
3. **Plan** -- for non-trivial changes, write a short plan and present it. Skip for trivial tasks.
4. **Execute** -- perform the smallest correct action for the task.
5. **Validate** -- run repo-native checks (tests, lint, build) before claiming success.
6. **Report** -- present results in the output format below.

## Interaction Protocol

### Intent Confirmation (Step 1)
Before starting work, confirm the user's intent:
```
I will [action] targeting [scope].
- Mode: [mode]
- Focus: [focus area]
- Validation: [what will be checked]

Proceed? (yes / adjust scope / cancel)
```
Skip this step when `--auto` is set.

### Progress Updates
For multi-step work, show brief inline updates:
```
[step N/total] description of current step...
```

### Results Presentation
Present findings or results with stable IDs for reference:
```
### Results

**F1** [severity] title -- file:line
  description and evidence

**F2** [severity] title -- file:line
  description and evidence

---
Summary: N findings (X critical, Y suggestions)
```

### User Response (when applicable)
After presenting findings, the user may respond with:
- `a-1,2,3` -- accept findings 1, 2, 3
- `r-4` -- reject finding 4
- `e-5` -- edit/discuss finding 5
- `all` -- accept all findings
Or the user may give free-text follow-up instructions.

## Validation
- run the smallest relevant repo-native commands first
- if a claim cannot be verified, say so explicitly
- do not claim success without fresh evidence
- list what was validated and what could not be checked

## Output
Results follow this structure:
- **summary**: one sentence on what was done
- **scope**: what was analyzed or changed
- **findings/changes**: itemized list with IDs and severity where applicable
- **validation**: what checks ran and their results
- **remaining risk**: open questions or unchecked areas
- **next steps**: suggest logical follow-up actions or ask if more detail is needed

## Examples

### Example 1: Basic usage
```
/adk-SKILL-NAME do the thing
```
Describe what happens.

### Example 2: Scoped usage
```
/adk-SKILL-NAME do the thing --scope src/api --auto
```
Describe what happens differently with flags.

## Related Skills
- `adk-other-skill` -- when the task shifts direction
- `adk-another-skill` -- for a complementary workflow
