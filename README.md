# Agents Dev Kit — a Claude Code plugin marketplace

A focused, Claude-optimized engineering toolkit, packaged as a **single-plugin Claude Code marketplace**. Install it and you get five self-contained skills, a set of tailored sub-agents, and pre-wired (env-gated) MCP servers.

Every skill is **self-contained** (its whole contract lives in its own folder), ships its **own phased workflow and tailored persona**, and uses the **Workflow tool** to fan out the heavy steps (multi-dimension review, multi-source investigation) with adversarial verification.

## Install

In Claude Code:

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@agents-devkit
```

Then invoke any skill with its namespaced command:

```text
/adk:review <pr-url | . | path | doc>
/adk:pr-review <github-pr-url>
/adk:implement <jira | gh-issue | "build the X">
/adk:investigate <symptom | datadog-url | slack-alert>
/adk:document <intent> --type <runbook|adr|rca|pr-body|...>
```

Skills also auto-trigger by intent (e.g. "review this PR", "why is checkout slow") — the namespaced command is just the explicit way.

## The skills

| Skill | What it does |
|---|---|
| `review` | Lightweight, polymorphic review of a PR / local diff / doc / thread. Six dimensions, severity-tiered findings with `file:line` evidence. Read-only by default; `--fix` applies + pushes after confirmation. |
| `pr-review` | Heavyweight, **GitHub-only** deep PR review: a read-only `git worktree` at the PR head, cross-file context, a Workflow that fans out one agent per dimension + feature-flag tracing + adversarial verification, then posts inline comments via the `gh` CLI. Never merges. |
| `implement` | Build a change from a Jira ticket / GitHub issue / Slack thread / freeform prose. Plans before it acts, writes the smallest correct change with tests, validates with the repo's own tooling. |
| `investigate` | Read-only multi-source RCA: pins an explicit window, fans out one agent per data source (Datadog / Slack / Statsig / Mixpanel / Snowflake / Looker / deploys), requires ≥2 agreeing signals before naming a root cause. |
| `document` | Draft any markdown artifact (runbook / ADR / RCA / PR body / migration guide / …), reader-first and cited. Drafts locally; never publishes. |

## The agents

Tailored sub-agents the skills' workflows spawn: `code-reviewer`, `security-auditor`, `test-engineer`, `implementer`, `investigator`, `doc-writer`, `context-gatherer`. Each is a sharp, single-role worker — see `plugins/adk/agents/`.

## How it talks to the outside world

- **GitHub** — the **`gh` CLI only** (`gh pr view/diff/review`, `gh api`). Run `gh auth login` first.
- **git** — used **directly** (`git`) for commits, branches, worktrees.
- **Cloning** — **SSH only** (`git clone git@github.com:owner/repo.git`). No HTTPS clones.
- Bitbucket / GitLab / self-hosted forges are **out of scope** — GitHub only.

## MCP servers + required env vars

The plugin ships `.mcp.json` with these servers. Each is **opt-in via environment variables** — set the ones for the data sources you use; the rest stay dormant. None are required for the core code skills (`review`, `pr-review`, `implement` use `gh`/`git`).

| MCP server | Used by | Environment variables |
|---|---|---|
| `datadog` | investigate | `DATADOG_API_KEY`, `DATADOG_APP_KEY` |
| `atlassian` | implement, document, investigate, pr-review | `ATLASSIAN_SITE`, `ATLASSIAN_USERNAME`, `ATLASSIAN_API_TOKEN` (needs `uvx`) |
| `slack` | investigate, implement | `SLACK_BOT_TOKEN`, `SLACK_USER_TOKEN` (needs `npx`) |
| `statsig` | pr-review, investigate | `STATSIG_CONSOLE_API_KEY` |
| `mixpanel` | investigate | OAuth on first use — no env vars |
| `snowflake` | investigate | `SNOWFLAKE_CONNECTION_NAME`, `SNOWFLAKE_ACCESS_TOKEN`, `SNOWFLAKE_SERVICE_CONFIG_FILE`, `SNOWFLAKE_HOME` (needs `uvx`) |
| `looker` | investigate | `LOOKER_BASE_URL`, `LOOKER_CLIENT_ID`, `LOOKER_CLIENT_SECRET` (needs `uvx`) |
| `google` | document, investigate | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `USER_GOOGLE_EMAIL`, `GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR` (needs `uvx`) |

Set these in your shell environment before launching Claude Code; `.mcp.json` expands `${VAR}` at connection time. A server whose env vars are unset simply won't connect, and the skills degrade honestly (they mark the source as skipped).

### Prerequisites

- [`gh`](https://cli.github.com/) (authenticated: `gh auth login`)
- `git` with an SSH key configured for GitHub
- `uvx` (from [`uv`](https://docs.astral.sh/uv/)) for the Atlassian / Snowflake / Looker / Google MCP servers
- `npx` (Node) for the Slack MCP server

## Repository layout

```
.claude-plugin/marketplace.json     # the marketplace (one plugin: adk)
plugins/adk/
├── .claude-plugin/plugin.json      # plugin manifest
├── .mcp.json                       # env-gated MCP servers
├── agents/                         # tailored sub-agents
└── skills/<skill>/                 # one self-contained folder per skill
    ├── SKILL.md                    # entry point + frontmatter
    ├── persona.md                  # the skill's tailored voice
    ├── workflow.md                 # phased process + Workflow orchestration
    ├── rules.md                    # hard rules, refusals, safety
    └── …                           # dispatch / dimensions / types as needed
```

> The previous Textual TUI and `adk` CLI (queue, embeddings/SCIP pipeline, multi-host installers) live on the [`adk-cli`](https://github.com/sujeet-pro/agents-devkit/tree/adk-cli) branch. `main` is the marketplace.

## License

MIT — see [LICENSE](LICENSE).
