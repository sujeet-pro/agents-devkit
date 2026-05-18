# workflow: Phase 3 — validate

> The gate before Phase 4. Determines whether the work goes in the report as completed-and-shippable, or completed-but-needs-attention, or rolled back.

## Steps (in order; STOP on first failure unless `--continue-on-error`)

1. **Repo-native validators**: detect from `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.
   - Typecheck: `npm run typecheck` / `mypy` / `tsc --noEmit` / `cargo check` / etc.
   - Lint: `eslint` / `ruff` / `golangci-lint` / `clippy` / etc.
   - Tests: scoped to changed files when the repo supports it, else full suite.
2. **Cross-source consistency** (skill-specific): for `/adk-investigate`, ≥2 independent signals must agree. For `/adk-document`, every claim must cite. For `/adk-implement`, the diff must compile + pass narrow tests.
3. **Constitution check**: scan the diff/output against `shared/constitution.md` rules. Forbid shared-state changes that weren't confirmed.
4. **Self-coherence**: does the result actually match the plan? Did it answer the user's restated goal? If no, mark as "completed differently than planned" and explain.

## Validator output

```markdown
# validation: <task-slug>

## native validators
- typecheck (tsc): ✓ 0 errors
- lint (eslint): ✓ 0 errors, 2 warnings (in unchanged code; ignored)
- tests (affected): ✓ 12 passed, 0 failed

## cross-source (skill-specific)
- 2 independent signals correlated: ✓ (DD logs + recent deploy)

## constitution
- shared-state writes: 0 (none required)
- force-push: 0
- protected-branch touches: 0

## self-coherence
- plan goal: "implement coupon engine MVP for SF-1234"
- delivered: matches plan ✓
- deviation note: scope adjusted mid-execution (added 1 test, removed 1 edge case per user input)
```

## Failure handling

| Failure | Action |
|---|---|
| Typecheck/lint/test failure on changed code | STOP. Report errors verbatim. Suggest fix or revert. |
| Test failure on unrelated code | STOP if blocking; else flag in report. |
| Cross-source disagreement | STOP. Report both signals. Refuse to conclude root cause. |
| Constitution violation attempt | REFUSE the action. Surface the rule. Continue with the rest of the plan if possible. |
| Self-coherence failure | Report as "completed differently than planned"; the user decides next step. |

## When validation is the entire skill

`/adk-review` and `/adk-investigate` are mostly Phase 3 — they ARE validation. In those skills, Phase 2 (execute) is thin (e.g., "pull the diff", "fetch logs"), and Phase 3 (validate) is where the findings come from.
