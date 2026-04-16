# adk-SKILL-NAME

One-line description matching the SKILL.md description field.

## Quick Start

```bash
# Install
npx skills add adk-SKILL-NAME

# Basic usage
/adk-SKILL-NAME <task>

# With options
/adk-SKILL-NAME <task> --flag value --scope src/

# Auto mode (skip confirmations)
/adk-SKILL-NAME <task> --auto

# Show help
/adk-SKILL-NAME --help
```

## What This Skill Does

2-3 sentences explaining the skill's purpose, approach, and what makes it distinct from related skills.

## Command Reference

| Invocation | Behavior |
| --- | --- |
| `/adk-SKILL-NAME <task>` | Default mode with intent confirmation |
| `/adk-SKILL-NAME <task> --flag value` | Narrowed to specific mode |
| `/adk-SKILL-NAME <task> --scope path` | Limited to specific directory |
| `/adk-SKILL-NAME <task> --auto` | Skip confirmations, use defaults |
| `/adk-SKILL-NAME --help` | Print skill summary and stop |

## Dependencies

| Dependency | Required | Install |
| --- | --- | --- |
| `git` | yes | `brew install git` (macOS) |
| `python3` | yes | `brew install python@3` (macOS) |
| MCP: `server-name` | for feature X | See [MCP Setup](#mcp-setup) |

The pre-flight script checks all dependencies automatically:
```bash
python3 scripts/preflight.py .
```

## Skill Layout

```
adk-SKILL-NAME/
  SKILL.md              # Skill definition and routing
  README.md             # This file -- operating manual
  scripts/
    preflight.py        # Dependency and environment checks
  references/
    _shared/            # Shared ADK guidance (synced from ai-guidelines/)
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
    persona.md          # Skill-specific persona and hard rules
    workflow.md         # Detailed workflow steps and mode variations
```

## Workflow

### Step 1: Pre-flight
Run dependency checks. Stop if required tools are missing.

### Step 2: Intent Confirmation
Restate the task, scope, and expected outcome. Ask the user to confirm.
Skipped with `--auto`.

### Step 3: Inspect
Read only the code, docs, or sources relevant to the task.

### Step 4: Plan (non-trivial tasks)
Present a short plan before making changes. Skipped for trivial tasks.

### Step 5: Execute
Perform the smallest correct action.

### Step 6: Validate
Run repo-native checks (tests, lint, build) and report results.

### Step 7: Report
Present structured results with findings IDs, validation outcome, and remaining risk.

## Interaction Protocol

### Confirmations
By default, the skill confirms intent before starting and presents results before taking action.
Use `--auto` to skip confirmations and proceed with defaults.

### Findings Format
When the skill produces findings (reviews, audits, analyses), each finding has a stable ID:
```
F1 [Critical] Title -- path/to/file.ext:42
   Description and evidence.
F2 [Should Have] Title -- path/to/file.ext:88
   Description and evidence.
```

### User Response
After seeing findings, respond with:
- `a-1,2` -- accept findings 1 and 2
- `r-3` -- reject finding 3
- `e-4` -- discuss/edit finding 4
- `all` -- accept everything
- Or give free-text instructions for what to do next.

## Output Format

Results always include:
1. **Summary** -- one sentence on what was done
2. **Scope** -- what was analyzed or changed
3. **Findings/Changes** -- itemized with IDs
4. **Validation** -- what ran and passed/failed
5. **Remaining risk** -- open questions
6. **Next steps** -- suggested follow-up

## Examples

### Example 1
```
/adk-SKILL-NAME describe the basic scenario
```
Brief description of what the skill does in this case.

### Example 2
```
/adk-SKILL-NAME describe a scoped scenario --scope src/api --auto
```
Brief description of scoped/auto behavior.

## What Success Looks Like

- [ ] Task completed as confirmed in intent step
- [ ] Validation checks passed (or gaps explicitly noted)
- [ ] Results presented with stable IDs and severity
- [ ] No unverified claims
- [ ] User knows what to do next
