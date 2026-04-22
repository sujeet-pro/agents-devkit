# `scoping` — artifact format

`.temp/task-<slug>/scope.md`:

```markdown
# Scope — <task-slug>

Locked by `scoping` skill on <ISO timestamp>.
Source: `.temp/task-<slug>/requirements.md`.

## Change tolerance
`<surgical | bounded | transformative>`

## Blast radius (touched)
- `path/to/file1`
- `path/to/file2`
- ...

## In scope
- <specific file/component/endpoint with one-line "what changes">
- ...

## Out of scope (explicit)
- <non-goal from requirements>
- <tempting drift the agent must NOT do>
- ...

## Success criteria (per slice)
1. <testable criterion>
2. ...

## Milestones
| # | Title | Touches | Validates with | Independently mergeable? |
|---|-------|---------|----------------|--------------------------|
| 1 | <title> | <files> | <test/check> | yes |
| 2 | <title> | <files> | <test/check> | yes |

## Dependencies
- <other repo / team / infra>
- ...

## Rollback
- Strategy: <revert PR | feature flag <name> | none-needed>
- Owner: <who pushes the revert if needed>
- Validation after rollback: <one-liner>

## Sign-off
- User confirmed: <date>
```
