# ADK Build Workflow

## Phases

### Phase 1: Confirm
Clarify the task, scope, constraints, validation target, and when relevant the current state, target state, acceptable blast radius, and desired confidence with the user.

**Inputs:** user task description, `--mode`, `--scope`, `--plan` flags
**Actions:**
- Parse the task and identify expected outcome
- Identify the mode (`implement`, `debug`, or `verify`)
- Determine scope (full repo or `--scope` path)
- If the implementation path is still ambiguous, run the shared brainstorming workflow before locking the plan
- If `--plan` is provided, read and adopt the existing plan
- Present confirmation summary to user

**Gate:** User approval required. Skip when `--auto` is set.

**Outputs:** confirmed task, mode, scope, constraints

### Phase 2: Scope
Read only the local code and sources relevant to the chosen mode.

**Actions:**
- Read files within the declared scope
- In debug mode: gather error context, stack traces, recent git history
- In verify mode: identify validation targets and existing test coverage
- In implement mode: read the code that will be changed and its immediate dependencies
- No speculative exploration outside scope

**Outputs:** understanding of current state, relevant code context

### Phase 3: Plan
Write or refine a short plan before non-trivial changes.

**Actions:**
- Draft a numbered list of concrete implementation steps
- Capture whether the change should be `surgical`, `bounded`, or `transformative`
- If `--plan` was provided, validate it against current code state
- If the path is still unsettled, use the brainstorming workflow to choose the implementation direction before drafting steps
- In debug mode: list hypotheses ranked by likelihood
- In verify mode: skip this phase (no changes planned)
- Identify which steps may benefit from subagent dispatch

**Gate:** Plan approval required. Skip when `--auto` is set or change is trivial (single-file, low-risk).

**Outputs:** approved implementation plan

### Phase 4: Implement
Apply the smallest correct change for the selected mode.

**Actions:**
- Execute plan steps in order
- Dispatch `adk-implementer` subagent for complex parallel file changes
- In debug mode: follow the debugger workflow (hypothesize, test, isolate, fix)
- In verify mode: skip this phase entirely
- Stay within declared scope; flag any necessary out-of-scope changes

**Subagent dispatch criteria:**
- Changes span 3+ files across different modules
- Parallel work is possible (independent file changes)
- Do not dispatch for trivial single-file edits

**Model selection for subagents:**
- Mechanical changes (isolated functions, clear spec, 1-2 files) → fast model
- Integration work (multi-file coordination, pattern matching) → standard model
- Architectural judgment or broad codebase understanding → most capable model

**Handling subagent status:**
- **DONE** → proceed to Phase 5 validation
- **DONE_WITH_CONCERNS** → read concerns; address correctness issues before validation, note observational ones
- **NEEDS_CONTEXT** → provide missing context, re-dispatch
- **BLOCKED** → assess blocker: provide context, break task smaller, or escalate to user. Never retry without changing something.

**Outputs:** code changes applied

### Phase 5: Validate
Run repo-native validation before claiming success.

**Actions:**
- Run the smallest relevant validation commands (test suite, linter, type checker)
- Dispatch `adk-test-engineer` when test files were created or modified
- In verify mode: this is the primary phase -- run all relevant checks
- If validation fails: stop, report the failure, and wait for direction
- If validation cannot run: say so explicitly with reason

**Outputs:** validation results (pass/fail with output)

### Phase 6: Report
Summarize what changed, what was validated, and what remains.

**Actions:**
- List changed files with one-line diff summary each
- Include validation command output
- State remaining risk and open items
- Offer deeper detail on request

**Outputs:** structured report in standard output format

## Validation Rules
- Run the smallest relevant repo-native commands first
- If a claim cannot be verified, say so explicitly
- Never say a bug is fixed or tests pass without fresh evidence
- Validation failure blocks the Report phase until resolved or acknowledged
- In debug mode: verify the fix resolves the original symptom and does not introduce regressions

## Mode-Specific Flows

### Implement Mode
Confirm → Scope → Plan → Implement → Validate → Report

### Debug Mode
Confirm → Scope → Plan (hypotheses) → Implement (debugger workflow) → Validate → Report

### Verify Mode
Confirm → Scope → ~~Plan~~ → ~~Implement~~ → Validate → Report

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Confirm): skip user approval, proceed with parsed intent
- Phase 3 (Plan): skip plan approval, proceed with generated plan
- Phase 4 (Implement): proceed without wave-by-wave approval
- Phase 5 (Validate): still runs; stop on failure even in auto mode
- Phase 6 (Report): still reports full results
