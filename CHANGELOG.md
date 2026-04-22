# Changelog

All notable changes to the `adk` Claude Code plugin will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Per the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference#version-management), the version in `.claude-plugin/plugin.json` is what Claude Code uses to detect updates — bump it whenever you ship changes.

## [Unreleased]

### Added

- Explicit component path declarations in `.claude-plugin/plugin.json` for `skills`, `agents`, `hooks`, `mcpServers`, and `monitors` (matches the [Plugin manifest schema](https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema)).
- `adk-npm` plugin entry in `.claude-plugin/marketplace.json` so users can install ADK from the npm registry (`source: { source: "npm", package: "agents-devkit" }`) and pin a semver version, in addition to the default `adk` entry that tracks the latest commit on `main` via `source: { source: "github", repo: "sujeet-pro/agents-devkit" }`.
- `bin/canonical/system-prompt.md` — the canonical ADK primer that the `SessionStart` hook injects into every session. Single source of truth.
- `SessionStart` hook of type `command` that `cat`s `${CLAUDE_PLUGIN_ROOT}/bin/canonical/system-prompt.md`. This is the [supported plugin path](https://code.claude.com/docs/en/plugins-reference#hooks) for adding plugin-level context to every session — Claude Code captures the stdout of `SessionStart` `command` hooks and adds it to the conversation.
- Local-marketplace install path (`/plugin marketplace add ~/code/agents-devkit`) documented in both `README.md` and `docs/guide/getting-started/installation.md` for contributors.
- `claudePlugin` block in `package.json` pointing at the manifest and marketplace files.
- `CHANGELOG.md` (this file) — listed in the [standard plugin layout](https://code.claude.com/docs/en/plugins-reference#standard-plugin-layout).

### Changed

- Marketplace `source` for the `adk` plugin moved from the (invalid) string shorthand `"github:sujeet-pro/agents-devkit"` to the documented object form `{ "source": "github", "repo": "sujeet-pro/agents-devkit" }`.
- `SessionStart` hook no longer scoped to `matcher: "compact"` — it now fires on every session start (`startup`, `resume`, `compact`).
- Doc concept pages (`docs/concepts/hooks.md`, `mcp.md`, `agents.md`) rewritten to reflect the current single-Claude-plugin shape (the previous text described a now-removed per-runtime split into `hooks/claude.json`, `agents-claude/`, `mcp-config/servers/*.json`).

### Fixed

- `marketplace.json` `source` field is now schema-correct per the [Plugin sources spec](https://code.claude.com/docs/en/plugin-marketplaces#plugin-sources). The previous form failed to install in modern Claude Code.

## [1.0.0] - 2026-04-22

### Added

- Initial Claude Code plugin packaging (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`).
- 59 skills under `skills/<name>/SKILL.md`.
- 10 subagents under `agents/<role>.md`.
- Hook configuration at `hooks/hooks.json` covering `PreToolUse:Bash` (block dangerous shell), `PostToolUse:Edit|Write` (validate `SKILL.md` frontmatter), `Stop` (enforce four-phase validator), and `SessionStart` (banner).
- MCP server registry at `.mcp.json` for `github`, `bitbucket`, `jira`, `confluence`, `google-drive`, `slack`, `gmail`, `datadog`, `mixpanel`, `chrome-devtools`, `cursor-ide-browser`, `playwright`, and `brainstorming`.
- Background monitor at `monitors/monitors.json` (`ci-status`, fired on `cicd-monitor` skill invocation).
- Plugin-level defaults at `settings.json` (`subagentStatusLine`).
- Bundled CLI scripts in `bin/` (auto-added to the Bash tool's PATH per the [`bin/` spec](https://code.claude.com/docs/en/plugins-reference#file-locations-reference)): `adk-setup`, `adk-install`, `adk-mcp-install`, `adk-update-memory`, `adk-doctor`, `adk-validate`, `adk-sync-contracts`.
- `agents-skills/adk-<name>` symlink farm so the same skills are reachable from non-Claude harnesses (Cursor, Codex, Gemini, Antigravity) via `npx skills add`.
