# adk-migrate

Upgrade frameworks, libraries, or patterns with breaking-change analysis and staged validation.

## Quick Start

Install via npx skills, then invoke:

```
/adk-migrate "Upgrade React from v17 to v18" --source react
```

```
/adk-migrate "Replace moment.js with date-fns" --source moment --scope src/utils/
```

```
/adk-migrate "Move from REST client v2 to v3 API shape" --scope src/api/
```

```
/adk-migrate "Upgrade TypeScript from 4.x to 5.x" --source typescript --auto
```

## What This Skill Does

Manages framework, library, and pattern migrations with a staged approach. It researches current breaking changes and migration notes, maps them to actual local usage, plans the migration in waves, applies one wave at a time with validation, and reports what moved, what remains, and residual risk.

## Command Reference

| Invocation | Description |
| --- | --- |
| `/adk-migrate "<task>"` | Migrate with auto-detected source |
| `/adk-migrate "<task>" --source <name>` | Name the primary migration target explicitly |
| `/adk-migrate "<task>" --scope <path>` | Limit the migration surface to a specific area |
| `/adk-migrate "<task>" --auto` | Skip confirmations, use defaults |
| `/adk-migrate --help` | Show the skill description and stop |

## Dependencies

| Dependency | Required? | Install Command |
| --- | --- | --- |
| git | Yes | `brew install git` |
| python3 | Yes | `brew install python@3` |

## Skill Layout

```
adk-migrate/
  SKILL.md              # Skill definition and instructions
  README.md             # This file
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Migration workflow details
    persona.md           # Agent persona guidance
    _shared/
      ai-guidelines-overview.md
      constitution.md
      output-format.md
      research-protocol.md
```

## Workflow

1. **Confirm target** -- verify the migration target, scope, and rollback expectations with the user
2. **Read local usage** -- understand how the current version is used in the codebase
3. **Research breaking changes** -- fetch current migration notes and breaking-change lists
4. **Plan waves** -- organize the migration into staged waves for incremental validation
5. **Apply per wave** -- apply one wave at a time with validation after each
6. **Report** -- list what moved, what remains, and residual risk

## Interaction Protocol

- **Confirmations**: Before executing, the skill confirms source/target versions, scope, and rollback strategy. Use `--auto` to skip.
- **Findings format**: A breaking changes map is shown before execution. Each migration wave is presented for approval. Validation results follow each wave.
- **User response syntax**: Reply with "approve wave", "skip this wave", "adjust scope to ...", or "rollback" after reviewing each wave.

## Output Format

1. **Summary** -- one-line description of the migration performed
2. **Scope** -- frameworks/libraries and files affected
3. **Changes** -- per-wave breakdown of what was migrated
4. **Validation** -- test and build output per wave
5. **Remaining risk** -- known incompatibilities, deprecated usages still present, untested paths
6. **Next steps** -- remaining waves, manual verification steps, or follow-up migrations

## Examples

### Framework upgrade
```
> /adk-migrate "Upgrade React from v17 to v18" --source react

Breaking changes found: 3 affecting local code
  - ReactDOM.render -> createRoot (12 call sites)
  - automatic batching behavior change (2 custom batching wrappers)
  - stricter StrictMode warnings (informational only)

Wave 1: Update package.json and lock file
  Validation: build succeeds with warnings
Wave 2: Replace ReactDOM.render with createRoot (12 files)
  Validation: 48 tests pass, 0 regressions
Wave 3: Remove custom batching wrappers (2 files)
  Validation: all tests pass

Remaining risk: StrictMode warnings in 3 components (non-blocking)
```

### Library replacement with scope
```
> /adk-migrate "Replace moment.js with date-fns" --source moment --scope src/utils/

Local usage: 23 moment calls across 8 files in src/utils/
Migration map: moment.format -> format, moment.diff -> differenceInDays, ...

Wave 1: Add date-fns dependency, create adapter layer
Wave 2: Replace formatting calls (14 sites)
Wave 3: Replace diff/comparison calls (9 sites)
Wave 4: Remove moment dependency

Remaining risk: 2 calls use moment.locale() -- date-fns locale import needed
```

## What Success Looks Like

- [ ] Source and target versions are confirmed before any changes
- [ ] Breaking changes are mapped to actual local usage
- [ ] Migration proceeds in validated waves
- [ ] Each wave has validation output
- [ ] Rollback or containment strategy is explicit
- [ ] Residual risk and remaining work are stated clearly
