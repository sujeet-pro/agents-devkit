---
name: adk-improve
description: |
  Improve, learn, refresh-metadata, update-defaults, self-improve, train-skill, learn-from-session. The self-improvement loop. Always interactive (asks first: improve skill defaults from decision logs, metadata via MCP introspection, or both). For defaults: runs scripts/proposal_generator.py against `~/.agents-devkit/improve/learning/decisions.jsonl`, drafts proposed updates to `~/.agents-devkit/config/overrides.yaml.defaults.*`, presents each with ≥3 evidence lines, applies on confirm; rotates decisions.jsonl to learning/archive/ after each run; appends summary to learning/summary.md. For metadata: runs scripts/metadata_introspector.py to refresh `~/.agents-devkit/improve/metadata/<source>.json` from every reachable MCP. Bounded: cannot change shared/constitution.md; cannot change Must-do/Must-not-do sections of any SKILL.md (those are constitution-grade). Each proposal requires per-item confirmation regardless of mode. Never auto-applies. Min-evidence default 3 (configurable). Manual-only by design (disable-model-invocation: true) so the agent doesn't auto-trigger improvements mid-session.
allowed-tools: [Read, Edit, Write, Bash]
argument-hint: "[--target defaults|metadata|both] [--since <date>] [--min-evidence N] [--dry-run]"
metadata:
  category: core
  kind: task
  layer: 0
  paths: []
  model: opus
  effort: medium
  user-invocable: true
  disable-model-invocation: true
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-github, adk-mcp-datadog, adk-mcp-statsig, adk-mcp-atlassian, adk-mcp-mixpanel, adk-mcp-slack, adk-mcp-snowflake, adk-mcp-looker]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [improve-target, min-evidence, apply-policy]
---

# adk-improve

Read accumulated decision logs + introspect MCPs; propose updates to `overrides.yaml`.

**Global skill** — intermediate artifacts go to `~/.agents-devkit/improve/<ts>/`. Mutates `~/.agents-devkit/config/overrides.yaml` and `~/.agents-devkit/improve/metadata/<source>.json` on confirm; never touches the cwd repo.

## Modes (mandatory interactive choice at start)

The skill ALWAYS asks first, even under `--auto`:

```
What do you want to improve?
  [1] skill defaults — based on accumulated decision logs since <date>
  [2] metadata — re-introspect all configured data sources
  [3] both
  [4] custom — specify target
```

(`--target` flag pre-selects.)

## Workflow — defaults (option 1)

```
Phase 0 — read learning state
  - ~/.agents-devkit/improve/learning/decisions.jsonl (current cycle)
  - ~/.agents-devkit/improve/learning/summary.md (history)
  - ~/.agents-devkit/config/overrides.yaml.defaults (current state)

Phase 1 — advise
  - Show count of decisions since last improve run
  - Ask: scope (all skills / one skill / custom), min-evidence threshold (default 3)
  - Show summary of detected patterns (programmatic via scripts/proposal_generator.py)

Phase 2 — execute (proposal review loop)
  - For each proposal:
    1. Show: skill, fork_id, current_default, proposed_default, evidence_count, confidence
    2. Show: ≥3 evidence lines verbatim (with task-slugs and reasons)
    3. Ask: accept / reject (with reason) / defer
  - On accept: write to `overrides.yaml.defaults.<skill>.<fork_id>`. Add comment with date + evidence count.

Phase 3 — validate
  - Each applied proposal: re-read overrides.yaml, confirm value present
  - No proposals modified hard rules (constitution / Must-do)

Phase 4 — report + rotate logs
  - Print: N proposals accepted, M deferred, K rejected
  - Append run summary to ~/.agents-devkit/improve/learning/summary.md
  - Archive current decisions.jsonl to ~/.agents-devkit/improve/learning/archive/<ts>-decisions.jsonl
  - Start fresh empty decisions.jsonl
  - Update overrides.yaml.learning_state.last_improve_run
```

## Workflow — metadata (option 2)

```
Phase 0 — list configured MCPs from mcp/ and overrides.yaml
Phase 1 — advise: confirm which to refresh; warn about OAuth requirements
Phase 2 — execute: scripts/metadata_introspector.py (which archives previous + writes fresh)
Phase 3 — validate: all files written, JSON valid
Phase 4 — report: diff vs prior (new dashboards, removed gates, etc.)
  - Update overrides.yaml.learning_state.last_metadata_refresh
```

## Hard rules

1. **Never modify**: `shared/constitution.md`, any skill's `Must do` / `Must not do` / `Hard rules` sections, `agents/*.md` core personas.
2. **Only modify**: `~/.agents-devkit/config/overrides.yaml` (defaults block + enriched block + learning_state block) and `~/.agents-devkit/improve/metadata/*.json`.
3. **Never auto-apply** a proposal under `--auto`. Each proposal requires per-item confirm — `--auto` only skips the "what do you want to improve" question if `--target` is passed.
4. **Rotate decisions.jsonl** after every successful improve run. Archive, never delete.
5. **Show ≥3 evidence lines** per proposal. < 3 = surface as "observation, not enough evidence yet".

## Persona

No dedicated persona file; pulls from `shared/advisor.md` heavily. Narration: `shared/narration.md`.

## Fork IDs

| fork_id | options | recommendation |
|---|---|---|
| `improve-target` | defaults / metadata / both / custom | both (most info per run) |
| `min-evidence` | 2 / 3 / 5 | 3 (configurable per skill in overrides) |
| `apply-policy` | per-proposal-confirm / batch-confirm | per-proposal-confirm |

## Refusals

- Empty decision log AND empty metadata staleness → refuse, suggest "use some skills first".
- A proposal would change a hard rule → refuse, surface as "needs your direct edit".
- `--auto` without `--target` → refuse, ask the mandatory first question.
