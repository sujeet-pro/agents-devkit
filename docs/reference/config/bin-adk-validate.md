---
title: 'adk-validate'
description: 'adk-validate'
artifact_kind: bin
---

# adk-validate

adk-validate

Structural + content validator for the adk plugin. Runs on every PR and via
`npm run validate`.

Checks:
  - .claude-plugin/plugin.json valid
  - For every skills/<name>/:
      * SKILL.md present
      * frontmatter has `name` matching folder
      * frontmatter has `description`
      * references/interaction-contract.md exists and is byte-identical to bin/canonical/interaction-contract.md
      * references/how-it-works.md exists
      * references/modes.md exists
      * references/validator.md exists (or task-prefixed equivalent for migrated skills)
  - For every agents-skills/adk-<name>: symlink resolves to skills/<name>
  - For every agents/<role>.md: frontmatter has `name` matching basename (no .md)
  - hooks/hooks.json parses
  - .mcp.json parses
  - settings.json parses

Also re-emits skills-manifest.json from the live tree.

Usage:
  bin/adk-validate              # report; exit 0 if OK, 1 if any error
  bin/adk-validate --strict     # also fail on warnings
  bin/adk-validate --fix        # propagate canonical files (run sync-contracts) before checking

## Usage

```bash
node bin/adk-validate
```

From an installed plugin the script is in `PATH`:

```bash
adk-validate
```

## Source

`bin/adk-validate` — Node.js CLI script.
