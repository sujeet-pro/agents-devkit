---
title: The 6-Phase Workflow
description: How ADK skills plan, confirm, execute, and validate work
order: 4
---

# The 6-Phase Workflow

Every non-trivial ADK skill follows a structured 6-phase workflow. The key principle: **human interaction happens first, not after hidden research**.

## Why This Matters

Traditional AI workflows often surprise users: the agent researches extensively, makes assumptions, and presents a finished result that might not match what the user wanted. ADK flips this — confirming intent and approach before investing in execution.

## The Phases

| Phase | Name | What Happens |
| ----- | ---- | ------------ |
| 0 | **Intent Expansion** | Expand the prompt, show concise reasoning, identify skills/tools/MCPs, and confirm direction early |
| 1 | **Research & Options** | Research the problem, scan the codebase, and surface 2-3 viable options |
| 2 | **Approach Selection** | Let the user choose, mix, or simplify the direction |
| 3 | **Planning** | Produce an executable plan with files, sequencing, and verification |
| 4 | **Execute** | Run the approved plan |
| 5 | **Validate & Learn** | Validate the result, simplify when needed, and explain the key takeaway |

### Phase 0: Intent Expansion

**Always runs.** Restates the goal, shows reasoning, identifies required skills and tools, and confirms direction.

```text
Intent:
- Goal: review PR #42 for security and performance
- Skills: code-review-pr (primary), coding (guidelines)
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

| Complexity | Files | Phases Used |
| ---------- | ----- | ----------- |
| Trivial | 1 | 0 inline, 4, 5 quick |
| Small | 2-3 | 0 inline, 1 lite, 3 brief, 4, 5 |
| Medium | 4-8 | All 6 phases |
| Large | >8 | All 6 phases with PE check and phased execution |

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
