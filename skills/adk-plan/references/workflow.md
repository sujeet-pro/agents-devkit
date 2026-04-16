# ADK Plan Workflow

## Phases

### Phase 1: Clarify
Confirm the goal, scope, depth, success criteria, and when relevant the current state, target state, acceptable blast radius, and desired confidence with the user.

**Inputs:** user task description, `--depth`, `--scope` flags
**Actions:**
- Parse the task and identify expected outcome
- Determine depth level (`brief`, `standard`, `deep`)
- Identify scope (full repo or `--scope` path)
- Define success criteria
- If the request is still direction-setting rather than sequencing work, run the shared brainstorming workflow first
- Present confirmation summary to user

**Gate:** User approval required. Skip when `--auto` is set.

**Outputs:** confirmed goal, scope, depth, success criteria

### Phase 2: Research
Inspect local code and gather external information needed for planning.

**Actions:**
- Read files within the declared scope
- Inspect project structure, dependencies, and conventions
- Check git history for related changes or decisions
- Dispatch `adk-research-agent` for unknown external facts or constraints
- Carry forward the brainstormed current state, target state, change tolerance, and confidence target when they matter to the plan
- Record findings that influence approach selection

**Outputs:** code context, research findings, constraints

### Phase 3: Options
Surface viable approaches with trade-offs when meaningful choices exist.

**Actions:**
- Identify 1-3 viable approaches based on research
- Analyze trade-offs: effort, risk, complexity, maintainability
- Present options with pros, cons, and effort estimates
- For trivial tasks with one obvious approach, state the approach and proceed

**Gate:** User selects approach. Skip when `--auto` is set (uses recommended option).

**Outputs:** selected approach with rationale

### Phase 4: Draft
Write the wave-based plan with T-IDs, validation, and effort estimates.

**Actions:**
- Organize tasks into sequential waves (2-4 tasks per wave; tasks within a wave must be independent)
- Assign T-IDs: `T{wave}.{task}` (e.g. T1.1, T1.2, T2.1) — every task gets one, no exceptions
- Specify files (created, modified, deleted) per task
- Attach validation step per significant task (test, build, lint, curl)
- Include effort estimates with rationale (file count, complexity, test coverage)
- Verify wave dependencies: no parallel tasks depend on each other within a wave
- Check requirement coverage: every explicit requirement maps to at least one task

**Example wave table:**

| T-ID | Task | Files | Validation | Effort |
| --- | --- | --- | --- | --- |
| T1.1 | Add auth middleware | `src/middleware/auth.ts` (create) | `npm test -- auth` | S — single file, pattern exists |
| T1.2 | Add JWT util | `src/lib/jwt.ts` (create) | `npm test -- jwt` | S — isolated utility |
| T2.1 | Wire middleware into routes | `src/routes/*.ts` (modify) | `curl -H "Auth: ..."` | M — touches 4 route files |

**Gate:** Plan approval required. Skip when `--auto` is set.

**Outputs:** wave-based plan with T-IDs

### Phase 5: Refine
Incorporate user feedback and adjust the plan.

**Actions:**
- Process user feedback: approve, drop, add, reorder tasks
- Adjust scope, effort estimates, or wave structure
- Re-validate wave dependencies after changes
- Present revised plan if changes are significant

**Outputs:** refined plan

### Phase 6: Persist
Finalize the plan and summarize open questions separately.

**Actions:**
- Format the final plan in standard output format
- Separate open questions from the plan body
- Summarize risks with mitigation strategies
- Output the plan for execution or handoff

**Outputs:** final plan document

## Validation Rules
- Every significant task includes a validation step
- Risks and assumptions are explicit in dedicated sections
- The plan is small enough to execute in waves
- No task depends on a parallel task within the same wave
- Each explicit requirement is addressed by at least one task
- Effort estimates include rationale

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Clarify): skip user approval, proceed with parsed intent
- Phase 3 (Options): select recommended option automatically
- Phase 4 (Draft): skip plan approval, proceed with generated plan
- Phase 5 (Refine): skip (no interactive feedback)
- Phase 6 (Persist): still outputs full plan with all sections
- Validation rules still apply in full
