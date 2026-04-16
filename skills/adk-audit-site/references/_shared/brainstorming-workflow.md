# Brainstorming Workflow

## Purpose

Use this workflow when a task needs design closure before implementation, documentation, or execution.

This is the shared contract for:
- ambiguous requests
- high-risk changes
- tasks with multiple viable approaches
- work that needs explicit blast-radius control
- tasks that may produce a design artifact before implementation

## Default Rule

- Prefer the `brainstorming` MCP server when it is available.
- If it is missing, warn once with install guidance and run the same workflow manually.
- The workflow must not disappear just because the MCP is missing.
- Skill-specific workflows decide how much of this loop they need.

## Required Inputs

Capture these fields before locking a direction:
- `task`: what needs to be decided or delivered
- `skillContext`: which skill or workflow is driving the brainstorm
- `currentState`: what exists today
- `targetState`: what state should be reached
- `changeTolerance`: `surgical`, `bounded`, or `transformative`
- `desiredConfidence`: threshold needed before finalizing direction
- `artifactPreference`: `none`, `proposal`, `prd`, `rfc`, `hld`, `lld`, `tdd`, `plan`, or `all`

## Confidence Defaults

Use these defaults unless the user gives a better threshold:

| Situation | Default |
| --- | --- |
| production-safe, minimal-change, or surgical work | `95` |
| standard feature, refactor, migration, or docs work | `90` |
| exploratory, personal-project, or transformative work | `85` |

## Change Tolerance

| Mode | Meaning |
| --- | --- |
| `surgical` | minimal file churn, smallest safe fix, lowest acceptable blast radius |
| `bounded` | moderate change inside a defined surface, some restructuring allowed |
| `transformative` | broader redesign or destructive change is acceptable if it better reaches the target state |

## Iteration Loop

1. Capture the required inputs.
2. Identify what is missing: current state, target state, research, options, or user answers.
3. Research unknowns when the confidence bar cannot be met from repo evidence alone.
4. Surface 2-3 viable options when real trade-offs exist.
5. Ask follow-up questions until the remaining ambiguity is no longer direction-changing.
6. Decide whether confidence meets the threshold.
7. Finalize the direction or explicitly accept the remaining gap.

## Stop Conditions

Use one primary next step at any given moment:
- `ask-user`: required inputs or direction-changing questions are still open
- `research`: repo or external evidence is still too weak for the confidence target
- `compare-options`: the options are still under-defined or not yet chosen
- `finalize`: the direction is ready to hand off
- `bypass`: the task is trivial enough to skip the full loop

## Artifact Routing

Route the finalized brainstorm into the next artifact or skill:

| Preference | Default Route |
| --- | --- |
| `none` | continue in the calling skill |
| `proposal` | `adk-write-docs` using a proposal or RFC-style template |
| `prd` | `adk-spec` |
| `rfc` | `adk-write-docs` |
| `hld` | `adk-write-docs` |
| `lld` | `adk-write-docs` |
| `tdd` | `adk-write-docs` |
| `plan` | `adk-plan` |
| `all` | `adk-write-docs` plus `adk-plan` as needed |

The calling skill may tighten this routing. Example: `adk-build` may route directly into implementation once the brainstorm is settled and no persistent artifact is requested.

## MCP-First Behavior

When the `brainstorming` MCP server is available:
- use it to store structured session state
- update the session as research findings, options, and user answers arrive
- use its route recommendation as guidance, not as the only source of truth

When the server is unavailable:
- show one warning with install guidance
- mirror the same fields manually in the conversation
- keep the same confidence and routing rules

## Warning Template

Use wording close to this:

`Warning: the brainstorming MCP server is not configured. Continuing with the fallback workflow. Install it for structured state, stronger iteration support, and cleaner handoff between design and implementation.`

## Skill-Specific Adaptation

Each skill should tailor the loop:
- `adk-research`: refine the question and evidence bar
- `adk-spec`: lock scope and artifact type before writing
- `adk-plan`: settle options and blast radius before drafting tasks
- `adk-build`: settle minimal vs broader change strategy before code edits
- `adk-refactor`: justify restructuring and acceptable churn
- `adk-migrate`: lock risk, rollback, and compatibility assumptions
- `adk-design`: treat UI/UX direction as the option space
- `adk-write-docs`: decide whether a persistent doc is needed and which template fits

Lighter skills may use only a compressed gate instead of the full loop.
