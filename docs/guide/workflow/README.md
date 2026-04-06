---
title: The 6-Phase Workflow
description: How ADK skills plan, confirm, execute, and validate work
order: 3
---

# The 6-Phase Workflow

Every non-trivial ADK skill follows a structured 6-phase workflow. The key principle: **human interaction happens first, not after hidden research**.

## Why This Matters

Traditional AI workflows often surprise users: the agent researches extensively, makes assumptions, and presents a finished result that might not match what the user wanted. ADK flips this — confirming intent and approach before investing in execution.

## The Phases

### Phase 0: Intent Expansion

**Always runs.** Restates the goal, shows reasoning, identifies required skills and tools, and confirms direction.

```text
Intent:
- Goal: review PR #42 for security and performance
- Skills: review-pr (primary), coding (guidelines)
- Tools: GitHub MCP (available)
- Complexity: Medium (8 files changed)
```

For trivial tasks, this is a single-line confirmation. For large tasks, it includes a Principal Engineer check.

### Phase 1: Research & Options

Scoped by confirmed intent. Scans the codebase, reads official docs, and produces 2-3 concrete approaches with pros, cons, effort, and risk.

### Phase 2: Approach Selection

The user picks, mixes, or simplifies the approach. For large tasks, PE questions are resurfaced with research context.

### Phase 3: Planning

Generates an executable plan: tasks grouped into parallel waves, affected files, verification steps, and sequencing.

### Phase 4: Execute

Runs the approved plan autonomously. Uses child agents for parallel execution. Shows progress at wave boundaries.

### Phase 5: Validate & Learn

Iterative validation loop: run tests, self-review, check for over-engineering, simplify. Produces a "what to know" summary.

## Complexity-Adaptive Skipping

Not every task needs all 6 phases:

| Complexity | Files | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------------|-------|---------|---------|---------|---------|---------|---------|
| Trivial | 1 | inline | skip | skip | skip | direct | quick |
| Small | 2-3 | inline | lite | inline | brief | execute | verify |
| Medium | 4-8 | confirm | full | select | full | execute | full |
| Large | >8 | confirm+PE | full | select+PE | full | phased | full |

## Auto Mode

Pass `--auto` to any skill to skip human confirmations:

```text
/adk:use --auto implement user registration with email verification
```

In auto mode, all phases still execute, but the skill doesn't pause for approval at Phases 0, 2, and 3. It uses the first approach and generates a plan without waiting for user input.

> [!WARNING]
> Auto mode is powerful but skips the safety net of human review. Use it for well-understood, lower-risk tasks.

## The Principal Engineer Check

For Medium and Large complexity tasks, skills apply a PE lens before committing:

1. **Do we need this?** Is the problem real? Already solved elsewhere?
2. **What's the simplest version?** Minimum viable, not imagined future problem.
3. **What are the alternatives?** 2-3 other ways with trade-offs.
4. **What are the maintenance costs?** Dependencies, complexity, testing surface.
5. **Will this make sense in 6 months?** Readable without asking the author.
