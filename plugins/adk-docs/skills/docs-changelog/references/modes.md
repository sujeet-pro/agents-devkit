# `docs-changelog` — modes

Supports `--auto` (default), `-i`, and `--fix`. See
`references/interaction-contract.md` for universal shape.

## `--auto` (default)

- Phases 0–3 run without approval gates.
- Produces `changelog-entry.md`; does NOT modify `CHANGELOG.md`.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when:
  - The `<from>..<to>` range is wide and classification needs review.
  - Some commits are ambiguous (refactor-or-feature? perf-or-chore?).
  - A specific entry's phrasing needs tuning.

## `--fix`

- Composes with `--auto` and `-i`.
- Modifies `CHANGELOG.md` by inserting the new version block at the
  canonical position. Does NOT commit; stages via `git add`.
- If `CHANGELOG.md` already has a block for `<to-tag>`, the skill:
  - Under `--auto`: stops and asks for opt-in to overwrite.
  - Under `-i --fix`: always asks.
- Backs up `CHANGELOG.md` to `.temp/task-<slug>/backup/CHANGELOG.md`
  before write.

## Guardrails (all modes)

1. Never runs `git commit`, `git push`, or `git tag`.
2. Never deletes or rewrites a previously-published version block
   without explicit opt-in.
3. Never writes outside `CHANGELOG.md` and `.temp/task-<slug>/`.
4. Never auto-promotes an "unreleased" section to a versioned one —
   that's a release-management decision the user owns.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | draft only |
| `-i` | per-phase approval; draft only |
| `--fix` | draft + insert into CHANGELOG.md + git add |
| `-i --fix` | per-phase approval + insert + git add |
| `--auto --fix` | end-to-end; single ask if target version block already exists |
