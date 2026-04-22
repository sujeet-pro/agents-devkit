# Contributing to ADK

ADK is a single Claude Code plugin (`.claude-plugin/plugin.json`) distributed exclusively via the marketplace at `.claude-plugin/marketplace.json`. There is no npm publish path, no multi-harness installer, and no parallel runtime-specific source folders. Everything below assumes a clone of this repo and a recent Node.js for the docs build.

## Quick start

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install                 # only required for the docs site build
npm run validate            # bin/adk-validate — structural checks; regenerates skills-manifest.json
npm run validate:sync       # bin/adk-sync-contracts --check
npm run docs:build          # build gh-pages/ from docs/
```

Then load the plugin into Claude Code for live testing:

```bash
claude --plugin-dir "$(pwd)"
```

After editing any plugin component:

```text
/reload-plugins
```

## Repository layout

| Path | Contents |
| --- | --- |
| `.claude-plugin/plugin.json` | Plugin manifest (`name: "adk"`) |
| `.claude-plugin/marketplace.json` | Marketplace catalog (single `adk` plugin entry) |
| `skills/<name>/` | All skills, bare folder names. `SKILL.md` + flat `references/` |
| `agents/<role>.md` | Specialized subagents — Markdown + YAML frontmatter |
| `hooks/hooks.json` | Lifecycle hooks (Pre/Post tool, Stop, SessionStart) |
| `.mcp.json` | MCP server registry — `${ENV_VAR}` placeholders resolved by Claude Code from the user's shell env |
| `monitors/monitors.json` | Background monitors (`gh pr checks --watch`) |
| `settings.json` | Plugin defaults (`subagentStatusLine`) |
| `bin/canonical/` | Source of truth for the interaction contract and `SessionStart` primer |
| `bin/internal/` | `manifest.mjs`, `generate-skill-docs.mjs` |
| `bin/adk-validate`, `bin/adk-sync-contracts` | Repo CLI scripts (added to the Bash tool's `PATH` while the plugin is enabled) |
| `docs/`, `gh-pages/` | Pagesmith docs source + built site |
| `.claude/skills/prj-update-docs/` | Repo-local project skill (loaded as `/prj-update-docs` only when working in this repo) |

There are no `agents-skills/` symlinks, no `agents-cursor/`, no `agents-codex/`, no `mcp-config/`, no `global-prompts/`, no `cli/`. Everything lives where the [Claude plugin spec](https://code.claude.com/docs/en/plugins-reference) expects it.

## Hard rules for skills

- Skill folder name uses kebab-case (no `adk-` prefix). Skills are invoked as `/adk:<folder-name>`.
- Every `SKILL.md` has YAML frontmatter with `name` (matching the folder) and `description`. Other supported keys: see the [skills frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference).
- Body soft cap is 500 lines.
- `references/` is flat; no subdirectories.
- Every `references/<file>` cited in `SKILL.md` must exist on disk.
- The skill must accept `--auto`. Even routers that mostly hand off should mention `--auto` so the contract is visible.
- The skill must include `references/interaction-contract.md` as a byte-identical copy of `bin/canonical/interaction-contract.md`. Edit the canonical file and run `npm run sync-contracts` — never edit per-skill copies.

## Adding or updating a skill

1. Create `skills/<name>/` with `SKILL.md` and `references/`. Decide the **task token** (used to prefix reference filenames for migrated skills, e.g. `pr-` for `review-pr`). New skills can use bare reference names.
2. Author the `SKILL.md`: `When to use`, `When NOT to use`, `Inputs` (mark `--auto`), `Workflow` (numbered phases with explicit `Approval gate unless --auto` calls AND a `Validate (per validator.md)` step before the final report), `Output format`, `Anti-patterns`.
3. Author the standard reference set:
   - `how-it-works.md` (required) — mermaid diagram + decision flow
   - `modes.md` (required) — which `--mode review|fix|auto` this skill supports
   - `validator.md` (required, or `<task>-validator.md`) — the four-phase validator gate
   - `interaction-contract.md` (required) — synced from `bin/canonical/`
   - Optional: `persona.md`, `workflow.md`, `clarifying-questions.md`, `output-format.md`, `artifact-format.md`, `anti-patterns.md`, `examples.md`, `research-protocol.md`, `mcp-fallback.md`, `multi-repo.md`, `scripts/`
4. Run `npm run validate` and fix any error.
5. Update the catalog tables in `README.md` and `CLAUDE.md` if you changed the skill count or category map.
6. Run `npm run docs:build` to confirm the docs site still renders.

## Adding or updating a subagent

Subagents live at `agents/<role>.md` with Markdown + YAML frontmatter. See the [subagent frontmatter reference](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields).

> Note: plugin subagents do **not** support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields. They are silently ignored when loading agents from a plugin. Add the equivalent rules to `permissions.allow` in `settings.json` if you need them.

1. Write `agents/<role>.md` with at least `name` (matching the basename) and `description`.
2. Optional fields: `tools`, `disallowedTools`, `model`, `maxTurns`, `skills`, `memory`, `effort`, `background`, `color`.
3. Run `npm run validate`.

## Adding or updating a hook

1. Edit `hooks/hooks.json` directly. The format matches `.claude/settings.json` hooks; see the [hooks reference](https://code.claude.com/docs/en/hooks-guide#configure-hook-location).
2. Run `npm run validate` (parses the file as JSON).

## Adding or updating an MCP server

1. Add an entry under `mcpServers` in `.mcp.json` with `${ENV_VAR}` placeholders for any required secrets.
2. Include a `description` and document the required env vars in `docs/guide/getting-started/installation.md` under "Configure MCP servers".
3. Run `npm run validate` to confirm the file is valid JSON.

## Editing the interaction contract or system-prompt primer

1. Edit `bin/canonical/interaction-contract.md` (or `bin/canonical/system-prompt.md`).
2. Run `npm run sync-contracts` to propagate the new contract into every skill's `references/interaction-contract.md` byte-identically.
3. Run `npm run validate` to confirm the sync.

The `system-prompt.md` is read by the `SessionStart` hook in `hooks/hooks.json` (via `cat ${CLAUDE_PLUGIN_ROOT}/bin/canonical/system-prompt.md`) and injected into every Claude session.

## Validation commands

```bash
npm run validate            # spec-level: frontmatter, name match, references, manifest regen
npm run validate:sync       # confirm bin/canonical is propagated byte-identically
npm run sync-contracts      # propagate bin/canonical into every skill
npm run skills:manifest     # alternative manifest regen via bin/internal/manifest.mjs
npm run docs:skills         # regenerate docs/reference/skill-*.md mirrors from each SKILL.md
npm run docs:build          # docs:skills + pagesmith-docs build
```

## Release checklist

1. `npm run validate` — `0 errors`.
2. `npm run validate:sync` — `0 errors`.
3. `npm run docs:build` — confirm `gh-pages/` builds; commit it.
4. Bump `version` in `.claude-plugin/plugin.json` (and optionally `package.json`).
5. Update `CHANGELOG.md`.
6. `git tag v<version> && git push --tags`.
7. Claude Code clients tracking the marketplace pull updates via `/plugin marketplace update sujeet-pro-adk`.

## What this repo deliberately does NOT have

- No npm distribution. Distribution is exclusively via `.claude-plugin/marketplace.json`.
- No multi-harness installer. ADK targets Claude Code and Claude Desktop only.
- No `agents-skills/`, `agents-cursor/`, `agents-codex/`, or `agents-gemini/` symlink farms.
- No `mcp-config/servers/<server>.json` split — all MCP servers live in a single `.mcp.json`.
- No `global-prompts/` folder — the system-prompt primer is a single file at `bin/canonical/system-prompt.md` injected via the `SessionStart` hook.
- No Bash install script.
- No Python anywhere.

If you find a doc that mentions any of the above, it's stale — please fix it in the same PR as your change.
