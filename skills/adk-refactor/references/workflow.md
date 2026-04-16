# ADK Refactor Workflow

## Phases

### Phase 1: Understand
Read current structure, capture a behavior baseline, establish the contract, and confirm acceptable blast radius.

**Inputs:** user task description, `--scope` flag
**Actions:**
- Read the code in the target area
- Identify the structural concerns that need improvement
- Locate existing tests that define the behavior contract
- Capture whether the refactor should be `surgical`, `bounded`, or `transformative`
- **Capture baseline:** run the full test suite and record pass/fail counts as the regression reference point
- Catalog what the test suite covers vs. what is unverified
- Present scope, behavior contract, and baseline results to user

**Gate:** Confirm scope and behavior contract with user. Skip when `--auto` is set.

**Outputs:** confirmed refactor scope, behavior contract, test coverage map, baseline test results

### Phase 2: Analyze
Map dependencies and assess risk.

**Actions:**
- Trace dependencies between the refactor target and its consumers
- Identify breaking-change risk (public API surface, cross-module references)
- Catalog which changes are internal (safe) vs. external-facing (risky)
- Identify areas without test coverage that the refactor will touch
- Assess whether the refactor can be done in small, independently correct steps

**Outputs:** dependency map, risk assessment, coverage gaps

### Phase 3: Plan
Propose the refactoring approach with before/after structure.

**Actions:**
- Design the target structure (naming, boundaries, module organization)
- If the acceptable churn is still unclear, run the shared brainstorming workflow before finalizing the target structure
- Create before/after structure sketches for key areas
- Order the sequence of changes so each step is independently correct
- Identify which steps can be parallelized via subagent dispatch
- List what each step preserves and what it changes

**Gate:** Plan approval required. Skip when `--auto` is set.

**Outputs:** approved refactor plan with sequenced steps and before/after sketches

### Phase 4: Refactor
Apply changes one structural concern at a time.

**Actions:**
- Execute plan steps in sequence
- Change exactly one structural concern per step
- Dispatch `adk-implementer` subagent for parallel file changes when the refactor spans multiple modules
- Run regression checks between meaningful steps
- Stop and revert if a step makes the code worse, not better
- Flag any discovered bugs or feature gaps as separate work -- do not fix them during the refactor

**Subagent dispatch criteria:**
- Refactor spans 3+ files across different modules
- Changes within each file are independent (e.g., rename across consumers)
- Do not dispatch for single-module refactors

**Handling subagent status:**
- **DONE** → run regression check for this step
- **DONE_WITH_CONCERNS** → read concerns; if behavior preservation is in doubt, verify before continuing
- **NEEDS_CONTEXT** → provide dependency graph or test baseline context, re-dispatch
- **BLOCKED** → if design judgment needed, handle inline; if plan is wrong, revise plan

**Outputs:** refactored code with regression checks between steps

### Phase 5: Validate
Run the full test suite and verify behavior preservation.

**Actions:**
- Run the full test suite (not just targeted tests)
- Run linter and type checker if available
- Dispatch `adk-test-engineer` if tests needed updating to match new structure
- Compare test results against the baseline from Phase 1
- Flag any test changes that may mask regressions

**Outputs:** validation results (pass/fail with output), comparison against baseline

### Phase 6: Report
Summarize structural improvements and preservation evidence.

**Actions:**
- Present before/after structure comparison
- List changed files with one-line descriptions
- Include test suite output
- Note migration steps for downstream consumers if any API surface changed
- State remaining risk and open items
- Offer deeper walkthrough on request

**Outputs:** structured report in standard output format

## Validation Rules
- Behavior-preserving checks run after each meaningful step, not just at the end
- Full test suite runs before the Report phase
- Refactor scope stays tight -- no scope creep into unrelated code
- New abstractions are justified with concrete readability or maintenance gains
- If behavior cannot be verified (no tests), flag it explicitly
- Test changes during a refactor are suspect -- verify they do not mask regressions

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Understand): skip user confirmation, proceed with inferred scope and contract
- Phase 3 (Plan): skip plan approval, proceed with generated plan
- Phase 4 (Refactor): proceed without step-by-step approval
- Phase 5 (Validate): still runs; stop on regression even in auto mode
- Phase 6 (Report): still reports full results
