# Brainstorming Workflow

## Required inputs
Capture before locking direction:
- `task` — what needs to be decided or delivered
- `currentState` — what exists today (with evidence)
- `targetState` — what state should be reached
- `changeTolerance` — `surgical` / `bounded` / `transformative`
- `desiredConfidence` — threshold needed before finalizing
- `artifactPreference` — `none` / `proposal` / `prd` / `rfc` / `hld` / `lld` / `tdd` / `plan` / `all`

## Confidence defaults
| Situation | Default |
| --- | --- |
| production-safe, surgical work | 95 |
| standard feature, refactor, migration, docs | 90 |
| exploratory, personal, transformative | 85 |

## Iteration loop
1. Capture required inputs.
2. Identify what is missing (state, research, options, user answers).
3. Research unknowns when confidence cannot be met from repo evidence alone.
4. Surface 2-3 viable options when real trade-offs exist.
5. Ask follow-up questions until remaining ambiguity is no longer direction-changing.
6. Decide whether confidence meets threshold.
7. Finalize direction, or explicitly accept the gap.

## Stop conditions
- `ask-user` — required inputs / direction-changing questions still open.
- `research` — repo or external evidence still too weak.
- `compare-options` — options still under-defined.
- `finalize` — direction is ready to hand off.
- `bypass` — task is trivial enough to skip the full loop.

## Artifact routing
| Preference | Default route |
| --- | --- |
| `none` | continue in calling skill |
| `proposal` / `rfc` / `hld` / `lld` / `tdd` | `adk-docs-write` |
| `prd` | `adk-plan-spec` |
| `plan` | `adk-plan-roadmap` |
| `all` | `adk-docs-write` plus `adk-plan-roadmap` |
