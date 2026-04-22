# `observability-datadog` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/observability-datadog.md`.

## Phase 1 — pre-execution
- [ ] Inputs valid.
- [ ] `.temp/task-<slug>/` exists.
- [ ] Required MCP servers reachable (or fallback documented).

## Phase 2 — mid-flow
- [ ] Each step's preconditions met before the next runs.
- [ ] No write outside `.temp/task-<slug>/`.

## Phase 3 — pre-handoff (before publishing the artifact)
- [ ] Artifact matches `references/artifact-format.md` shape.
- [ ] Every claim has cited evidence.
- [ ] No remote write happened without an approval gate.

## Phase 4 — post-execution
- [ ] Final report exists.
- [ ] All side effects accounted for.
- [ ] User acknowledged (or `--auto`).
