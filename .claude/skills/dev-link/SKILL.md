---
name: dev-link
description: Use when contributing to DevKit to symlink the current working directory as the active plugin for Claude Code, Cursor, Codex, Gemini, or OpenCode
user_invocable: true
arguments:
  - name: action
    description: "link (default) or unlink"
    required: false
  - name: platform
    description: "Target platform: all (default), claude, cursor, codex, gemini, opencode"
    required: false
---

# DevKit Contributor Link

Links the current working directory as the active DevKit plugin for development and testing. This replaces the marketplace/published version with a symlink so local edits are reflected immediately.

This skill is only available inside the DevKit repo (`.claude/skills/dev-link/`).

## Platform Paths

| Platform | Target Path (symlink destination) |
|----------|----------------------------------|
| Claude Code | `~/.claude/plugins/marketplaces/devkit-marketplace` |
| Cursor | `~/.cursor/plugins/devkit` |
| Codex CLI | `~/.devkit` |
| Gemini CLI | Gemini extensions directory for `agents-devkit` |
| OpenCode | OpenCode plugin cache for `devkit` |

## Link (default)

When `action=link` or no action specified:

1. Detect the current working directory (must contain `skills/` and `agents/` directories — abort if not a DevKit repo)
2. For each target platform (or the specified one):
   a. Check if the target path already exists
   b. If it's a directory (not a symlink), back it up: `mv <target> <target>.backup.<timestamp>`
   c. If it's already a symlink, remove it
   d. Create the symlink: `ln -s <cwd> <target>`
   e. Log: `Linked: <target> -> <cwd>`
3. For Claude Code specifically:
   - **Remove the `devkit@devkit-marketplace` entry from `~/.claude/plugins/installed_plugins.json`**: Claude Code discovers plugins from BOTH the marketplace directory scan AND the `installed_plugins.json` entries. If both exist, every skill loads twice (once as `skill-name`, once as `devkit:skill-name`). Removing the installed entry means the plugin is only discovered via the marketplace symlink.
   - Back up the original `installed_plugins.json` as `installed_plugins.json.backup.<timestamp>` before modifying
   - After linking, tell the user to restart Claude Code or run `/reload-plugins` to pick up changes
4. Log summary of all links created

Example output:
```
## DevKit Dev Link

Linking /Users/you/personal/agents-devkit as active DevKit...

Claude Code: ~/.claude/plugins/marketplaces/devkit-marketplace -> /Users/you/personal/agents-devkit
  Run /reload-plugins to activate.

Cursor: ~/.cursor/plugins/devkit -> /Users/you/personal/agents-devkit
  Restart Cursor to activate.

Codex CLI: ~/.devkit -> /Users/you/personal/agents-devkit
  Already a symlink (no change).

Done. Local edits now reflect immediately.
```

## Unlink

When `action=unlink`:

1. For each target platform (or the specified one):
   a. Check if the target path is a symlink
   b. If it is a symlink, remove it: `rm <target>`
   c. If a backup exists (`<target>.backup.*`), offer to restore the most recent one
   d. If no backup, log that the user should reinstall via the platform's official method
   e. Log: `Unlinked: <target>`
2. For Claude Code:
   - **Restore `~/.claude/plugins/installed_plugins.json`**: If a backup exists (`installed_plugins.json.backup.*`), restore the most recent one so the `installPath` points back to the original cache directory
   - Tell the user to reinstall: `/plugin install devkit@devkit-marketplace` then `/reload-plugins`
3. Log summary

Example output:
```
## DevKit Dev Unlink

Unlinking development symlinks...

Claude Code: removed symlink ~/.claude/plugins/marketplaces/devkit-marketplace
  Reinstall with: /plugin install devkit@devkit-marketplace

Cursor: removed symlink ~/.cursor/plugins/devkit
  Reinstall with: /add-plugin devkit

Done. Development links removed.
```

## Safety

- Never delete a real directory — only remove symlinks
- Always backup non-symlink directories before replacing
- Verify the current directory is a valid DevKit repo before linking
- Show the user exactly what will happen before making changes
