# Contributing to DevKit

## Quick Start

```bash
# Clone the repo
git clone https://github.com/sujeet-pro/claude-devkit.git
cd claude-devkit

# Install for development (symlinks — edits reflect immediately)
zsh install.zsh

# Or install in copy mode (for testing without live edits)
zsh install.zsh --copy
```

## Project Structure

```
agents-devkit/
├── agents/              # Agent definitions (one .md per agent)
├── lib/                 # Shared Node.js utilities
│   └── src/             # ES module source files
├── profiles/            # Repo-type detection rules
├── scripts/             # Shell scripts for validation, setup, sync
├── settings/            # Claude-specific settings and MCP docs
├── skills/              # Skill library (one directory per skill)
│   └── _references/     # Guidelines, reference docs, diagram specs
│       ├── guidelines/  # Coding and document guidelines
│       ├── mermaid/     # Mermaid diagram syntax references
│       ├── excalidraw/  # Excalidraw JSON format references
│       └── drawio/      # Draw.io style references
├── .claude-plugin/      # Claude Code plugin metadata
├── .cursor-plugin/      # Cursor plugin metadata
├── .codex/              # Codex setup docs
├── .opencode/           # OpenCode setup docs
├── manifest.json        # Upstream source tracking (copy/ref)
└── install.zsh          # Idempotent installer
```

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: "Use when..."
   user_invocable: true
   arguments:
     - name: arg-name
       description: "..."
       required: true
   ---
   ```
2. Add preflight: `zsh scripts/check-skill-deps.zsh <skill-name>`
3. Reference `skills/_references/agentic-teams.md` if the skill uses child agents
4. Add the skill to `scripts/check-skill-deps.zsh` case statement
5. Add to `settings/base-settings.json` contextInstructions
6. Cross-reference with `/devkit:` prefix
7. Use `review-*` for comment-only review skills and `write-*` for direct drafting or revise-in-place skills

## Adding a Guideline

1. Create in `skills/_references/guidelines/<category>/<name>.md`
2. Update `skills/review-pr/SKILL.md` or `skills/write-doc/SKILL.md` guideline loading if applicable
3. Cite authoritative sources (specs, official docs) over blog posts

## Adding an Agent

1. Create `agents/<agent-name>.md` with YAML frontmatter:
   ```yaml
   ---
   name: agent-name
   description: "..."
   model: opus | sonnet
   tools:
     - Glob
     - Grep
     - Read
     - ...
   ---
   ```
2. Keep tool lists minimal and realistic

## Testing Changes

```bash
# Validate prerequisites
zsh scripts/check-prerequisites.zsh

# Validate environment
zsh scripts/check-env.zsh

# Check skill dependencies
zsh scripts/check-skill-deps.zsh <skill-name>

# List all installable items
zsh install.zsh --list

# Run the contributor improve skill
# (inside Claude Code, from this repo)
/improve
```

## Syncing Upstream Sources

DevKit tracks upstream sources in `manifest.json`:

- **Copy sources** (diagramkit, superpowers): Files are copied into this repo
- **Ref sources** (pagesmith): Skills reference upstream content

To sync:
```bash
zsh scripts/sync-sources.zsh              # Sync all copy sources
zsh scripts/sync-sources.zsh --source diagramkit  # Sync one source
zsh scripts/sync-sources.zsh --dry-run    # Preview changes
```

Or use the improve skill which handles sync as part of its audit.

## Platform Adapters

When making changes visible to end users, ensure consistency across:
- `.claude-plugin/plugin.json` — version, keywords
- `.cursor-plugin/plugin.json` — version, keywords
- `.codex/INSTALL.md` — references
- `.opencode/INSTALL.md` — references
- `gemini-extension.json` — version

## Conventions

- Scripts: `#!/usr/bin/env zsh` + `set -euo pipefail`
- Skill descriptions: start with "Use when..."
- Skill cross-references: use `/devkit:` prefix
- Git: use system identity, no Co-Authored-By trailers
- Intermediary artifacts: `.temp/` directory (gitignored)
- Plans: `.temp/plans/<plan-id>.md` with checkbox steps
