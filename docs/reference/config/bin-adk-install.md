---
title: 'adk-install'
description: 'adk-install'
artifact_kind: bin
---

# adk-install

adk-install

Local symlink installer for non-Claude agents (Cursor, Codex, Gemini, Antigravity, generic).
Symlinks `agents-skills/adk-<name>` from this plugin into the user's agent skill folders.

macOS only.

Usage:
  bin/adk-install                          # auto-detect installed agents, link into all of them
  bin/adk-install --target cursor          # only Cursor
  bin/adk-install --target cursor,codex    # multiple
  bin/adk-install --mode global            # link into ~/.cursor/skills/ etc. (default)
  bin/adk-install --mode project           # link into <cwd>/.cursor/skills/ etc.
  bin/adk-install --dry-run                # preview, no writes

## Usage

```bash
node bin/adk-install
```

From an installed plugin the script is in `PATH`:

```bash
adk-install
```

## Source

`bin/adk-install` — Node.js CLI script.
