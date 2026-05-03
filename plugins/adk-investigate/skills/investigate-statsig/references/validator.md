# `investigate-statsig` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-statsig.md`.

## Phase 0 — pre-execution

- [ ] User's question captured verbatim.
- [ ] `--use` resolved to one of `pulse`, `gates-list`, `gates-detail`, `audit-log`, `metrics-catalog`.
- [ ] Experiment / gate / metric name resolved (`verified` from `statsig.md` OR `inferred`).
- [ ] Time window resolved to a concrete `[from, to]` pair (for `audit-log`, `pulse`).

## Phase 1 — preflight

- [ ] `bin/adk-mcp-health --shipped` shows `statsig: connected`.
- [ ] `STATSIG_CONSOLE_API_KEY` env var present.
- [ ] `bin/adk-info --check statsig` returns 0.
- [ ] `~/.config/adk/statsig.md` has `project`, `default_environment`, plus `common_experiments` / `common_gates` / `exposure_metric_conventions` if shorthand was used.

## Phase 2 — execute

- [ ] Each MCP call is logged to `.temp/task-<slug>/investigation/statsig/calls.md` before execution.
- [ ] Raw responses written to `raw/`.
- [ ] No `omni_write` tool invoked. Any attempt → fail loud.
- [ ] No more than 5 substantive calls in a single Phase 2 (`List_*` cheap calls excluded).

## Phase 3 — summarize

### `--use pulse`-specific

- [ ] Sample size (`n` per arm) stated.
- [ ] p-value stated for primary + each secondary + each guardrail.
- [ ] Days-in-experiment stated.
- [ ] For each guardrail moving the wrong way at `p<0.1`, marked `REGRESSION (veto)`.
- [ ] Recommendation is one of `ship | iterate | kill`, anchored to rubric inputs.
- [ ] If recommendation = `ship`, NO guardrail is marked `REGRESSION (veto)`. (Hard gate.)

### `--use audit-log`-specific

- [ ] Each entry has `time + object + action + actor`.
- [ ] No more than 50 entries displayed (group by object/actor; surface top recent).

### Common

- [ ] Every result row has a Statsig console link.
- [ ] If a likely cause is named, confidence stated.

## Phase 4 — pre-handoff

- [ ] `.temp/task-<slug>/investigation/statsig.md` exists.
- [ ] Sections per `--use` per `output-format.md`.
- [ ] Every artifact referenced in the report exists at the cited path.
- [ ] Final status banner printed.

## On any check failure

- Log to `validation/investigate-statsig.md` with the failing check + remediation.
- Block next phase.
- Same check failing 3 times → surface; do not loop.
