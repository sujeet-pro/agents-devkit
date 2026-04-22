# Inventory rules — what counts as an artifact

Per the directory map in [`AGENTS.md`](../../../../AGENTS.md), enumerate every artifact in
this repo and map it to exactly one canonical doc page. New artifacts are detected on every
run; deleted artifacts produce a "propose deletion" entry in the report.

## Discovery commands

Use `git ls-files` so generated / temp / dependency files never leak into the inventory.

```bash
# Skills
git ls-files 'skills/*/SKILL.md'

# Subagents
git ls-files 'agents/*.md'

# Hooks (single file with multiple hook entries)
git ls-files 'hooks/hooks.json'

# Bin scripts (executables in PATH when plugin is enabled)
git ls-files 'bin/*' | grep -v '^bin/canonical/' | grep -v '^bin/internal/'

# MCP servers
git ls-files '.mcp.json'

# Monitors
git ls-files 'monitors/monitors.json'

# Top-level config + memory
git ls-files --max-depth 0 \
  | grep -E '\.(json5|json|md)$' \
  | grep -E '^(AGENTS|CLAUDE|GEMINI|README|REFERENCE|CONTRIBUTING|pagesmith\.config|settings|all|llms)'
```

## Artifact → page map

| Artifact source                                | Doc page                                        | Notes                                                                                |
| ---------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------ |
| `skills/<name>/SKILL.md`                       | `docs/reference/skill-<name>.md`                | One page per skill. Mirrors the existing convention from `bin/internal/generate-skill-docs.mjs`. |
| `skills/<name>/references/*.md`                | merged into the skill page as sub-sections      | Never separate pages — the skill page must be self-contained.                        |
| `agents/<role>.md`                             | `docs/reference/agents/<role>.md`               | One page per agent persona.                                                          |
| `hooks/hooks.json` entries                     | `docs/reference/config/hooks.md`                | Single page; one section per hook entry (`PreToolUse`, `PostToolUse`, `Stop`, etc.). |
| `bin/<script>`                                 | `docs/reference/config/bin-<script>.md`         | Skip files under `bin/canonical/` and `bin/internal/`.                               |
| `.mcp.json` server entries                     | `docs/reference/config/mcp-<server>.md`         | One page per server; expand `${ENV_VAR}` to the resolved env name (not the value).   |
| `monitors/monitors.json` entries               | `docs/reference/config/monitor-<name>.md`       | One page per monitor.                                                                |
| `pagesmith.config.json5`                       | `docs/reference/config/pagesmith-config.md`     | Document every key in use + link to the upstream schema.                             |
| `settings.json`                                | `docs/reference/config/settings.md`             | Plugin-level Claude defaults.                                                        |
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`        | `docs/concepts/memory-files.md`                 | One concept page covering all three; link to the source files.                       |

## Always ignore

- Anything under `node_modules/`, `.temp/`, `.git/`, `gh-pages/`, `.diagramkit/`,
  `.cache/`, `dist/`, `build/`.
- Symlinks under `agents-skills/` (folder-level mirrors of `skills/`).
- Files matched by `.gitignore`.

## Drift edge cases

| Situation                                           | Action                                                                             |
| --------------------------------------------------- | ---------------------------------------------------------------------------------- |
| New artifact, no doc page yet                       | Create the page from `page-template.md`.                                           |
| Artifact source was deleted, doc page still exists  | Propose deletion in the report; do not delete automatically unless `--mode fix`.   |
| Renamed artifact (`git diff --diff-filter=R`)       | Create new page, propose deletion of the old page, surface the rename in report.   |
| Multiple skills sharing one description (top router) | Each gets its own page; routers cross-link to every task they delegate to.        |
| External upstream (e.g. `node_modules/diagramkit/skills/*`) | Don't generate pages for them. Cross-link instead, prefixed with `node_modules/`. |
