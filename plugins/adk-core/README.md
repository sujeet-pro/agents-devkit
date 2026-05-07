# adk-core

> The universal baseline for the `adk` marketplace. Required by every other adk plugin.

## What it ships


| Component           | What                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------ |
| **Skills (8)**      | `auto`, `prompt-expand`, `setup`, `config-update`, `info`, `temp-folder`, `mode-contract`, `context-gather` |
| **Agents (3)**      | `dispatcher`, `prompt-expander`, `context-gatherer`                                        |
| **Hooks**           | `PreToolUse:Bash` safety, `SessionStart` banner, `PostToolUse:Edit|Write` task/frontmatter checks |
| **Bin scripts (3)** | `adk-info`, `adk-task-slug`, `adk-mcp-health`                                              |
| **Templates (10)**  | Starter `~/.config/adk/<topic>.md` for every meta-info topic                               |


No MCP server shipped — `adk-core` provides infrastructure only.

## Skills

### `auto` — top-level prompt-routing dispatcher

The default entry point for free-form prompts. Reads the user's request, picks the right adk skill (or chain), and dispatches it via the `dispatcher` subagent.

```text
/adk-core:auto "fix the checkout bug since 13:00"
/adk-core:auto https://github.com/acme/checkout-api/pull/2841
/adk-core:auto "review my changes" -i
```

### `prompt-expand` — standalone prompt expander

Read-only. Produces a structured `skill-plan.md` from a free-form prompt without executing anything.

```text
/adk-core:prompt-expand "what would you do for: <prompt>"
```

### `setup` — bootstrap a fresh adk install

Creates `~/.config/adk/*.md` from templates; checks CLI deps; lists missing env vars referenced by every plugin's `.mcp.json`.

```text
/adk-core:setup                   # walk every topic
/adk-core:setup --target datadog  # one topic
/adk-core:setup --auto            # repeat-run health check
```

### `config-update` — refresh meta-info against live sources

Different from `setup` (which bootstraps files from templates): keeps drift-prone fields current by querying each source — Datadog dashboards, Statsig active experiments, Mixpanel top events, GitHub repos / CODEOWNERS, Snowflake schema — cross-referencing names against code, and proposing diffs. Read-only against sources; writes only to `~/.config/adk/*.md`, and only under `--fix`.

```text
/adk-core:config-update                     # diagnostic sweep across all topics
/adk-core:config-update --target statsig    # one topic
/adk-core:config-update --fix               # apply proposed changes after confirmation
/adk-core:config-update --auto --fix        # unattended apply (still asks per removal)
```

### `info` — read & merge meta-info

Read-only wrapper around `bin/adk-info`. Outputs JSON.

```text
/adk-core:info                          # dump all
/adk-core:info datadog                  # just one topic
/adk-core:info datadog site             # one key
/adk-core:info --check                  # validate schemas
/adk-core:info --missing                # list missing-but-recommended fields
```

### `temp-folder` — canonical .temp/ layout

Defines the `.temp/task-<slug>/` working-artifact layout. Other skills shell out to `bin/adk-task-slug` to create their workspace.

### `mode-contract` — universal --auto / -i / --fix definition

Reference-only skill. Documents the contract; ships `scripts/parse-mode.sh` that other skills source.

### `context-gather` — multi-source link follower

Pulls Jira tickets, Confluence pages, GDocs, Slack threads, Gmail threads, GitHub PRs/issues into a single `context.md`.

```text
/adk-core:context-gather "https://acme.atlassian.net/browse/CHK-1234 and https://acme.slack.com/..."
```

## Hooks

- **`PreToolUse:Bash`** — blocks dangerous commands: force-push to protected branches, `rm -rf` of project root or `~/.config/adk/`, `gh pr merge` without explicit user request, `git reset --hard` on protected branches, `git clean -fd` at repo root.
- **`SessionStart`** — prints the status banner via `hooks/banner.sh` (active plugins, loaded meta-info topics).
- **`PostToolUse:Edit|Write`** — touches `.temp/task-<slug>/.last-modified` for monitor visibility; verifies SKILL.md frontmatter when SKILL.md files are edited.

