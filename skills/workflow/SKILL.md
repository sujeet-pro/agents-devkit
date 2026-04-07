---
name: adk-workflow
description: "adk - [helper] [framework] Helper skill that provides the 6-phase workflow framework with complexity-adaptive phase skipping. Invoked by all full-tier skills."
user-invocable: false
argument-hint: "[--complexity trivial|small|medium|large]"
allowed-tools: [Read]
workflow-tier: helper
---

# 6-Phase Workflow Framework

This skill provides the structured 6-phase workflow that all full-tier DevKit skills follow. It front-loads human interaction into the early phases and makes execution autonomous. Phases are adaptive — simpler tasks skip phases based on the complexity table below.

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--complexity` | `trivial`, `small`, `medium`, `large` | auto-detect | Force a specific complexity level |
| `--auto` | flag | off | Skip user confirmations in Phases 0, 2, 3. All phases still execute but without waiting for human input. |

### Behavior Variations

- **Auto-detect** (default): estimates complexity from scope, file count, and architectural impact
- **`--complexity <level>`**: overrides auto-detection
- **`--auto`**: runs all phases without user confirmation pauses — useful for CI, scripted invocations, or when the invoking skill has already confirmed intent

### Examples

```
(invoked automatically by all full-tier skills)
/adk:workflow --complexity medium
/adk:workflow --complexity trivial --auto
```

---

## Workflow

This is a helper skill invoked by other skills, not directly by users. It provides the workflow framework — the invoking skill executes the phases.

## Conditional Reference Loading

Not all shared skills are needed for every task. Load shared skills based on complexity:

- **Always**: `/adk:workflow`, `/adk:communication`, `/adk:preflight-check`, `/adk:interaction`
- **Medium and Large only**: `/adk:principal-engineer`, `/adk:agentic-teams`
- **When producing output**: `/adk:output-format`

---

## Phases

### Phase 0: Intent Expansion & Confirmation

Confirm understanding before doing any work. This phase ALWAYS runs.

- Restate the user's goal in one line
- Show reasoning chain (2-4 bullets explaining your thinking process)
- List skills needed with rationale for each
- List tools/MCPs needed with availability status (available / unavailable / degraded)
- Estimate complexity (Trivial / Small / Medium / Large) with justification
- For Medium/Large: load and apply `/adk:principal-engineer`
- Confirm with user per `/adk:interaction` — use the Intent Confirmation protocol (inline rendering with approve/edit/simplify/cancel). For Trivial: 1-line confirm inline.
- Save to `.temp/<task-slug>/00-intent.md`

### Phase 1: Research & Options Discovery

Research scoped by confirmed intent, not by the AI's initial interpretation.

- For Medium/Large: load `/adk:agentic-teams` and launch research child agents per its contract
- Search official docs, specs, RFCs, and maintainer guidance
- Scan the codebase for existing patterns, conventions, and related code
- Identify constraints, dependencies, and integration points
- End with 2-3 concrete approaches, each containing:
  - Summary (1-2 sentences)
  - Pros and cons
  - Effort estimate (hours or complexity)
  - Risk level (Low / Medium / High)
- Present approaches per `/adk:interaction` — use the Approach Selection protocol (numbered list with select/mix/discuss).
- Save to `.temp/<task-slug>/01-approaches.md`

### Phase 2: Approach Selection (Interactive)

User picks approach via TUI or inline for Small tasks.

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
- For Medium/Large: assign team shapes from `/adk:agentic-teams` to each wave
- Plan must be resumable — track done vs remaining
- Present plan per `/adk:interaction` — use the Plan Approval protocol (wave/task list with approve/add/remove/cancel).
- Save to `.temp/<task-slug>/03-plan.md`

### Phase 4: Execute (Autonomous)

Implement the plan without requiring human interaction.

- Execute waves sequentially; tasks within each wave run in parallel via child agents
- Each child agent receives full context for its task
- After each wave, verify completion before starting the next
- Update progress in `.temp/<task-slug>/04-progress.md` at wave boundaries
- Show progress inline per `/adk:interaction` — use the Progress Dashboard protocol (wave status updates at boundaries).
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

---

## Self-Review Principles

Applied during Phase 5 iteration loop. These are non-negotiable quality gates.

- Code must be human-readable, maintainable, and extensible
- Do only the minimum changes required — no gold-plating
- Do not implement features that might be needed in the future
- Three similar lines of code is better than a premature abstraction
- If it works and reads clearly, it is done

---

## Complexity-Adaptive Phase Skipping

| Complexity | Files | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------------|-------|---------|---------|---------|---------|---------|---------|
| Trivial    | 1     | inline  | skip    | skip    | skip    | direct  | quick   |
| Small      | 2-3   | inline  | lite    | inline  | brief   | execute | verify  |
| Medium     | 4-8   | confirm | full    | select  | full    | execute | full    |
| Large      | >8    | confirm+PE | full | select+PE | full  | phased  | full (10 iter) |

### Phase Descriptions by Complexity

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

---

## Complexity Detection

Estimate complexity by evaluating these factors:

| Factor | Trivial | Small | Medium | Large |
|--------|---------|-------|--------|-------|
| Files affected | 1 | 2-3 | 4-8 | >8 |
| Architectural decisions needed | No | No | Maybe | Yes |
| Requirements fully clear | Yes | Yes | Mostly | Partially |
| New abstractions required | No | No | Maybe | Yes |
| Discrete sub-tasks | 1 | 2-3 | 4-6 | >6 |

When uncertain, default to Medium.

---

## Auto Mode

When `--auto` is passed to a skill (or the skill passes it to this workflow):

- **Phase 0**: state intent and complexity, but do not wait for user confirmation — proceed immediately
- **Phase 1**: execute research normally
- **Phase 2**: select the recommended approach automatically (first-ranked or lowest-risk)
- **Phase 3**: generate the plan and proceed without approval pause
- **Phase 4**: execute normally
- **Phase 5**: validate normally

All phases still execute — auto mode only removes the human confirmation gates. The invoking skill is responsible for deciding when `--auto` is appropriate (e.g., when it has already confirmed intent with the user).

---

## Output Rules

- **Concise by default** — show the compact result first, then offer "Need a detailed breakdown?" at the end
- All output is **markdown by default** unless the user requests otherwise
- Follow `/adk:communication` for tone and structure
- Lead with the conclusion or result, then supporting detail
- Use consistent heading hierarchy: `##` for sections, `###` for subsections
- Include a summary section at the top of every deliverable
- Code examples use fenced code blocks with language tags
- Tables use GFM pipe syntax
- Findings include severity, confidence, and actionable next steps
- After task completion, always offer to elaborate — do not dump detailed output unless the user asks for it or passes `--verbosity detailed`
