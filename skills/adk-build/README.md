# adk-build

Implement or enhance code with a plan, focused research, and validation.

## Quick Start

Install via npx skills, then invoke:

```
/adk-build "Add retry logic to the HTTP client" --mode implement --scope src/http/
```

```
/adk-build "Users report 500 errors on /api/health" --mode debug
```

```
/adk-build "Confirm the pagination fix works for edge cases" --mode verify --scope src/api/pagination.ts
```

```
/adk-build "Add caching layer for user lookups" --plan docs/caching-plan.md
```

## What This Skill Does

Builds, fixes, or verifies code changes using a small evidence-first workflow. It confirms the task and scope, reads only the code needed, writes a short plan for non-trivial changes, implements the smallest correct change, and runs repo-native validation before reporting results.

## Command Reference

| Invocation | Description |
| --- | --- |
| `/adk-build "<task>"` | Build a feature using implement mode (default) |
| `/adk-build "<task>" --mode debug` | Root-cause and fix a bug |
| `/adk-build "<task>" --mode verify` | Verify that a change is actually complete |
| `/adk-build "<task>" --plan <path>` | Follow an existing plan file |
| `/adk-build "<task>" --scope <path>` | Limit analysis to one area |
| `/adk-build "<task>" --auto` | Skip confirmations, use defaults |
| `/adk-build --help` | Show the skill description and stop |

## Dependencies

| Dependency | Required? | Install Command |
| --- | --- | --- |
| git | Yes | `brew install git` |
| python3 | Yes | `brew install python@3` |

## Skill Layout

```
adk-build/
  SKILL.md              # Skill definition and instructions
  README.md             # This file
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Build workflow details
    persona.md           # Agent persona guidance
    _shared/
      ai-guidelines-overview.md
      constitution.md
      output-format.md
      research-protocol.md
```

## Workflow

1. **Confirm scope** -- verify the task, mode, scope, constraints, and validation target with the user
2. **Read local code** -- read only the code and sources needed for the chosen mode
3. **Plan** -- write or refine a short plan before making non-trivial changes
4. **Implement** -- make the smallest correct change for the selected mode
5. **Validate** -- run repo-native validation before claiming success
6. **Report** -- list changed files, validation results, and remaining risk

## Interaction Protocol

- **Confirmations**: Before starting, the skill confirms the task, mode, and scope. Use `--auto` to skip.
- **Findings format**: Changed files are listed with a one-line diff summary each. Validation output is included inline.
- **User response syntax**: Reply with "proceed", "adjust scope to ...", or "stop" after seeing the plan.

## Output Format

1. **Summary** -- one-line description of what was done
2. **Scope** -- files and directories affected
3. **Changes** -- list of changed files with diff summaries
4. **Validation** -- command output from repo-native checks
5. **Remaining risk** -- known gaps or unverified claims
6. **Next steps** -- suggested follow-up actions

## Examples

### Build a new feature
```
> /adk-build "Add retry logic to the HTTP client" --mode implement --scope src/http/

Confirmed: implement retry logic in src/http/
Plan: add RetryPolicy class, wrap fetch calls, add unit tests
Changed files:
  src/http/retry-policy.ts  (new, 45 lines)
  src/http/client.ts        (+12 -3)
  tests/http/retry.test.ts  (new, 38 lines)
Validation: 14 tests passed, 0 failed
Remaining risk: no integration test for timeout scenarios
```

### Debug a production issue
```
> /adk-build "Users report 500 errors on /api/health" --mode debug

Root cause: health check queries a stale DB connection pool
Fix: add connection validation before health query
Changed files:
  src/api/health.ts  (+8 -2)
  tests/api/health.test.ts  (+15)
Validation: all tests pass, manual curl returns 200
```

### Verify a prior change
```
> /adk-build "Confirm the pagination fix works for edge cases" --mode verify --scope src/api/pagination.ts

Verified: pagination handles empty results, single page, and last-page boundary
No code changes needed
Validation: 6 existing tests pass, 2 new edge-case tests added
```

## What Success Looks Like

- [ ] Task is confirmed with clear scope before any code changes
- [ ] Only the minimal necessary code is changed
- [ ] Repo-native validation passes
- [ ] Changed files are listed with diff summaries
- [ ] Remaining risk is stated explicitly
- [ ] No guesswork -- claims are backed by evidence
