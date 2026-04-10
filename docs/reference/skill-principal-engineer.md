---
title: 'principal-engineer'
description: 'Principal Engineer questioning framework applied before committing to significant work. Five questions: need, simplest, alternatives, maintenance, clarity'
skill_name: principal-engineer
category: guideline
workflow_tier: helper
user_invocable: false
---

# principal-engineer

`principal-engineer` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`principal-engineer` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

This helper does not expose a broad user-facing parameter surface beyond the narrow controls in `SKILL.md`. In practice, task skills load it indirectly and supply the context it needs.

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


## Additional Reference

### When to Apply

- Complexity >= Medium
- Architectural changes (new modules, changed boundaries, new dependencies)
- New abstractions (interfaces, base classes, shared utilities)
- Significant effort (>2 hours estimated work)

### The Five Questions

1. **"Do we need this?"** — Is the problem real? Is it already solved by existing code, a library, or an established pattern in this codebase?

2. **"What's the simplest version?"** — What is the minimum viable approach that solves the actual problem, not the imagined future problem?

3. **"What are the alternatives?"** — Are there 2-3 other ways to achieve this? What are their trade-offs in effort, risk, and maintenance?

4. **"What are the maintenance costs?"** — What does this add to the ongoing burden? New dependencies, complexity, testing surface, deployment considerations?

5. **"Will this make sense in 6 months?"** — Will someone reading this code, doc, or decision understand why it was done without asking the author?

### Presenting Findings

Use this format when surfacing PE findings to the user:

```
### Principal Engineer Check

**Need**: [Yes — clearly needed / Maybe — consider alternative / Questionable — here's why]
**Simplest version**: [description of minimum viable approach]
**Trade-off**: [key trade-off of recommended vs simple approach]
**Maintenance cost**: [Low/Medium/High — with one-line justification]
```

Keep it to 4 lines. If the answer to all five questions is straightforward, collapse to a single line: "PE check: clearly needed, simple approach, low maintenance."

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
