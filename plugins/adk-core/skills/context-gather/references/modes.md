# `context-gather` — mode contract

Supports `--auto` (default) and `-i`. Read-only — no `--fix`.

## `--auto` (default)

- Fetch all sources in parallel.
- Write `context.md`.
- Report success / failure per source.

## `-i` / `--interactive`

- For each source, ask "fetch this?" before calling the connector.
- Useful when the prompt has many links and the user wants to scope.

## No `--fix`

- This skill is read-only.

## Composition

- When called from `auto`, `--auto` is propagated.
- When called from a mutation skill (e.g. `code-bugfix` mid-flow needs additional context), `-i` is appropriate so the user controls the scope.
