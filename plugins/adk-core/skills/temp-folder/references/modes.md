# `temp-folder` — mode contract

`temp-folder` supports `--auto` only. There's no interactive flow (the convention is fixed).

## `--auto` (default)

- Generate slug, create folder, emit slug + path.
- No prompts.
- Idempotent: re-running with the same prompt returns the same slug.

## No `-i` / `--fix`

- The skill is non-interactive — there's nothing to ask.
- The skill never mutates anything outside `.temp/`, and only by `mkdir -p`.

## `--print-only` (orthogonal)

- Echo the slug; do NOT create the folder.
- Useful when a caller just wants to compute a slug.
