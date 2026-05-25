---
title: 'adk-setup'
description: 'Set-up, configure-overrides, init-config, refresh-metadata, verify-mcps, check-env. Stewards `$ADK_CONFIG_HOME/core.yaml` and the metadata cache. NOT a CLI-dep installer — brew, gh, jq, uv, node are the user''s...'
skill: 'adk-setup'
source: 'skills/adk-setup/SKILL.md'
group: 'skills'
order: 1008
---
# adk-setup

Set-up, configure-overrides, init-config, refresh-metadata, verify-mcps, check-env. Stewards `$ADK_CONFIG_HOME/core.yaml` and the metadata cache. NOT a CLI-dep installer — brew, gh, jq, uv, node are the user's job (SETUP.md prints the exact commands). NOT a wiring tool — install.sh handles symlinks, MCP merges, hook wiring, AGENTS.md pointers. This skill picks up where install.sh stops: filling user data files (conversationally) and introspecting MCPs (with the agent's MCP client, which install.sh / curl cannot do). Four modes. --init: conversational scaffolding of core.yaml (workspaces, repos, data dictionary, RAG config). --enrich: queries every reachable MCP (Datadog dashboards, Statsig experiments, Mixpanel events, Snowflake schemas, Looker dashboards, Atlassian spaces, GitHub repos), summarizes findings, writes `enriched:` block + `$ADK_DATA_HOME/improve/metadata/<source>.json`. Never overwrites manually-set values. --check: superset of `scripts/adk_mcp_health.py` — also probes stdio MCPs (Atlassian via uvx, Slack via npx, Snowflake via uvx) via real MCP-client invocation, and offers conversational guidance when something's broken. --diff: read-only preview of --enrich. Never modifies shell rc files. Never puts a raw token in core.yaml (regex-enforced).

## Source

`skills/adk-setup/SKILL.md`

## Frontmatter

```yaml
name: adk-setup
description: |
  Set-up, configure-overrides, init-config, refresh-metadata, verify-mcps, check-env. Stewards `$ADK_CONFIG_HOME/core.yaml` and the metadata cache. NOT a CLI-dep installer — brew, gh, jq, uv, node are the user's job (SETUP.md prints the exact commands). NOT a wiring tool — install.sh handles symlinks, MCP merges, hook wiring, AGENTS.md pointers. This skill picks up where install.sh stops: filling user data files (conversationally) and introspecting MCPs (with the agent's MCP client, which install.sh / curl cannot do). Four modes. --init: conversational scaffolding of core.yaml (workspaces, repos, data dictionary, RAG config). --enrich: queries every reachable MCP (Datadog dashboards, Statsig experiments, Mixpanel events, Snowflake schemas, Looker dashboards, Atlassian spaces, GitHub repos), summarizes findings, writes `enriched:` block + `$ADK_DATA_HOME/improve/metadata/<source>.json`. Never overwrites manually-set values. --check: superset of `scripts/adk_mcp_health.py` — also probes stdio MCPs (Atlassian via uvx, Slack via npx, Snowflake via uvx) via real MCP-client invocation, and offers conversational guidance when something's broken. --diff: read-only preview of --enrich. Never modifies shell rc files. Never puts a raw token in core.yaml (regex-enforced).
allowed-tools: [Read, Edit, Write, Bash, WebFetch]
argument-hint: "(--init [--from-v2]) | (--enrich [--source <name>|all]) | (--check) | (--diff) [--detailed] [--deep]"
metadata:
  category: core
  kind: task
  layer: 0
  paths: []
  model: sonnet
  effort: low
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-github, adk-mcp-datadog, adk-mcp-statsig, adk-mcp-atlassian, adk-mcp-mixpanel, adk-mcp-slack, adk-mcp-snowflake, adk-mcp-looker]
  needs_meta_info: []
  forks_emitted: [init-source, enrich-sources, conflict-with-existing, model-depth]
```

## Workflow body

# adk-setup

Bootstrap + maintain `$ADK_CONFIG_HOME/core.yaml`.

**Global skill** — runs from anywhere; intermediate artifacts go to `$ADK_DATA_HOME/setup/<ts>/` (per `shared/paths.md`). Touches `$ADK_CONFIG_HOME/` (config) but not the cwd.

