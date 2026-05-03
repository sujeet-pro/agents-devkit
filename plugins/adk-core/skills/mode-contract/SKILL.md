---
name: mode-contract
description: |
  The universal definition of `--auto`, `-i`, `--fix`, and `--auto --fix` modes used by every adk skill. Reference-only skill: it documents the contract and provides the parsing helpers other skills source. Use when authoring a new skill, when debugging which mode is active, or when the user asks "what does --fix do?". Do NOT use to execute any work — this skill is documentation + a tiny shell helper. Do NOT use to override the contract for one skill (override at the per-skill SKILL.md level if absolutely necessary, and document the deviation).
metadata:
  category: meta
  kind: task
  modes: [auto]
  layer: 0
argument-hint: "[--explain] [--parse <flags>]"
---

# mode-contract — universal --auto / -i / --fix definition

Reference-only skill that documents the mode contract and ships a tiny shell helper at `scripts/parse-mode.sh` that other skills source to normalize flags into env vars.

## When to use

- Authoring a new adk skill — read this to understand the contract.
- Debugging "which mode is active right now?" — invoke `--explain` to dump the parsed mode.
- The user asks "what does `--fix` do?" — point them here.

## When NOT to use

- Execute work — this skill is documentation + a tiny shell helper, not an executor.
- Override the contract for one skill — overrides happen at the per-skill SKILL.md level, and must be documented as deviations.

## The contract

| Flag | Default? | Meaning |
| --- | --- | --- |
| `--auto` | yes | End-to-end. Skip per-phase approval gates. Still **stops** before destructive shared-state actions (push, post, delete, merge). |
| `-i` / `--interactive` | no | Per-phase approval gates. Show the plan, ask for approval, allow edits. Mutually exclusive with `--auto`. |
| `--fix` | no | Apply changes locally, validate, push. Only on skills where mutation is the goal. |
| `--auto --fix` | no | Compose: auto-apply changes AND skip per-phase approval. Still NEVER auto-merges, force-pushes, or deletes branches. |

## Hard rules across all skills

1. `--fix` is only available where mutation is the skill's purpose: `review-pr`, `review-code-changes`, `review-feedback`, `docs-review`, `audit-pr`. Other skills that have `--fix` semantics use it for "apply suggested changes" — same rule.
2. Push to a remote branch is a "shared-state" action and ALWAYS asks before the first push, even under `--auto --fix`. Subsequent pushes within the same session may proceed without re-asking.
3. Posting a comment on a PR is a shared-state action; same rule as push.
4. Merging a PR is NEVER auto. Always asks.
5. Deleting a branch is NEVER auto. Always asks.
6. Force-pushing to `main` / `master` / `develop` / any branch in `~/.config/adk/github.md.forbid_force_push_branches` is BLOCKED, even under `--auto --fix`.
7. `--auto` and `-i` are mutually exclusive. `--auto -i` is a parse error.

## Parsing helpers

```
Phase 1 — preflight
  - Verify `scripts/parse-mode.sh` exists before offering --parse output.
  - No MCP or connector is required for this reference-only skill.

Phase 2 — explain or parse
  - For --explain, print the contract table.
  - For --parse, source the helper and print normalized env vars.
```

`scripts/parse-mode.sh` exports normalized env vars after sourcing:

```bash
source "${CLAUDE_PLUGIN_ROOT}/skills/mode-contract/scripts/parse-mode.sh"
parse_mode "$@"

echo "$ADK_MODE"   # auto | interactive
echo "$ADK_FIX"    # 0 | 1
```

The function emits an error and returns non-zero if `--auto -i` are both passed.

## Persona

> Contract documenter. Single source of truth for mode semantics across the marketplace.

See `references/persona.md`.

## Constitution

**Must do:**

1. Document the contract once; every other skill links here.
2. Keep `parse-mode.sh` minimal — flag parsing only, no side effects beyond exporting env vars.

**Must not do:**

1. Execute any user-visible work.
2. Add new modes without a marketplace-wide migration plan.
3. Change the contract without updating every skill's SKILL.md.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Re-defining the contract in each skill (refer here instead).
- Adding a new mode for one skill's convenience.
- Treating `--auto --fix` as license to merge.

## Output

`--explain`: prints the contract as a markdown table.

`--parse <flags>`: prints the resulting env vars (debug aid).

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Contract documenter |
| `references/contract.md` | The full contract (longer prose) |
| `references/parse-mode-spec.md` | What `parse-mode.sh` does + edge cases |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Mode combinations + behavior table |
| `references/modes.md` | Trivially: this skill itself supports only `--auto` |
| `references/interaction-contract.md` | Canonical interaction contract |
| `scripts/parse-mode.sh` | Shell helper — source from other skills |
