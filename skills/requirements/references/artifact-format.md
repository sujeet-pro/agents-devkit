# `requirements` — artifact format

`.temp/task-<slug>/requirements.md`:

```markdown
# Requirements — <task-slug>

Captured by `requirements` skill on <ISO timestamp> with user `<user>`.
Source context: `.temp/task-<slug>/context.md` (if present).

## Outcome
<one sentence>

## Users
- <user type>: <one sentence>
- ...

## Triggers
- <event / condition>

## Behavior
1. <step>
2. <step>
3. <step>

## Inputs
- <data shape, format, validation>

## Outputs
- <data shape, format>

## Success measures (testable)
- <measure>
- <measure>

## Must-haves (P0)
- <item>
- <item>
(3-7 items)

## Nice-to-haves (P1+)
- <item>

## Non-goals (we are NOT doing)
- <item>
- <item>

## Edge cases
| Case | Expected behavior |
| --- | --- |
| empty | ... |
| max | ... |
| overflow | ... |
| network fail | ... |
| unauthorized | ... |
| concurrent | ... |

## Constraints
- Technical: ...
- Business: ...
- Regulatory: ...
- Platform: ...

## Open questions (escalate to scoping)
- <question>
- <question>

## Sign-off
- User confirmed: <date>
```
