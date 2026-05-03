# `code-migrate` — mode contract

`code-migrate` supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — mutation IS the goal.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- **Still WebFetches the migration guide.** The guide is the source of truth; `--auto` does NOT skip the read.
- **Still validates between groups.** The per-group validation invariant is the safety net.
- Refuses any irreversible destructive op (the `adk-core` `PreToolUse:Bash` hook blocks the obvious ones).

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm `<from>` and `<to>` versions.
    - Phase 2 — review the curated `migration-notes.md` (this gate often surfaces operator knowledge — "we're not adopting that recommended-but-optional change").
    - Phase 4 — confirm the group sequence in `plan.md` (most-valuable gate — the operator may know a sequencing constraint).
    - Phase 5 — between groups; if a group fails, the operator decides next action.
    - Phase 7 — confirm the report.

## `--scope <path>`

- Optional, composes with `--auto` and `-i`.
- Restricts the inventory + edits to the given subtree.
- Useful for monorepo migrations where only one package is migrating first (e.g. "migrate `packages/checkout` to React 19; the others stay on 18").
- The dependency version bump (Phase 5 group Z) only applies to the scoped subtree's package.json (or equivalent).

## What `code-migrate` will NEVER do, even under `--auto`

1. Apply migration changes from memory; the guide MUST be fetched.
2. Bundle multiple framework migrations in one task (one framework, one direction).
3. Skip per-group validation (if a group fails silently, the rest of the migration is unverified).
4. Apply optional changes silently — they're flagged in the plan.
5. Push, commit, or open a PR.
6. Migrate on top of a red baseline.
7. Treat a CHANGELOG line as instruction without verifying against the migration guide. CHANGELOGs summarize; guides instruct.
8. Skip the smoke check if the change is runtime-affecting.

## What `--auto` MAY do without asking

- Resolve "latest" version via WebFetch + record in Decisions.
- Pick the order of two equally-low-blast-radius groups.
- Choose between two equivalent code transformations when the migration guide is silent (record in Decisions).

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → code-migrate → review-code-changes`. `auto` propagates flags down.
- Migrations are typically one-task-per-major-version-bump. If the user says "migrate React 18 → 20" (skipping 19), the skill should split into 18→19, then 19→20 — two consecutive `code-migrate` tasks. (Surface in Phase 0.)
- Tool replacements are one-task. Jest → Vitest, Webpack → Vite, etc.
- Called directly with `--auto`, runs end-to-end with documented defaults.
- Called directly with `-i`, runs interactively.

## Invalid combinations

- `--auto -i` — refused at parse.
- `--fix` — silently ignored. Migrations always mutate.

## When NOT to use --auto for a migration

Some migrations carry runtime semantic changes that benefit from operator review BEFORE applying:

- Node 16 → 18 → 20: changes to `fetch`, `URL`, default ESM behavior — operator may want to see the impact list before approving.
- React 18 → 19: ref-handling changes, `use()` hook semantics — review the guide quotes.
- Spring Boot 2 → 3: Jakarta EE namespace migration (`javax.*` → `jakarta.*`) — all-or-nothing.

In all cases, the skill surfaces "this migration has runtime semantic changes" in Phase 2 and recommends `-i` for the first run.
