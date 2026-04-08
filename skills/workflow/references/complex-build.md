# Complex Build Workflow

Shape: **confirm → research → select approach → plan → execute → validate**

For tasks with multiple valid approaches, architectural decisions, or significant scope. Full human-in-the-loop with explicit approval gates before execution begins.

## When to Use

- Feature implementation (greenfield or significant)
- TDD development
- Framework/library migrations
- Design direction creation
- Full codebase audits
- PR code review (full review mode)
- Repository-wide code review
- Deep research
- Execution planning
- Multi-agent team coordination

## Steps

### 1. Confirm

Confirm understanding before doing any work. This step always runs fully.

- Restate the user's goal in one line
- Show reasoning chain (2-4 bullets)
- List skills and tools needed with rationale
- Estimate complexity (Small / Medium / Large) with justification
- Apply Principal Engineer check (5 questions: need? simplest? alternatives? maintenance? clarity in 6 months?)
- Confirm with user (approve / edit / simplify / cancel)
- Save to `.temp/<task-slug>/intent.md`

### 2. Research

Research scoped by confirmed intent, not by the AI's initial interpretation.

- Search official docs, specs, RFCs, and maintainer guidance
- Scan the codebase for existing patterns, conventions, and related code
- Identify constraints, dependencies, and integration points
- For Medium/Large: launch research child agents via `/adk:agentic-teams`
- End with 2-3 concrete approaches, each containing:
  - Summary (1-2 sentences)
  - Pros and cons
  - Effort estimate
  - Risk level (Low / Medium / High)
- Save to `.temp/<task-slug>/approaches.md`

### 3. Select Approach

User picks the approach. Interactive.

- Present approaches with concrete trade-offs
- For Large: resurface PE questions with research context
- Ask targeted clarifying questions (one at a time)
- Capture chosen direction with explicit rationale
- Record constraints or modifications the user added
- Save to `.temp/<task-slug>/approach.md`

### 4. Plan

Generate an executable plan from the chosen approach.

- Decompose into discrete tasks with:
  - File paths affected
  - Verification commands
  - Effort estimates per task
- Group independent tasks into waves for parallel execution
- Identify sequential dependencies between waves
- For Medium/Large: assign team shapes from `/adk:agentic-teams` to each wave
- Plan must be resumable — track done vs remaining
- Present plan for approval (approve / add / remove / cancel)
- Save to `.temp/<task-slug>/plan.md`

### 5. Execute

Implement the plan without requiring human interaction.

- Execute waves sequentially; tasks within each wave run in parallel via child agents
- Each child agent receives full context for its task
- After each wave, verify completion before starting the next
- Update progress in `.temp/<task-slug>/progress.md` at wave boundaries
- On failure: surface error, offer [Retry | Skip | Abort | Fix Manually]

### 6. Validate

Verify, review, refine, and summarize.

- Iteration loop (up to 10 iterations):
  1. Run all validation: tests, linting, formatting, type checking, security, performance
  2. Self-review changes against original intent and approach rationale
  3. Check for correctness, edge cases, and regressions
  4. Check for over-engineering: remove unused abstractions, unnecessary future-proofing
  5. Simplify: prefer readable, maintainable code with minimum changes
  6. Fix issues and re-validate
  7. Stop when: all checks pass AND no further simplification possible
- Produce a "What to know" section
- Produce a summary of what was done, validated, and remaining notes
- Save to `.temp/<task-slug>/summary.md`

## `--auto` Behavior

All steps execute without human confirmation gates:
- Step 1: state intent, proceed immediately
- Step 2: research normally
- Step 3: select the recommended approach (first-ranked or lowest-risk)
- Step 4: generate plan, proceed without approval
- Steps 5-6: execute and validate normally

## Self-Review Principles

Applied during Step 6 iteration loop:

- Code must be human-readable, maintainable, and extensible
- Do only the minimum changes required — no gold-plating
- Do not implement features that might be needed in the future
- Three similar lines of code is better than a premature abstraction
- If it works and reads clearly, it is done

## Complexity Scaling

| Step | Medium | Large |
|------|--------|-------|
| Confirm | Full + PE | Full + PE + assumptions audit |
| Research | Full scan | Full + agentic teams |
| Select Approach | 2-3 options, user picks | 2-3 options + PE resurface |
| Plan | Wave decomposition | Waves + team shapes |
| Execute | Wave-based parallel | Phased with checkpoints |
| Validate | Loop (up to 5 iter) | Loop (up to 10 iter) |
