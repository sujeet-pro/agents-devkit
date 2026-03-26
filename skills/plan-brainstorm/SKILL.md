---
name: plan-brainstorm
description: Use before major implementation or documentation work to shape the problem, options, and constraints before a plan or build starts
user_invocable: true
arguments:
  - name: topic
    description: "Problem or feature to brainstorm"
    required: true
  - name: scope
    description: "Scope: narrow, broad (default: broad)"
    required: false
---

# Brainstorming

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

Use this when the solution is still fuzzy and you need to explore options before committing to a plan.

## Preflight

Before brainstorming, run:

`zsh scripts/check-skill-deps.zsh plan-brainstorm`

## Required Child Agents

Run at least these child agents in parallel:

- **Context analyst**: reads the relevant repository code, existing docs, git history, and related issues to understand the current state. Produces a context brief with architecture constraints, existing patterns, and relevant precedents.
- **Options researcher** (`research-agent`): researches approaches used in similar projects, official recommendations, and industry best practices. Produces an options catalog with 2-5 approaches and their tradeoffs.
- **Review agent**: reviews the proposed options for feasibility, risk, and alignment with the existing codebase. Flags unrealistic options and identifies hidden constraints.

## Workflow

1. **Read context.** Launch the context analyst to scan the repo and gather constraints.
2. **Clarify goals.** State the problem, desired outcome, and non-negotiable constraints explicitly.
3. **Research options.** Launch the options researcher to find approaches.
4. **Propose options.** Present 2-5 options, each with:
   - approach description
   - pros and cons
   - estimated effort (small, medium, large)
   - risk assessment (low, medium, high)
   - key assumptions
5. **Review.** Launch the review agent to validate feasibility.
6. **Write design summary.** Produce the final brainstorm output.

Save intermediary artifacts to `.temp/brainstorm/`.

## Output

```
## Design Summary

### Problem
<clear problem statement>

### Goals
- <goal 1>
- <goal 2>

### Constraints
- <constraint 1>
- <constraint 2>

### Options

#### Option 1: <name>
- Approach: <description>
- Pros: <list>
- Cons: <list>
- Effort: <small/medium/large>
- Risk: <low/medium/high>

#### Option 2: <name>
...

### Recommendation
<recommended option with justification>

### Open Questions
- <question 1>
- <question 2>
```

## Adjacent Skills

- `/devkit:plan-write` for turning the chosen option into an execution plan
- `/devkit:dev-implement` for implementing the planned feature
- `/devkit:research` for deeper research on specific options
