# `prompt-expand` — mode contract

`prompt-expand` supports `--auto` and `-i`. It does NOT support `--fix` (it doesn't mutate anything).

## `--auto` (default)

- Runs the expansion end-to-end and writes `skill-plan.md`.
- Surfaces a one-line summary; offers to read the file.

## `-i` / `--interactive`

- Per-step approval (rarely useful for this skill since it's read-only).
- Use to tweak entity resolution interactively before writing the output.

## Composition

- This skill never mutates. There is no `--fix` mode.
- Calling this from another skill (e.g. mid-flow re-expansion) inherits the parent's `--auto` flag.
