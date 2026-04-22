# `mode-contract` — anti-patterns

- Inventing a fourth mode (`--mode dry-run`, `--mode verify`, `--mode plan-only`). The contract has THREE modes. If you need a different behavior, expose it via per-skill flags or a different skill.
- Allowing `--mode fix` on skills that act on other-people's-things (billing, prod deploy, force-push, schema drop). Reject the flag.
- Treating `--auto` as a synonym for `--mode auto`. They are orthogonal.
- A `fix`-mode that does not re-validate at the end.
- A `review`-mode that mutates source files (even "harmless" formatting).
- Skills that silently change behavior between modes — every difference must be documented in `references/modes.md`.
