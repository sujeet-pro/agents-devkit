# Agent Development Kit (ADK)

> A Claude Code plugin shipping 50+ composable, self-contained, highly-interactive skills covering the full developer loop. Built for [Claude Code](https://code.claude.com) and Claude Desktop.

`adk` is a [Claude Code plugin](https://code.claude.com/docs/en/plugins) (`.claude-plugin/plugin.json`) packed with skills for discovery, brainstorm, requirements, scoping, planning, design, frontend (with 5-sample mockups), build, review, browser-based validation, docs (wraps [pagesmith](https://github.com/sujeet-pro/pagesmith) + [diagramkit](https://github.com/sujeet-pro/diagramkit)), audits, publishing (`gh` CLI everywhere), CI/CD monitor + auto-fix, and observability (Datadog, Mixpanel).

Every skill:

- Is **highly interactive by default**, with explained options and approval gates. Pass `--auto` for unattended runs.
- Supports `--mode review | fix | auto` where applicable.
- Is **fully self-contained**: every reference file ships inside the skill folder, including a byte-identical copy of `interaction-contract.md`.
- Writes intermediate artifacts under `.temp/task-<slug>/`.

The plugin also ships:

- **10 specialized subagents** under `agents/` (research, dispatcher, brainstorm-facilitator, code-reviewer, debugger, doc-writer, implementer, plan-reviewer, security-reviewer, test-engineer).
- **Lifecycle hooks** at `hooks/hooks.json` — Pre/Post tool gates, Stop validators, and a `SessionStart` primer.
- **MCP server registry** at `.mcp.json` — GitHub, Bitbucket, Jira, Confluence, Drive, Slack, Gmail, Datadog, Mixpanel, Chrome DevTools, Playwright, brainstorming.
- **Background monitors** at `monitors/monitors.json` — `gh pr checks --watch` for `cicd-monitor`.
- **Plugin defaults** at `settings.json` (subagent status line).

## Install

ADK is distributed as a Claude Code plugin via the marketplace at `.claude-plugin/marketplace.json`. The marketplace exposes three install paths (all use the same `/plugin install` flow inside Claude Code):

1. **Marketplace + GitHub source** — tracks `main`, refreshed on `/plugin marketplace update`.
2. **Marketplace + local clone** — point the marketplace at a local checkout so your edits are live and refreshable through the standard `/plugin` lifecycle.
3. **Marketplace + npm source** — install the plugin from the [`agents-devkit`](https://www.npmjs.com/package/agents-devkit) npm package and pin to a semver release.

A fourth, dev-only path uses `claude --plugin-dir` to load the plugin directly without registering a marketplace.

### Path 1 — From the marketplace (GitHub, tracks `main`) — recommended

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

The default `adk` entry uses a `github` plugin source with no pinned `ref`/`sha`, so it always tracks the latest commit on `main`. Refresh with:

```text
/plugin marketplace update sujeet-pro-adk
/reload-plugins
```

### Path 2 — From a local clone (contributors / live edits)

Clone the repo and add it as a **local marketplace** so the standard `/plugin install`, `/plugin update`, `/plugin disable`, and `/plugin uninstall` commands all operate on your working tree.

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
```

```text
# Inside Claude Code, point the marketplace at the local clone:
/plugin marketplace add ~/code/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

After editing skills, agents, hooks, MCP, or monitors in the clone:

```text
/reload-plugins
```

After `git pull`:

```text
/plugin marketplace update sujeet-pro-adk
/reload-plugins
```

The marketplace name (`sujeet-pro-adk`) is read from `.claude-plugin/marketplace.json`, so the install command is identical across Path 1 and Path 2 — only the **source** of the marketplace is different.

### Path 3 — From the npm registry (semver-pinned)

The marketplace also exposes an `adk-npm` entry whose source is the [`agents-devkit`](https://www.npmjs.com/package/agents-devkit) npm package. Use this when you want a pinned, reproducible install instead of tracking `main`.

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk-npm@sujeet-pro-adk
/reload-plugins
```

Behind the scenes Claude Code runs `npm install` against the public npm registry. To pin an exact version, install through the interactive `/plugin` UI (which lets you set version constraints) or via the CLI:

```bash
claude plugin install adk-npm@sujeet-pro-adk
```

### Path 4 — Direct (`--plugin-dir`, no marketplace)

For one-off plugin development against a clone, without registering a marketplace:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
claude --plugin-dir "$(pwd)"
```

See [`docs/guide/getting-started/installation.md`](docs/guide/getting-started/installation.md) for the full guide, including MCP env-var setup and the non-interactive `claude plugin` CLI for CI.

## First skill

```text
/adk:auto    Build me a feature that lets users export their data as CSV. Source: JIRA-1234.
```

`/adk:auto` reads the prompt, gathers context (Jira / Confluence / Slack / GDocs / Gmail via MCP if links present), runs requirements + scoping with you, then dispatches the right downstream skills (build, test, browser validation, PR, CI monitor) as parallel subagents.

If you already know the skill: `/adk:plan-brainstorm`, `/adk:review-pr`, `/adk:audit-repo`, etc.

## Skill catalog

50+ skills across 11 layers — full list in [`skills-manifest.json`](skills-manifest.json) (regenerated by `npm run validate`). Highlights:

- **Meta** — `auto`, `setup`, `temp-folder`, `mode-contract`
- **Discovery** — `context-gather` (Jira/Confluence/Slack/GDocs/Gmail), `requirements`, `scoping`, `plan-research`
- **Plan** — `plan-brainstorm`, `plan-spec`, `plan-design`, `plan-roadmap`, `plan-proposal`
- **Frontend** — `frontend-design` (5-sample mockups), `frontend-mockup`, `frontend-feature`, `frontend-react-csr`
- **Build** — `build-feature`, `build-bugfix`, `build-refactor`, `build-migrate`, `build-test`, `build-deps`
- **Review** — `review-pr`, `review-local`, `review-feedback`, `review-doc`, `validate-browser`
- **Docs** — `docs-write`, `doc-site-setup` (wraps pagesmith), `doc-site-diagrams` (wraps diagramkit), `visualize-diagram`, `visualize-chart`
- **Audit** — `audit-repo`, `audit-site`, `audit-pr`
- **Publish** — `publish-commit`, `publish-github`, `publish-bitbucket`, `publish-confluence`, `publish-gdrive`, `cicd-monitor`, `cicd-fix`
- **Observability** — `observability-datadog`, `analytics-mixpanel`, `observability-incident`
- **Bootstrap** — `adopt-ai-in-repo`, `personal-skill-create`

## Repo layout

| Path | Purpose |
| --- | --- |
| `.claude-plugin/plugin.json` | Plugin manifest (`name: "adk"`) |
| `.claude-plugin/marketplace.json` | Marketplace catalog with the `adk` entry |
| `skills/<name>/SKILL.md` | All skills, bare folder names, no `adk-` prefix |
| `agents/<role>.md` | Specialized subagents (Markdown + YAML frontmatter) |
| `hooks/hooks.json` | Pre/Post tool, Stop, SessionStart hooks |
| `.mcp.json` | Bundled MCP server registry (`${ENV_VAR}` placeholders) |
| `monitors/monitors.json` | Background monitors |
| `settings.json` | Plugin-level Claude defaults |
| `bin/` | Repo CLI scripts (validator, contract sync, internal helpers) |
| `bin/canonical/` | Single source of truth for the interaction contract and `SessionStart` primer |
| `docs/`, `gh-pages/` | Pagesmith docs site source + built output |

See [`CLAUDE.md`](CLAUDE.md) for the canonical contract any agent working **on** this repo should follow.

## License

MIT
