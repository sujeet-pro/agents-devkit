# Standard Task Workflow

Shape: **confirm → research → execute → validate**

For tasks with a known general approach that benefit from scanning context before execution. No approach selection or detailed planning — the "how" is clear, but the "what exactly" benefits from research.

## When to Use

- Document writing and revision (most doc types)
- Document review
- Code review comment fixes
- Refactoring with clear patterns
- Spec writing
- Project management actions
- Publishing workflows

## Steps

### 1. Confirm

Confirm intent and scope. More thorough than Quick Action — surface assumptions and constraints.

- Restate the user's goal
- List assumptions, constraints, and source requirements
- Identify which helpers or connectors are needed
- For Medium/Large: apply Principal Engineer check
- For `--auto`: state intent without waiting for confirmation
- Save to `.temp/<task-slug>/intent.md` when complexity >= Medium

### 2. Research

Scan context scoped by confirmed intent. Gather what's needed for execution.

- Scan the codebase for existing patterns, conventions, and related content
- Search official docs, specs, or related material when relevant
- Identify constraints, dependencies, and integration points
- For Medium/Large with parallel needs: launch research child agents via `/adk:agentic-teams`
- End with a clear understanding of what to do — not options to pick from

### 3. Execute

Do the work. May use child agents for larger tasks.

- Execute the task following the skill's specific instructions
- For Medium+: use wave-based execution with child agents
- Update progress in `.temp/<task-slug>/progress.md` at wave boundaries for Large tasks
- On failure: surface error, offer [Retry | Skip | Abort | Fix Manually]

### 4. Validate

Verify the work, iterate if needed, summarize.

- Run available validation: tests, linting, formatting, type checking
- Self-review against original intent
- Check for over-engineering — remove unnecessary complexity
- Iteration loop: fix issues and re-validate (up to 5 iterations for Medium, 10 for Large)
- Produce a "What to know" summary: 2-3 sentences on key decisions
- Save summary to `.temp/<task-slug>/summary.md` when complexity >= Medium

## `--auto` Behavior

All steps execute without confirmation pauses. Step 1 states intent but does not wait for approval. Step 4 validates normally.

## Artifacts

Save `.temp/` artifacts when complexity >= Medium. For Small/Trivial, output directly without intermediate files.

## Complexity Scaling

| Step | Small | Medium | Large |
|------|-------|--------|-------|
| Confirm | Inline restatement | Full confirmation + PE | Full + PE |
| Research | Lite scan | Full codebase + docs | Full + agentic teams |
| Execute | Direct | Wave-based | Phased with checkpoints |
| Validate | Single pass | Loop (up to 5 iter) | Loop (up to 10 iter) |
