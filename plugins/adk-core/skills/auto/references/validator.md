# `auto` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/auto-validator.md`.

## Phase 0 — pre-execution

- `.temp/task-<slug>/` exists and is gitignored.
- User's prompt captured verbatim in `prompt.txt`.
- Verb classification recorded.
- Entity resolution table recorded with verified/inferred labels.
- If any links in prompt, `context-gather` is queued.

## Phase 1 — preflight

- `bin/adk-info --check` returned 0.
- `bin/adk-mcp-health` shows all required MCPs as `connected`.
- `git status` captured (informational unless mutation chain).
- No required env var is `MISSING` for the proposed chain.

## Phase 2 — after context-gather (if ran)

- `context.md` exists.
- Every link in the prompt is accounted for (OK / access-denied / 404).
- No quote >15 words from any source.

## Phase 3 — after skill-plan proposal

- `skill-plan.md` exists with: Prompt, Restated intent, Resolved entities, Links, Recommended chain, Alternatives, Missing inputs.
- Every skill in the chain exists in the marketplace (no invented names).
- No destructive skill (`--fix`, publish, merge) without explicit user opt-in or top-level `--auto --fix`.
- User approved (unless `--auto`).

## Phase 4 — after dispatch

- All dispatched subagents returned (none stuck).
- Each subagent's per-skill validator file exists at `validation/per-skill/<skill>.md`.
- No subagent wrote outside `.temp/task-<slug>/`.
- `dispatch.md` aggregates each subagent's status + artifact path.

## Phase 5 — pre-handoff

- `report.md` covers: Result, Decisions, Skills-run, Validation, Residual-risk, Artifact-index.
- Every artifact referenced in `report.md` actually exists at the cited path.
- No remote write happened without an approval gate (or `--auto`).
- Final status banner printed.

## On any check failure

- Log the failure to `auto-validator.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, surface to the user — do NOT loop forever.