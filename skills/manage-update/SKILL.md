---
name: manage-update
description: Use to update DevKit skills, agents, and guidelines from GitHub or from a local filesystem path
user_invocable: true
arguments:
  - name: source
    description: "Update source: github (default), fs"
    required: false
  - name: path
    description: "Local filesystem path when source=fs (required when source=fs)"
    required: false
  - name: dry-run
    description: "Preview changes without applying (default: false)"
    required: false
---

# Update DevKit

## Overview

Updates the DevKit installation with the latest skills, agents, guidelines, and scripts. Can pull from GitHub (default) or copy from a local filesystem path for contributor testing.

## Preflight

1. Verify `git`, `jq`, and `rsync` are available
2. If `source=github` (default): verify internet connectivity
3. If `source=fs`: verify the provided `path` exists and contains a valid DevKit repo (has `skills/` and `agents/` directories)

## GitHub Update (default)

When `source=github` or no source specified:

1. Locate the DevKit installation directory
   - Check `CLAUDE_DEVKIT_DIR` environment variable
   - Check `~/.claude/.devkit-manifest` for the recorded `devkit_dir`
   - Fall back to the directory containing this skill
2. Run `git pull --ff-only` in the DevKit directory
   - If ff-only fails, warn the user about local modifications
3. Run `zsh scripts/sync-sources.zsh` to sync copy-type upstream sources (diagramkit, superpowers)
4. Check ref-type sources (pagesmith) for updates and report changes
5. Run `zsh scripts/setup-node.zsh` to update Node.js dependencies
6. Run `zsh install.zsh --skip-checks` to re-link everything
7. Display summary of what changed

## Filesystem Update

When `source=fs`:

<HARD-GATE>
The `path` argument is required when `source=fs`. Abort if not provided.
</HARD-GATE>

1. Validate the source path exists and contains DevKit files
2. Copy files from the source path to the DevKit installation:
   ```
   rsync -a --exclude='.git' --exclude='node_modules' --exclude='.temp' --exclude='lib/node_modules' <path>/ <devkit-dir>/
   ```
   Note: This copies files, NOT symlinks. This is intentional for contributor testing.
3. Run `zsh scripts/setup-node.zsh` to update Node.js dependencies
4. Run `zsh install.zsh --skip-checks` to re-link everything
5. Display summary of what changed

## Dry Run

When `dry-run=true`:

- For GitHub: run `git fetch` and show `git log HEAD..origin/main --oneline`
- For filesystem: run `rsync -an` (dry-run mode) and show what would change
- Do not apply any changes

## Output

```
## DevKit Update Summary

Source: github | fs (<path>)
Mode: applied | dry-run

### Changes
- N skills updated
- N agents updated
- N guidelines updated
- N scripts updated
- Upstream sources: diagramkit (synced/skipped), superpowers (synced/skipped)

### Actions Taken
- git pull: <result>
- sync-sources: <result>
- install: <result>
```

## Script Alternative

This skill can also be run as a standalone script:

```bash
zsh scripts/update-devkit.zsh                    # GitHub update
zsh scripts/update-devkit.zsh --fs /path/to/repo # Filesystem update
zsh scripts/update-devkit.zsh --dry-run           # Preview only
```
