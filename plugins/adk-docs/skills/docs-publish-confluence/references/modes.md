# `docs-publish-confluence` — modes

Supports `--auto` (default) and `-i`. Does NOT support `--fix`:
publishing IS the mutation; the skill's purpose is the write itself.

## `--auto` (default)

- Phases 0–3 run without approval gates.
- Phase 4 STILL asks once before publishing. This is a shared-state
  write; the ask survives `--auto`.
- Phase 5 verifies and reports.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when:
  - Space or parent are ambiguous.
  - The existence check found a page but the last editor is a bot
    and you still want to review the diff.
  - You want to inspect the converted XHTML before publish.

## Guardrails (all modes)

1. Single ask before publish, every run, every mode. Reviewers /
   page watchers get Confluence notifications; confirmation is
   cheap.
2. Never overwrites a human-authored page without an explicit
   opt-in (second, more explicit ask).
3. Never changes page restrictions or sharing.
4. Cap of 1 page per invocation (batches are user-driven loops).
5. Never deletes; never moves.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | convert + existence-check + ask-once + publish + verify |
| `-i` | per-phase approval; ask-once still required |
| `--space X` | override space (CLI wins over `docs.md`) |
| `--parent "Y"` | override parent (CLI wins over `docs.md`) |

## When the connector disagrees

- Connector rejects the publish (permission, rate limit, 5xx): the
  skill preserves the plan and surfaces the connector error
  verbatim. No retry loop.
- Connector returns a 409 version conflict on update: re-run Phase
  3 + show the new last-editor; re-ask.
- Connector returns 404 for a parent that existed in Phase 1: the
  parent was deleted mid-run; stop and surface.
