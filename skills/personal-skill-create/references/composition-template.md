# `personal-skill-create` — composition template

When generating the personal skill's SKILL.md, follow this composition pattern:

```markdown
---
name: <user-name>
description: <derived from purpose>
metadata:
  modes: [auto]
---

# <user-name> — <purpose>

This personal skill composes:
- `@adk:<skill-A>` (a.k.a. `adk-<skill-A>`) — <role>
- `@adk:<skill-B>` (a.k.a. `adk-<skill-B>`) — <role>
- `agents/<role>.md` subagent — <role>

## When to use

<one paragraph>

## Workflow

1. Call `@adk:<skill-A>` with `<inputs>`. Output: `<artifact path>`.
2. For each item in <output>, call `@adk:<skill-B>` with ...
3. Aggregate results.
4. Final report at `.temp/task-<slug>/personal-<user-name>/report.md`.

## Output

`.temp/task-<slug>/personal-<user-name>/...`

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Sequence diagram of composed calls |
| `references/interaction-contract.md` | Inherits from runtime (NOT propagated from plugin) |
```
