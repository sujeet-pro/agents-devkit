# `code-api` — mode contract

`code-api` supports `--auto` (default) and `-i` / `--interactive`. Plus `--breaking`. Does **not** support `--fix` — mutation IS the goal.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- **Still captures use cases.** Auto does NOT skip Phase 2; without use cases, the design is by-vibes.
- **Still sketches 2-3 candidates.** Single-candidate designs are not designs.
- **Still produces a concrete artifact.** Auto does NOT settle for "we agreed to a shape" — there's an OpenAPI / .proto / .d.ts / CLI spec at the end.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm the contract type + new vs evolution.
    - Phase 2 — confirm the 3 use cases (this gate is high-value — operator may know domain context).
    - Phase 3 — review the candidates (operator may suggest a 4th).
    - Phase 4 — confirm the picked candidate + rationale (the most-valuable gate).
    - Phase 6 — confirm the deprecation plan (if `--breaking`).
    - Phase 7 — confirm the report.

## `--breaking`

Optional. Acknowledges this design has a breaking change. Triggers:

- Phase 6 (deprecation plan) becomes REQUIRED.
- The report includes a "breaking change summary" section.
- The skill defaults the deprecation window to "at least one major version + 90 days" — operator can override.

If the design implies a breaking change but `--breaking` was NOT set, the skill STOPS at Phase 4 and asks the operator to confirm + re-invoke with `--breaking`.

## What `code-api` will NEVER do, even under `--auto`

1. Skip use-case capture.
2. Sketch only one candidate.
3. Wave at the design without producing an artifact.
4. Make breaking changes without a deprecation plan.
5. Push the implementation behind the contract — that's `code-write`.
6. Push, commit, or open a PR.
7. Auto-publish the API change to a docs site or Confluence.
8. Add validation in three layers when the constitution says boundary-only.

## What `--auto` MAY do without asking

- Pick the contract type from context (REST when the file system shows OpenAPI files, etc.).
- Pick between two equivalent candidates if the use-case fit is identical.
- Default the deprecation window to "1 major + 90 days" when `--breaking` is set.
- Apply Hyrum's Law caveats by default (boundary-supported vs observable-but-unsupported).

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → code-api → code-write (implement behind the contract) → code-test (test the contract) → review-code-changes`.
- For SDK / library design, the chain is often `auto → code-api → docs-write (write usage docs) → code-write → code-test → review-code-changes`.
- Called directly with `--auto`, runs end-to-end producing the artifact.
- Called directly with `-i`, runs interactively with operator input on use cases + candidate selection.

## Invalid combinations

- `--auto -i` — refused at parse.
- `--fix` — silently ignored. `code-api` always mutates (produces an artifact).
