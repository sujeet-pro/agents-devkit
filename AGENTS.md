# DevKit

This repository contains the DevKit multi-agent skills pack: shared skills, agents, guidelines, scripts, and platform adapters for Claude, Cursor, Codex, OpenCode, Gemini, and related coding agents.

## Project Structure

```text
claude-devkit/
├── .claude-plugin/         # Claude plugin + marketplace metadata
├── .cursor-plugin/         # Cursor plugin metadata
├── .codex/                 # Codex install instructions
├── .opencode/              # OpenCode install docs + plugin bridge
├── agents/                 # Shared agent definitions
├── lib/                    # Shared Node.js utilities
├── profiles/               # Repo-type detection rules
├── repo-configs/           # Per-repo instruction templates
├── scripts/                # Validation, setup, sync, and model helpers
├── settings/               # Claude-specific settings + MCP routing docs
├── skills/                 # Shared skill library used by all platforms
│   └── _references/        # Shared reference docs, guidelines, and diagram specs
├── manifest.json           # Upstream source tracking (copy/ref)
└── install.zsh             # Idempotent installer
```

## Naming

- Use short, searchable skill names.
- Prefer frontmatter descriptions that start with `Use when...`.
- Keep descriptions focused on triggering conditions, not the whole workflow.
- Use the working namespace `devkit` for any platform-specific packaging.
- Cross-reference other skills with the `/devkit:` prefix.

## Adding Or Updating Skills

1. Create or update `skills/<skill-name>/SKILL.md`.
2. Keep the name user-friendly and the description short enough for agent discovery.
3. If the skill depends on external tooling, add or update the corresponding checks in `scripts/check-skill-deps.zsh`.
4. If the skill needs helper files, keep them in the same skill directory or in a clearly shared reference directory such as `skills/_references/`.
5. Add the skill to `settings/base-settings.json` contextInstructions.
6. Update README/install docs if the skill changes the public catalog or prerequisites.

## Adding Agents

1. Create or update a single Markdown file under `agents/`.
2. Keep the frontmatter concise and tool lists realistic.
3. Avoid agent names that are platform-specific unless the agent really is platform-specific.

## Adding Guidelines

1. Create in `skills/_references/guidelines/<category>/<name>.md`.
3. Cite authoritative sources (specs, official docs) over blog posts.

## Adding Platform Support

1. Put thin platform-specific metadata or bootstrap logic in a hidden top-level folder:
   - `.claude-plugin/`
   - `.cursor-plugin/`
   - `.codex/`
   - `.opencode/`
   - `gemini-extension.json`
2. Keep the skills themselves in shared root folders instead of duplicating them per platform.
3. If a platform needs tool mapping or bootstrap text, point it at `skills/use/`.

## Upstream Sources

DevKit tracks upstream sources in `manifest.json`:

- **Copy sources** (diagramkit, superpowers): Files are copied into this repo and can be updated via `scripts/sync-sources.zsh`.
- **Ref sources** (pagesmith): Skills reference upstream content but are authored locally.

## Node.js Utilities

Shared utilities live in `lib/` with a `package.json` for dependency management. Run `scripts/setup-node.zsh` to install. The installer calls this automatically.

## .temp Folder

Skills produce intermediary artifacts (plans, drafts, research notes) in `.temp/` at the working directory root. This directory is gitignored. Plans use checkbox steps for resume capability.

## MCP And Tooling Conventions

- Skills that require MCP access must validate the relevant environment or config first.
- Skills that require local CLIs should point to `scripts/check-skill-deps.zsh <skill-name>` before they rely on them.
- Scripts must start with `#!/usr/bin/env zsh` and use `set -euo pipefail`.
- Keep scripts portable across macOS and Linux where possible.

## Git Rules

- Use the system git identity.
- Do not change `git config` user settings in this repo.
- Do not add `Co-Authored-By` trailers.

## Testing

Use the smallest relevant validation loop for the change:

```bash
zsh scripts/check-prerequisites.zsh
zsh scripts/check-env.zsh
zsh scripts/check-skill-deps.zsh <skill-name>
zsh install.zsh --list
```

For platform packaging changes, also validate the affected manifest files and install docs.
