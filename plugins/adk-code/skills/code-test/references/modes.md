# `code-test` — mode contract

`code-test` supports `--auto` (default) and `-i` / `--interactive`. Plus three test-type flags (`--unit`, `--integration`, `--e2e`) and `--coverage`. Does **not** support `--fix` — mutation IS the goal.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- **Still runs fail-first verification on every new test.** Auto does NOT skip the red→green transition; that's the proof the test is real.
- **Still runs the full affected-package suite at Phase 5.**
- Refuses any irreversible destructive op.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm target + scope + framework.
    - Phase 3 — confirm the behavior list (this is the most-valuable gate; the operator may know behaviors the skill missed).
    - Phase 4 — review tests batch-by-batch as they're authored (optional finer-grained approval).
    - Phase 6 — confirm the report.

## `--unit`, `--integration`, `--e2e`

Mutually exclusive with each other (cannot pass two at once). Each forces the test type:

- `--unit` — fast, isolated, mock external deps.
- `--integration` — touches the real DB / HTTP / file system; slower; closer to reality.
- `--e2e` — drives the full system through its public interface (HTTP API, browser, CLI); slowest; most realistic.

If none specified, the skill picks based on the target's nature (Phase 0).

## `--coverage`

Optional. Composes with `--auto` / `-i` / `--unit` / `--integration` / `--e2e`. Triggers:

- Run coverage at Phase 5 final validation.
- Capture lines + branches before / after.
- Include the delta in the report.

If the repo doesn't have a coverage tool configured, surface that and skip the delta (don't auto-install).

## What `code-test` will NEVER do, even under `--auto`

1. Skip the fail-first verification. The verification is the proof.
2. Mock the system under test.
3. Test private internals.
4. Disable / skip an existing test to make a new one pass.
5. Add tests in the same diff as a bug fix (escalate to `code-bugfix`).
6. Add tests in the same diff as production code (escalate to `code-write`, which adds its own tests).
7. Push, commit, or open a PR.
8. Add snapshot tests on heavily-nested objects without a written rationale (snapshots drift; targeted assertions don't).
9. Generate vacuous tests for coverage numbers ("test that 2+2=4 as `function add` test").

## What `--auto` MAY do without asking

- Pick the test type (unit / integration / e2e) when none specified, based on the target's nature.
- Pick the trio shape (which boundary, which error) when multiple are equally relevant — record in Decisions.
- Add up to 5 tests per behavior trio (3 minimum); more requires `-i` or explicit operator request.
- Skip behaviors that require a harness the repo doesn't have (e.g. e2e on a repo with no e2e harness — surface in Decisions).

## Composition

- Called from `/adk-core:auto`, the chain is `auto → code-test → review-code-changes`. `auto` propagates flags down.
- Called as a prerequisite to `code-refactor` (when the target has thin coverage and the operator wants a safety net first), the slug is preserved across the two tasks.
- Called directly with `--auto`, runs end-to-end.
- Called directly with `-i`, runs interactively.

## Invalid combinations

- `--auto -i` — refused at parse.
- `--unit --integration` — refused; pick one.
- `--fix` — silently ignored. `code-test` always mutates.
