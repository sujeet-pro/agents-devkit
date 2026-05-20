---
title: 'shared/decision-log-schema'
description: '```json'
source: 'shared/decision-log-schema.md'
group: 'shared'
order: 5603
---
# shared/decision-log-schema

> Source: `shared/decision-log-schema.md`

# shared/decision-log-schema.md

> The append-only JSONL at `~/.agents-devkit/improve/learning/decisions.jsonl`. One line per non-trivial fork. Consumed by `/adk-improve` to propose updates to `~/.agents-devkit/config/overrides.yaml.defaults.*`.

## Line shape

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
  "workspace": "quince-work",
  "task_slug": "implement-SF-1234",
  "evidence": null
}
```

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `ts` | ISO8601 UTC | When the fork was resolved |
| `skill` | string | adk-implement / adk-review / … (no leading slash) |
| `sub_flow` | string \| null | the loaded `references/<name>.md` or null if the skill is monolithic |
| `fork_id` | string | stable identifier for THIS fork across runs (e.g. `scope`, `test-framework`, `severity-bar`, `tone`) |
| `fork_type` | enum | `user-answered`, `auto-defaulted`, `override-applied`, `inferred` |
| `default_offered` | string \| null | what the skill recommended |
| `user_chose` | string \| null | what the user picked (or what the agent picked if `auto-defaulted`) |
| `task_slug` | string | the `.temp/` task folder name |

## Optional fields (rich training signal — include when known)

| Field | Type | Meaning |
|---|---|---|
| `question` | string | exact question asked (for `user-answered`) |
| `options` | string[] | the options presented |
| `reason_if_given` | string \| null | the user's stated reason; gold for learning |
| `repo` | string | repo name from overrides.yaml |
| `workspace` | string | workspace name from overrides.yaml |
| `evidence` | string \| null | for `auto-defaulted`: the rationale, e.g. "3 prior tickets in this repo chose vertical-slice" |
| `prior_decisions_count` | integer | count of prior matching fork_ids in log (used by /adk-improve confidence) |

## Fork types (`fork_type`)

- **`user-answered`** — agent asked; user explicitly chose. **Highest weight** in learning.
- **`auto-defaulted`** — agent picked recommended default under `--auto`. Useful for "did the silent default match what the user would have picked?" detection (compare with later overrides).
- **`override-applied`** — applies an existing override from `overrides.yaml.defaults`. **No learning weight** (this is the *result* of prior learning, not new data).
- **`inferred`** — agent inferred from context without offering choice (e.g., "this repo uses pytest, not jest"). Logged for traceability; light learning weight.

## Stable `fork_id`s

Each skill maintains a list in its `SKILL.md` of the canonical fork_ids it can emit. Examples:

- `/adk-implement`: `scope`, `test-framework`, `pr-strategy`, `commit-style`, `linter-tolerance`, `breaking-change-policy`
- `/adk-review`: `severity-bar`, `dimensions`, `auto-post-policy`, `confidence-threshold`
- `/adk-investigate`: `window`, `time-resolution`, `cross-source-required`, `confidence-threshold`
- `/adk-document`: `tone`, `audience`, `template`, `length-target`
- `/adk-sync`: `idempotency`, `conflict-resolution`, `format-conversion-strictness`

Adding a fork_id to a skill is a deliberate change — it's a new dimension the user can train on.

## What does NOT get logged

- Decisions made entirely inside `shared/constitution.md` (e.g., "refused to force-push"). These are not training signals; they're hard rules.
- Internal tool calls (which MCP, which API). Those go to `task-slug/trace.md` if needed for debugging.
- PII (user emails inside data, message bodies, etc.). Decision logs reference *categories* not *content*.

## File hygiene

- Append-only during a session. Never truncate mid-session.
- Rotated by `/adk-improve` on completion: current file archived to `~/.agents-devkit/improve/learning/archive/<ts>-decisions.jsonl`, a fresh empty file replaces it, and the summary appended to `~/.agents-devkit/improve/learning/summary.md`.
- The archive is the durable history. `/adk-improve` reads `summary.md` + `decisions.jsonl` (the current cycle) when deciding what to propose.
