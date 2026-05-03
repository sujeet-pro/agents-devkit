# `mode-contract` — own mode contract

This skill is reference-only. It supports `--auto` (the default) and the orthogonal `--explain` / `--parse` flags.

## `--auto` (default)

- Just renders the contract and the parser spec.
- No execution.

## `--explain`

- Renders the contract as a markdown table to stdout.
- Useful for documentation generation.

## `--parse <flags>`

- Sources `parse-mode.sh` and prints the resulting env vars.
- Debug aid for skill authors.

## No `-i` / `--fix`

- Nothing to interact about (reference only).
- Nothing to mutate.
