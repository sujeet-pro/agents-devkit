# `auto` — mode contract

`auto` itself supports `--auto` (the default) and `-i` / `--interactive`. It does **not** support `--fix` directly — but it propagates `--fix` to downstream skills if the user passes `--auto --fix` or `-i --fix` in the original prompt.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- Still validates after every phase.
- Still surfaces a final report (changes, validation evidence, decisions auto-picked, residual risk).
- Refuses any irreversible destructive op the dispatched skill marks "never auto" (`pr-merge`, force-push to protected, `rm -rf`, schema drop).

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates: shows the chosen plan, asks for confirmation, allows edits.
- Used when the user wants to inspect the chain or iterate on the classification before dispatch.

## `--fix` propagation

- `auto` does not have a `--fix` flag of its own.
- If the user writes `/adk-core:auto "review the PR and fix the comments" --fix`, `auto` parses `--fix` and propagates it to the dispatched `review-pr` skill (which DOES support `--fix`).
- If the dispatched chain has no `--fix`-supporting skill, `auto` reports "no skill in this chain supports `--fix`; ignored".

## Composition

- `--auto --fix` composes: dispatched skills run end-to-end with `--fix`. Still NEVER auto-merges.
- `-i --fix` composes: per-phase approvals AND `--fix` propagated.
- `--auto -i` is invalid and refused at parse.