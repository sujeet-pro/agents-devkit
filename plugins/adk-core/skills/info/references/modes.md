# `info` — mode contract

`info` is read-only. Supports `--auto` and `-i` (the latter is rarely useful since the skill never asks questions).

## `--auto` (default)

- Single shell-out to `bin/adk-info`. No prompts.
- Output to stdout.

## `-i` / `--interactive`

- If output is large (>50 lines), paginate with offer-depth.
- Otherwise behaves the same as `--auto`.

## No `--fix`

This skill never mutates. There is no `--fix` mode.

## No re-read loop

The skill always reads fresh from disk. There is no caching to invalidate.
