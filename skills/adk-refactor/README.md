# adk-refactor

Improve code structure without changing behavior.

## Quick Start

Install via npx skills, then invoke:

```
/adk-refactor "Extract duplicated validation logic into a shared module" --scope src/validators/
```

```
/adk-refactor "Rename UserManager to UserService and split read/write concerns"
```

```
/adk-refactor "Move database queries out of the controller layer" --scope src/controllers/
```

## What This Skill Does

Restructures code for better readability, boundaries, and maintainability while preserving existing behavior. It confirms the intended unchanged behavior, inspects current structure and tests, applies the smallest safe sequence of refactors one concern at a time, and runs regression checks after each step.

## Command Reference

| Invocation | Description |
| --- | --- |
| `/adk-refactor "<task>"` | Refactor code with behavior preservation |
| `/adk-refactor "<task>" --scope <path>` | Limit the refactor surface to a specific area |
| `/adk-refactor "<task>" --auto` | Skip confirmations, use defaults |
| `/adk-refactor --help` | Show the skill description and stop |

## Dependencies

| Dependency | Required? | Install Command |
| --- | --- | --- |
| git | Yes | `brew install git` |
| python3 | Yes | `brew install python@3` |

## Skill Layout

```
adk-refactor/
  SKILL.md              # Skill definition and instructions
  README.md             # This file
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Refactor workflow details
    persona.md           # Agent persona guidance
    _shared/
      ai-guidelines-overview.md
      constitution.md
      output-format.md
      research-protocol.md
```

## Workflow

1. **Confirm behavior contract** -- verify the behavior that must be preserved and whether tests cover it
2. **Inspect structure** -- read the current code structure and existing tests
3. **Plan refactors** -- choose the smallest safe sequence of structural changes
4. **Apply one at a time** -- change one structural concern per step
5. **Regress after each step** -- run regression checks after each meaningful change
6. **Report** -- present preserved behavior evidence and structural gains

## Interaction Protocol

- **Confirmations**: Before starting, the skill confirms the refactor scope and the behavior-preservation intent. Use `--auto` to skip.
- **Findings format**: Before/after structure comparison for each changed area. Regression test output is included inline.
- **User response syntax**: Reply with "proceed", "adjust scope to ...", or "revert last step" after seeing the plan.

## Output Format

1. **Summary** -- one-line description of the structural improvement
2. **Scope** -- files and directories affected
3. **Changes** -- before/after structure for each refactored area
4. **Validation** -- regression check output
5. **Remaining risk** -- areas not yet covered by tests or still needing cleanup
6. **Next steps** -- suggested follow-up refactors or test additions

## Examples

### Extract shared logic
```
> /adk-refactor "Extract duplicated validation logic into a shared module" --scope src/validators/

Confirmed: extract shared validation, preserve all existing behavior
Plan: create shared/validation.ts, update 4 consumers
Changed files:
  src/validators/shared/validation.ts  (new, 32 lines -- extracted from duplicates)
  src/validators/user.ts               (-18 lines, now imports shared)
  src/validators/order.ts              (-15 lines, now imports shared)
  src/validators/product.ts            (-12 lines, now imports shared)
  src/validators/payment.ts            (-14 lines, now imports shared)
Validation: 42 tests pass, 0 regressions
Structural gain: 59 lines of duplication removed
```

### Rename and split concerns
```
> /adk-refactor "Rename UserManager to UserService and split read/write concerns"

Before: UserManager (1 class, 340 lines, mixed read/write)
After:  UserReadService (120 lines) + UserWriteService (180 lines)
Validation: all 28 tests pass after updating imports
Remaining risk: 3 integration tests reference old class name via string -- grep to confirm
```

## What Success Looks Like

- [ ] Behavior is confirmed unchanged with test evidence
- [ ] Refactor scope is confirmed before changes begin
- [ ] Changes are applied one structural concern at a time
- [ ] Before/after structure is presented for each change
- [ ] Regression checks pass after each step
- [ ] No new abstractions without clear justification
