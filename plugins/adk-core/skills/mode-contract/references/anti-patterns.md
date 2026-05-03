# `mode-contract` — anti-patterns

- **Re-defining the contract in each skill's SKILL.md.** Reference here instead. Single source of truth.
- **Adding a new mode for one skill's convenience.** Three modes cover every use case. New modes need a marketplace-wide migration plan.
- **Treating `--auto --fix` as license to merge.** It's not. Merge is always a human action, even with both flags.
- **Skipping the first-push gate under `--auto --fix`.** The first push of a session always asks; subsequent pushes don't.
- **Force-pushing to a protected branch when `--auto --fix` is on.** Blocked. The hook also catches this.
- **Allowing `--auto -i` to silently drop one of them.** Parse error. Refuse.
- **Using `parse-mode.sh` for anything beyond flag parsing.** It's intentionally minimal.
- **Letting individual skills invent their own flag names** (`--unattended`, `--review-only`). Use the canonical 3.
