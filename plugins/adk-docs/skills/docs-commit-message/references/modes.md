# `docs-commit-message` — modes

Supports `--auto` (default), `-i`, and `--fix`. See
`references/interaction-contract.md` for universal shape.

## `--auto` (default)

- Phases 0–3 run without approval gates.
- Produces `commit-msg.txt`; does NOT run `git commit`.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when:
  - The staged diff is ambiguous across multiple logical changes.
  - The repo's convention detection is unclear.

## `--fix`

- Composes with `--auto` and `-i`.
- Runs `git commit --file .temp/task-<slug>/commit-msg.txt` AFTER
  one explicit confirmation — the confirmation is **not skipped**
  by `--auto`.
- Never uses `--amend`, `-a`, or `--no-verify`.
- If the pre-commit / commit-msg hook rejects, the skill surfaces
  the hook output and either loops back to Phase 2 or stops; it
  never bypasses hooks.

## Guardrails (all modes)

1. Never runs `git add` or `git add -p`. Staging is the user's
   decision.
2. Never runs `git push`.
3. Never runs `git commit --amend`. That's out of scope; the user
   owns amend.
4. Never writes to `.git/` directly.
5. Under `--fix`, if the staged diff changes between Phase 1 and
   Phase 4 (detected via `git diff --cached | sha1sum` comparison),
   refuses to commit; re-stages Phase 1 with a warning.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | draft `commit-msg.txt` only |
| `--style conventional` | draft with the conventional-commits format |
| `-i` | per-phase approval; draft only |
| `--fix` | draft + single-ask + `git commit` |
| `-i --fix` | per-phase approval + single-ask + `git commit` |
| `--auto --fix` | end-to-end; single-ask before `git commit` |
| `--no-verify` | **not supported**; skill refuses at parse time |
| `--amend` | **not supported**; skill refuses at parse time |
