# Agent Development Kit (ADK)

> A Claude Code plugin shipping 50+ composable, self-contained, highly-interactive skills covering the full developer loop. Also installable via npm, repo clone, or `npx skills` for Cursor, Codex, Gemini, and Antigravity.

`adk` is a Claude Code plugin (`.claude-plugin/plugin.json`) packed with skills for discovery, brainstorm, requirements, scoping, planning, design, frontend (with 5-sample mockups), build, review, browser-based validation, docs (wraps [pagesmith](https://github.com/sujeet-pro/pagesmith) + [diagramkit](https://github.com/sujeet-pro/diagramkit)), audits, publishing (`gh` CLI everywhere), CI/CD monitor + auto-fix, and observability (Datadog, Mixpanel).

Every skill:

- Is **highly interactive by default**, with explained options and approval gates. Pass `--auto` for unattended runs.
- Supports `--mode review | fix | auto` where applicable.
- Is **fully self-contained**: every reference file ships inside the skill folder, including a byte-identical copy of `interaction-contract.md`.
- Writes intermediate artifacts under `.temp/task-<slug>/`.

## Install

> Whichever path you pick, finish with **`/adk:setup`** (Claude) or **`npx adk`** (any other harness) to install CLI deps, register MCP servers, and write the managed block into your user-level memory file.

### 1. Claude Code plugin (primary)

```text
# In Claude Code:
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
/adk:setup            # interactive — wires MCP, CLI deps, and user memory
```

Local development against a clone:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install
claude --plugin-dir "$(pwd)"
```

### 2. npm module (works for every harness)

Useful when you want a pinned version, are not on Claude Code yet, or are driving setup from a non-Claude harness.

```bash
# One-shot
npx --yes agents-devkit adk

# Project-pinned (CI-friendly)
npm install --save-dev agents-devkit && npx adk

# Global
npm install -g agents-devkit && adk
```

`adk` (alias for `adk-setup`) auto-detects which agents are installed — Claude Code, Claude Desktop, Cursor, Codex CLI, Gemini CLI, Antigravity — and:

- symlinks every `agents-skills/adk-<name>` folder into the right per-agent skill directory,
- registers MCP servers via `claude mcp add` (when Claude is present),
- updates the user-level memory file for each detected harness so each one auto-discovers ADK.

Per-step CLIs:

```bash
npx adk-install                # symlink skill folders into detected harnesses
npx adk-mcp-install            # register MCP servers from .mcp.json
npx adk-update-memory          # write managed block into ~/.claude/CLAUDE.md etc.
npx adk-doctor                 # health check
```

### 3. Clone + symlink (for contributors)

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
npm install
node bin/adk-setup            # same as `/adk:setup` and `npx adk`
```

Symlinks point back at the clone, so `git pull` instantly refreshes every linked harness and local skill edits show up live.

Selective install:

```bash
node bin/adk-install --target cursor                  # only Cursor
node bin/adk-install --target cursor,codex            # multiple
node bin/adk-install --mode project                   # link into <cwd>/.cursor/skills/ etc.
node bin/adk-install --dry-run

node bin/adk-update-memory --target claude            # only ~/.claude/CLAUDE.md
node bin/adk-update-memory --remove                   # remove the managed block
```

macOS only.

### 4. `npx skills add` (skills only)

The third-party [`skills`](https://skills.sh) loader picks up the `agents-skills/adk-<name>` folders. **Subagents, hooks, MCP servers, monitors, and the user-memory wiring are NOT installed via this path** — use one of the paths above for the full kit.

```bash
npx skills add sujeet-pro/agents-devkit
npx skills add sujeet-pro/agents-devkit -a claude-code
npx skills add sujeet-pro/agents-devkit -s adk-plan-brainstorm -s adk-review-pr
```

## First skill

```text
/adk:auto    Build me a feature that lets users export their data as CSV. Source: JIRA-1234.
```

`/adk:auto` reads the prompt, gathers context (Jira / Confluence / Slack / GDocs / Gmail via MCP if links present), runs requirements + scoping with you, then dispatches the right downstream skills (build, test, browser validation, PR, CI monitor) as parallel subagents.

If you already know the skill: `/adk:plan-brainstorm`, `/adk:review-pr`, `/adk:audit-repo`, etc.

## Skill catalog

59 skills across 11 layers — full list in [`skills-manifest.json`](skills-manifest.json). Highlights:

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

See [`AGENTS.md`](AGENTS.md) for the canonical map and [`CLAUDE.md`](CLAUDE.md) for the Claude-specific delta.

## License

MIT
