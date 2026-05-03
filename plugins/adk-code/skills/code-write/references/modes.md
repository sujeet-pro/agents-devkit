# `code-write` — mode contract

`code-write` supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — mutation IS the goal of this skill, so `--fix` would be redundant. The `--fix` flag is reserved for read-default skills like `adk-review:review-pr` where mutation is opt-in.

## `--auto` (default)

- Skips per-phase approval gates (Phase 0 expand, Phase 3 plan).
- Picks the documented `(default)` option at every decision (see `references/clarifying-questions.md`).
- Still validates after every meaningful change.
- Still surfaces a final `report.md` with: changes, validation evidence, decisions auto-picked, residual risk, what was deliberately NOT done.
- Refuses any irreversible destructive op (none expected for `code-write` — but if a sub-tool accidentally tries `git push --force`, the `adk-core` `PreToolUse:Bash` hook blocks it).

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm restated prompt + resolved repo + likely-files set.
    - Phase 3 — confirm `plan.md` (files touched, approach, validation plan).
    - Phase 4 — between implementer and test-engineer, confirm the implementer hand-off if anything looks off.
    - Phase 6 — confirm the report before closing the task.
- Allows the user to edit the plan or the file set before execution.

## `--scope <path>`

- Optional, composes with `--auto` and `-i`.
- Restricts reads and edits to the given subtree of the repo.
- Useful for monorepo work: `--scope packages/checkout` keeps the implementer from drifting into adjacent packages.

## What `code-write` will NEVER do, even under `--auto`

1. Push, commit, or open a PR — `code-write` produces a working tree, period.
2. Force-push to any branch.
3. Delete branches.
4. Touch files outside the planned set without re-confirming (even `--auto` re-confirms here).
5. Edit on top of a red baseline. Baseline must be green or the user must explicitly opt-in.
6. Auto-resolve a merge conflict.
7. Auto-install a new dependency without surfacing it for confirmation in the plan.

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → code-write → review-code-changes`. `auto` propagates its `--auto` / `-i` flag down.
- Called directly with `--auto`, runs end-to-end without approval gates and writes the final `report.md`.
- Called directly with `-i`, runs interactively with per-phase approval.

## Invalid combinations

- `--auto -i` — refused at parse. Mutually exclusive.
- `--fix` — silently ignored with a warning in the report. `code-write` always mutates; `--fix` is meaningless.