`--detailed` increases MCP/config diagnostics. `--deep` selects the stronger model profile per `shared/model-depth.md`; use it when reconciling ambiguous config, migrations from older installs, or many failing connectors.

## Modes

### --init

Scaffolds `$ADK_CONFIG_HOME/core.yaml` with full structure + comments. Behavior:

1. If `$ADK_CONFIG_HOME/core.yaml` exists → refuse; show user `--diff` instead.
2. Else → write fresh templates for `core.yaml`, `repos.md`, `connectors/*.md`, and `links.json5`.
4. Walk the user through filling: workspaces (cap 3 questions), one starter repo, RAG config.

Then: print "edit `$ADK_CONFIG_HOME/core.yaml` (defaults / workspaces / rag) and `$ADK_CONFIG_HOME/repos.md` (per-repo entries). Add new data sources by editing `$ADK_CONFIG_HOME/connectors/<name>.md`. Re-run `/adk-setup --enrich` to populate auto-discovery."

### --enrich

For each MCP (or `--source <name>` for one), call `scripts/enrich_metadata.py`:

1. Query reachable MCPs via curl / programmatic calls.
2. Write `$ADK_DATA_HOME/improve/metadata/<source>.json` (overwrites; archives previous).
3. Propose updates to `$ADK_CONFIG_HOME/connectors/<name>.md` frontmatter — only ADD; never delete manually-set values. Per-update user confirmation required.
4. Surface MCPs that couldn't be reached (env var missing, OAuth not done, etc.) with the exact fix.

### --check

For each agent (claude / cursor / codex / junie):
- Detect installation.
- Verify symlinks point to this repo's `skills/`.
- Verify MCP config merged.

For each env var: present / missing / aliased.

For each MCP: reachable / not-reachable + reason, AND — if the user's
`creds` CLI is installed (mac-setup's `~/.config/creds/` layout) — the
creds-system probe status for the same service (OK / FAIL / MISCONFIGURED).
This surfaces the common "env-vars are set but the token is invalid"
case that env-presence checks alone cannot detect. The cross-reference
is purely additive: `--no-creds` disables it, and it auto-skips on
machines without the `creds` CLI.

For core.yaml: workspaces count, repos count, data_sources presence, defaults presence.

### --diff

Read-only preview of what `--enrich` would change. Useful before committing.

## Workflow

```
Phase 0 — context-gather (minimal — this skill is mostly a config tool)
  - Detect environment (OS, agents installed, $ADK_CONFIG_HOME/ state)

Phase 1 — advise
  - Up to 3 questions depending on mode:
    --init: which workspace type (work / personal / both), confirm primary repo location, RAG enabled?
    --enrich: which sources, confirm OAuth flows if needed
    --check / --diff: no questions

Phase 2 — execute (mostly programmatic — script-driven)
  - --init: write core.yaml / repos.md / connectors/*.md / links.json5 templates
  - --enrich: run scripts/enrich_metadata.py
  - --check: build verification table
  - --diff: dry-run enrich

Phase 3 — validate
  - File written + syntactically valid YAML
  - Enrichment didn't overwrite manual fields

Phase 4 — report
  - --init: pointer to the file, next-steps to fill it
  - --enrich: count of fields added; list of unreachable sources with fixes
  - --check: the verification table
```

## Hard rules

1. **Never** overwrite a manually-set value in `core.yaml`. Only the `enriched:` and `learning_state:` blocks are auto-managed.
2. **Never** put a token / secret in `core.yaml`. Regex-check before writing.
3. **Never** chmod or modify the user's shell rc files. Print export lines; the user adds them.
4. **Never** OAuth a third-party service automatically. Print the URL; user clicks.

## Persona

- Light persona (no shared file). Walks tone is "calm sysadmin", not "enthusiastic onboarder".

## Fork IDs

| fork_id | options | recommendation |
|---|---|---|
| `init-source` | fresh / migrate-from-v2 | migrate-from-v2 if v2 files detected |
| `enrich-sources` | all / specific list | all reachable |
| `conflict-with-existing` | abort / merge-non-destructive | merge-non-destructive |

## Refusals

- `--init` when file exists → refuse, suggest `--diff`.
- `--enrich` when no MCPs configured → refuse, point at `mcp/README.md` + env vars.
- Migration when source file has unparseable YAML → refuse, show parse error, suggest manual fix.

## References shipped

_(References authored on first real use of each sub-flow.)_
