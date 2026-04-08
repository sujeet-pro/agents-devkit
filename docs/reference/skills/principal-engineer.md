---
title: "principal-engineer"
description: Five-question engineering bar applied before committing to significant work
skill_name: principal-engineer
category: guideline
workflow_tier: helper
user_invocable: false
---

# principal-engineer

Questioning framework applied before committing to significant work. Challenges the approach with five questions.

## Purpose

Forces a sanity check on non-trivial tasks to prevent over-engineering, missed alternatives, and unclear solutions.

## Five Questions

1. **Need** — Do we actually need this? What problem does it solve?
2. **Simplest** — What's the simplest version that solves the problem?
3. **Alternatives** — What are the alternatives? Why this approach over others?
4. **Maintenance** — What are the maintenance costs? Who maintains it?
5. **Clarity** — Will this be clear to someone reading it in 6 months?

## When Applied

- Complexity >= Medium
- Architecture changes or new abstractions
- Work estimated at > 2 hours
- Phase 0 (initial check) and Phase 2 (with research context, for Large tasks)

## Output Format

Compact "PE check" block with each question answered in one line.

## Invoked By

Loaded by the workflow helper set for Medium and Large complexity tasks.
