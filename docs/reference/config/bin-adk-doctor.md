---
title: 'adk-doctor'
description: 'adk-doctor'
artifact_kind: bin
---

# adk-doctor

adk-doctor

Health check. Reports presence of required CLI tools, gh auth status,
MCP server registrations (via `claude mcp ls`), env vars referenced by
.mcp.json, and the result of `bin/adk-validate`.

## Usage

```bash
node bin/adk-doctor
```

From an installed plugin the script is in `PATH`:

```bash
adk-doctor
```

## Source

`bin/adk-doctor` — Node.js CLI script.
