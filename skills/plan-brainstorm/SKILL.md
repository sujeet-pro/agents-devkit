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
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
  - name: party
    description: "Enable party mode: multiple persona agents debate options (default: false)"
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

## Party Mode

When `party=true`, run additional child agents as different personas debating the options:
- **Pragmatist**: focuses on what can be shipped fastest with least risk
- **Idealist**: focuses on the best long-term architecture regardless of short-term cost
- **Risk Assessor**: focuses on what could go wrong, security implications, scaling concerns
- **User Advocate**: focuses on user experience, accessibility, developer ergonomics

Each persona reviews all options and provides a brief position statement. Synthesize into the options presentation.

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
6. **Interactive voting.** Present each option for scoring using the following format:

   ```text
   ## Option [N/total]: <name>

   Approach: <description>
   Effort: [small|medium|large]  Risk: [low|medium|high]

   Pros:
   - <pro>

   Cons:
   - <con>

   Persona Views (if party mode):
   - Pragmatist: "<position>"
   - Idealist: "<position>"
   - Risk Assessor: "<position>"
   - User Advocate: "<position>"

   Your score (1-5, or "skip"): ___
   ```

   After all options scored, present ranking:

   ```text
   ## Options Ranking

   | Rank | Option | Your Score | AI Recommendation |
   |------|--------|-----------|-------------------|
   | 1 | <name> | 5 | ★ Recommended |
   | 2 | <name> | 4 | |
   | 3 | <name> | 2 | |

   Select option: [1] | [2] | [3] | [D]iscuss further | [C]ombine options
   ```

7. **Write design summary.** Produce the final brainstorm output.

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

## Decision Capture

After user selects an option, save the decision in ADR-compatible format to `.temp/brainstorm/<topic-slug>-decision.md`:
```markdown
# Decision: <chosen option name>

## Context
<problem statement>

## Options Considered
<all options with scores>

## Decision
<chosen option with justification>

## Consequences
<expected tradeoffs>
```

Reference `/devkit:write-adr` if a formal ADR is needed.

## Adjacent Skills

- `/devkit:plan-write` for turning the chosen option into an execution plan
- `/devkit:dev-implement` for implementing the planned feature
- `/devkit:research` for deeper research on specific options
- `/devkit:write-adr` for formalizing the decision
- `/devkit:constitution-write` if the decision affects project principles
