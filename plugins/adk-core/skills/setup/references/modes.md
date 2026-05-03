# `setup` — mode contract

Supports `--auto` and `--mode auto|fix`.

## `--mode auto` (default)

- Each install / edit step is gated by approval (e.g. "open `mixpanel.md` in `$EDITOR` now?").
- Good for first run.

## `--mode fix`

- Same as auto, but skips per-step approval gates.
- Still does NOT auto-install tools or auto-edit shell rc — those rules are absolute.
- Good for repeat runs where the user just wants the diagnostic report.

## `--auto`

- Skips approval gates entirely.
- Equivalent to `--mode fix` for this skill (since `setup` never auto-mutates outside `~/.config/adk/`).
- Useful in CI / repeatable provisioning.

## Composition

- `--auto` and `--mode fix` are equivalent here; using both is redundant but allowed.
- This skill does NOT support `--fix` (different from `--mode fix` — there's no "apply findings" semantics).
