# `docs-pr-description` — modes

Supports `--auto` (default), `-i`, and `--fix`. See
`references/interaction-contract.md` for the universal shape.

## `--auto` (default)

- All phases run without approval gates.
- Produces `pr-body.md` and a report.
- Does NOT push / edit the remote PR body. `--fix` does that.

## `-i` / `--interactive`

- Per-phase approval gates.
- Typical use: review the classification (area table) and the draft
  title/summary before the body is written.

## `--fix`

- Composes with `--auto` and `-i`.
- Runs `gh pr edit <number> --body-file .temp/task-<slug>/pr-body.md`
  (or the equivalent `github` MCP call when adk-review is installed).
- **Always asks once** before the first remote write, even under
  `--auto --fix`. A PR body is a shared artifact with reviewers CC'd
  via GitHub notifications; confirmation is cheap, drive-by surprises
  are expensive.

## Guardrails (all modes)

1. Never opens, merges, or closes a PR. This skill only edits the body.
2. Never runs `gh pr review --approve` or `--request-changes`.
3. Never force-pushes. Doesn't touch branches at all.
4. Never drops an existing PR body section without user confirmation
   (diff between old body and new body is shown on `-i`).
5. On remote write failure (auth, rate limit, permission), preserve
   the new body in `.temp/task-<slug>/pr-body.md` and surface the
   exact fix command.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | draft-only; writes to `pr-body.md` |
| `-i` | per-phase approval; draft-only |
| `--fix` | draft + edit remote PR body (single ask) |
| `-i --fix` | per-phase approval + edit remote PR body |
| `--auto --fix` | full run; single ask before remote write |
