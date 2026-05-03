# `docs-write` — modes

`docs-write` supports `--auto` (default), `-i` / `--interactive`, and
`--fix`. Read `references/interaction-contract.md` for the universal
shape of each; this file captures only what's skill-specific.

## `--auto` (default)

- Phase 0 (slug + classification), Phase 1 (preflight), Phase 2
  (gather sources), Phase 3 (draft) run without approval gates.
- Phase 4 validator errors still stop the flow and surface to the user
  — the draft is not promoted to the canonical path automatically.
- Still writes only to `.temp/task-<slug>/`. `--fix` is what promotes
  to the canonical path.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when:
  - The doc type is ambiguous ("write the docs" — README? ADR? runbook?).
  - The target path is unclear (e.g. a monorepo with nested READMEs).
  - The audience setting disagrees with the doc's natural calibration.
- Allows the user to edit the evidence map before the draft is produced.

## `--fix`

- Composes with `--auto` or `-i`.
- **What `--fix` does:** after the validator passes, write the draft to
  the canonical path (README.md / docs/adr/NNNN-*.md / etc.) and `git
  add` the file. Produces a staged, uncommitted change.
- **What `--fix` does NOT do:** run `git commit`, run `git push`, edit
  shared Confluence / GDoc pages, or touch files outside the resolved
  target.
- **`--fix` always asks once** before overwriting an existing file. Even
  under `--auto --fix`. The ask is: "Overwrite `<path>` (last modified
  by `<author>` on `<date>`)?".
- **Never amends** a previous commit or any git state beyond staging.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | default: `--auto` mode, draft only, no canonical write |
| `--fix` | `--auto` + write canonical path + `git add` |
| `-i` | per-phase approval; draft only |
| `-i --fix` | per-phase approval + canonical write + `git add` |
| `--auto --fix` | end-to-end; single ask before overwriting an existing target path |
| `--auto -i` | invalid (parser refuses) |
