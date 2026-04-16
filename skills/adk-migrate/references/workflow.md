# ADK Migrate Workflow

## Phases

### Phase 1: Assess
Identify current stack, target stack, migration scope, acceptable blast radius, and rollback expectations.

**Inputs:** user task description, `--source`, `--scope` flags
**Actions:**
- Identify the source framework/library and current version in use
- Identify the target version or replacement
- Catalog all local usage of the source (imports, API calls, configuration)
- Determine migration scope (full repo or `--scope` path)
- Capture whether the migration should stay `surgical`, `bounded`, or `transformative`
- Assess rollback feasibility (git branch, feature flags, etc.)
- Present scope, target, and rollback expectations to user

**Gate:** Confirm scope, target, and rollback expectations with user. Skip when `--auto` is set.

**Outputs:** confirmed migration target, usage catalog, scope, rollback strategy

### Phase 2: Research
Gather breaking-change guidance and migration resources. This phase must complete before any code changes.

**Actions:**
- Dispatch `adk-research-agent` to research:
  - Official migration guides and changelogs
  - Breaking change lists for the target version
  - Available codemods or automated migration tools (official and third-party)
  - Known compatibility issues and community migration experiences
- Fallback: research inline if subagent is unavailable
- Cross-reference breaking changes with the local usage catalog from Phase 1
- Build breaking-change map: each change linked to affected local files and line numbers
- Classify each breaking change: codemod-automatable vs. manual-only
- Identify whether incremental adoption (adapter pattern, compatibility layer) is viable as an alternative to full migration

**Research priority order:**
1. Official migration guides (e.g., react.dev/blog, nextjs.org/docs/upgrading)
2. Release changelogs and breaking change lists
3. GitHub issues labeled "migration" or "breaking change"
4. Available codemods (official CLI tools, jscodeshift transforms, ast-grep rules)
5. Community migration experiences (for edge cases only)

**Outputs:** breaking-change map, migration guide references, codemod availability, incremental adoption assessment

### Phase 3: Plan
Create a staged migration plan with rollback strategy.

**Actions:**
- Group breaking changes into ordered waves by dependency and risk
- If there are still multiple viable migration strategies, run the shared brainstorming workflow before finalizing the waves
- Each wave is a cohesive set of changes that can be validated independently
- Define validation criteria for each wave
- Document rollback strategy (per-wave and full rollback)
- Identify which waves can use subagent dispatch for parallel file changes
- Estimate effort and risk per wave

**Gate:** Plan approval required. Skip when `--auto` is set.

**Outputs:** approved migration plan with ordered waves, validation criteria, rollback strategy

### Phase 4: Execute
Apply one wave at a time with validation checkpoints.

**Actions:**
- Execute waves in order
- **Codemod first:** for each wave, run available codemods before manual changes. Review codemod output, then fix what it missed.
- Within each wave, dispatch `adk-implementer` subagent for parallel file changes
- Run validation after each wave before proceeding to the next
- Stop on validation failure until resolved or explicitly acknowledged
- **Rollback checkpoint:** after each wave, verify rollback is still possible (e.g., `git stash` or branch state). Tag or commit each wave boundary.

**Subagent dispatch criteria:**
- Wave affects 3+ files with independent changes
- File-level changes are parallelizable (no cross-file ordering dependency within the wave)
- Do not dispatch for trivial single-file waves

**Handling subagent status:**
- **DONE** → run wave validation
- **DONE_WITH_CONCERNS** → read concerns; compatibility concerns must be addressed before validation
- **NEEDS_CONTEXT** → provide breaking-change map entry and migration guide excerpt, re-dispatch
- **BLOCKED** → research more, revise approach, or escalate to user. Never retry without new information.

**Wave approval:** In interactive mode, present each wave before applying. In `--auto` mode, proceed automatically but stop on validation failure.

**Outputs:** migrated code with validation checkpoints per wave

### Phase 5: Validate
Comprehensive testing of migrated code.

**Actions:**
- Run per-wave validation (targeted tests for changed areas)
- After all waves: run full regression suite
- Dispatch `adk-test-engineer` when test files were created or modified
- Verify no behavioral regressions beyond intended migration changes
- **Test rollback path:** for high-risk migrations, actually revert to the pre-migration state and verify the rollback is clean, then re-apply
- Flag any area that could not be validated
- Verify that the migration did not introduce new dependencies or remove needed ones without documentation

**Outputs:** validation results per wave, full regression results, rollback test results

### Phase 6: Report
Summarize the migration with actionable next steps.

**Actions:**
- Migration log: what moved, what remains
- Validation results per wave and overall
- Remaining manual steps (if any)
- Rollback instructions
- Residual risk and known incompatibilities
- Offer deeper detail on request

**Outputs:** structured report in standard output format

## Validation Rules
- Breaking changes are traced to actual local usage, not generic lists
- Each wave has its own validation pass before the next wave starts
- Full regression suite runs after all waves complete
- Rollback or containment strategy is explicit and tested where possible
- If validation cannot run (no tests), say so explicitly and flag the risk
- Validation failure blocks the next wave until resolved or acknowledged

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Assess): skip user confirmation, proceed with parsed intent
- Phase 3 (Plan): skip plan approval, proceed with generated plan
- Phase 4 (Execute): proceed wave-by-wave without approval, but stop on validation failure
- Phase 5 (Validate): still runs; stop on regression even in auto mode
- Phase 6 (Report): still reports full results