## Bin scripts

All three live under `bin/` and are auto-added to `$PATH` while `adk-core` is enabled.

### `adk-info`

```bash
adk-info                       # dump merged JSON
adk-info <topic>               # dump one topic
adk-info <topic> <key>         # dotted-path access
adk-info --check               # validate every file's schema
adk-info --missing             # list keys that skills want but aren't set
adk-info --resolve-env         # substitute ${ENV_VAR} placeholders
```

Implemented in Node (~300 LOC); ships its own minimal YAML parser (no external deps).

### `adk-task-slug`

```bash
adk-task-slug "<prompt>"               # echo slug; create .temp/task-<slug>/
adk-task-slug "<prompt>" --print       # echo slug only; do NOT create folder
adk-task-slug "<prompt>" --date        # date-prefix the slug
```

### `adk-mcp-health`

```bash
adk-mcp-health             # full report (workspace + shipped + env vars)
adk-mcp-health --workspace # workspace connectors only
adk-mcp-health --shipped   # adk-shipped MCPs only
adk-mcp-health --env       # env-var presence only
adk-mcp-health --json      # machine-readable JSON
```

## Templates

`skills/setup/templates/*.md` — starter `~/.config/adk/<topic>.md` for each topic. The `setup` skill copies them into place and opens for editing.


| Topic       | Owner skill(s)                                                                                |
| ----------- | --------------------------------------------------------------------------------------------- |
| `info`      | all (operator profile)                                                                        |
| `repos`     | all (repo → folder mapping)                                                                   |
| `github`    | `adk-review:*`, `adk-docs:docs-pr-description`, `investigate-deploy`, incident/RCA            |
| `datadog`   | `investigate-datadog`, incident/experiment/RCA, `code-perf`                                   |
| `mixpanel`  | `investigate-mixpanel`, `investigate-experiment`, optional RCA user-impact pass               |
| `statsig`   | `investigate-statsig`, `investigate-experiment`, `investigate-rca`                            |
| `snowflake` | `adk-investigate:investigate-snowflake`                                                       |
| `slack`     | `adk-investigate:investigate-incident`, `investigate-rca`                                     |
| `review`    | `adk-review:*`                                                                                |
| `docs`      | `adk-docs:*`, `adk-docs:docs-publish-*`                                                       |


## Agents


| Agent              | Persona                                                    | Used by                 |
| ------------------ | ---------------------------------------------------------- | ----------------------- |
| `dispatcher`       | Coordinator that spawns parallel subagents per skill chain | `auto`                  |
| `prompt-expander`  | Linguistic + entity-resolution helper                      | `auto`, `prompt-expand` |
| `context-gatherer` | Multi-source link follower                                 | `context-gather`        |


## Installation

```text
/plugin install adk-core@adk
/reload-plugins
/adk-core:setup
```

`adk-core` is auto-installed as a dependency of every other adk plugin, so you can usually skip the explicit install.

## Repo layout

```
adk-core/
├── .claude-plugin/plugin.json
├── README.md                     # this file
├── hooks/
│   ├── hooks.json
│   └── banner.sh
├── bin/
│   ├── adk-info                  # Node
│   ├── adk-task-slug             # Bash
│   └── adk-mcp-health            # Bash
├── agents/
│   ├── dispatcher.md
│   ├── prompt-expander.md
│   └── context-gatherer.md
└── skills/
    ├── auto/{SKILL.md, references/*.md}
    ├── prompt-expand/{SKILL.md, references/*.md}
    ├── setup/{SKILL.md, references/*.md, templates/*.md}
    ├── config-update/{SKILL.md, references/*.md}
    ├── info/{SKILL.md, references/*.md}
    ├── temp-folder/{SKILL.md, references/*.md}
    ├── mode-contract/{SKILL.md, references/*.md, scripts/parse-mode.sh}
    └── context-gather/{SKILL.md, references/*.md}
```

