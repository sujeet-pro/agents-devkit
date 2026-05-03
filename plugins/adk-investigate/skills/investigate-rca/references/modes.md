# `investigate-rca` — mode contract

`investigate-rca` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix`.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - Window: `±2h around symptom` (parsed from prompt or `--symptom-time`).
  - Statsig audit window: `[symptom-2h, symptom+2h]`.
  - Code deep dive: enabled if leading hypothesis is code regression.
  - Mixpanel impact check: enabled if affected service has a known user-facing funnel.
- Internally chains `investigate-incident`, `investigate-statsig`, `git blame`, `investigate-mixpanel` (optional).
- Still validates after every phase.
- Still surfaces a final RCA report.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 1: shows preflight, asks "proceed?".
  - Phase 4: shows the implicated files before `git blame`, asks "blame these?".
  - Phase 5: asks "run Mixpanel impact check?" (default yes if user-facing).
  - Phase 6: shows the RCA draft, asks for review before final emit.
  - Phase 7: NEVER auto-publishes. Always stops at `.temp/`.

## `--fix` is not supported

- This skill produces a learning artifact (the RCA), not a code change.
- The RCA's action items are testable but they are queued for the team to action; the skill itself doesn't apply them.
- If the operator passes `--fix`, the skill rejects with: "investigate-rca produces a post-mortem artifact only; for the actual code fix, chain `/adk-code:code-bugfix` separately based on the action items".

## What `--auto` will NEVER do

1. Auto-publish the RCA to Confluence / GDoc / docs site. Always stops at `.temp/`.
2. Name an individual as root cause. The author + reviewer are metadata in the timeline; they never appear in the "root cause" sentence.
3. Issue an action item that is not testable.
4. Skip the timeline.
5. Single-source root cause (inherits the rule from `investigate-incident`).
6. Auto-trigger any remediation (rollback, gate flip, restart). The RCA describes; the operator decides.

## Composition with `--auto --fix` from `/adk-core:auto`

If the operator invokes `/adk-core:auto "RCA for X outage" --auto --fix`:

- `auto` propagates `--fix` to dispatched skills.
- This skill (`investigate-rca`) does NOT have `--fix`; it ignores the flag with a note in the RCA's `Action items` section: "for the code fix, action items below should be queued via `/adk-code:code-bugfix`".
- The RCA itself is read-only; mutation happens in the followup skills the action items name.
