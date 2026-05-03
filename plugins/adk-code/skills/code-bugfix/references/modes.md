# `code-bugfix` — mode contract

`code-bugfix` supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` — mutation IS the goal of this skill, so `--fix` is meaningless. The reproducer-first protocol is non-negotiable in either mode.

## `--auto` (default)

- Skips per-phase approval gates (Phase 0 expand, Phase 2 reproducer review, Phase 3 plan, Phase 6 report).
- Picks the documented `(default)` option at every decision (see `references/clarifying-questions.md`).
- Still validates after every meaningful change.
- Still **always** writes the failing reproducer first. `--auto` does NOT skip the reproducer step — the reproducer is the proof; without it, the fix is unverified.
- Still **always** runs the full affected-package suite at Phase 5.
- Still **always** re-runs the reproducer post-patch to confirm green.
- Refuses any irreversible destructive op (none expected; `git push --force` would be blocked by the `adk-core` `PreToolUse:Bash` hook anyway).

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm restated bug + suspected area.
    - Phase 2 — confirm the reproducer captures the bug correctly (this is the most valuable gate — a wrong reproducer means everything that follows is wrong).
    - Phase 3 — confirm the root cause + patch plan.
    - Phase 6 — confirm the report.
- Allows the user to refine the reproducer or override the diagnosis before patching.

## `--scope <path>`

- Optional, composes with `--auto` and `-i`.
- Restricts reads / edits to the given subtree. Useful when the bug is suspected to be in a specific package.
- The reproducer test still goes in the test location the repo conventions dictate, even if outside `--scope` — surface that as a deviation.

## What `code-bugfix` will NEVER do, even under `--auto`

1. Skip the reproducer step. The reproducer is non-negotiable.
2. Patch without diagnosing the root cause first. (Symptom-patching for documented upstream bugs is allowed but counts as "diagnosed: upstream".)
3. Refactor / rename / clean up adjacent code in the same diff.
4. Bundle a security mitigation. Security fixes follow `code-security` (which has its own threat-model + regression-test discipline).
5. Push, commit, or open a PR.
6. Disable an existing test to make the new one pass. If a test conflicts, surface it.
7. Auto-resolve a merge conflict.

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → investigate-incident (optional) → code-bugfix → review-code-changes`. `auto` propagates `--auto` / `-i` down.
- For incidents, the chain may include `/adk-investigate:investigate-incident` first (multi-source diagnosis); `code-bugfix` then receives the suspected hypothesis as a starting point but still writes its own reproducer and confirms the root cause itself.
- Called directly with `--auto`, runs end-to-end without approval gates.
- Called directly with `-i`, runs interactively with per-phase approval.

## Invalid combinations

- `--auto -i` — refused at parse. Mutually exclusive.
- `--fix` — silently ignored with a warning in the report. `code-bugfix` always mutates; `--fix` is meaningless.
