---
title: 'adk-validate'
description: 'Structural and content validator for the adk Claude Code plugin. Runs on every PR and via `npm run validate`.'
artifact_kind: bin
---

# adk-validate

Structural + content validator for the adk Claude Code plugin. Runs on every PR via the `validate` GitHub Actions job and locally via `npm run validate`.

## Checks

- `.claude-plugin/plugin.json` is valid and `name === "adk"`.
- For every `skills/<name>/`:
  - `SKILL.md` is present.
  - Frontmatter `name` matches the folder basename.
  - Frontmatter has a `description`.
  - `references/interaction-contract.md` exists and is byte-identical to `bin/canonical/interaction-contract.md`.
  - `references/how-it-works.md` exists.
  - `references/modes.md` exists.
  - `references/validator.md` exists (or the task-prefixed equivalent for migrated skills).
- For every `agents/<role>.md`: frontmatter `name` matches the basename (no `.md`).
- `hooks/hooks.json`, `.mcp.json`, and `settings.json` parse as valid JSON.

Also re-emits `skills-manifest.json` from the live tree on every run.

## Usage

```bash
node bin/adk-validate              # report; exit 0 if OK, 1 if any error
node bin/adk-validate --strict     # also fail on warnings
node bin/adk-validate --fix        # propagate canonical files (run sync-contracts) before checking
```

From an installed plugin the script is on `PATH`:

```bash
adk-validate
```

Or via npm script:

```bash
npm run validate
```

## Source

`bin/adk-validate` — Node.js CLI script.
