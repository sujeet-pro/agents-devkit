# `code-refactor` — mode contract

`code-refactor` supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — mutation IS the goal.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- **Still runs every micro-step with green-suite verification.** Auto does NOT skip the per-step validation; the green-between-steps invariant is the safety net of the whole skill.
- Refuses any irreversible destructive op.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm the move + scope.
    - Phase 3 — confirm the micro-step list (this is the most valuable gate; the operator may know a sequencing constraint the skill missed).
    - Phase 4 — between micro-steps if any goes red and required revert.
    - Phase 6 — confirm the report.
- Allows the operator to edit the micro-step sequence before execution.

## `--scope <path>`

- Optional, composes with `--auto` and `-i`.
- Restricts reads / edits to the given subtree.
- Useful for monorepo refactors: `--scope packages/checkout` keeps the move inside one package.
- For cross-package renames, `--scope` is too narrow; surface that and ask whether to continue.

## What `code-refactor` will NEVER do, even under `--auto`

1. Mix behavior changes with structural changes — STOP if any micro-step accidentally changes behavior (caught by snapshot or assertion failures).
2. Update snapshots `--update`-style. Snapshots changing = behavior changed.
3. Modify public API surface. If the rename / extraction crosses the public-API boundary, it's `code-api`, not `code-refactor`.
4. Add features. Fix bugs. Tune perf. (Each is its own skill.)
5. Push, commit, or open a PR.
6. Continue past a red step that didn't revert cleanly. STOP.
7. Rewrite a file from scratch. A refactor is a sequence of small moves; rewriting is a different operation that needs more discussion.

## What `--auto` MAY do without asking

- Choose between two equivalent micro-step orderings (e.g. delete the old path before vs after updating one of the call-sites — both safe if the suite is green at every step).
- Apply mechanical renames in a single pass when there is no ambiguity (e.g. simple text replace across files where the symbol is unique).
- Skip an `if dirty tree: ask` gate IF the dirty changes are clearly unrelated to the refactor scope (e.g. unrelated package).

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → code-refactor → review-code-changes`. `auto` propagates `--auto` / `-i` down.
- For larger restructures, `code-refactor` is sometimes called multiple times with different slugs ("Refactor 1/3", "Refactor 2/3", "Refactor 3/3") — each independently revertible.
- Called directly with `--auto`, runs end-to-end.
- Called directly with `-i`, runs interactively.

## Invalid combinations

- `--auto -i` — refused at parse.
- `--fix` — silently ignored with a warning. `code-refactor` always mutates.
