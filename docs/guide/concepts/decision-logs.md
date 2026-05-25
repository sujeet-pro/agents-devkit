---
title: Decision logs + /adk-improve
description: Every non-trivial fork in every skill run gets one JSONL line. /adk-improve reads these and proposes default updates to overrides.yaml. Your skills get more accurate as you use them.
order: 8
---

# Decision logs + the self-improvement loop

The most important thing in adk. Every skill run accumulates evidence; `/adk-improve` turns evidence into defaults.

## The file

`$ADK_DATA_HOME/improve/learning/decisions.jsonl` — append-only, one line per non-trivial fork.

Schema in `shared/decision-log-schema.md`. Required fields: `ts`, `skill`, `fork_id`, `fork_type`, `default_offered`, `user_chose`, `task_slug`.

Example:

```json
{
  "ts": "2026-05-18T14:22:03Z",
  "skill": "adk-implement",
  "sub_flow": "from-jira",
  "fork_id": "scope",
  "fork_type": "user-answered",
  "question": "smallest version that helps you ship today?",
  "options": ["vertical-slice", "full", "spike"],
  "default_offered": "vertical-slice",
  "user_chose": "full",
  "reason_if_given": "demo Monday",
  "repo": "storefront-bff",
  "workspace": "personal-work",
  "task_slug": "implement-SF-1234"
}
```

## Fork types

- **`user-answered`** — agent asked; user explicitly chose. **Highest weight** in learning.
- **`auto-defaulted`** — agent picked recommended default under `--auto`. Useful for "did silent default match user preference?" detection.
- **`override-applied`** — applies an existing override from `overrides.yaml.defaults`. **No learning weight** (this is the result of prior learning).
- **`inferred`** — agent inferred from context without offering choice (e.g., "this repo uses pytest"). Logged for traceability; light weight.
- **`escalation`** — hand-off to `/adk-explain` or refusal. Useful for refining when to offer choice up-front.

## What gets logged

- Every question the user answered.
- Every default the agent picked silently under `--auto`.
- Every override from overrides.yaml that the skill applied.
- Every refusal / escalation.

## What does NOT get logged

- Hard rules from `shared/constitution.md` (those are non-negotiable, not training signals).
- Internal tool calls (which MCP, which API). Those go to `task-slug/trace.md` if needed.
- PII / message bodies / token values. Logs reference *categories*, not *content*.

## `/adk-improve` — the self-improvement loop

`/adk-improve` is always interactive. Asks first:

```
What do you want to improve?
  [1] skill defaults — based on accumulated decision logs since <date>
  [2] metadata — re-introspect all configured data sources
  [3] both
  [4] custom — specify target
```

### For "skill defaults"

`scripts/proposal_generator.py` does the pattern detection (deterministic, no AI):

1. Group decisions by `(skill, sub_flow, fork_id)`.
2. For each group, find the `user_chose` value that wins ≥ `min_evidence` (default 3) times AND differs from the usual `default_offered`.
3. Emit a proposal: "your default for `adk-implement.scope` should change from `vertical-slice` to `full`".
4. AI step drafts the proposal as user-facing prose with quoted evidence lines.
5. Each proposal requires per-item confirm. You accept / reject / defer.

On accept: writes to `$ADK_CONFIG_HOME/overrides.yaml.defaults.<skill>.<fork_id>` with a comment naming the date + evidence count.

After the run:
- Appends a summary to `$ADK_DATA_HOME/improve/learning/summary.md`.
- Archives the current `decisions.jsonl` to `$ADK_DATA_HOME/improve/learning/archive/<ts>-decisions.jsonl`.
- Starts a fresh empty `decisions.jsonl`.

### For "metadata"

`scripts/metadata_introspector.py` queries every reachable MCP and refreshes `$ADK_DATA_HOME/improve/metadata/<source>.json`. Prior version archived to `$ADK_DATA_HOME/improve/metadata/archive/<ts>/`.

## Bounded surface

`/adk-improve` can change:
- `$ADK_CONFIG_HOME/overrides.yaml.defaults.*` (your per-skill defaults)
- `$ADK_DATA_HOME/improve/metadata/*.json` (auto-discovered metadata cache)

`/adk-improve` **cannot** change:
- `shared/constitution.md` (constitution-grade)
- Any skill's `Must do` / `Must not do` / hard-rule sections
- Personas' core operating rules
- The shared workflows / advisor.md / question-first.md

These require direct human edits to the repo.

## When to run

- After a "burst" of skill invocations on a single repo (5+ runs).
- After joining a new project (your defaults may drift).
- When `/adk-setup --check` reports stale metadata (last_metadata_refresh > 30 days ago).
- Whenever the SessionStart banner says "N pending proposals — run /adk-improve".

## Seeded evidence

`install.sh` seeds your `decisions.jsonl` with foundational design decisions from `shared/seed-decisions.jsonl` on first install. This means your first `/adk-improve` run already has evidence (12 entries — your design Q&A from the v3 build sessions) — useful test data for the proposal flow.

## Next

- [Question-first](./question-first.md) — how Q&A enters the log
- [Plan/Act mode](./plan-act-mode.md)
