# Changelog

All notable changes to the `adk` Claude Code plugin will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Per the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference#version-management), the version in `.claude-plugin/plugin.json` is what Claude Code uses to detect updates — bump it whenever you ship changes.

## [Unreleased]

### Added

- Re-introduced the `adk-npm` plugin entry in `.claude-plugin/marketplace.json` (`source: { source: "npm", package: "agents-devkit" }`) so users can install the plugin from the npm registry and pin to a semver release alongside the GitHub-tracking `adk` entry. See the [npm plugin source spec](https://code.claude.com/docs/en/plugin-marketplaces#npm-packages).
- Re-introduced `.github/workflows/publish.yml` for OIDC trusted publishing of the `agents-devkit` npm package, simplified for the Claude-only plugin layout (drops the deleted multi-harness installer dry-run gate; adds an automatic version sync into `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` so plugin and npm versions never diverge).
- README and `docs/guide/getting-started/installation.md` rewritten to surface three install paths side-by-side: marketplace+GitHub (tracks `main`), marketplace+local-clone (live edits), marketplace+npm (semver-pinned).

### Changed

- `package.json` is publishable again: removed `private: true`, added a `files` allowlist of plugin components.

## [1.1.0] - 2026-04-22

### Changed

- **Claude-only refocus.** ADK is now distributed exclusively as a Claude Code plugin via the marketplace at `.claude-plugin/marketplace.json`. There is no `npx skills add` path and no parallel multi-harness installer. Two plugin sources are supported: `github` (tracks `main`) and `npm` (semver-pinned).
- `.claude-plugin/plugin.json` slimmed to the [default plugin layout](https://code.claude.com/docs/en/plugins-reference#standard-plugin-layout) — removed explicit `skills`, `agents`, `hooks`, `mcpServers`, `monitors` pointers (Claude Code auto-discovers them at the conventional locations).
- `bin/adk-validate` no longer enforces the `agents-skills/` symlink farm or the dual-form `@adk:foo / adk-foo` cross-reference convention. Cross-references are now plain `/adk:<skill>` form.
- `.claude/skills/prj-update-docs/` now ships the full skill content directly (no longer a pointer to `.agents/`).
- `skills/setup/SKILL.md` rewritten to drop references to the deleted multi-harness installer scripts. It is now a CLI-deps + shell-env health check only.
- Doc concept pages (`docs/concepts/{agents,hooks,mcp,memory-files}.md`) and `docs/guide/getting-started/installation.md` rewritten for the Claude-only shape.
- `package.json` slimmed: removed all `bin` entries, removed npm-install scripts (`install:local`, `install:mcp`, `install:memory`, `setup`, `doctor`). Kept docs build (`docs:dev`, `docs:build`, `docs:preview`) and validators (`validate`, `validate:sync`, `sync-contracts`, `skills:manifest`).
- CI workflow simplified — dropped the "Installer dry-run" job that ran the deleted Node CLI.

### Removed

- `.agents/`, `.codex/`, `.cursor/` repo-local skill mirrors and `agents-skills/` symlink farm — the only remaining repo-local skill is `.claude/skills/prj-update-docs/`.
- `bin/adk-install`, `bin/adk-mcp-install`, `bin/adk-update-memory`, `bin/adk-doctor`, `bin/adk-setup` — the multi-harness installer suite.
- `bin/internal/validate-content.mjs` — orphaned (referenced a missing `validate.mjs`).
- `AGENTS.md`, `GEMINI.md` — the canonical Claude memory file is `CLAUDE.md`.
- `REFERENCE.md`, `llms.txt` — outdated multi-harness reference docs.
- `node_modules/`, `package-lock.json` — re-generated on demand by `npm install` for the docs build.
- Multi-harness `bin/adk-install`, `bin/adk-mcp-install`, `bin/adk-update-memory`, `bin/adk-doctor`, `bin/adk-setup` — replaced by the Claude plugin host's native loading of skills, agents, hooks, MCP, and monitors.

## [1.0.0] - 2026-04-22

### Added

- Initial Claude Code plugin packaging (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`).
- 59 skills under `skills/<name>/SKILL.md`.
- 10 subagents under `agents/<role>.md`.
- Hook configuration at `hooks/hooks.json` covering `PreToolUse:Bash` (block dangerous shell), `PostToolUse:Edit|Write` (validate `SKILL.md` frontmatter), `Stop` (enforce four-phase validator), and `SessionStart` (banner).
- MCP server registry at `.mcp.json` for `github`, `bitbucket`, `jira`, `confluence`, `google-drive`, `slack`, `gmail`, `datadog`, `mixpanel`, `chrome-devtools`, `cursor-ide-browser`, `playwright`, and `brainstorming`.
- Background monitor at `monitors/monitors.json` (`ci-status`, fired on `cicd-monitor` skill invocation).
- Plugin-level defaults at `settings.json` (`subagentStatusLine`).
- Bundled CLI scripts in `bin/` (auto-added to the Bash tool's PATH per the [`bin/` spec](https://code.claude.com/docs/en/plugins-reference#file-locations-reference)).
- `bin/canonical/system-prompt.md` — the canonical ADK primer that the `SessionStart` hook injects into every session.
- `agents-skills/adk-<name>` symlink farm for non-Claude harnesses (removed in 1.1.0).
