# adk — agents-devkit

A single-repo, multi-agent skill kit for Principal Engineer workflows: implement, review, investigate, document, sync — composed with an advisor-strategy wrapper and a self-improving decision-log loop.

> **Marketplace? No.** v3 installs directly to the active agent(s) at user level via `./install.sh`. No plugin registry, no `/plugin install`. Clone the repo, run install, the skills appear in your agent.

## Supported agents

| Agent | Status | What's installed |
|---|---|---|
| Claude Code | full | skills, agents, slash commands, MCPs, `CLAUDE.md` global pointer |
| Cursor | full | rules (`.mdc`), MCP config, global rules pointer |
| Codex (OpenAI CLI) | partial | prompts, MCP entries in `~/.codex/config.toml`; see `agents-codex/README.md` for gaps |
| Junie (JetBrains AI) | partial | `~/.junie/guidelines.md` append; see `agents-junie/README.md` for gaps |

## Install

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
./install.sh                  # autodetects installed agents and wires them up
./install.sh --target claude  # only one
./install.sh --target all     # try every supported agent regardless of detection
./install.sh --uninstall      # removes by marker, leaves your overrides
```

After install, fill in `~/.agents-devkit/config/overrides.yaml` (created by `./install.sh` if missing). See `SETUP.md` for env-var requirements.

## Skills

```text
/adk-implement   write code from any input (Jira / GH issue / Slack / TDD / Confluence / freeform)
/adk-review      lightweight review of any target (PR URL / local / doc / comment thread / whole repo)
/adk-pr-review   deep PR review with worktree + LanceDB embeddings + SCIP + feature-flow tracing
                 (GitHub + Bitbucket Cloud; requires ollama + optional scip-* binaries)
/adk-pr-reviews  batch driver — reads a CSV of PR URLs, runs N reviews in parallel; skips merged
                 + stable rows. Designed for periodic execution (cron-friendly).
/adk-investigate query 3P data sources (Datadog / Mixpanel / Statsig / Snowflake / Looker / Atlassian)
/adk-document    generate any written artifact (RCA / ADR / runbook / PR body / commit msg / diagram / report)
/adk-sync        bidirectional bridge to 3P (Confluence / Jira / GDoc / GH PR body / Slack)
/adk-setup       bootstrap overrides, enrich metadata, verify env+MCPs
/adk-improve     read decision logs → propose default updates; refresh metadata
/adk-explain     advisor agent for "I don't know which to pick"
```

Each skill is task-based and polymorphic on input. Internal sub-flows are file-referenced (lazy-loaded). Every skill goes through a mandatory **question-first** phase that doubles as training data for the self-improvement loop.

## Key concepts

- **One source of truth for user data:** `~/.agents-devkit/config/overrides.yaml` — workspaces, repos, data dictionaries (Snowflake/Looker/Mixpanel tables and columns), defaults, RAG config.
- **Project-scoped overrides:** `<repo>/.adk/overrides.yaml` + `<repo>/ai-guidelines/` (or `docs/`).
- **Two task-folder roots** (see `shared/paths.md`): repo-bound skills write under `<repo>/.temp/adk/<skill>/<task>/`; global skills (pr-review, investigate, sync, …) write under `~/.agents-devkit/<area>/<task>/`. The latter root is created by `install.sh`.
- **Self-improving:** every Q&A and override is logged; `/adk-improve` reads logs and proposes updated defaults that get applied to `~/.agents-devkit/config/overrides.yaml` after you confirm.
- **Metadata cache:** `~/.agents-devkit/improve/metadata/<source>.json` — built by `/adk-setup --enrich` and refreshed by `/adk-improve --metadata`. Skills consult it instead of re-introspecting on every run.
- **RAG optional:** drop an `RAG_MCP_URL` into env, set `rag.enabled: true` in overrides, and every skill's context-gather phase pulls company knowledge alongside MCP results.

## Honest limits

- macOS primary; Linux works. Windows unsupported.
- GitHub and Bitbucket Cloud supported (Bitbucket via `adk-mcp-bitbucket` + REST). GitLab and Bitbucket Server are not in scope.
- Codex and Junie are shipped with the gaps documented; full feature parity is Claude + Cursor.
- Slack support requires `SLACK_CREDENTIALS_FILE` to be a shell-sourceable file exporting `SLACK_BOT_TOKEN` and/or `SLACK_USER_TOKEN`.

## Where to read next

- `AGENTS.md` — how prompts get routed (read first if you're an agent).
- `SETUP.md` — env vars + install walkthrough (read first if you're a human).
- `shared/constitution.md` — universal rules.
- `skills/adk-*/SKILL.md` — per-skill specs.
