# adk-plan

Create an executable implementation plan with scoped files, risks, and validation checkpoints.

## Quick Start

```
npx adk-plan "migrate the auth module from session-based to JWT"
```

Or as a slash command:

```
/adk-plan migrate the auth module from session-based to JWT
```

## What This Skill Does

Turns a request into a small, reviewable, executable plan with explicit validation steps. Plans are organized into sequential waves with numbered task IDs (T1.1, T1.2, T2.1) so users can reference, accept, modify, or reject individual tasks. The skill inspects the codebase, surfaces viable approaches when choices matter, and attaches validation to every meaningful task.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What needs to be planned |
| `--depth` | `brief`, `standard`, `deep` | `standard` | How much detail to include |
| `--scope` | path | none | Limit the planning surface |
| `--auto` | flag | off | Skip confirmations and emit the plan without interactive approval |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required | Notes |
| --- | --- | --- | --- |
| `git` | command | yes | Must be on PATH |
| `python3` | command | yes | Must be on PATH |

## Skill Layout

```
adk-plan/
  SKILL.md                                # Skill definition
  README.md                               # This file
  scripts/
    preflight.py                          # Pre-flight checks
  references/
    workflow.md                           # Workflow guidance
    persona.md                            # Persona guidance
    _shared/
      ai-guidelines-overview.md           # Shared AI guidelines
      constitution.md                     # Shared constitution
      research-protocol.md                # Shared research protocol
      output-format.md                    # Shared output format
```

## Workflow

1. Confirm the goal, scope, and success criteria with the user.
2. Inspect the relevant local code and docs.
3. Surface 1-3 viable approaches when choices matter.
4. Write the smallest executable plan that covers the approved path.
5. Attach validation to every meaningful task.
6. Report open questions separately from the plan.

## Interaction Protocol

- **Confirm task and depth**: before generating, confirm the goal, depth, and scope with the user (unless `--auto`).
- **Present plan waves for approval**: plans are organized into sequential waves with numbered task IDs (T1.1, T1.2, T2.1, etc.).
- **User can accept, modify, or reject individual tasks**: after presenting a wave, pause for feedback. The user may approve all, remove specific tasks, reorder, or add tasks.
- **Open questions are separated**: unknowns and assumptions are listed after the plan, not inline.
- **Iterate until approved**: the plan is not final until the user explicitly approves it.

## Output Format

Each plan includes:
- **Summary**: one-sentence description of the plan
- **Changed scope**: files and areas affected
- **Plan waves**: ordered groups of tasks with IDs (T1.1, T1.2, etc.), each with a validation step
- **Remaining risk**: explicit risks and assumptions
- **Open questions**: items needing user input

## Examples

Standard plan:
```
/adk-plan migrate the auth module from session-based to JWT
```

Deep plan with scoped surface:
```
/adk-plan --depth deep --scope src/api redesign the error handling strategy
```

Brief plan:
```
/adk-plan --depth brief add dark mode support to the settings page
```

## What Success Looks Like

- [ ] Every significant task includes a validation step
- [ ] Risks and assumptions are explicit
- [ ] The plan is small enough to execute in waves
- [ ] Tasks have unique IDs (T1.1, T1.2) for easy reference
- [ ] Open questions are separated from the plan body
- [ ] The user approved the final plan before execution begins
