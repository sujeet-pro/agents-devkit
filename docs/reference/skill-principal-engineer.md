---
title: "principal-engineer"
description: "Principal Engineer questioning framework for validating significant work"
skill_name: principal-engineer
category: guideline
workflow_tier: helper
user_invocable: false
---

# principal-engineer

A questioning framework applied before committing to significant work. Surfaces five questions that challenge necessity, simplicity, alternatives, maintenance cost, and long-term clarity to prevent over-engineering and wasted effort.

## Purpose

- Gate significant work with structured critical thinking before execution
- Prevent premature abstraction, unnecessary dependencies, and speculative features
- Surface simpler alternatives that achieve the same goal with less effort and risk
- Ensure decisions will still make sense to future readers in 6 months

## Activation Criteria

This skill is loaded conditionally, not for every task:

| Condition | Applies |
|-----------|---------|
| Complexity >= Medium | yes |
| Architectural changes (new modules, changed boundaries, new dependencies) | yes |
| New abstractions (interfaces, base classes, shared utilities) | yes |
| Significant effort (>2 hours estimated work) | yes |
| Trivial or Small complexity | no |

## Key Behaviors

### The Five Questions

1. **"Do we need this?"** — Is the problem real? Is it already solved by existing code, a library, or an established pattern in this codebase?
2. **"What's the simplest version?"** — What is the minimum viable approach that solves the actual problem, not the imagined future problem?
3. **"What are the alternatives?"** — Are there 2-3 other ways to achieve this? What are their trade-offs in effort, risk, and maintenance?
4. **"What are the maintenance costs?"** — What does this add to the ongoing burden? New dependencies, complexity, testing surface, deployment considerations?
5. **"Will this make sense in 6 months?"** — Will someone reading this code, doc, or decision understand why it was done without asking the author?

### Presentation Format

When surfacing PE findings to the user, use this compact format:

```
### Principal Engineer Check

**Need**: [Yes — clearly needed / Maybe — consider alternative / Questionable — here's why]
**Simplest version**: [description of minimum viable approach]
**Trade-off**: [key trade-off of recommended vs simple approach]
**Maintenance cost**: [Low/Medium/High — with one-line justification]
```

If all five questions have straightforward answers, collapse to a single line: "PE check: clearly needed, simple approach, low maintenance."

## What It Provides

- A structured decision gate that prevents over-engineering before work begins
- Compact presentation format for surfacing findings to users
- Integration points with Phase 0 (intent expansion) and Phase 2 (approach selection) of the workflow
- Concrete examples of redirecting work toward simpler solutions

### Example Outcomes

| Scenario | PE Finding | Result |
|----------|-----------|--------|
| Caching layer requested, but DB already has query caching at <50ms | Questionable need | Configured existing DB cache TTL instead |
| Plugin system for 3 notification channels (only email used today) | Premature abstraction | Implemented email directly with clean interface |
| Full REST-to-GraphQL migration for 40 endpoints | Over-scoped | Added sparse fieldsets to 3 over-fetching endpoints |

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | complexity >= medium |
| `code-review-repo` | always (repo-wide reviews are inherently medium+) |
| `audit` | complexity >= medium |
| `dev-build` | complexity >= medium |
| `dev-refactor` | complexity >= medium |
| `dev-migrate` | complexity >= medium |
| `docs-write` | complexity >= medium |
| `design` | complexity >= medium |
| `plan` | complexity >= medium |
| `spec` | complexity >= medium |
| `workflow` (Phase 0) | complexity >= medium; Phase 2 for Large tasks |
