---
name: manage-update
description: Use to update DevKit skills, agents, and guidelines from GitHub with automatic setup validation and platform-native reload
user_invocable: true
arguments:
  - name: dry-run
    description: "Preview changes without applying (default: false)"
    required: false
  - name: no-auto-install
    description: "Skip auto-installing missing tools after update (default: false — auto-install is ON)"
    required: false
  - name: refresh-mcp
    description: "Re-read ~/.zshenv and refresh MCP server configuration (default: false)"
    required: false
---

# Update DevKit

## Overview

Updates the DevKit installation by pulling the latest from GitHub, syncing upstream sources, and running setup validation. Works across all platforms — users always install via the official approach for their platform.

## Platform Install Paths

Detect which platform this is running on and locate the DevKit repo directory:

| Platform | DevKit Repo Location | How Users Install |
|----------|---------------------|-------------------|
| Claude Code | `~/.claude/plugins/marketplaces/devkit-marketplace` | `/plugin marketplace add sujeet-pro/agents-devkit` then `/plugin install devkit@devkit-marketplace` |
| Cursor | `~/.cursor/plugins/devkit` or Cursor plugin cache | `/add-plugin devkit` in Cursor |
| Codex CLI | `~/.devkit` | Clone to `~/.devkit`, symlink skills |
| Gemini CLI | Gemini extensions directory | `gemini extensions install https://github.com/sujeet-pro/agents-devkit` |
| OpenCode | OpenCode plugin cache (git-backed) | Add to `opencode.json` plugin array |

Resolution order:
1. `CLAUDE_DEVKIT_DIR` environment variable (if set)
2. Platform-specific path based on detected host
3. Fall back to the directory containing this skill (traverse up from SKILL.md to repo root)

## Preflight

1. Verify `git` is available
2. Verify internet connectivity (try `git ls-remote` on the repo)
3. Log: `Updating DevKit from GitHub...`
4. Log: `DevKit directory: <resolved-path>`
5. Log: `Platform: <detected-platform>`

## Update Flow

### 1. Git Pull

```bash
cd <devkit-dir>
git pull --ff-only
```

- If ff-only fails, warn: "Fast-forward pull failed. You may have local modifications. Consider: `git stash && git pull --ff-only && git stash pop`"
- Log each step so the user can see progress and stop if needed

### 2. Sync Upstream Sources

```bash
zsh scripts/sync-sources.zsh
```

Syncs copy-type sources (diagramkit, superpowers) and checks ref-type sources (pagesmith).

### 3. Node.js Dependencies

```bash
zsh scripts/setup-node.zsh
```

### 4. Platform Reload

After pulling updates, trigger the platform-specific reload:

| Platform | Reload Action |
|----------|---------------|
| Claude Code | Tell the user to run `/reload-plugins` to pick up changes. If the plugin was installed via marketplace, also suggest `/plugin update devkit@devkit-marketplace` |
| Cursor | Tell the user to restart Cursor or re-add the plugin |
| Codex CLI | Symlinks auto-reflect; no action needed |
| Gemini CLI | Tell the user to restart Gemini CLI |
| OpenCode | Tell the user to restart OpenCode |

### 5. Run Setup Validation

After the update, automatically run the `/devkit:manage-setup` flow:

- **Default**: auto-install mode is ON — missing required tools and packages will be installed automatically
- **If `no-auto-install=true`**: run in check-only mode, report what's missing without installing
- Log: `Running post-update setup validation (auto-install: ON)...`
- Log: `To skip auto-install, run: /devkit:manage-update no-auto-install=true`

The setup validation covers:
- CLI tools (required + recommended)
- npm packages
- MCP server connectivity
- If anything is missing, ask the user whether to install it (unless auto-install is on, in which case install and log)

### 6. MCP Configuration Refresh (when `refresh-mcp=true`)

When the user has updated environment variables in `~/.zshenv` (e.g., rotated API tokens):

1. Source `~/.zshenv` to pick up new values
2. Re-run the MCP server configuration from the `claude.json` template using `envsubst`
3. Write updated MCP entries to `~/.claude.json`
4. Log which servers were reconfigured
5. Validate connectivity for each reconfigured server

This is also triggered automatically if the update introduces new environment variables that aren't set.

## Dry Run

When `dry-run=true`:

- Run `git fetch` and show `git log HEAD..origin/main --oneline`
- Do not apply any changes
- Show what setup validation would check

## Output

Log each step in real time so the user can monitor progress:

```
## DevKit Update

[1/6] Git pull...
  Already up to date. | Pulled 3 new commits.

[2/6] Syncing upstream sources...
  diagramkit: synced (commit abc1234)
  superpowers: synced (commit def5678)
  pagesmith: checked (ref only, no changes)

[3/6] Node.js dependencies...
  Up to date.

[4/6] Platform reload...
  Claude Code: run /reload-plugins to apply changes.

[5/6] Setup validation (auto-install: ON)...
  CLI tools: 7/7 required OK, 2 recommended missing
  npm packages: 3/3 required OK
  MCP servers: 4/4 configured
  Installing missing: brew install sd yq... done.

[6/6] Complete.
  DevKit updated successfully.
```

## Adjacent Skills

- `/devkit:manage-setup` for standalone setup validation and tool installation
- `/devkit:manage-validate` for MCP-only validation
