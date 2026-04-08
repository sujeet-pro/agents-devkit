# DevKit 6-Phase Workflow

Every non-trivial DevKit skill follows a structured 6-phase workflow that front-loads human interaction. Phases are adaptive — simpler tasks skip phases based on the complexity table below.

## Conditional Reference Loading

Not all references are needed for every task. Load references based on complexity:

- **Always**: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/inline-interaction.md`
- **Medium and Large only**: `references/principal-engineer.md`, `references/agentic-teams.md`
- **When producing output**: `references/output-formats.md`

## Phases

### Phase 0: Intent Expansion & Confirmation

Confirm understanding before doing any work. This phase ALWAYS runs.

- Restate the user's goal in one line
- Show reasoning chain (2-4 bullets explaining your thinking process)
- List skills needed with rationale for each
- List tools/MCPs needed with availability status (available / unavailable / degraded)
- Estimate complexity (Trivial / Small / Medium / Large) with justification
- For Medium/Large: load and apply `references/principal-engineer.md`
- Confirm with user per `references/inline-interaction.md` — use the Intent Confirmation protocol (inline rendering with approve/edit/simplify/cancel). For Trivial: 1-line confirm inline.
- Save to `.temp/<task-slug>/00-intent.md`

### Phase 1: Research & Options Discovery

Research scoped by confirmed intent, not by the AI's initial interpretation.

- For Medium/Large: load `references/agentic-teams.md` and launch research child agents per its contract
- Search official docs, specs, RFCs, and maintainer guidance
- Scan the codebase for existing patterns, conventions, and related code
- Identify constraints, dependencies, and integration points
- End with 2-3 concrete approaches, each containing:
  - Summary (1-2 sentences)
  - Pros and cons
  - Effort estimate (hours or complexity)
  - Risk level (Low / Medium / High)
- Present approaches per `references/inline-interaction.md` — use the Approach Selection protocol (numbered list with select/mix/discuss).
- Save to `.temp/<task-slug>/01-approaches.md`

### Phase 2: Approach Selection (Interactive)

User picks approach inline in the conversation.

- Present approaches with concrete trade-offs
- For Large tasks: resurface PE questions from Phase 0 with research context
- Ask targeted clarifying questions (one at a time, not a wall of questions)
- Capture chosen direction with explicit rationale
- Record any constraints or modifications the user added
- Save to `.temp/<task-slug>/02-approach.md`

### Phase 3: Planning (Interactive)

Generate an executable plan from the chosen approach.

- Decompose into discrete tasks with:
  - File paths affected
  - Verification commands
  - Effort estimates per task
- Group independent tasks into waves for parallel execution
- Identify sequential dependencies between waves
- For Medium/Large: assign team shapes from `references/agentic-teams.md` to each wave
- Plan must be resumable — track done vs remaining
- Present plan per `references/inline-interaction.md` — use the Plan Approval protocol (wave/task list with approve/add/remove/cancel).
- Save to `.temp/<task-slug>/03-plan.md`

### Phase 4: Execute (Autonomous)

Implement the plan without requiring human interaction.

- Execute waves sequentially; tasks within each wave run in parallel via child agents
- Each child agent receives full context for its task
- After each wave, verify completion before starting the next
- Update progress in `.temp/<task-slug>/04-progress.md` at wave boundaries
- Show progress inline per `references/inline-interaction.md` — use the Progress Dashboard protocol (wave status updates at boundaries).
- On failure: surface error, offer [Retry | Skip | Abort | Fix Manually]

### Phase 5: Validate & Learn

Automatically verify, review, refine, and summarize.

- **Iteration loop** (up to 10 iterations):
  1. Run all available validation: tests, linting, formatting, type checking, security, performance
  2. Self-review the changes against original intent and approach rationale
  3. Check for correctness, edge cases, and regressions
  4. Check for over-engineering: remove unused abstractions, unnecessary future-proofing, verbose patterns
  5. Simplify: prefer readable, maintainable code with minimum changes required
  6. Fix any issues found and re-validate
  7. Stop when: all checks pass AND no further simplification possible, OR 10 iterations reached
- Produce a "What to know" section: 2-3 sentences explaining the key decision or pattern the user should understand
- Produce a summary of what was done, what was validated, and any remaining notes
- Save to `.temp/<task-slug>/05-summary.md`

**Self-review principles:**
- Code must be human-readable, maintainable, and extensible
- Do only the minimum changes required — no gold-plating
- Do not implement features that might be needed in the future
- Three similar lines of code is better than a premature abstraction
- If it works and reads clearly, it is done

## Complexity-Adaptive Phase Skipping

| Complexity | Files | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------------|-------|---------|---------|---------|---------|---------|---------|
| Trivial    | 1     | inline  | skip    | skip    | skip    | direct  | quick   |
| Small      | 2-3   | inline  | lite    | inline  | brief   | execute | verify  |
| Medium     | 4-8   | confirm | full    | select  | full    | execute | full    |
| Large      | >8    | confirm+PE | full | select+PE | full  | phased  | full (10 iter) |

**Phase descriptions by complexity:**
- **skip**: Phase is not executed
- **inline**: Abbreviated version — brief confirm or select in the conversation
- **confirm**: Full intent confirmation using the inline interaction protocol
- **confirm+PE**: Full intent confirmation with Principal Engineer check
- **select**: Full approach selection / plan approval using the inline interaction protocol
- **select+PE**: Full selection with Principal Engineer check
- **lite**: Abbreviated version — quick scan, no deep research
- **brief**: High-level plan without wave decomposition
- **direct**: Execute the change directly without wave orchestration
- **verify**: Single validation pass without iteration loop
- **full**: Complete phase as described above
- **execute**: Standard wave-based execution
- **phased**: Execute in multiple sequential phases with progress checkpoints

## Complexity Detection

Estimate complexity by counting:
- Number of files likely affected
- Whether architectural decisions are needed
- Whether requirements are fully clear
- Whether new abstractions are required
- Number of discrete sub-tasks

When uncertain, default to Medium.

## Output Rules

- All output is **markdown by default** unless the user requests otherwise
- Follow `references/communication-style.md` for tone and structure
- Use consistent heading hierarchy: `##` for sections, `###` for subsections
- Include a summary section at the top of every deliverable
- Code examples use fenced code blocks with language tags
- Tables use GFM pipe syntax
- Findings include severity, confidence, and actionable next steps
